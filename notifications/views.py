import json

from django.shortcuts import render
from django.http import HttpResponseNotAllowed, HttpResponse, HttpResponseNotFound, HttpResponseForbidden
from .models import User, Notification


# Create your views here.
def create_notification(request):
    user = User.get_user("tumanov-nv@1502.moscow")
    user.role = 7
    if request.method == "GET":
        if user.role == 7:
            return render(request, "403.html", status=403)
        if request.GET.get("select"):
            send_to = {}
            return render(request, "list.html", {"send_to": send_to})
        return render(request, "news-creating.html")
    return HttpResponseNotAllowed(["GET"])


def news(request):
    # TODO: Получение пользователя
    user = User.get_user("tumanov-nv@1502.moscow")
    user.role = 7
    if request.method == "GET":
        return HttpResponse(json.dumps(Notification.get_by_reciver(user)))
    elif request.method == "POST":
        # TODO: Добавление новости
        if user.role == 7:
            return render(request, "403.html", status=403)
        news = Notification([request.POST["reciver"]], user.fio, request.POST["text"], request.POST["head"])
        news.save()
        return HttpResponse()
    return HttpResponseNotAllowed(["GET", "POST"])


def news_by_id(request, news_id):
    # TODO: Получение пользователя
    user = User.get_user("tumanov-nv@1502.moscow")
    news = Notification.get_by_id(news_id)
    if news is None:
        return HttpResponseNotFound()
    if f"roll:{user.role}" not in news.recivers and f"id:{user.id}" not in news.recivers:
        return HttpResponseForbidden()
    if request.method == "GET":
        return HttpResponse(json.dumps(news))
    elif request.method == "PUT":
        if user.role == 7:
            return render(request, "403.html", status=403)
        # TODO: Редактирование новости
        return HttpResponse()
    elif request.method == "DELETE":
        if user.role == 7:
            return render(request, "403.html", status=403)
        # TODO: Удаление новости
        return HttpResponse()
    return HttpResponseNotAllowed(["GET", "PUT", "DElETE"])


def notifications(request):
    if request.method == "GET":
        return render(request, "index.html")
    return HttpResponseNotAllowed(["GET"])


def notification(request, news_id):
    if request.method == "GET":
        return render(request, "news.html", {"id": news_id})
    return HttpResponseNotAllowed(["GET"])
