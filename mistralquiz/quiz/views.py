from django.shortcuts import render, get_object_or_404

# Create your views here.


from .models import Quiz, Question, Answer
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def index(request):
    num_quizzes = Quiz.objects.all().count()
    return render(request, 'quiz/index.html', context={"num_quizzes":num_quizzes})


def submit_quiz(request, quiz_id):
    if request.method == 'POST':
        quiz = get_object_or_404(Quiz, pk=quiz_id)
        score = 0

        questions = Question.objects.filter(quiz=quiz)
        for question in questions : 
            selected_answer_id = request.POST.get(f'question_{question.id}')
            if selected_answer_id:
                selected_answer = Answer.objects.get(pk=selected_answer_id)
                if selected_answer.is_correct:
                    score += 1
       
        return render(request, 'quiz/quizresult.html', {'score': score})

def quizlist(request):
    base_url = "https://developer.mozilla.org/en-US/docs/Learn_web_development"

    response = requests.get(base_url)
    soup= BeautifulSoup(response.text, "html.parser")
    sidebar = soup.find('div', class_="sidebar-body")
    urls=[]
    quizzes=[]
    for link in sidebar.find_all("a"):
        urls.append(urljoin(base_url, link.get('href')))
        if Quiz.objects.filter(url=urljoin(base_url, link.get('href'))):
            quizzes.append(Quiz.objects.filter(url=urljoin(base_url, link.get('href')))[0])

    structure={"Getting started modules":{"Environment setup":[0,5], "Your first website":[5,10], "Web standards":[10,13],"Soft skills":[13,17] },
               "Core modules":{"Structuring content with HTML":[17,35], "CSS styling basics":[35,54],"CSS text styling":[54,59], "CSS layout":[59,67], "Dynamic scripting with JavaScript":[67,89], "JavaScript frameworks and libraries":[89,98], "Accessibility":[98,106], "Design for developers": [106,107], "Version control":[107,108]},
               "Extension modules":{"Advanced JavaScript objects":[108,113], "Client-side web APIs":[113,118], "Asynchronous JavaScript":[118,122], "Web forms":[122,132], "Understanding client-side tools":[132,136], "Server-side websites":[136,164], "Web performance":[164,174], "Testing":[174,180], "Transform and animate CSS":[180,181], "Security and privacy":[181,182]},
               "Further resources":{"How to solve common problems":[182,188], "About":[188,189], "Resources for educators":[189,190], "Changelog":[190,191]}
               }


    return render(request, 'quiz/quizlist.html', {'quizzes': quizzes, "structure":structure})

def quizdetail(request, quiz_id):
    quiz = Quiz.objects.get(id=quiz_id)
    qadict = {question:[a for a in Answer.objects.filter(question=question)] for question in Question.objects.filter(quiz=quiz)}
    return render(request, 'quiz/quizdetail.html', {'quiz': quiz, 'qadict':qadict})
