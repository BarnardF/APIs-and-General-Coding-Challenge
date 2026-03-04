"""
APIs and General Coding Challenge (Python version)

I initially worked through the challenge in Python to build an understanding of the API interactions 
and data structures before translating the logic to Google Apps Script

"""
import os
import requests
import re
from dotenv import load_dotenv

load_dotenv()

#--------------Section A--------------------
"""
#https://developer.nytimes.com/docs/articlesearch-product/1/overview
https://api.nytimes.com/svc/search/v2/articlesearch.json?&fq=typeOfMaterials%3AReview AND section.name%3AMovies&api-key={api-key}
"""

NYT_API_KEY = os.getenv("NYT_API_KEY")
NYT_API_URL = f"https://api.nytimes.com/svc/search/v2/articlesearch.json?&fq=typeOfMaterials%3AReview AND section.name%3AMovies&api-key={NYT_API_KEY}"


try:
    response = requests.get(NYT_API_URL)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    print(f"API error: {e}")


filter_word = input("enter a filter word: ").lower().strip()
filtered_reviews = []


# print("All returned reviews:")
for movie in data['response']['docs']:
    raw_headline = movie.get('headline', {}).get('main', "N/A")
    cleaned_headline = raw_headline.lower()

    # filter by filter word
    if filter_word in cleaned_headline:
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


print(f"\nFiltered reviews according to filter word: '{filter_word}': {len(filtered_reviews)} found")
if not filtered_reviews:
    print(f"No reviews found containing: {filter_word}")
else:
    for review in filtered_reviews:
        for key, value in review.items():
            print(f"{key}: {value}")


#--------------Section B--------------------
"""
MDB title matching is imperfect, movie titles differ between NYT and TMDB.
Strategy: 
1. search using the most specific title available (from NYT keywords), 
2. then match by release year. 
3. Falls back to top result if no year match.
https://developer.themoviedb.org/docs/search-and-query-for-details
https://developer.themoviedb.org/reference/search-movie
"""
TMDB_TOKEN = os.getenv("TMDB_TOKEN")

TMDB_SEARCH_URL  = f"https://api.themoviedb.org/3/search/movie"
TMDB_DETAILS_URL = "https://api.themoviedb.org/3/movie"

tmdb_headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_TOKEN}"
}


combined_results = []

for review in filtered_reviews:
    movie_title = review['movie_title']
    pub_year = review['pub_date'][:4]

    # search movie id
    try:
        search_response = requests.get(TMDB_SEARCH_URL, headers=tmdb_headers, params = {"query": movie_title, "page": 1})
        search_response.raise_for_status()
        results = search_response.json().get('results', [])

        if not results:
            print(f"No TMDB match for: {movie_title}")
            continue

        # match by release year
        movie_id = None
        for result in results:
            if result.get("release_date", "")[:4] == pub_year:
                movie_id = result["id"]
                break
        # fallback
        if not movie_id:
            movie_id = results[0]["id"]
    except requests.exceptions.RequestException as e:
        print(f"TMD search error for '{movie_title}': {e}")
        continue

    # get all movie details
    try:
        details_response = requests.get(f"{TMDB_DETAILS_URL}/{movie_id}", headers=tmdb_headers)
        details_response.raise_for_status()
        details = details_response.json()

    except requests.exceptions.RequestException as e:
        print(f"TMD details error for '{movie_title}': {e}")
        continue

    # extract 15 fields from TMDB
    # tmdb_id
    # title
    # original_title
    # release_date
    # budget
    # revenue
    # popularity
    # vote_average
    # vote_count
    # genres
    # overview
    # origin_country
    # original_language
    # homepage
    # tagline
    tmdb_fields = {
        "tmdb_id": details.get("id", "N/A"),
        "tmdb_title": details.get("title", "N/A"),
        "original_title": details.get("original_title", "N/A"),
        "release_date": details.get("release_date", "N/A"),
        "budget": details.get("budget", "N/A"),
        "revenue": details.get("revenue", "N/A"),
        "popularity": details.get("popularity", "N/A"),
        "vote_average": details.get("vote_average", "N/A"),
        "vote_count": details.get("vote_count", "N/A"),
        "genres": ", ".join([g["name"] for g in details.get("genres", [])]),
        "overview": details.get("overview", "N/A"),
        "origin_country": details.get("origin_country", "N/A"),
        "original_language": details.get("original_language", "N/A"),
        "homepage": details.get("homepage", "N/A"),
        "tagline": details.get("tagline", "N/A")
    }
    # https://stackoverflow.com/questions/62498441/dict-dict-2-how-python-dictionary-alternative-operator-works
    combined_results.append(review | tmdb_fields) 

print(f"\nCombined results: {len(combined_results)} movies")
for movie in combined_results:
    for key, value in movie.items():
        print(f"{key}: {value}")
