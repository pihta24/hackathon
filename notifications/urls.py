from django.urls import path
from . import views

urlpatterns = [
    path("", views.notifications),
    path("<int:news_id>", views.notification),
    path("create", views.create_notification),
    path("api/news", views.news),
    path("api/news/<int:news_id>", views.news_by_id)
]
