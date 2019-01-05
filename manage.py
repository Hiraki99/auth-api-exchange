import sys
from flask_script import Manager,Command
from flask_migrate import Migrate, MigrateCommand
from flask_sqlalchemy import SQLAlchemy
# from server import app,db
from AuthAPI import app,db

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def initdb():
    "Just say hello"
    print('Init Database')
    db.create_all()

if __name__ == '__main__':
    manager.run()
    
