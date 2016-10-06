from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Template, Context, RequestContext
from django.template.loader import get_template
from models import Blog
from datetime import datetime
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages

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
    if request.method=="POST":
        blog = Blog.objects.get(id=id)
        blog.name = request.POST["name"]
        blog.text = request.POST["text"]
        blog.save()
        return HttpResponseRedirect('/blog/')
    else:
        t = get_template('edit.html')
        html = t.render(Context({'SITE_NAME': SITE_NAME, 'blog': Blog.objects.get(id=id)}), request)
        return HttpResponse(html)

@csrf_protect
def add(request):
    if request.method=="POST":
        blog = Blog()
        blog.name = request.POST["name"]
        blog.text = request.POST["text"]
        blog.time = datetime.today()
        blog.save()
        messages.add_message(request,messages.INFO,"Blog post added")
        return HttpResponseRedirect('/blog/')
    else:
        return render(request, 'add.html')

@csrf_protect
def delete(request, id):
    if request.method=="POST" and request.POST["choice1"]=="Yes":
        blog = Blog.objects.get(id=id)
        blog.delete()
        messages.add_message(request, messages.INFO, "Blog post removed")
        return HttpResponseRedirect('/blog/')
    else:
        t = get_template('delete.html')
        html = t.render(Context({'SITE_NAME': SITE_NAME, 'blog': Blog.objects.get(id=id)}), request)
        return HttpResponse(html)