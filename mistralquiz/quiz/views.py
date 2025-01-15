from django.shortcuts import render

# Create your views here.


from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt
import json

import os
from mistralai import Mistral
from bs4 import BeautifulSoup


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
