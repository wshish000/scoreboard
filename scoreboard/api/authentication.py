from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from ..models import User
from . import api
from .errors import unauthorized, forbidden

#采用auth认证方式
auth = HTTPBasicAuth()


#没带密码验证token，带密码验证密码
@auth.verify_password
def verify_password(number_or_token, password):
    if number_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(number_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(number=number_or_token.lower()).first()
    if not user:
        return False
    #设置当前用户
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    pass


#如果使用此处的登出会有bug
@api.route('/logout', methods=['GET', 'POST'])
def logout():
    g.current_user = None
    return {
        'code': 200,
        'data': {
            'userList': ""
        }
    }


#获取token，相当于登录
@api.route('/tokens', methods=['POST'])
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')

    if g.current_user.name == 'Administrator':
        userList = {
            'token': g.current_user.generate_auth_token(expiration=360),
            'role': 'Administrator',
            'name': g.current_user.name,
        }
    else:
        userList = {
            'token': g.current_user.generate_auth_token(expiration=360),
            'role': g.current_user.role.name,
            'name': g.current_user.name,
        }
    response = {
        'code': 200,
        'data': {
            'userList': userList
        }
    }
    return jsonify(response)
