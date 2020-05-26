import os
from scoreboard import create_app, db
from flask_migrate import Migrate
from scoreboard.models import User, Role, Permission, Basic
from flask_cors import CORS

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
