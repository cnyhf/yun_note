import hashlib

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .models import User


def reg_view(request):
    # 注册
    if request.method == 'GET':
        # GET 返回页面
        return render(request, 'user/register.html')
    # POST 处理提交数据
    elif request.method == 'POST':
        username = request.POST['username']
        password_1 = request.POST['password_1']
        password_2 = request.POST['password_2']
    # 1, 两个密码保持一致
    if password_1 != password_2:
        return HttpResponse('两次密码输入不一致')
    # 哈希算法 - 给定明文，计算一段定长的，不可逆的值；md5,sha-256
    # 特点：（1）定长输出：不管明文长度为多少，哈希值都是定长的，md5 - 32位16进制
    # （2）不可逆：无法反向计算出 对应的 明文
    # （3）雪崩效应：输入改变，输出必然变
    # 场景：（1）密码处理  （2）文件完整性校验
    # 如何使用：
    m = hashlib.md5()
    m.update(password_1.encode())
    # password传过来是普通字符串，而这里要求字节串，要encode一下
    password_m = m.hexdigest()
    # 2, 当前用户名是否可用
    old_users = User.objects.filter(username=username)
    if old_users:
        return HttpResponse('用户名已注册')
    # 3, 插入数据
    try:
        user = User.objects.create(username=username, password=password_m)
    except Exception as e:
        # 有可能 报错 - 重复插入【唯一索引注意并发写入问题】
        print('--create user error %s' %(e))
        return HttpResponse('用户名已注册')
    # 免登录一天
    request.session['username'] = username
    request.session['uid'] = user.id
    # TODO 修改session存储时间为一天

    return HttpResponseRedirect('/index')


def login_view(request):
    # 登陆
    if request.method == 'GET':
        # GET返回页面

        # 检查登陆状态，如果登陆了，显示‘已登陆’
        if request.session.get('username') and request.session.get('uid'):
            # return HttpResponse('已登陆')
            return HttpResponseRedirect('/index')

        # 检查Cookies
        c_username = request.COOKIES.get('username')
        c_uid = request.COOKIES.get('uid')
        if c_username and c_uid:
            # 回写session
            request.session['username'] = c_username
            request.session['uid'] = c_uid
            # return HttpResponse('已登陆')
            return HttpResponseRedirect('/index')
        return render(request, 'user/login.html')
    # POST提交处理数据
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
        except Exception as e:
            print('login user error %s' % (e))
            return HttpResponse('用户名或密码错误！')
        # 比对密码
        m = hashlib.md5()
        m.update(password.encode())
        if m.hexdigest() != user.password:
            return HttpResponse('用户名或密码错误！')
        # 记录会话状态
        request.session['username'] = username
        request.session['uid'] = user.id

        resp = HttpResponseRedirect('/index')
        # 判断用户是否点选了‘记住用户名’
        if 'remember' in request.POST:
            # 点选了 - >Cookies存储 username，uid 时间3天
            resp.set_cookie('username', username, 3600*24*3)
            resp.set_cookie('uid', user.id, 3600*24*3)

        return resp


def logout_view(request):
    # 删除session值
    if 'username' in request.session:
        del request.session['username']
    if 'uid' in request.session:
        del request.session['uid']
    # 删除Cookies
    resp = HttpResponseRedirect('/index')
    if 'username' in request.COOKIES:
        resp.delete_cookie('username')
    if 'uid' in request.COOKIES:
        resp.delete_cookie['uid']
    return resp