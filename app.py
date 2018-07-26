from flask import Flask, request, render_template


app = Flask(__name__)


@app.route('/')
def top():
    return render_template('top.html')


@app.route('/playlist', methods=['POST'])
def playlist():
    # Get an Artist’s Top Tracks
    return render_template('playlist.html')


@app.route('/save', methods=['POST'])
def save():
    # Create a Playlist
    return render_template('save.html')


if __name__ == '__main__':
    app.run(debug=True)
