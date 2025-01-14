from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('submit-link/', views.submit_link, name='submit_link'), # type: ignore
    path('submit-quiz/', views.submit_quiz, name='submit_quiz'), # type: ignore
]