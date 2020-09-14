from flask import g, jsonify, request, current_app
from . import api
from ..models import User, Role, Basic, LongRunStandard, SitUpStandard, PullUpStandard, RetraceStandard
from .. import db
from sqlalchemy import func


#年龄标准分割线，为方便计算，都统一减了一
age_list = [15, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 57, 60]


#寻找插入点
def search_insert(nums, target):
    if not nums:
        return 0
    for i, num in enumerate(nums):
        if num >= target:
            return i
    return len(nums)


#获取最高分/最低分，以及各科目的最高分
@api.route('/score/getAnalysis', methods=['GET', 'POST'])
def getAnalysis():
    week = db.session.query(func.max(Basic.week).label('max_week')).one().max_week

    highest_score = Basic.query.filter_by(week=week).order_by(Basic.score.desc()).first().score
    highest_score_name = Basic.query.filter_by(week=week).order_by(Basic.score.desc()).first().name

    lowest_score = Basic.query.filter_by(week=week).order_by(-Basic.score.desc()).first().score
    lowest_score_name = Basic.query.filter_by(week=week).order_by(-Basic.score.desc()).first().name

    sit_up = Basic.query.filter_by(week=week).order_by(Basic.sit_up.desc()).first().sit_up
    sit_up_name = Basic.query.filter_by(week=week).order_by(Basic.sit_up.desc()).first().name

    pull_up = Basic.query.filter_by(week=week).order_by(Basic.pull_up.desc()).first().pull_up
    pull_up_name = Basic.query.filter_by(week=week).order_by(Basic.pull_up.desc()).first().name

    retrace = Basic.query.filter_by(week=week).order_by(-Basic.retrace.desc()).first().retrace
    retrace_name = Basic.query.filter_by(week=week).order_by(-Basic.retrace.desc()).first().name

    tmp = Basic.query.filter_by(week=week).order_by(-Basic.long_run.desc()).first().long_run
    long_run_name = Basic.query.filter_by(week=week).order_by(-Basic.long_run.desc()).first().name

    return {
        'code': 200,
        'data': {
            'highest_score': highest_score,
            'highest_score_name': highest_score_name,
            'lowest_score': lowest_score,
            'lowest_score_name': lowest_score_name,
            'pull_up': pull_up,
            'pull_up_name': pull_up_name,
            'sit_up': sit_up,
            'sit_up_name': sit_up_name,
            'retrace': retrace,
            'retrace_name': retrace_name,
            'long_run': {'long_run_min': tmp//60, 'long_run_sec':tmp%60},
            'long_run_name': long_run_name
        }
    }


#获取上周优秀/良好/及格/不及格人数，用于画饼状图
@api.route('/score/getLastWeek', methods=['GET', 'POST'])
def getLastWeek():
    week = db.session.query(func.max(Basic.week).label('max_week')).one().max_week

    a = Basic.query.filter_by(week=week).filter(Basic.score > 360).count()

    b = Basic.query.filter_by(week=week).filter(Basic.score.between(320, 360)).count()
    c = Basic.query.filter_by(week=week).filter(Basic.score.between(240, 319)).count()
    d = Basic.query.filter_by(week=week).filter(Basic.score < 240).count()

    return {
        'code': 200,
        'data': {
            'a': a,
            'b': b,
            'c': c,
            'd': d,
        }
    }


#获取登录用户最近一周的各科分数
@api.route('/score/getLastWeekScore', methods=['GET', 'POST'])
def getLastWeekScore():
    lastWeekScore = []
    user = g.current_user

    record = Basic.query.filter_by(name=user.name).order_by(Basic.week.desc()).first()

    lastWeekScore.append(record.sit_up_score)
    lastWeekScore.append(record.pull_up_score)
    lastWeekScore.append(record.retrace_score)
    lastWeekScore.append(record.long_run_score)
    print(lastWeekScore)

    return {
        'code': 200,
        'data': {
            'lastWeekScore': lastWeekScore
        }
    }


#获取每周平均分数，用于画折线图
@api.route('/score/getAverage', methods=['GET', 'POST'])
def getAverage():
    max_week = db.session.query(func.max(Basic.week).label('max_week')).one().max_week

    week = []
    averageScore = []
    for i in range(1, max_week + 1):
        tmp = db.session.query(func.avg(Basic.score).label('average_score')).filter(Basic.week == i).filter(Basic.score > 0).one().average_score
        week.append(i)
        averageScore.append(round(tmp))

    return {
        'code': 200,
        'data': {
            'week': week,
            'averageScore': averageScore
        }
    }


#获取登录用户各周的分数，用于画折线图
@api.route('/score/getPersonalScore', methods=['GET', 'POST'])
def getPersonalScore():
    max_week = db.session.query(func.max(Basic.week).label('max_week')).one().max_week

    week = []
    score = []
    user = g.current_user

    for i in range(1, max_week + 1):
        tmp = Basic.query.filter_by(name=user.name).filter(Basic.week == i).first().score
        week.append(i)
        score.append(tmp)
    print(score)
    return {
        'code': 200,
        'data': {
            'week': week,
            'score': score
        }
    }


#获取各周各科的成绩平均分，用于管理员画各科目的折线图
@api.route('/score/getSeveral', methods=['GET', 'POST'])
def getSeveral():
    max_week = db.session.query(func.max(Basic.week).label('max_week')).one().max_week

    week = []
    sitUpAverage = []
    pullUpAverage = []
    retraceAverage = []
    longRunAverage = []
    for i in range(1, max_week + 1):
        week.append(i)

        sit_up_tmp = db.session.query(func.avg(Basic.sit_up_score).label('sit_up_average')).filter(Basic.week == i).filter(Basic.sit_up_score > 0).one().sit_up_average
        sitUpAverage.append(round(sit_up_tmp))

        pull_up_tmp = db.session.query(func.avg(Basic.pull_up_score).label('pull_up_average')).filter(
            Basic.week == i).filter(Basic.pull_up_score > 0).one().pull_up_average
        pullUpAverage.append(round(pull_up_tmp))

        retrace_tmp = db.session.query(func.avg(Basic.retrace_score).label('retrace_average')).filter(
            Basic.week == i).filter(Basic.retrace_score > 0).one().retrace_average
        retraceAverage.append(round(retrace_tmp))

        long_run_tmp = db.session.query(func.avg(Basic.long_run_score).label('long_run_average')).filter(
            Basic.week == i).filter(Basic.long_run_score > 0).one().long_run_average
        longRunAverage.append(round(long_run_tmp))

    return {
        'code': 200,
        'data': {
            'week': week,
            'sitUpAverage': sitUpAverage,
            'pullUpAverage': pullUpAverage,
            'retraceAverage': retraceAverage,
            'longRunAverage': longRunAverage
        }
    }


#获取登录用户各周各科的成绩，用于登录用户画自己各科目的折线图
@api.route('/score/getCategoryScore', methods=['GET', 'POST'])
def getCategoryScore():
    max_week = db.session.query(func.max(Basic.week).label('max_week')).one().max_week

    week = []
    sitUpScore = []
    pullUpScore = []
    retraceScore = []
    longRunScore = []
    user = g.current_user
    for i in range(1, max_week + 1):
        week.append(i)

        sit_up_tmp = Basic.query.filter_by(name=user.name).filter(Basic.week == i).first().sit_up_score
        sitUpScore.append(sit_up_tmp)

        pull_up_tmp = Basic.query.filter_by(name=user.name).filter(Basic.week == i).first().pull_up_score
        pullUpScore.append(pull_up_tmp)

        retrace_tmp = Basic.query.filter_by(name=user.name).filter(Basic.week == i).first().retrace_score
        retraceScore.append(retrace_tmp)

        long_run_tmp = Basic.query.filter_by(name=user.name).filter(Basic.week == i).first().long_run_score
        longRunScore.append(long_run_tmp)

    return {
        'code': 200,
        'data': {
            'week': week,
            'sitUpScore': sitUpScore,
            'pullUpScore': pullUpScore,
            'retraceScore': retraceScore,
            'longRunScore': longRunScore
        }
    }


#获取每周的最高分与最低分，用于管理员画折线图
@api.route('/score/getMaxandMin', methods=['GET', 'POST'])
def getMaxandMin():
    max_week = db.session.query(func.max(Basic.week).label('max_week')).one().max_week

    week = []
    maxData = []
    minData = []
    for i in range(1, max_week + 1):
        week.append(i)
        max_score = Basic.query.filter(Basic.week==i).order_by(Basic.score.desc()).first().score
        maxData.append(max_score)
        min_score = Basic.query.filter(Basic.week==i).order_by(-Basic.score.desc()).first().score
        minData.append(min_score)

    return {
        'code': 200,
        'data': {
            'week': week,
            'maxData': maxData,
            'minData': minData
        }
    }


#管理员获取成绩列表，可实现按周或者按姓名查询
@api.route('/score/getList', methods=['GET', 'POST'])
def getScoreList():
    week = request.args.get('week')
    name = request.args.get('name')
    page = request.args.get('page')
    limit = request.args.get('limit')

    if not page:
        page = 1
    if not limit:
        limit = 20

    page = int(page)
    limit = int(limit)

    if name and not week:
        user = User.query.filter_by(name=name).first()
        total = Basic.query.filter_by(author=user).count()

        pagination = Basic.query.filter_by(author=user).paginate(page, per_page=limit, error_out=False)
        basics = pagination.items

        basicList = []
        for basic in basics:
            basicList.append(basic.to_json())

        return {
            'code': 200,
            'data': {
                'total': total,
                'scoreList': basicList
            }
        }

    elif week and not name:
        total = Basic.query.filter_by(week=week).count()

        pagination = Basic.query.filter_by(week=week).paginate(page, per_page=limit, error_out=False)
        basics = pagination.items

        basicList = []
        for basic in basics:
            basicList.append(basic.to_json())

        return {
            'code': 200,
            'data': {
                'total': total,
                'scoreList': basicList
            }
        }

    total = Basic.query.order_by(Basic.id.desc()).count()

    pagination = Basic.query.order_by(Basic.id.desc()).paginate(page, per_page=limit, error_out=False)
    basics = pagination.items

    basicList = []
    for basic in basics:
        basicList.append(basic.to_json())

    response = {
        'code': 200,
        'data': {
            'total': total,
            'scoreList': basicList
        }
    }
    return jsonify(response)


#获取个人成绩数据
@api.route('/score/getPersonalData', methods=['GET', 'POST'])
def getPersonalData():
    user = g.current_user
    total = Basic.query.filter_by(author=user).count()

    tmp = Basic.query.filter_by(author=user).all()
    personalData = []
    for basic in tmp:
        personalData.append(basic.to_json())

    return {
        'code': 200,
        'data': {
            'total': total,
            'personalData': personalData
        }
    }


#手动编辑用户成绩
@api.route('/score/edit', methods=['GET', 'POST'])
def editScore():
    id = int(request.args.get('id'))
    week = int(request.args.get('week'))
    name = request.args.get('name')
    situp = int(request.args.get('situp'))
    pullup = int(request.args.get('pullup'))
    longrun_min = int(request.args.get('longrun_min'))
    longrun_sec = int(request.args.get('longrun_sec'))
    retrace = float(request.args.get('retrace'))
    remark = request.args.get('remark')
    longrun = longrun_min * 60 + longrun_sec

    basic = Basic.query.get_or_404(int(id))

    basic.week = week
    basic.name = name
    basic.sit_up = situp
    basic.pull_up = pullup
    basic.long_run = longrun
    basic.long_run_min = longrun_min
    basic.long_run_sec = longrun_sec
    basic.retrace = retrace
    basic.remark = remark

    user = User.query.filter_by(name=name).first()
    i = search_insert(age_list, user.age)

    long_run_tmp = LongRunStandard.query.filter(LongRunStandard.age.between(age_list[i - 1] + 1, age_list[i]),
                                                LongRunStandard.duration >= longrun).order_by(
        -LongRunStandard.duration.desc()).first()

    long_run_score = (long_run_tmp.score if long_run_tmp.score < 100 else 100 + (
            long_run_tmp.duration - longrun) // 5) if long_run_tmp else 0

    sit_up_tmp = SitUpStandard.query.filter(SitUpStandard.age.between(age_list[i - 1] + 1, age_list[i]),
                                            SitUpStandard.duration <= situp).order_by(
        SitUpStandard.duration.desc()).first()

    sit_up_score = (
        sit_up_tmp.score if sit_up_tmp.score < 100 else 100 + (situp - sit_up_tmp.duration) // 2) if sit_up_tmp else 0

    pull_up_tmp = PullUpStandard.query.filter(PullUpStandard.age.between(age_list[i - 1] + 1, age_list[i]),
                                              PullUpStandard.duration <= pullup).order_by(
        PullUpStandard.duration.desc()).first()

    pull_up_score = (pull_up_tmp.score if pull_up_tmp.score < 100 else 100 + (
            pullup - pull_up_tmp.duration) // 1) if pull_up_tmp else 0

    retrace_tmp = RetraceStandard.query.filter(RetraceStandard.age.between(age_list[i - 1] + 1, age_list[i]),
                                               RetraceStandard.duration >= retrace).order_by(
        -RetraceStandard.duration.desc()).first()

    retrace_score = (retrace_tmp.score if retrace_tmp.score < 100 else 100 + int((
                                                                                         retrace_tmp.duration - retrace) // 0.1)) if retrace_tmp else 0

    basic.sit_up_score = sit_up_score
    basic.pull_up_score = pull_up_score
    basic.long_run_score = long_run_score
    basic.retrace_score = retrace_score
    basic.score = long_run_score + sit_up_score + pull_up_score + retrace_score

    db.session.add(basic)
    db.session.commit()

    return {
        'code': 200,
        'data': {
            'message': '修改成功'
        }
    }


#手动添加用户成绩
@api.route('/score/add', methods=['GET', 'POST'])
def add_score():
    week = int(request.args.get('week'))
    name = request.args.get('name')
    situp = int(request.args.get('situp'))
    pullup = int(request.args.get('pullup'))
    retrace = float(request.args.get('retrace'))
    longrun_sec = int(request.args.get('longrun_sec'))
    longrun_min = int(request.args.get('longrun_min'))
    longrun = longrun_min * 60 + longrun_sec

    user = User.query.filter_by(name=name).first()
    i = search_insert(age_list, user.age)

    long_run_tmp = LongRunStandard.query.filter(LongRunStandard.age.between(age_list[i - 1] + 1, age_list[i]),
                                                LongRunStandard.duration >= longrun).order_by(
        -LongRunStandard.duration.desc()).first()

    long_run_score = (long_run_tmp.score if long_run_tmp.score < 100 else 100 + (
                long_run_tmp.duration - longrun) // 5) if long_run_tmp else 0

    sit_up_tmp = SitUpStandard.query.filter(SitUpStandard.age.between(age_list[i - 1] + 1, age_list[i]),
                                            SitUpStandard.duration <= situp).order_by(
        SitUpStandard.duration.desc()).first()

    sit_up_score = (sit_up_tmp.score if sit_up_tmp.score < 100 else 100 + (situp - sit_up_tmp.duration) // 2) if sit_up_tmp else 0

    pull_up_tmp = PullUpStandard.query.filter(PullUpStandard.age.between(age_list[i - 1] + 1, age_list[i]),
                                              PullUpStandard.duration <= pullup).order_by(
        PullUpStandard.duration.desc()).first()

    pull_up_score = (pull_up_tmp.score if pull_up_tmp.score < 100 else 100 + (
                pullup - pull_up_tmp.duration) // 1) if pull_up_tmp else 0

    retrace_tmp = RetraceStandard.query.filter(RetraceStandard.age.between(age_list[i - 1] + 1, age_list[i]),
                                               RetraceStandard.duration >= retrace).order_by(
        -RetraceStandard.duration.desc()).first()

    retrace_score = (retrace_tmp.score if retrace_tmp.score < 100 else 100 + int((
                retrace_tmp.duration - retrace) // 0.1)) if retrace_tmp else 0

    basic = Basic(author=user, week=week, name=name,
                  sit_up=situp, pull_up=pullup,
                  long_run=longrun, retrace=retrace, long_run_min=longrun_min, long_run_sec=longrun_sec,
                  long_run_score=long_run_score, retrace_score=retrace_score, sit_up_score=sit_up_score, pull_up_score=pull_up_score,
                  score=long_run_score + sit_up_score + pull_up_score + retrace_score)
    db.session.add(basic)
    db.session.commit()

    return {
        'code': 200,
        'data': {
            'message': '添加成功'
        }
    }


#删除某条成绩
@api.route('/score/remove', methods=['GET', 'POST'])
def removeScore():
    id = request.args.get('id')
    basic = Basic.query.get_or_404(id)
    db.session.delete(basic)
    db.session.commit()
    return {
        'code': 200,
        'data': {
            'message': '删除成功'
        }
    }


#批量删除成绩
@api.route('/score/batchremove', methods=['GET', 'POST'])
def batchremoveScore():
    ids = request.args.get('ids')
    for id in ids.split(','):
        basic = Basic.query.get_or_404(id)
        db.session.delete(basic)
    db.session.commit()
    return {
        'code': 200,
        'data': {
            'message': '批量删除成功'
        }
    }


