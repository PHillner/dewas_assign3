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

def archive(request):
    return render(request, 'archive.html', Context({'blogs':Blog.objects.order_by("time")}))

def blog(request, id):
    if Blog.exists(id):
        blog = Blog.objects.get(id=id)
        update_session_stats(request, 'blog')
        return render(request, 'blog.html', Context({'blog':blog}))
    else:
        messages.add_message(request, messages.ERROR, "Sorry, the blog post you requested does not exist!")
        return HttpResponseRedirect('/')

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
    elif request.method=="GET":
        return render(request, 'edit.html', Context({'blog':Blog.objects.get(id=id)}))
    else:
        messages.add_message(request, messages.INFO,
                             "The blog is locked due to the fact that it is being edited by someone else. Please try again later.")
        return redirect('/blog/'+id+'/')

@login_required(login_url="/login/")
@csrf_protect
def add(request):
    if request.method=="POST" and request.user.is_authenticated:
        blog = Blog()
        blog.name = request.POST["name"]
        blog.text = request.POST["text"]
        blog.time = datetime.now()
        blog.save()
        update_session_stats(request, 'add')
        messages.add_message(request,messages.SUCCESS,"Blog post added")
        return HttpResponseRedirect('/')
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
        return HttpResponseRedirect('/')
    else:
        return render(request, 'delete.html', Context({'blog':Blog.objects.get(id=id)}))

def register_context(request):
    return Context({'fname': str(request.POST['first_name']), 'lname': str(request.POST['last_name']),
                'email': str(request.POST['email']), 'uname': str(request.POST['username'])})

@csrf_protect
def createuser(request):
    if request.method == "POST" and not request.user.is_authenticated:
        if str(request.POST['username']) is None or str(request.POST['username']) is ''\
                or str(request.POST['password']) is  None or str(request.POST['password']) is ''\
                or str(request.POST['password_check']) is None or str(request.POST['password_check']) is '':
            messages.add_message(request, messages.ERROR, "You need to fill at least the username and password fields to register.")
            return render(request, 'createuser.html', register_context(request))
        elif str(request.POST['password']) != str(request.POST['password_check']):
            messages.add_message(request, messages.ERROR, "Passwords must match!")
            return render(request, 'createuser.html', register_context(request))
        else:
            user = authenticate(username=request.POST.get("username"))
            if user is not None:
                messages.add_message(request, messages.ERROR, "Unable to register to given credentials.\n"
                                                              "Try other username.")
                return render(request, 'createuser.html', register_context(request))
            else:
                uname = str(request.POST['username'])
                passw = str(request.POST['password'])
                user = User.objects.create_user(uname,password=passw)
                user.first_name = str(request.POST['first_name'])
                user.last_name = str(request.POST['last_name'])
                user.email = str(request.POST['email'])
                if user is None:
                    messages.add_message(request, messages.ERROR, "Registration failed.")
                    return render(request, 'createuser.html', register_context(request))
                messages.add_message(request, messages.INFO, "Registration successful!")
                return render(request, 'home.html')

    elif request.method == "GET" and not request.user.is_authenticated:
        return render(request, 'createuser.html', Context({'fname': '',
                                                           'lname': '',
                                                           'email': '',
                                                           'uname': ''}))
    else:
        messages.add_message(request, messages.WARNING, "You can't do that.")
        if request.POST.get("next"):
            return redirect(request.POST.get("next"))
        else:
            return HttpResponseRedirect('/')