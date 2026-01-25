from django.shortcuts import render

def hint_message(request, message, redirect, id=None):
    message = {
        "message": message,
        "id": id,
        "redirect": redirect,
    }
    return render(request, "hint_message.html", message)