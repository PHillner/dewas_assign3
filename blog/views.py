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

def update_session_stats(request, page):
    if not "session_start" in request.session:
        request.session["session_start"] = str(datetime.now())
        request.session["visited"] = 0
        request.session["created"] = 0
        request.session["edited"] = 0
        request.session["deleted"] = 0

    if page=='blog':
        request.session["visited"] += 1
    elif page=='add':
        request.session["created"] += 1
    elif page=='edit':
        request.session["edited"] += 1
    elif page=='delete':
        request.session["deleted"] += 1

def session_stats_reset(request):
    request.session.flush()
    update_session_stats(request, request.POST.get("next"))
    messages.add_message(request,messages.INFO, "Session statistics has been reset.")
    return redirect(request.POST.get("next"))

def home(request):
    update_session_stats(request, 'home')
    return render(request, 'home.html', Context({'blogs':Blog.objects.order_by("time").reverse()}))

def blog(request, id):
    if Blog.exists(id):
        blog = Blog.objects.get(id=id)
        update_session_stats(request, 'blog')
        return render(request, 'blog.html', Context({'blog':blog}))
    else:
        messages.add_message(request, messages.ERROR, "Sorry, the blog post you requested does not exist!")
        return HttpResponseRedirect('/blog/')

@login_required(login_url="/login/")
@csrf_protect
def edit(request, id):
    if request.method=="POST" and request.user.is_authenticated:
        blog = Blog.objects.get(id=id)
        blog.name = request.POST["name"]
        blog.text = request.POST["text"]
        blog.save()
        update_session_stats(request, 'edit')
        if request.POST.get("next"):
            return redirect(request.POST.get("next"))
        else:
            return redirect('/blog/'+id+'/')
    else:
        return render(request, 'edit.html', Context({'blog':Blog.objects.get(id=id)}))

@login_required(login_url="/login/")
@csrf_protect
def add(request):
    if request.method=="POST" and request.user.is_authenticated:
        blog = Blog()
        blog.name = request.POST["name"]
        blog.text = request.POST["text"]
        blog.time = datetime.today()
        blog.save()
        update_session_stats(request, 'add')
        messages.add_message(request,messages.SUCCESS,"Blog post added")
        return HttpResponseRedirect('/blog/')
    else:
        return render(request, "add.html")

@login_required(login_url="/login/")
@csrf_protect
def delete(request, id):
    if request.method=="POST" and request.POST.get("choice1") and request.user.is_authenticated:
        blog = Blog.objects.get(id=id)
        blog.delete()
        update_session_stats(request, 'delete')
        messages.add_message(request, messages.SUCCESS, "Blog post removed")
        return HttpResponseRedirect('/blog/')
    else:
        return render(request, 'delete.html', Context({'blog':Blog.objects.get(id=id)}))

@csrf_protect
def createuser(request):
    if request.method == "POST" and not request.user.is_authenticated:
        user = authenticate(request.username)
        if user is not None:
            messages.add_message(request, messages.ERROR, "Unable to register to given credentials.\n"
                                                          "Try other username.")
            return render(request, 'createuser.html')
        else:
            user = User.objects.create_user(request.username,password=request.password)

    elif request.method == "GET" and not request.user.is_authenticated:
        return render(request, 'createuser.html')
    else:
        messages.add_message(request, messages.WARNING, "You can't do that.")
        if request.POST.get("next"):
            return redirect(request.POST.get("next"))
        else:
            return HttpResponseRedirect('/blog/')