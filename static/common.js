var artists = new Vue({
    el: '#artists',
    delimiters: ['[[', ']]'],
    data: {
        artists: [
            {name: 'RADWIMPS', id: '1EowJ1WwkMzkCkRomFhui7'},
            {name: 'The Chainsmokers', id: '69GGBxA162lTqCwzJG5jLp'}
        ]
    },
    methods: {

        append: function() {
            this.artists.push({
                name: document.querySelector('#new_artist_name').value,
                id: '1EowJ1WwkMzkCkRomFhui7'
            });
            document.querySelector('#new_artist_name').value = '';
        },

        remove: function(index) {
            this.artists.splice(index, 1);
        }

    }
});

var request = superagent;
function artistSearch(text) {
    var self = this;
    request
        .get("/api/artists")
        .query({q: text})
        .end(function(err, res){
            self.clearSuggestArea();
            artist_names = []
            for (var artist of res.body) {
                artist_names.push(artist.name)
            }
            self.candidateList = artist_names;
            var resultList = self._search(text);
            if (resultList.length != 0) self.createSuggestArea(resultList);
        });
}

function startSuggest() {
    new Suggest.Local(
        "new_artist_name", // 入力のエレメントID
        "suggest",         // 補完候補を表示するエリアのID
        [],                // 補完候補の検索対象となる配列
        {dispMax: 10, interval: 1000, hookBeforeSearch: artistSearch}
    );
}

window.addEventListener ?
    window.addEventListener('load', startSuggest, false) :
    window.attachEvent('onload', startSuggest);
