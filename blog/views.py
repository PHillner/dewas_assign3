from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Template, Context, RequestContext
from django.template.loader import get_template
from models import Blog

# Create your views here.


def home(request):
    t = get_template(home.html)
    html = t.render(Context({'added':0,'removed':0}))
    return HttpResponse(html)

def blog(request, id):
    if Blog.exists(id):
        blog = Blog.getById(id)
    else:
        return None
    t = get_template(blog.html)
    html = t.render(Context({'id':blog.id,'name':blog.name,'date':blog.date}))
    return HttpResponse(html)

def edit(request, id):
    if Blog.exists(id):
        blog = Blog.getById(id)
    else:
        return None
    t = get_template(edit.html)
    html = t.render(Context({'id':blog.id,'name':blog.name,'date':blog.date}))
    return HttpResponse(html)

def add(request):
    t = get_template(home.html)
    html = t.render(Context({'added':1,'removed':0}))
    return HttpResponse(html)

def delete(request, id):
    if Blog.exists(id):
        blog = Blog.getById(id)
    else:
        return None
    t = get_template(home.html)
    html = t.render(Context({'added':0,'removed':1}))
    return HttpResponse(html)