from flask import g, render_template, redirect, request, url_for, flash, abort, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm, PasswordResetForm
import json


#访问此蓝本之前需要做的事情
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()


@auth.route('/login', methods=['GET', 'POST'])
def login():
    # form = LoginForm()
    # if form.validate_on_submit():
    #     user = User.query.filter_by(number=form.number.data.lower()).first()
    #     if user is not None and user.verify_password(form.password.data):
    #         login_user(user, form.remember_me.data)
    #         next = request.args.get('next')
    #         if next is None or not next.startswith('/'):
    #             next = url_for('main.index')
    #         return redirect(next)
    #     flash('Invalid email or password.')
    # return render_template('auth/login.html', form=form)
    print("successfully!")
    if(request.get_data(as_text=True)):
        data = request.get_data(as_text=True)  # request.get_data()接收数据，数据格式为bytes，加上as_text=True参数后就变成Unicode了
        print(data)
        data = json.loads(data)
        print(data)
        print(type(data))
        number = data['username']
        password = data['password']
        user = User.query.filter_by(number=number).first()
        if user is not None and user.verify_password(password):
            login_user(user)
            if(user.name == 'Administrator'):
                userList = {
                    'token': user.generate_auth_token(3000),
                    'role': 'Caption',
                    'name': user.name,
                }
            else:
                userList = {
                    'token': user.generate_auth_token(3000),
                    'role': 'User',
                    'name': user.name,
                }
            response = {
                'code': 200,
                'data': {
                    'userList': userList
                }
            }
            print(response)
            return jsonify(response)
        else:
            response = {
                'code': -1,
                'data': {
                    'msg': '密码错误',
                    'status': 'fail'
                }
            }
            return jsonify(response)
    else:
        print('hahhahahhahhaha')
        response = {
            'code': 401
        }
        return jsonify(response)
        # abort(401)



#个人理解：如果前后端采用token方式维持登录状态，那么就不需要采用Flask-Login这个模块来管理登录状态了
@auth.route('/logout', methods=['GET', 'POST'])
# @login_required
def logout():
    # logout_user()
    g.current_user = None
    return {
        'code': 200,
        'data': {
            'userList': ""
        }
    }
    # flash('You have been logged out.')
    # return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(number=form.number.data.lower(), name=form.name.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Register successfully!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

    # print("successfully!")
    # data = request.get_data(as_text=True)  #request.get_data()接收数据，数据格式为bytes，加上as_text=True参数后就变成Unicode了
    # data = json.loads(data)
    # print(data)
    # print(type(data))
    # number = data['number']
    # name = data['name']
    # password = data['password']
    # if User.query.filter_by(number=number).first() is not None:
    #     abort(400)  # existing user
    # user = User(number=number, name=name, password=password)
    # db.session.add(user)
    # db.session.commit()
    # return jsonify({'name': user.name})


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(number=form.number.data.lower()).first()
        if user:
            if User.reset_password(user.id, new_password=form.password.data):
                db.session.commit()
                flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)
