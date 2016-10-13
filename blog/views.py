from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Template, Context, RequestContext
from django.template.loader import get_template
from models import Blog
from datetime import datetime
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

# Create your views here.
SITE_NAME = "Blog 42"

def home(request):
    t = get_template('home.html')
    html = t.render(Context({'SITE_NAME':SITE_NAME,'blogs':Blog.objects.order_by("time").reverse()}), request)
    return HttpResponse(html)

def blog(request, id):
    if Blog.exists(id):
        blog = Blog.objects.get(id=id)
        t = get_template('blog.html')
        html = t.render(Context({'SITE_NAME':SITE_NAME,'blog':blog}), request)
        return HttpResponse(html)
    else:
        t = get_template('blog.html')
        html = t.render(Context({'SITE_NAME':SITE_NAME,'blog':0}), request)
        return HttpResponse(html)

@csrf_protect
def edit(request, id):
    if request.method=="POST" and request.COOKIES.has_key("logd_in"):
        blog = Blog.objects.get(id=id)
        blog.name = request.POST["name"]
        blog.text = request.POST["text"]
        blog.save()
        return HttpResponseRedirect('/blog/')
    elif request.COOKIES.has_key("logd_in"):
        t = get_template('edit.html')
        html = t.render(Context({'SITE_NAME': SITE_NAME, 'blog': Blog.objects.get(id=id)}), request)
        return HttpResponse(html)
    else:
        messages.add_message(request, messages.INFO, "Unauthorized, please log in.")
        return HttpResponseRedirect('/blog/')

@csrf_protect
def add(request):
    if request.method=="POST" and request.user.is_authenticated:
        blog = Blog()
        blog.name = request.POST["name"]
        blog.text = request.POST["text"]
        blog.time = datetime.today()
        blog.save()
        messages.add_message(request,messages.INFO,"Blog post added")
        return HttpResponseRedirect('/blog/')
    elif request.user.is_authenticated:
        return render(request, 'add.html')
    else:
        messages.add_message(request, messages.INFO, "Unauthorized, please log in.")
        return HttpResponseRedirect('/blog/')

@csrf_protect
def delete(request, id):
    if request.method=="POST" and request.POST.get("choice1") and request.user.is_authenticated:
        blog = Blog.objects.get(id=id)
        blog.delete()
        messages.add_message(request, messages.INFO, "Blog post removed")
        return HttpResponseRedirect('/blog/')
    elif request.user.is_authenticated:
        t = get_template('delete.html')
        html = t.render(Context({'SITE_NAME': SITE_NAME, 'blog': Blog.objects.get(id=id)}), request)
        return HttpResponse(html)
    else:
        messages.add_message(request, messages.INFO, "Unauthorized, please log in.")
        return HttpResponseRedirect('/blog/')

@csrf_protect
def login(request):
    if request.method == "POST":
        username = request.username
        password = request.password
        user = authenticate(username, password)
        if user is not None:
            login(request, username)
            messages.add_message(request, messages.INFO, "Logged in.")
            return HttpResponseRedirect('/blog/')
        else:
            messages.add_message(request, messages.ERROR, "Login credential error.")
            t = get_template('login.html')
            html = t.render(Context({'SITE_NAME': SITE_NAME}), request)
            return HttpResponse(html)
    elif request.method=="GET":
        t = get_template('login.html')
        html = t.render(Context({'SITE_NAME': SITE_NAME}), request)
        return HttpResponse(html)

@csrf_protect
def logout(request):
    t = get_template('logout.html')
    html = t.render(Context({'SITE_NAME': SITE_NAME}), request)
    r = HttpResponse(html)
    return r

@csrf_protect
def register(request):
    if request.method == "POST" and not request.user.is_authenticated:
        user = authenticate(request.username)
        if user is not None:
            messages.add_message(request, messages.ERROR, "Unable to register to given credentials.\n"
                                                          "Try other username.")
            t = get_template('register.html')
            html = t.render(Context({'SITE_NAME': SITE_NAME}), request)
            return HttpResponse(html)
        user = User.objects.create_user(request.username,password=request.password)

    if request.method == "GET" and not request.user.is_authenticated:
        t = get_template('register.html')
        html = t.render(Context({'SITE_NAME': SITE_NAME}), request)
        return HttpResponse(html)
    else:
        user = authenticate(request.username)