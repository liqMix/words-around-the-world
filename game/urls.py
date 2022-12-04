from django.urls import path, include

from . import views

app_name = 'game'
urlpatterns = [
    path('', views.GameView.as_view(), name='index'),
    path('accounts/', include("django.contrib.auth.urls")),
]
