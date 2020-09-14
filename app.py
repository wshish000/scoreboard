import os
from scoreboard import create_app, db
from flask_migrate import Migrate
from scoreboard.models import User, Role, Permission, Basic
from flask_cors import CORS

#logging的妙用
# import logging
# logging.basicConfig(level=logging.DEBUG,#控制台打印的日志级别
#     filename='log_new.log',  # 将日志写入log_new.log文件中
#     filemode='a',##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
#     #a是追加模式，默认如果不写的话，就是追加模式
#     format=
#     '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
#     #日志格式
#     )

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
CORS(app, supports_credentials=True)
migrate = Migrate(app, db)
print(migrate)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role, Permission=Permission, Basic=Basic)


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
