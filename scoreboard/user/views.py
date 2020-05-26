from flask_login import login_required, current_user
from flask import render_template, redirect, url_for, abort, flash, request, current_app, make_response
from . import user
from flask_sqlalchemy import get_debug_queries
from .forms import EditProfileForm, AddForm
from .. import db
from ..models import User, Permission, Role
from ..decorators import admin_required, permission_required, caption_required


@user.route('/info', methods=['GET', 'POST'])
@login_required
def info():
    print("successfully!")
    data = request.get_data(as_text=True)  # request.get_data()接收数据，数据格式为bytes，加上as_text=True参数后就变成Unicode了
    data = json.loads(data)
    print(data)
    token = data['token']
    user = User.verify_auth_token(token)
    print(user.name)
    print(user.role.name)
    userList = {
        roles: [user.role.name],
        name: user.name,
        avatar:'https://wx.qlogo.cn/mmopen/vi_32/un2HbJJc6eiaviaibvMgiasFNlVDlNOb9E6WCpCrsO4wMMhHIbsvTkAbIehLwROVFlu8dLMcg00t3ZtOcgCCdcxlZA/132'
    }
    response = {
        'code': 200,
        'data': {
            'userList': userList
        }
    }
    return jsonify(response)
@user.route('/user-list', methods=['GET', 'POST'])
@login_required
@caption_required
def user_list():
    users = User.query.all()
    return render_template('user_list.html', users=users)


@user.route('/delete/<int:id>', methods=['GET', 'POST'])
@login_required
@caption_required
def delete(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('Delete successfully!')
    users = User.query.all()
    return render_template('user_list.html', users=users)


@user.route('/add', methods=['GET', 'POST'])
@login_required
@caption_required
def add():
    form = AddForm()
    if form.validate_on_submit():
        user = User(number=form.number.data.lower(), name=form.name.data, password=form.password.data, role=Role.query.get(form.role.data), born_time=form.born_time.data,
                    military_time=form.military_time.data, sex=form.sex.data, height=form.height.data, weight=form.weight.data, level=form.level.data, job=form.job.data)
        db.session.add(user)
        db.session.commit()
        flash('Add successfully!')
        users = User.query.all()
        return redirect(url_for('user.user_list', users=users))
    return render_template('add_user.html', form=form)


@user.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@caption_required
def edit_profile(id):
    user = User.query.get_or_404(id)
    form = EditProfileForm(user=user)
    if form.validate_on_submit():
        user.number = form.number.data
        user.name = form.name.data
        user.role = Role.query.get(form.role.data)

        user.born_time = form.born_time.data
        user.military_time = form.military_time.data
        user.sex = form.sex.data
        user.height = form.height.data
        user.weight = form.weight.data
        user.level = form.level.data
        user.job = form.job.data

        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('main.index'))
    form.number.data = user.number
    form.name.data = user.name
    form.role.data = user.role_id

    form.born_time = user.born_time
    form.military_time = user.military_time
    form.sex = user.sex
    form.height = user.height
    form.weight = user.weight
    form.level = user.level
    form.job = user.job

    return render_template('edit_profile.html', form=form, user=user)
