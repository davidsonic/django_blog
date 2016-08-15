# -*- coding: utf-8 -*-

from django.shortcuts import render,redirect
import logging
from django.conf import settings
from models import *   #newly add
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger  #Ctrl+ left_mouse
from django.db import connection  # 支持mysql语句查询
from django.db.models import Count  # 评论排行
from blog.forms import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout,login,authenticate  #django标准登录模块

#日志
logger=logging.getLogger('blog.views')


# Create your views here.
# 接着要在setttings.py中的context_processer 中进行添加
def global_setting(request):
    SITE_NAME=settings.SITE_NAME
    SITE_DESC=settings.SITE_DESC  #for locals()

    #获取 分类信息
    category_list = Category.objects.all()[:5]  # 获取文章分类

    #获取archive_list
    distinct_date_list = []
    archive_list = Article.objects.values('date_publish')
    for date in archive_list:
        date2 = date['date_publish'].strftime('%Y-%m文章存档')
        if date2 not in distinct_date_list:
            distinct_date_list.append(date2)
    archive_list = distinct_date_list

    # 中文乱码
    # archive_list = Article.objects.distinct_date()

    # 广告数据
    # 标签运数据
    # 友情链接
    # 文章排行榜数据
    #评论排行， 不能用order_by，因为comment不在article对象中
    comment_count_list=Comment.objects.values('article').annotate(comment_count=Count('article')).order_by('-comment_count')
    article_comment_list=[Article.objects.get(pk=comment['article']) for comment in comment_count_list]  #根据id取出文章名字

    # return {'category_list': category_list,
    #         'archive_list': archive_list,
    #         'SITE_NAME':settings.SITE_NAME,
    #         'SITE_DESC':settings.SITE_DESC,
    #         'article_comment_list': article_comment_list,
    #         }

    return locals()



def index(request):
    try:
        # 广告数据
        # 最新文章数据
        article_list=Article.objects.all()
        article_list=getPage(request,article_list)


        #文章归档
        #1.先要去获取到文章中有的年份和月份
        # method1   raw  (Exception: raw query must contain the primary key)

        # print Article.objects.values('date_publish').distinct()

        # archive_list=Article.objects.raw('select id, DATE_FORMAT(date_publish,:"%%Y-%%m") as cid, col_date from blog_article')
        # for archive in archive_list:
        #     print archive

        # method2
        # cursor=connection.cursor()
        # cursor.execute("select distinct date_format(date_publish,'%Y-%m') as col_date from blog_article order by date_publish")
        # row=cursor.fetchall()
        # print row

        file=open('sss.txt','r')
        site_name=settings.SITE_NAME  # method1
    except Exception as e:
        logger.error(e)

    return render(request,'index.html',locals())

    # return render(request, 'index.html', {'category_list':category_list,'article_list':article_list})
    #  1.locals(), 2.index->base.html was automatically refactored,
    # but we should use index,because it inherits base.html
    # use dictionary to give to template base.html
    # there is an alternative to use locals() to pass all the local variables to templates

    # return render(request,'index.html',locals())



def archive(request):
    try:
        #先获取客户端提交的信息
        year=request.GET.get('year',None)
        month=request.GET.get('month',None)
        article_list = Article.objects.filter(date_publish__icontains=year+'-'+month)  #过滤
        article_list=getPage(request,article_list)

    except Exception as e:
         logger.error(e)

    return render(request,'archive.html',locals())



# 分页代码
def getPage(request,article_list):
    paginator=Paginator(article_list,5)
    try:
        page=int(request.GET.get('page',1))
        article_list=paginator.page(page)
    except (EmptyPage,InvalidPage,PageNotAnInteger):
        article_list=paginator.page(1)

    return article_list



def category(request):
    try:
        # 先获取客户端提交的信息
        cid = request.GET.get('cid', None)
        try:
            category = Category.objects.get(pk=cid)
        except Category.DoesNotExist:
            return render(request, 'failure.html', {'reason': '分类不存在'})
        article_list = Article.objects.filter(category=category)
        article_list = getPage(request, article_list)
    except Exception as e:
        logger.error(e)
    return render(request, 'category.html', locals())



