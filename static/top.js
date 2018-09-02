var artists = new Vue({
    el: '#artists',
    delimiters: ['[[', ']]'],
    data: {
        artists: [],
        newArtistId: ''
    },
    methods: {

        artistAppend: function() {
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

        removeNewArtistId: function() {
            this.newArtistId = '';
        }

    }
});

function saveArtistId() {
    artists.newArtistId = this.dataset.artistId;
}

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
            if (artistNames.length != 0) {
                self.createSuggestArea(artistNames);
            }
            var suggests = document.querySelectorAll('#suggest > div');
            for (let i = 0; i < suggests.length; i++) {
                suggests[i].setAttribute('data-artist-id', artistIds[i]);
                suggests[i].addEventListener('click', saveArtistId, false);
            }
        });
}

function startSuggest() {
    new Suggest.Local(
        'new_artist_name', // 入力のエレメントID
        'suggest',         // 補完候補を表示するエリアのID
        [],                // 補完候補の検索対象となる配列
        {dispMax: 10, interval: 1000, hookBeforeSearch: artistSearch}
    );
}

window.addEventListener ?
    window.addEventListener('load', startSuggest, false) :
    window.attachEvent('onload', startSuggest);
