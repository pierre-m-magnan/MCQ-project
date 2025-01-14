from django.shortcuts import render

# Create your views here.


from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt
import json

import os
from mistralai import Mistral
from bs4 import BeautifulSoup
from pprint import pprint


api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"


def index(request):
    return render(request, 'quiz/index.html')

@csrf_exempt
def submit_link(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_link = data.get('link')
        r = requests.get(user_link)
        soup = BeautifulSoup(r.text, 'html.parser')
        article = soup.find('article')
        text = article.get_text()

        client = Mistral(api_key=api_key)

        chat_response = client.chat.complete(
            model = model,
            messages = [
                {
                    "role": "user",
                    "content": f"Generate 10 multiple-choice questions about the following text (each question/choices/answer combination must be provided in the form of a JSON object) : {text}",
                },
            ]
        )
        quiz = chat_response.choices[0].message.content

        # quiz = '```json\n[\n    {\n        "question": "What is the main objective of the tutorial on Django forms?",\n        "choices": [\n            "To understand how to write forms to get information from users and update the database.",\n            "To understand how to create an admin site.",\n            "To understand how to authenticate users.",\n            "To understand how to create a Django app from scratch."\n        ],\n        "answer": "To understand how to write forms to get information from users and update the database."\n    },\n    {\n        "question": "Which class is the heart of Django\'s form handling system?",\n        "choices": [\n            "FormView",\n            "Form",\n            "ModelForm",\n            "GenericView"\n        ],\n        "answer": "Form"\n    },\n    {\n        "question": "What does the \'action\' attribute in an HTML form specify?",\n        "choices": [\n            "The resource/URL where data is to be sent for processing when the form is submitted.",\n            "The HTTP method used to send the data.",\n            "The default value for the form fields.",\n            "The label for the form fields."\n        ],\n        "answer": "The resource/URL where data is to be sent for processing when the form is submitted."\n    },\n    {\n        "question": "What is the recommended HTTP method for forms that change user data?",\n        "choices": [\n            "GET",\n            "POST",\n            "PUT",\n            "DELETE"\n        ],\n        "answer": "POST"\n    },\n    {\n        "question": "What is the purpose of the {% csrf_token %} in Django templates?",\n        "choices": [\n            "To render the form fields.",\n            "To include cross-site request forgery protection.",\n            "To validate the form data.",\n            "To submit the form."\n        ],\n        "answer": "To include cross-site request forgery protection."\n    },\n    {\n        "question": "Which method is used to check if a form is valid in Django?",\n        "choices": [\n            "form.is_valid()",\n            "form.validate()",\n            "form.check_validity()",\n            "form.clean_data()"\n        ],\n        "answer": "form.is_valid()"\n    },\n    {\n        "question": "What is the purpose of the \'clean_<field_name>()\' method in Django forms?",\n        "choices": [\n            "To render the form fields.",\n            "To validate a single field.",\n            "To submit the form.",\n            "To include cross-site request forgery protection."\n        ],\n        "answer": "To validate a single field."\n    },\n    {\n        "question": "Which decorator is used to require that the user is logged in?",\n        "choices": [\n            "@login_required",\n            "@permission_required",\n            "@authenticate_user",\n            "@check_login"\n        ],\n        "answer": "@login_required"\n    },\n    {\n        "question": "What is the purpose of the \'ModelForm\' class in Django?",\n        "choices": [\n            "To create a form from a model.",\n            "To validate form data.",\n            "To render form fields.",\n            "To include cross-site request forgery protection."\n        ],\n        "answer": "To create a form from a model."\n    },\n    {\n        "question": "Which generic view is used to create a new record in Django?",\n        "choices": [\n            "CreateView",\n            "UpdateView",\n            "DeleteView",\n            "FormView"\n        ],\n        "answer": "CreateView"\n    }\n]\n```'
        if quiz.startswith("```json\n"):
            quiz = quiz[8:]
        if quiz.endswith("\n```"):
            quiz = quiz[:-4]
        if quiz : 
            try:
                json_object = json.loads(quiz)
                quiz = {'questions': json_object}
                correct_answers = {}
                for i, question in enumerate(quiz['questions']):
                    question['id'] = i  # Ajouter un identifiant unique à chaque question
                    correct_answers[i] = question['answer']
                    question.pop('answer') # pour éviter de donner les réponses dans le front
                request.session['correct_answers'] = correct_answers
                return JsonResponse(quiz)
            except json.JSONDecodeError as e:
                print(f"Erreur lors du parsing JSON : {e}")
                return None
        else:
            return JsonResponse({'error': 'Erreur lors de la génération du questionnaire'}, status=500)

@csrf_exempt
def submit_quiz(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_answers = data.get('answers')
        correct_answers = request.session.get('correct_answers', {})
        score = sum(1 for answer in user_answers if correct_answers.get(answer.get('questionId')) == answer.get('selectedOptionIndex'))       
        results = [{'questionId': answer.get('questionId'), 'isCorrect': correct_answers.get(answer.get('questionId')) == answer.get('selectedOptionIndex')} for answer in user_answers]
        return JsonResponse({'score': score, 'results': results})