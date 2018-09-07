import time

from flask import Flask, request, render_template, redirect, session, url_for, g, jsonify, abort
from flask_session import Session

from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, HiddenField
from wtforms.validators import DataRequired, NumberRange

import spotipy
from spotipy import oauth2

app = Flask(__name__)
app.config.from_pyfile('config.py')
Session(app)

sp_oauth = oauth2.SpotifyOAuth(client_id=app.config.get('SPOTIPY_CLIENT_ID'),
                               client_secret=app.config.get('SPOTIPY_CLIENT_SECRET'),
                               redirect_uri=app.config.get('SPOTIPY_REDIRECT_URI'),
                               scope='playlist-modify-public')


def is_valid_raw_data(message: str='request is not valid'):
    def _is_valid_raw_data(form, field):
        if field.raw_data is None or not all(field.raw_data):
            raise ValueError(message)
    return _is_valid_raw_data


class ArtistForm(FlaskForm):
    artist_id = HiddenField(validators=[is_valid_raw_data()])
    track_count = IntegerField(NumberRange(min=1, max=10), validators=[is_valid_raw_data()])


class PlaylistForm(FlaskForm):
    track_id = HiddenField(validators=[is_valid_raw_data()])
    playlist_name = StringField('プレイリスト名', validators=[DataRequired()])


@app.before_request
def before_request():
    if request.path == url_for('login'):
        return

    if session.get('token_info'):
        if session['token_info']['expires_at'] < int(time.time()):
            try:
                refresh_token = session['token_info']['refresh_token']
                session['token_info'] = sp_oauth.refresh_access_token(refresh_token=refresh_token)
            except spotipy.oauth2.SpotifyOauthError:
                return redirect(url_for('login'))
        g.access_token = session['token_info']['access_token']
    else:
        return redirect(url_for('login'))


@app.route('/')
def top():
    return render_template('top.html', form=ArtistForm())


@app.route('/login')
def login():
    if request.args.get('code'):
        try:
            session['token_info'] = sp_oauth.get_access_token(code=request.args.get('code'))
        except spotipy.oauth2.SpotifyOauthError:
            return redirect(url_for('login'))

    if session.get('token_info'):
        return redirect(url_for('top'))

    g.access_token = None
    return render_template('login.html', auth_url=sp_oauth.get_authorize_url())


@app.route('/playlist', methods=['POST'])
def playlist():
    tracks = []
    artist_form = ArtistForm()
    if not artist_form.validate_on_submit():
        abort(400)
    try:
        sp = spotipy.Spotify(auth=g.access_token)
        for artist_id, track_count in zip(artist_form.artist_id.raw_data, artist_form.track_count.raw_data):
            top_tracks = sp.artist_top_tracks(artist_id=artist_id, country='JP')
            tracks.extend(top_tracks['tracks'][0:int(track_count)])
    except spotipy.client.SpotifyException:
        abort(400)
    return render_template('playlist.html', tracks=tracks, form=PlaylistForm())


@app.route('/save', methods=['POST'])
def save():
    playlist_ = {}
    playlist_form = PlaylistForm()
    if not playlist_form.validate_on_submit():
        abort(400)
    try:
        sp = spotipy.Spotify(auth=g.access_token)
        user = sp.me()
        playlist_ = sp.user_playlist_create(user=user['id'], name=playlist_form.playlist_name.data)
        sp.user_playlist_add_tracks(user=user['id'], playlist_id=playlist_['id'], tracks=playlist_form.track_id.raw_data)
    except spotipy.client.SpotifyException:
        abort(400)
    return render_template('save.html', playlist=playlist_)


@app.route('/api/artists', methods=['GET'])
def api_artists():
    sp = spotipy.Spotify(auth=g.access_token)
    limit = request.args['limit'] if request.args.get('limit') else 20
    artists_ = sp.search(q=request.args.get('q'), limit=limit, type='artist', market='JP')
    artists = []
    for artist_ in artists_['artists']['items']:
        artists.append({'id': artist_['id'], 'name': artist_['name']})
    return jsonify(artists)


if __name__ == '__main__':
    app.run(debug=True)
