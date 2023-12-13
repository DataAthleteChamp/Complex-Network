import requests
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import json

nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')


def get_reviews(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    reviews = soup.find_all('p', class_='audience-reviews__review')
    return [review.get_text(strip=True) for review in reviews]


def analyze_sentiment(text):
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text)


url = 'https://www.rottentomatoes.com/m/the_hunger_games_the_ballad_of_songbirds_and_snakes/reviews?type=verified_audience'

reviews = get_reviews(url)
sentiments = [analyze_sentiment(review) for review in reviews]

data_to_save = []
for review, sentiment in zip(reviews, sentiments):
    data_to_save.append({"review": review, "sentiment": sentiment})

with open('reviews_sentiments.json', 'w', encoding='utf-8') as f:
    json.dump(data_to_save, f, ensure_ascii=False, indent=4)

print("Dane zostały zapisane do pliku JSON.")

for review, sentiment in zip(reviews, sentiments):
    print(f"Review: {review}\nSentiment: {sentiment}\n")