import logging

from django.db import DatabaseError
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth import login, authenticate

# Create your views here.
from apps.user.models import User

logger = logging.getLogger('django')


class RegisterView(View):

    def get(self, request):

        return render(request, 'register.html')

    def post(self, request):
        # 接收参数
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        smscode = request.POST.get('sms_code')

        # 判断参数是否齐全
        if not all([mobile, password, password2, smscode]):
            return HttpResponseBadRequest('缺少必传参数')

        # 保存注册数据
        try:
            user = User.objects.create_user(username=mobile, mobile=mobile, password=password)
        except DatabaseError:
            return HttpResponseBadRequest('注册失败')

        # 实现状态保持
        login(request, user)

        # 跳转到首页
        response = redirect(reverse('home:index'))
        # 设置cookie
        # 登录状态，会话结束后自动过期
        response.set_cookie('is_login', True)
        # 设置用户名有效期一个月
        response.set_cookie('username', user.username, max_age=30 * 24 * 3600)

        return response


class LoginView(View):

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        # 接受参数
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        # 认证字段已经在User模型中的USERNAME_FIELD = 'mobile'修改
        user = authenticate(mobile=mobile, password=password)

        # 实现状态保持
        login(request, user)

        # 响应登录结果
        response = redirect(reverse('home:index'))
        response.set_cookie('is_login', True)
        response.set_cookie('username', user.username, max_age=30 * 24 * 3600)

        return response


class UserCenterView(View):

    def get(self, request):
        # 获取用户信息
        user = request.user

        # 组织模板渲染数据
        context = {
            'username': user.username,
            'mobile': user.mobile,
            'avatar': user.avatar.url if user.avatar else None,
            'user_desc': user.user_desc
        }
        return render(request, 'center.html', context=context)

    def post(self, request):
        # 接收数据
        user = request.user
        avatar = request.FILES.get('avatar')
        username = request.POST.get('username', user.username)
        user_desc = request.POST.get('desc', user.user_desc)

        # 修改数据库数据
        try:
            user.username = username
            user.user_desc = user_desc
            if avatar:
                user.avatar = avatar
            user.save()
        except Exception as e:
            logger.error(e)
            return HttpResponseBadRequest('更新失败，请稍后再试')

        # 返回响应，刷新页面
        response = redirect(reverse('users:center'))
        # 更新cookie信息
        response.set_cookie('username', user.username, max_age=30 * 24 * 3600)
        return response
