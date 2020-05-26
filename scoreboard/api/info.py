from flask import g, jsonify, request, current_app, url_for
from . import api
from ..models import User, Role
from .. import db


#获取用户信息列表
@api.route('/info/getList', methods=['GET', 'POST'])
def getList():
    name = request.args.get('name')
    page = request.args.get('page')
    limit = request.args.get('limit')
    if not page:
        page = 1
    if not limit:
        limit = 20
    page = int(page)
    limit = int(limit)

    if name:
        total = User.query.filter_by(name=name).count()
        pagination = User.query.filter_by(name=name).paginate(page, per_page=limit, error_out=False)
        users = pagination.items
        userList = []
        for user in users:
            userList.append(user.to_json())
        return {
            'code': 200,
            'data': {
                'total': total,
                'memberList': userList
            }
        }

    total = User.query.order_by(User.id.desc()).count()
    pagination = User.query.order_by(User.id.desc()).paginate(page, per_page=limit, error_out=False)
    users = pagination.items
    userList = []
    for user in users:
        userList.append(user.to_json())
    response = {
        'code': 200,
        'data': {
            'total': total,
            'memberList': userList
        }
    }
    return jsonify(response)


#修改某用户的信息
@api.route('info/edit', methods=['GET', 'POST'])
def edit():
    id = request.args.get('id')
    number = request.args.get('number')
    name = request.args.get('name')
    job = request.args.get('job')
    level = request.args.get('level')
    age = request.args.get('age')
    height = request.args.get('height')
    weight = request.args.get('weight')

    user = User.query.get_or_404(int(id))

    user.number = number
    user.name = name
    user.job = job
    user.level = level
    user.age = int(age)
    user.height = int(height)
    user.weight = int(weight)
    db.session.add(user)
    db.session.commit()

    return {
        'code': 200,
        'data': {
            'message': '修改成功'
        }
    }


#添加用户
@api.route('/info/add', methods=['GET', 'POST'])
def add():
    number = request.args.get('number')
    name = request.args.get('name')
    job = request.args.get('job')
    level = request.args.get('level')
    age = request.args.get('age')
    height = request.args.get('height')
    weight = request.args.get('weight')

    user = User(number=number, name=name, password='123456',
                role=Role.query.get(1), height=height,
                weight=weight, level=level, job=job, age=age)
    db.session.add(user)
    db.session.commit()

    return {
        'code': 200,
        'data': {
            'message': '添加成功'
        }
    }


#删除用户
@api.route('/info/remove', methods=['GET', 'POST'])
def remove():
    id = request.args.get('id')
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return {
        'code': 200,
        'data': {
            'message': '删除成功'
        }
    }


#批量删除用户
@api.route('info/batchremove', methods=['GET', 'POST'])
def batchremove():
    ids = request.args.get('ids')
    for id in ids.split(','):
        user = User.query.get_or_404(id)
        db.session.delete(user)
    db.session.commit()
    return {
        'code': 200,
        'data': {
            'message': '批量删除成功'
        }
    }


#获取登录用户的信息
@api.route('/info/getInfo', methods=['GET', 'POST'])
def getInfo():
    user = g.current_user
    userList = {
        'roles': [g.current_user.role.name],
        'name': user.name,
        'avatar': ''
    }
    response = {
        'code': 200,
        'data': {
            'userList': userList
        }
    }
    return jsonify(response)


#登录用户获取详细信息
@api.route('/info/getPersonalInfo', methods=['GET', 'POST'])
def getPersonalInfo():
    user = g.current_user
    print(user.number, user.name, user.job, user.level, user.age, user.height, user.weight)
    response = {
        'code': 200,
        'data': {
            'number': user.number,
            'name': user.name,
            'job': user.job,
            'level': user.level,
            'age': user.age,
            'height': user.height,
            'weight': user.weight
        }
    }
    return jsonify(response)



#用户自行重设密码
@api.route('/info/reset_password', methods=['GET', 'POST'])
def reset_password():
    password = request.args.get('password')
    newpassword = request.args.get('newpassword')
    surepassword = request.args.get('surepassword')
    user = g.current_user
    if user.verify_password(password):
        User.reset_password(user.id, new_password=newpassword)
        db.session.commit()
        response = {
            'code': 200,
            'data': {
                'message': '修改密码成功'
            }
        }
        return jsonify(response)


#管理员重置用户密码
@api.route('/info/changePassword', methods=['GET', 'POST'])
def changePassword():
    name = request.args.get('name')
    newpassword = request.args.get('newpassword')
    surepassword = request.args.get('surepassword')
    user = User.query.filter_by(name=name).first()
    User.reset_password(user.id, new_password=newpassword)
    db.session.commit()
    response = {
        'code': 200,
        'data': {
            'message': '修改密码成功'
        }
    }
    return jsonify(response)


#管理员重置用户角色
@api.route('/info/changeRole', methods=['GET', 'POST'])
def changeRole():
    name = request.args.get('name')
    role = request.args.get('role')
    user = User.query.filter_by(name=name).first()
    role2 = Role.query.filter_by(id=int(role)).first()
    user.role = role2
    db.session.commit()
    response = {
        'code': 200,
        'data': {
            'message': '修改角色成功'
        }
    }
    return jsonify(response)
