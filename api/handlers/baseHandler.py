from tornado.web import RequestHandler
from tornado.gen import *
import simplejson as json
import jwt
from config import Settings
from api.core.user import UserHelper

settings=Settings()
class BaseHandler(RequestHandler):
    def __init__(self, application , request, **kwargs):
        super().__init__(application, request, **kwargs)

        self.jwt_options = {
            'verify_signature': True,
            'verify_exp': True,
            'verify_nbf': False,
            'verify_iat': True,
            'verify_aud': False
        }
        self.db = self.settings['db']
        self._uh = UserHelper(db=self.db)

    @coroutine
    def create_auth_token(self, id):
        print(settings.JwtAlgorithm)
        jwt_token = jwt.encode({"id": str(id)}, key=settings.CookieSecret, algorithm=settings.JwtAlgorithm)
        raise Return(jwt_token)

    @coroutine
    def set_auth_token_header(self, authToken=None):
        if authToken:
            self.set_secure_cookie(settings.AppName, authToken)
        self.set_header('Authorization', 'Bearer {}'.format(authToken))

    @coroutine
    def validate_auth_token(self, authToken):
        payload = jwt.decode(authToken, key=settings.CookieSecret, algorithm='HS256', verify=True, options=self.jwt_options)
        raise Return(payload)

    @coroutine
    def jwt_auth(self):
        auth = self.request.headers.get('Authorization')

        if auth:
            parts = auth.split()
            if parts[0].lower() != 'bearer':
                self._transforms = []
                self.set_status(401)
                self.write("invalid header authorization")
                self.finish()
            elif len(parts) == 1:
                self._transforms = []
                self.set_status(401)
                self.write("invalid header authorization")
                self.finish()
            elif len(parts) > 2:
                self._transforms = []
                self.set_status(401)
                self.write("invalid header authorization")
                self.finish()
            else:
                payload = jwt.decode(
                    parts[1],
                    self.settings['cookie_secret'],
                    options=self.jwt_options
                )
                raise Return(payload)

        else:
            self._transforms = []
            self.write("Missing authorization")
            self.finish()

    @coroutine
    def get_current_user(self):
        (payload)= yield self.jwt_auth()
        if payload:
            user = yield self._uh.getUserByUserId(payload['id'])
            if user:
                self._user = user
                raise Return(user)
    @coroutine
    def prepare(self):
        self._user = yield self.current_user
        if self.request.method == 'POST':
            self.args = json.loads(self.request.body)

    @coroutine
    def set_default_headers(self):
        print("setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "localhost")
        self.set_header("Access-Control-Allow-Headers", "content-type")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    @coroutine
    def options(self):
        # no body
        self.set_status(204)
        self.finish()

    @coroutine
    def set_authentication_headers(self, authToken):
        self.set_header('Authorization', 'Bearer {}'.format(authToken))

    @coroutine
    def authorize(self, user_profile):
        self.current_user = user_profile
        auth_token = yield self.create_auth_token(user_profile.UserId)
        self._user = user_profile
        self.set_cookie(settings.AppName, auth_token)
        self.set_auth_token_header(auth_token)
        raise Return(auth_token)
