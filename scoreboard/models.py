from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, request, url_for
from flask_login import UserMixin, AnonymousUserMixin
from scoreboard.exceptions import ValidationError
from . import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


#权限
class Permission:
    READ = 1
    WRITE = 2
    MODERATE = 4
    ADMIN = 8

#角色表
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        roles = {
            'User': [Permission.READ],  # 查看成绩
            'Captain': [Permission.READ, Permission.WRITE],  # 录入成绩与人员
            'Moderator': [Permission.READ, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.READ, Permission.WRITE, Permission.MODERATE, Permission.ADMIN]  # 所有权限
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def __repr__(self):
        return '<Role %r>' % self.name

#用户表
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(64), unique=True, index=True)  # 证件号
    name = db.Column(db.String(64), unique=True, index=True)  # 姓名
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)

    born_time = db.Column(db.Date(), default=datetime.utcnow)  # 出生年月
    military_time = db.Column(db.Date(), default=datetime.utcnow)  # 入伍年月
    age = db.Column(db.Integer)
    sex = db.Column(db.Integer, default=1)  # 性别
    height = db.Column(db.Integer)
    weight = db.Column(db.Float(2))
    level = db.Column(db.String(64))  # 级别
    job = db.Column(db.String(64))  # 岗位
    tuan = db.Column(db.Integer, default=0)
    ying = db.Column(db.Integer, default=0)
    lian = db.Column(db.Integer, default=0)

    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    basics = db.relationship('Basic', backref='author', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.number == current_app.config['BOARD_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def reset_password(id, new_password):
        user = User.query.get(int(id))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def to_json(self):
        json_user = {
            # 'url': url_for('api.get_user', id=self.id),
            'id': self.id,
            'number': self.number,
            'name': self.name,
            'job': self.job,
            'age': self.age,
            'level': self.level,
            'height': self.height,
            'weight': self.weight
        }
        return json_user

    def __repr__(self):
        return '<User %r>' % self.name


#匿名用户
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#3000米跑
class LongRunStandard(db.Model):
    __tablename__ = 'longrunstandards'
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    score = db.Column(db.Integer)


#引体向上
class PullUpStandard(db.Model):
    __tablename__ = 'pullupstandards'
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    score = db.Column(db.Integer)


#仰卧起坐
class SitUpStandard(db.Model):
    __tablename__ = 'situpstandards'
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    score = db.Column(db.Integer)


#30米*2折返跑
class RetraceStandard(db.Model):
    __tablename__ = 'retracestandards'
    id = db.Column(db.Integer, primary_key=True)
    age = db.Column(db.Integer)
    duration = db.Column(db.Float)
    score = db.Column(db.Integer)


#基础体能成绩表
class Basic(db.Model):
    __tablename__ = 'basics'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    week = db.Column(db.Integer, index=True)
    name = db.Column(db.String(64))
    sit_up = db.Column(db.Integer)
    pull_up = db.Column(db.Integer)
    long_run = db.Column(db.Integer)
    long_run_min = db.Column(db.Integer)
    long_run_sec = db.Column(db.Integer)
    retrace = db.Column(db.Float(2))
    score = db.Column(db.Integer)
    remark = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    score = db.Column(db.Integer)
    sit_up_score = db.Column(db.Integer)
    pull_up_score = db.Column(db.Integer)
    long_run_score = db.Column(db.Integer)
    retrace_score = db.Column(db.Integer)

    def to_json(self):
        json_basic = {
            # 'url': url_for('api.get_post', id=self.id),
            'id': self.id,
            'week': self.week,
            'name': self.name,
            'situp': self.sit_up,
            'pullup': self.pull_up,
            'longrun': self.long_run,
            'longrun_min': self.long_run_min,
            'longrun_sec': self.long_run_sec,
            'retrace': self.retrace,
            'remark': self.remark,
            'score': self.score,
            # 'author_url': url_for('api.get_user', id=self.author_id),
        }
        return json_basic

    @staticmethod
    def from_json(json_basic):
        body = json_basic.get('body')
        if body is None or body == '':
            raise ValidationError('basic does not have a body')
        return Basic(body=body)

