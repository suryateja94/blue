import tornado.ioloop
import tornado.web
from urls import urlpatterns
from db import Database
from config import Settings
settings = Settings()
class Application(object):
    def __init__(self):
        self.database = Database()
        self.initiateApp()

    def initiateApp(self):
        app = self.make_app()
        app.listen(8888)

    def make_app(self):
        db = self.database.get_motor_connection()
        return tornado.web.Application(urlpatterns,
                                       db = db,
                                       cookie_secret=settings.CookieSecret,
                                       debug=settings.Debug,
                                       key_version=settings.KeyVersion,
                                       version=settings.Version
                                       )

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

if __name__ == "__main__":
    app = Application()
    print("server is running on 8888")
    tornado.ioloop.IOLoop.current().start()
    io_loop = tornado.ioloop.IOLoop.instance()