from django.core.management.base import BaseCommand

from quiz.models import Quiz, Question, Answer

import requests
from bs4 import BeautifulSoup
import json
import os
from mistralai import Mistral

from urllib.parse import urljoin
from pprint import pprint

base_url = "https://developer.mozilla.org/en-US/docs/Learn_web_development"

class Command(BaseCommand):

    

    def handle(self, *args, **options):
        response = requests.get(base_url)
        soup= BeautifulSoup(response.text, "html.parser")  
        sidebar = soup.find('div', class_="sidebar-body")
        links = [urljoin(base_url, link.get('href')) for link in sidebar.find_all("a")]
        lastlinks = []
        for i, link in enumerate(links): 
            if not any(link in other_string for other_string in links[:i] + links[i+1:]):
                lastlinks.append(link)

        api_key = os.environ["MISTRAL_API_KEY"]
        model = "mistral-large-latest"

        done_urls = [I.url for I in Quiz.objects.all()]

        for i, link in enumerate(lastlinks) : 
            if link in done_urls : 
                continue

            r = requests.get(link)
        
            if r.status_code != 200:
                continue
            
            soup = BeautifulSoup(r.text, 'html.parser')
            article = soup.find('article')
            text = article.get_text()


            client = Mistral(api_key=api_key)

            chat_response = client.chat.complete(
                model = model,
                messages = [
                    {
                        "role": "user",
                        "content": f'Generate 10 multiple-choice questions about the following text (each question/choices/answer combination must be provided in the form of a JSON object with the following structure where \u007b"question":"...", choices:["...", "...", "...", "..."], "answer":"..."\u007d - with "..." representing blanks to be filled) : {text}',
                    },
                ]
            )
            quiz = chat_response.choices[0].message.content
            json_object = json.loads(quiz[quiz.index('['):len(quiz)-quiz[::-1].index(']')])
            
            series = Quiz()
            series.url = link
            series.title = soup.find('title').get_text()
            series.description = soup.find("div", class_='section-content').find('p').get_text()
            series.save()

            for entry in json_object :
                question = Question()
                question.quiz = series
                question.text = entry["question"]
                question.save()
                for choice in entry["choices"]:
                    answer = Answer()
                    answer.question = question
                    answer.text = choice
                    if entry["answer"] == choice : 
                        answer.is_correct = True
                    answer.save()
            



