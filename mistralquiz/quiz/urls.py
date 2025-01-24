from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('quizzes/', views.quizlist, name="quiz-list"),
    path('quiz/<int:quiz_id>', views.quizdetail, name='quiz-detail'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'), # type: ignore
]

