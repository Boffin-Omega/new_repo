from django.shortcuts import render
from . import util
from markdown2 import Markdown
markdowner = Markdown()
from django.http import HttpResponse, HttpResponseRedirect
from random import choice

def convert_md_to_html(title):
    content = util.get_entry(title)
    if content == None:
        return None
    return markdowner.convert(content)

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    body = convert_md_to_html(title)
    if body == None:
        return render(request, "encyclopedia/error.html")
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "body": body
    })
def search(request):
    #title = request.POST['q']
    #entry(request,title)
    if request.method == "POST":
        entry_search = request.POST['q'] # some random ahh method like how tf u expect me to know this
        body = convert_md_to_html(entry_search)
        if body is not None:
            return render(request, "encyclopedia/entry.html", {
                "title": entry_search,
                "body": body
            }) 
        return render(request, "encyclopedia/error.html")      

def new_page(request):
    if request.method == "POST":
        title = request.POST['new_page']
        markdown = request.POST['markdown']

        if title in util.list_entries():
            return HttpResponse(f"Error, page with name {request.POST['new_page']} already exists")

        if request.POST['markdown'] == None:
            return HttpResponse("Error, no markdown content found")

        util.save_entry(title, markdown)
        body = convert_md_to_html(title)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "body": body
        })
    elif request.method == "GET":
        return render(request, "encyclopedia/new_page.html",)

def random(request):
    entry_list = util.list_entries()
    title = choice(entry_list)
    body = convert_md_to_html(title)
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "body": body
    })
def edit(request):
    if request.method == 'POST':
        title = request.POST.get('title', 'untitled')
        new_markdown = request.POST.get('markdown')
        util.save_entry(title,new_markdown)
        return HttpResponseRedirect(f"wiki/{title}")
    
    title = request.GET['title']
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "markdown": util.get_entry(title)
    })