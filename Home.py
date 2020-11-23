from flask import Flask, Response,render_template, url_for, session,redirect
import cv2
from authlib.integrations.flask_client import OAuth
from LoginChecker import login_required

from flask_ngrok import run_with_ngrok

app = Flask(__name__)
app.secret_key = 'random secret'
#video = cv2.VideoCapture(0)
run_with_ngrok(app)
#oauth config
oauth = OAuth(app)
oauth.register(
    name='google',
    client_id="870438341559-8ajik00ohl2ok041nk76chntpid1qran.apps.googleusercontent.com",
    client_secret= "qgx5yH4yvSiLjUF5xUZUJdnN",
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)



@app.route('/', methods=['GET'])
def index():
    email = dict(session).get('email', None)
    return render_template('index.html')

@app.route('/video')
#@login_required
def videoPage():
    email = dict(session).get('email', None)
    return render_template('Video.html')

def gen(video):
    while True:
        success, image = video.read()
        ret, jpeg = cv2.imencode('.jpg', image)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    global video
    return Response(gen(video),mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/login')
def login():
    google = oauth.create_client('google.com')
    redirect_uri = url_for('authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = oauth.google.authorize_access_token()
    resp = oauth.google.get('userinfo')
    user_info = resp.json()
    # do something with the token and profile
    session['email'] = user_info['email']
    return redirect('/')

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

app.run()
