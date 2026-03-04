#I also worked through the challenge in Python to better understand the API interactions before moving to Apps Script. I’ve attached that script as well.
"""
NYT + TMDB Movie Review Challenge (Python Practice Version)
-----------------------------------------------------------
This script is my optional Python implementation of the internship challenge.
It fetches NYT movie reviews, filters by keyword, extracts movie titles,
and prepares data for TMDB queries.

Note:
- The official submission is in Google Apps Script with Google Sheets.
- This Python version was used to better understand the APIs and logic.
"""


import os
import requests
import re
from dotenv import load_dotenv

load_dotenv()

#--------------Section A--------------------
NYT_API_KEY = os.getenv("NYT_API_KEY")
# https://api.nytimes.com/svc/search/v2/articlesearch.json?&fq=typeOfMaterials%3AReview AND section.name%3AMovies&api-key={api-key}
API_URL = f"https://api.nytimes.com/svc/search/v2/articlesearch.json?&fq=typeOfMaterials%3AReview AND section.name%3AMovies&api-key={NYT_API_KEY}"


try:
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()
    # print(data['response'])
except requests.exceptions.RequestException as e:
    print(f"API error: {e}")


filter_word = input("enter a filter word: ")
cleaned_filter_word = filter_word.lower().strip()
filtered_reviews = []


# print("All returned reviews:")
docs = data['response']
for movie in docs['docs']:
    raw_headline = movie.get('headline', {}).get('main', "N/A")
    cleaned_headline = raw_headline.lower()
    # print(cleaned_headline)

    # filter by filter word
    if cleaned_filter_word in cleaned_headline:
        # extract movie title from smart quotes
        match = re.search(r"‘([^’]+)’", raw_headline) #copilot assisted with regex - 3 March
        if match:
            movie_title = match.group(1).strip()
        else:
            # fallback
            if "Review:" in raw_headline:
                movie_title = raw_headline.split("Review:")[0].strip()
            else:
                movie_title = raw_headline.split(":")[0].strip()
     
        new_movie = {
            # "headline": movie.get('headline', {}).get('main', 'N/A'),
            # "movie_title": movie.get('headline', {}).get('main', 'N/A').replace("‘", "").replace("’", "").strip(),
            "headline": raw_headline, 
            "movie_title": movie_title,        
            "abstract": movie.get('abstract', 'N/A'),
            "author": movie.get('byline', {}).get('original', 'N/A'),
            "article_id": movie.get('_id', 'N/a'),
            "pub_date": movie.get('pub_date', 'N/A'),
            "source": movie.get('source', 'N/A'),
            "web_url": movie.get('web_url', 'N/A')
        }
        filtered_reviews.append(new_movie)

# print("\n")

print(f"\nFiltered reviews according to filter word: '{filter_word}'")
if not filtered_reviews:
    print(f"No reviews found containing: {filter_word}")
else:
    for review in filtered_reviews:
        print("Headline:", review["headline"]) 
        print("Movie title:", review["movie_title"]) 
        print("Abstract:", review["abstract"]) 
        print("Author:", review["author"]) 
        print("Article ID:", review["article_id"]) 
        print("Publication Date:", review["pub_date"]) 
        print("Source:", review["source"]) 
        print("Web URL:", review["web_url"]) 


#--------------Section B--------------------
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

