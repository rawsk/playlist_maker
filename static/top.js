var artists = new Vue({
    el: '#artists',
    delimiters: ['[[', ']]'],
    data: {
        artists: [], //[{id, name}]
        newArtistId: '',
    },

    methods: {

        artistAppend: function() {
            if (!this.newArtistId) {
                return;
            }
            let newArtistName = document.querySelector('#new_artist_name');
            this.artists.push({
                name: newArtistName.value,
                id: this.newArtistId
            });
            newArtistName.value = '';
            this.newArtistId = '';
        },

        artistRemove: function(index) {
            this.artists.splice(index, 1);
        },

        removeNewArtistId: function(event) {
            let keyCode = event.keyCode;
            if (([8, 9, 32].indexOf(keyCode) >= 0) || (48 <= keyCode && keyCode <= 111) || (186 <= keyCode && keyCode <= 226)) {
                this.newArtistId = '';
            }
        },

        submit: function() {
            this.$validator.validateAll().then((result) => {
                if (result) {
                    document.querySelector('form#playlist').submit();
                }
            });
        },

    }
});

var request = superagent;
function artistSearch(text) {
    var self = this;
    request
        .get('/api/artists')
        .query({q: text})
        .end(function(err, res){
            self.clearSuggestArea();
            artistIds = [];
            artistNames = [];
            for (let artist of res.body) {
                artistIds.push(artist.id);
                artistNames.push(artist.name);
            }
            self.candidateList = artistNames;
            var resultList = self._search(text);
            if (resultList.length != 0) {
                self.createSuggestArea(resultList);
            }
            var suggests = document.querySelectorAll('#suggest > div');
            for (let i = 0; i < suggests.length; i++) {
                suggests[i].setAttribute('data-artist-id', artistIds[i]);
                suggests[i].addEventListener('click', function () { artists.newArtistId = this.dataset.artistId; }, false);
            }
        });
}

function startSuggest() {
    new Suggest.Local(
        'new_artist_name', // 入力のエレメントID
        'suggest',         // 補完候補を表示するエリアのID
        [],                // 補完候補の検索対象となる配列
        {dispMax: 10, interval: 100, hookBeforeSearch: artistSearch}
    );
}

window.addEventListener ?
    window.addEventListener('load', startSuggest, false) :
    window.attachEvent('onload', startSuggest);

document.querySelector('#new_artist_name').addEventListener('keydown', function(event){
    if (event.keyCode === 13) {
        let suggestArtist = document.querySelector('#suggest > div.select');
        if (suggestArtist != null && suggestArtist.dataset.artistId) {
            artists.newArtistId = suggestArtist.dataset.artistId;
        }
    }
}, false);
