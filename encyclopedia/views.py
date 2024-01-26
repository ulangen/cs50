from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from . import util

from random import randint
from markdown2 import markdown

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    content = util.get_entry(title)

    # The entry does not exist
    if content == None:
        return render(request, "encyclopedia/error.html", {
            "message": "Page not found."
        })

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": markdown(content)
    })

def search(request):
    question = request.GET["q"]

    entry = util.get_entry(question)

    # Show list of matches
    if entry == None:
        entries = util.list_entries()
        matches = []

        for entry in entries:
            if question in entry:
                matches.append(entry)

        # No matches found
        if len(matches) == 0:
            return render(request, "encyclopedia/error.html", {
                "message": "No matches found."
            })
        
        return render(request, "encyclopedia/search.html", {
            "entries": matches
        })

    return HttpResponseRedirect(reverse("entry", kwargs={"title": question}))

def create(request):
    # Save entry
    if request.method == "POST":
        title = request.POST["title"]
        
        # The entry does not exist
        if util.get_entry(title) == None:
            util.save_entry(title, request.POST["content"])
            return HttpResponseRedirect(reverse("entry", kwargs={"title": title}))
        
        # The entry already exists
        return render(request, "encyclopedia/error.html", {
            "message": "Page already exist."
        })

    return render(request, "encyclopedia/create.html")

def edit(request, title):
    # Save changes
    if request.method == "POST":
        content = request.POST["content"]
        util.save_entry(title, content)
        return HttpResponseRedirect(reverse('entry', kwargs={"title": title}))

    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": util.get_entry(title)
    })

def random_entry(request):
    index = randint(0, len(util.list_entries()) - 1)
    title = util.list_entries()[index]
    return HttpResponseRedirect(reverse("entry", kwargs={"title": title}))