# 按标签查询对应的文章列表
def tag(request):
    try:
        # 同学们自己实现该功能
        pass
    except Exception as e:
        logger.error(e)
    return render(request, 'archive.html', locals())



# 分页代码
def getPage(request, article_list):
    paginator = Paginator(article_list, 5)
    try:
        page = int(request.GET.get('page', 1))
        article_list = paginator.page(page)
    except (EmptyPage, InvalidPage, PageNotAnInteger):
        article_list = paginator.page(1)
    return article_list



# 文章详情
def article(request):
    try:
        # 获取文章id
        id = request.GET.get('id', None)
        try:
            # 获取文章信息
            article = Article.objects.get(pk=id)
        except Article.DoesNotExist:
            return render(request, 'failure.html', {'reason': '没有找到对应的文章'})

        # 评论表单
        comment_form = CommentForm({'author': request.user.username,
                                    'email': request.user.email,
                                    'url': request.user.url,
                                    'article': id} if request.user.is_authenticated() else{'article': id})  #判断是否已经登录


        # 获取评论信息
        comments = Comment.objects.filter(article=article).order_by('id')
        comment_list = []
        for comment in comments:
            for item in comment_list:
                if not hasattr(item, 'children_comment'):
                    setattr(item, 'children_comment', [])
                if comment.pid == item:
                    item.children_comment.append(comment)
                    break
            if comment.pid is None:
                comment_list.append(comment)
    except Exception as e:
        print e
        logger.error(e)
    return render(request, 'article.html', locals())





# 提交评论
def comment_post(request):
    try:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            #获取表单信息
            comment = Comment.objects.create(username=comment_form.cleaned_data["author"],
                                             email=comment_form.cleaned_data["email"],
                                             url=comment_form.cleaned_data["url"],
                                             content=comment_form.cleaned_data["comment"],
                                             article_id=comment_form.cleaned_data["article"],
                                             user=request.user if request.user.is_authenticated() else None)
            comment.save()
        else:
            return render(request, 'failure.html', {'reason': comment_form.errors})
    except Exception as e:
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])




# 注销
def do_logout(request):
    try:
        logout(request)
    except Exception as e:
        print e
        logger.error(e)
    return redirect(request.META['HTTP_REFERER'])



# 注册
def do_reg(request):
    try:
        if request.method == 'POST':
            reg_form = RegForm(request.POST)
            if reg_form.is_valid():
                # 注册
                user = User.objects.create(username=reg_form.cleaned_data["username"],
                                    email=reg_form.cleaned_data["email"],
                                    url=reg_form.cleaned_data["url"],
                                    password=make_password(reg_form.cleaned_data["password"]),)
                user.save()

                # 登录
                user.backend = 'django.contrib.auth.backends.ModelBackend' # 指定默认的登录验证方式
                login(request, user)
                return redirect(request.POST.get('source_url'))
            else:
                return render(request, 'failure.html', {'reason': reg_form.errors})
        else:
            reg_form = RegForm()
    except Exception as e:
        logger.error(e)
    return render(request, 'reg.html', locals())


# 登录
def do_login(request):
    try:
        if request.method == 'POST':
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                # 登录
                username = login_form.cleaned_data["username"]
                password = login_form.cleaned_data["password"]
                user = authenticate(username=username, password=password)
                if user is not None:
                    user.backend = 'django.contrib.auth.backends.ModelBackend' # 指定默认的登录验证方式
                    login(request, user)
                else:
                    return render(request, 'failure.html', {'reason': '登录验证失败'})
                return redirect(request.POST.get('source_url'))
            else:
                return render(request, 'failure.html', {'reason': login_form.errors})
        else:
            login_form = LoginForm()
    except Exception as e:
        logger.error(e)
    return render(request, 'login.html', locals())

