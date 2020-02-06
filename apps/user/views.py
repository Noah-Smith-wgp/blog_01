from django.db import DatabaseError
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

# Create your views here.
from apps.user.models import User


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

        # return redirect(reverse())
        # return redirect('/')
        return HttpResponse('注册成功，重定向到首页')
