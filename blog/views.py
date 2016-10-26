from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Template, Context, RequestContext
from django.template.loader import get_template
from models import Blog
from datetime import datetime
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.cache import cache

# Create your views here.

def make_header(request):
    tHeader = get_template('header.html')
    header = tHeader.render(Context({'user': request.user}))
    return header

def make_footer(request):
    tFooter = get_template('footer.html')
    footer = tFooter.render(Context({'request':request}))
    return footer

def update_cache_stats(request):
    if cache.get('session_start') is None:
        cache.set_many({'session_start':datetime.now(), 'visited':0,
                        'edited':0, 'created':0, 'deleted':0})
    elif request.path=='^blog/(?P<id>\d+)/?$' and request.method=='GET':
        n = cache.get('visited') +1
        cache.set('visited', n)
    elif request.path=='^edit/(?P<id>\d+)/?$' and request.method=='POST':
        n = cache.get('edited') + 1
        cache.set('edited', n)


def home(request):
    tBody = get_template('home.html')
    body = tBody.render(Context({'blogs':Blog.objects.order_by("time").reverse()}), request)
    t = get_template('template.html')
    html = t.render(Context({'page_body':body, 'header_body':make_header(request)}), request)
    return HttpResponse(html)

def blog(request, id):
    if Blog.exists(id):
        blog = Blog.objects.get(id=id)
        tBody = get_template('blog.html')
        body = tBody.render(Context({'blog':blog}), request)
        t = get_template('template.html')
        html = t.render(Context({'page_body':body, 'header_body':make_header(request)}), request)
        return HttpResponse(html)
    else:
        messages.add_message(request, messages.ERROR, "Sorry, the blog post you requested does not exist!")
        if request.POST.get("next"):
            return redirect(request.POST.get("next"))
        else:
            return HttpResponseRedirect('/blog/')

@login_required(login_url="/login/")
@csrf_protect
def edit(request, id):
    if request.method=="POST" and request.user.is_authenticated:
        blog = Blog.objects.get(id=id)
        blog.name = request.POST["name"]
        blog.text = request.POST["text"]
        blog.save()
        if request.POST.get("next"):
            return redirect(request.POST.get("next"))
        else:
            return HttpResponseRedirect('/blog/')
    elif request.COOKIES.has_key("logd_in"):
        tBody = get_template('edit.html')
        body = tBody.render(Context({'blog':Blog.objects.get(id=id)}), request)
        t = get_template('template.html')
        html = t.render(Context({'page_body':body, 'header_body':make_header(request)}), request)
        return HttpResponse(html)
    else:
        messages.add_message(request, messages.ERROR, "Unauthorized, please log in.")
        if request.POST.get("next"):
            return redirect(request.POST.get("next"))
        else:
            return HttpResponseRedirect('/login/')

@login_required(login_url="/login/")
@csrf_protect
def add(request):
    if request.method=="POST" and request.user.is_authenticated:
        blog = Blog()
        blog.name = request.POST["name"]
        blog.text = request.POST["text"]
        blog.time = datetime.today()
        blog.save()
        messages.add_message(request,messages.SUCCESS,"Blog post added")
        return HttpResponseRedirect('/blog/')
    elif request.user.is_authenticated:
        tBody = get_template('add.html')
        body = tBody.render(request)
        t = get_template('template.html')
        html = t.render(Context({'page_body': body, 'header_body':make_header(request)}), request)
        return HttpResponse(html)
    else:
        messages.add_message(request, messages.ERROR, "Unauthorized, please log in.")
        if request.POST.get("next"):
            return redirect(request.POST.get("next"))
        else:
            return HttpResponseRedirect('/login/')

@login_required(login_url="/login/")
@csrf_protect
def delete(request, id):
    if request.method=="POST" and request.POST.get("choice1") and request.user.is_authenticated:
        blog = Blog.objects.get(id=id)
        blog.delete()
        messages.add_message(request, messages.SUCCESS, "Blog post removed")
        return HttpResponseRedirect('/blog/')
    elif request.user.is_authenticated:
        tBody = get_template('delete.html')
        body = tBody.render(Context({'blog': Blog.objects.get(id=id)}), request)
        t = get_template('template.html')
        html = t.render(Context({'page_body': body, 'header_body':make_header(request)}), request)
        return HttpResponse(html)
    else:
        messages.add_message(request, messages.ERROR, "Unauthorized, please log in.")
        if request.POST.get("next"):
            return redirect(request.POST.get("next"))
        else:
            return HttpResponseRedirect('/login/')

@csrf_protect
def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, username)
            messages.add_message(request, messages.SUCCESS, "Logged in.")
            if request.POST.get("next"):
                return redirect(request.POST.get("next"))
            else:
                return HttpResponseRedirect('/blog/')
        else:
            messages.add_message(request, messages.ERROR, "Login credential error.")
            tBody = get_template('login_derp.html')
            body = tBody.render(request)
            t = get_template('template.html')
            html = t.render(Context({'page_body': body, 'header_body':make_header(request)}), request)
            return HttpResponse(html)
    elif request.method=="GET":
        tBody = get_template('login_derp.html')
        body = tBody.render(request)
        t = get_template('template.html')
        html = t.render(Context({'page_body': body, 'header_body':make_header(request)}), request)
        return HttpResponse(html)
    else:
        messages.add_message(request, messages.WARNING, "You can't do that.")
        if request.POST.get("next"):
            return redirect(request.POST.get("next"))
        else:
            return HttpResponseRedirect('/blog/')

@csrf_protect
def logout(request):
    if request.method=="POST" and request.POST.get("choice1") and request.user.is_authenticated:
        messages.add_message(request, messages.SUCCESS, "Logged out.")
        logout(request)
        if request.POST.get("next"):
            return redirect(request.POST.get("next"))
        else:
            tBody = get_template('home.html')
            body = tBody.render(request)
            t = get_template('template.html')
            html = t.render(Context({'page_body': body, 'header_body':make_header(request)}), request)
            return HttpResponse(html)
    elif request.method=="GET" and request.user.is_authenticated:
        tBody = get_template('logout_derp.html')
        body = tBody.render(request)
        t = get_template('template.html')
        html = t.render(Context({'page_body': body, 'header_body':make_header(request)}), request)
        return HttpResponse(html)
    else:
        messages.add_message(request, messages.ERROR, "Unable to log out. You first need to be logged in to do that.")
        tBody = get_template('home.html')
        body = tBody.render(request)
        t = get_template('template.html')
        html = t.render(Context({'page_body': body, 'header_body': make_header(request)}), request)
        return HttpResponse(html)

@csrf_protect
def register(request):
    if request.method == "POST" and not request.user.is_authenticated:
        user = authenticate(request.username)
        if user is not None:
            messages.add_message(request, messages.ERROR, "Unable to register to given credentials.\n"
                                                          "Try other username.")
            tBody = get_template('register.html')
            body = tBody.render(request)
            t = get_template('template.html')
            html = t.render(Context({'page_body': body, 'header_body':make_header(request)}), request)
            return HttpResponse(html)
        else:
            user = User.objects.create_user(request.username,password=request.password)

    elif request.method == "GET" and not request.user.is_authenticated:
        tBody = get_template('register.html')
        body = tBody.render(request)
        t = get_template('template.html')
        html = t.render(Context({'page_body': body, 'header_body':make_header(request)}), request)
        return HttpResponse(html)
    else:
        messages.add_message(request, messages.WARNING, "You can't do that.")
        if request.POST.get("next"):
            return redirect(request.POST.get("next"))
        else:
            return HttpResponseRedirect('/blog/')