import time

from flask import Flask, request, render_template, redirect, session, url_for, g, jsonify
from flask_session import Session

from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, HiddenField
from wtforms.validators import DataRequired

import spotipy
from spotipy import oauth2
from spotipy import util

app = Flask(__name__)
app.config.from_pyfile('config.py')
Session(app)

sp_oauth = oauth2.SpotifyOAuth(client_id=app.config.get('SPOTIPY_CLIENT_ID'),
                               client_secret=app.config.get('SPOTIPY_CLIENT_SECRET'),
                               redirect_uri=app.config.get('SPOTIPY_REDIRECT_URI'),
                               scope='playlist-modify-public')


class ArtistForm(FlaskForm):
    artist_id = HiddenField()


class PlaylistForm(FlaskForm):
    track_id = HiddenField()
    playlist_name = StringField('プレイリスト名')


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
    artist_form = ArtistForm()
    sp = spotipy.Spotify(auth=g.access_token)
    tracks = []
    for artist_id in artist_form.artist_id.raw_data:
        top_tracks = sp.artist_top_tracks(artist_id=artist_id, country='JP')
        tracks.extend(top_tracks['tracks'][0:3])
    return render_template('playlist.html', tracks=tracks, form=PlaylistForm(playlist_name='test'))


@app.route('/save', methods=['POST'])
def save():
    playlist_form = PlaylistForm()
    sp = spotipy.Spotify(auth=g.access_token)
    user = sp.me()
    playlist_ = sp.user_playlist_create(user=user['id'], name=playlist_form.playlist_name.data)
    sp.user_playlist_add_tracks(user=user['id'], playlist_id=playlist_['id'], tracks=playlist_form.track_id.raw_data)
    return render_template('save.html', playlist=playlist_)


@app.route('/api/artists', methods=['GET'])
def api_artists():
    sp = spotipy.Spotify(auth=g.access_token)
    artists_ = sp.search(q=request.args.get('q'), type='artist')
    artists = []
    for artist_ in artists_['artists']['items']:
        artists.append({'id': artist_['id'], 'name': artist_['name']})
    return jsonify(artists)


if __name__ == '__main__':
    app.run(debug=True)
