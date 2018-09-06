var playlist = new Vue({
    el: '#playlist',
    delimiters: ['[[', ']]'],
    data: {
        playlistName: '',
    },
    methods: {
        submit: function() {
            this.$validator.validateAll().then((result) => {
                if (result) {
                    document.querySelector('form#save').submit()
                }
            });
        },
    },
});

const sortable = new Sortable.default(document.querySelector('table.playlist'), {
    draggable: 'tr.track',
    mirror: {
        constrainDimensions: true,
    },
});