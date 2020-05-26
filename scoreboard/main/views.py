from flask_login import login_required, current_user
from flask import render_template, redirect, url_for, abort, flash, request, current_app, make_response
from . import main
from flask_sqlalchemy import get_debug_queries
from .forms import BasicForm
from .. import db
from ..models import User, Permission, Role, Basic, LongRunStandard, SitUpStandard, PullUpStandard, RetraceStandard
from ..decorators import admin_required, permission_required, caption_required

age_list = [15, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60]


def searchInsert(nums, target):
    if not nums:
        return 0
    for i, num in enumerate(nums):
        if num >= target:
            return i
    return len(nums)



@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@main.route('/type-in/<int:id>', methods=['GET', 'POST'])
@login_required
@caption_required
def type_in(id):
    user = User.query.get_or_404(id)
    form = BasicForm()
    if form.validate_on_submit():
        age = user.age
        print(age)
        i = searchInsert(age_list, age)
        print(i)
        long_run_tmp = LongRunStandard.query.filter(LongRunStandard.age.between(age_list[i - 1] + 1, age_list[i]), LongRunStandard.duration >= form.long_run.data).order_by(-LongRunStandard.duration.desc()).first()
        long_run_score = long_run_tmp.score if long_run_tmp.score < 100 else 100 + (long_run_tmp.duration - form.long_run.data) // 5
        print(form.sit_up.data)
        sit_up_tmp = SitUpStandard.query.filter(SitUpStandard.age.between(age_list[i - 1] + 1, age_list[i]), SitUpStandard.duration <= form.sit_up.data).order_by(SitUpStandard.duration.desc()).first()
        print(sit_up_tmp)
        sit_up_score = sit_up_tmp.score if sit_up_tmp.score < 100 else 100 + (form.sit_up.data - sit_up_tmp.duration) // 2
        pull_up_tmp = PullUpStandard.query.filter(PullUpStandard.age.between(age_list[i - 1] + 1, age_list[i]), PullUpStandard.duration <= form.pull_up.data).order_by(PullUpStandard.duration.desc()).first()
        pull_up_score = pull_up_tmp.score if pull_up_tmp.score < 100 else 100 + (form.pull_up.data - pull_up_tmp.duration) // 1
        retrace_tmp = RetraceStandard.query.filter(RetraceStandard.age.between(age_list[i - 1] + 1, age_list[i]), RetraceStandard.duration >= form.retrace.data).order_by(-RetraceStandard.duration.desc()).first()
        retrace_score = retrace_tmp.score if retrace_tmp.score < 100 else 100 + (retrace_tmp.duration - form.retrace.data) // 0.1
        basic = Basic(author=user, week=form.week.data, height=form.height.data, weight=form.weight.data, sit_up=form.sit_up.data, pull_up=form.pull_up.data,
                    long_run=form.long_run.data, retrace=form.retrace.data, timestamp=form.timestamp.data, score=long_run_score + sit_up_score + pull_up_score + retrace_score)
        db.session.add(basic)
        db.session.commit()
        flash('Type successfully!')
        users = User.query.all()
        return redirect(url_for('user.user_list', users=users))
    form.number.data = user.number
    form.name.data = user.name

    return render_template('type_in.html', form=form)


@main.route('/show/<number>')
@login_required
def show(number):
    user = User.query.filter_by(number=number).first()
    if user is None:
        abort(404)
    basics = user.basics.order_by(Basic.timestamp.desc()).all()
    return render_template('show_basics.html', user=user, basics=basics)
