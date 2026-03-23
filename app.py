import csv
import json
import os
import random
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from flask import Flask, render_template, request, jsonify, session

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)
app.secret_key = os.urandom(24)

HTTP_UA = (
    "CineMatch/2.0 (movie demo; https://github.com/) "
    "Python-urllib compatible; contact: local"
)

def fetch_omdb_data(title: str) -> dict | None:
    if not title:
        return None
        
    api_key = os.environ.get("OMDB_API_KEY")
    if not api_key:
        return None
        
    q = urllib.parse.quote(title)
    url = f"http://www.omdbapi.com/?apikey={api_key}&t={q}"
    req = urllib.request.Request(url, headers={"User-Agent": HTTP_UA})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("Response", "") == "True":
                return data
    except Exception:
        pass
    return None

def enrich_movie_data(movie: dict) -> None:
    omdb_data = fetch_omdb_data(movie.get("title", ""))
    if omdb_data:
        poster = omdb_data.get("Poster")
        if poster and poster != "N/A" and poster.startswith("http"):
            movie["poster"] = poster
            
        plot = omdb_data.get("Plot")
        if plot and plot != "N/A":
            movie["description"] = plot
            
        rating = omdb_data.get("imdbRating")
        if rating and rating != "N/A":
            movie["rating"] = rating
            
        genre = omdb_data.get("Genre")
        if genre and genre != "N/A":
            movie["genre"] = genre
            
    else:
        p = movie.get("poster") or ""
        if p.startswith("/static/cache/"):
            movie["poster"] = ""


def load_movies():
    movies = []
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'movies.csv')
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                movies.append(row)
    except FileNotFoundError:
        print("Error: movies.csv not found. Loading fallback dataset.")
        
    # If movies list is too small (meaning they only have Vikram and Baahubali), let's inject a robust fallback list!
    if len(movies) < 5:
        return movies + [
            # Kollywood
            {"title": "Vikram", "industry": "Kollywood", "genre": "Action"},
            {"title": "Baahubali", "industry": "Kollywood", "genre": "Action"},
            {"title": "Leo", "industry": "Kollywood", "genre": "Action"},
            {"title": "Darbar", "industry": "Kollywood", "genre": "Action"},
            {"title": "Master", "industry": "Kollywood", "genre": "Action"},
            {"title": "Kaithi", "industry": "Kollywood", "genre": "Action"},
            {"title": "Enthiran", "industry": "Kollywood", "genre": "Sci-Fi"},
            {"title": "2.0", "industry": "Kollywood", "genre": "Sci-Fi"},
            {"title": "Indru Netru Naalai", "industry": "Kollywood", "genre": "Sci-Fi"},
            {"title": "Maanaadu", "industry": "Kollywood", "genre": "Sci-Fi"},
            {"title": "Iru Mugan", "industry": "Kollywood", "genre": "Sci-Fi"},
            {"title": "I", "industry": "Kollywood", "genre": "Sci-Fi"},
            {"title": "Super Deluxe", "industry": "Kollywood", "genre": "Drama"},
            {"title": "Asuran", "industry": "Kollywood", "genre": "Drama"},
            
            # Bollywood
            {"title": "Sholay", "industry": "Bollywood", "genre": "Action"},
            {"title": "Dangal", "industry": "Bollywood", "genre": "Drama"},
            {"title": "PK", "industry": "Bollywood", "genre": "Sci-Fi"},
            {"title": "Koi Mil Gaya", "industry": "Bollywood", "genre": "Sci-Fi"},
            {"title": "Ra.One", "industry": "Bollywood", "genre": "Sci-Fi"},
            {"title": "Krrish", "industry": "Bollywood", "genre": "Sci-Fi"},
            {"title": "Ghajini", "industry": "Bollywood", "genre": "Action"},
            {"title": "War", "industry": "Bollywood", "genre": "Action"},
            {"title": "Pathaan", "industry": "Bollywood", "genre": "Action"},
            {"title": "Jawan", "industry": "Bollywood", "genre": "Action"},
            {"title": "3 Idiots", "industry": "Bollywood", "genre": "Drama"},
            
            # Hollywood
            {"title": "Inception", "industry": "Hollywood", "genre": "Sci-Fi"},
            {"title": "Interstellar", "industry": "Hollywood", "genre": "Sci-Fi"},
            {"title": "The Matrix", "industry": "Hollywood", "genre": "Sci-Fi"},
            {"title": "Avatar", "industry": "Hollywood", "genre": "Sci-Fi"},
            {"title": "Blade Runner 2049", "industry": "Hollywood", "genre": "Sci-Fi"},
            {"title": "The Dark Knight", "industry": "Hollywood", "genre": "Action"},
            {"title": "Avengers", "industry": "Hollywood", "genre": "Action"},
            {"title": "John Wick", "industry": "Hollywood", "genre": "Action"},
            {"title": "Mad Max", "industry": "Hollywood", "genre": "Action"},
            {"title": "Gladiator", "industry": "Hollywood", "genre": "Action"},
            {"title": "Titanic", "industry": "Hollywood", "genre": "Romance"}
        ]
        
    return movies

MOVIES = load_movies()


def _is_greeting(text: str) -> bool:
    t = text.strip().lower()
    if not t:
        return False
    return bool(
        re.match(r"^(hi|hello|hey|howdy|good\s+(morning|afternoon|evening))[\s!.,]*$", t)
    )

def _detect_genre_alias(user_message: str) -> str | None:
    u = user_message.lower().strip()
    if re.search(r"sci\s*[-]?\s*fi|science\s+fiction", u):
        return "sci-fi"
    return None

def _find_matched_genres(user_message: str, industry_movies: list) -> list[str]:
    if not industry_movies:
        return []
    canon: dict[str, str] = {}
    for m in industry_movies:
        g = m.get("genre", "")
        key = g.lower()
        if key and key not in canon:
            canon[key] = g

    u = user_message.lower().strip()
    u_flat = re.sub(r"[\s\-_]+", "", u)

    matched = []
    for g_lc, g_orig in canon.items():
        if g_lc == "sci-fi":
            if re.search(r"sci\s*[-]?\s*fi|science\s+fiction", u):
                matched.append(g_orig)
            continue
        g_flat = re.sub(r"[^a-z0-9]", "", g_lc)
        if len(g_flat) < 2:
            continue
        
        is_match = False
        if re.search(r"\b" + re.escape(g_lc) + r"\b", u):
            is_match = True
        elif re.search(r"\b" + re.escape(g_lc.replace("-", " ")) + r"\b", u):
            is_match = True
        elif g_flat in u_flat:
            if len(g_flat) >= 4 or g_flat == u_flat:
                is_match = True
                
        if is_match and g_orig not in matched:
            matched.append(g_orig)
            
    return matched

@app.route('/')
def home():
    session['step'] = 'industry'
    session['industry'] = None
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').lower().strip()
    
    if not user_message:
        return jsonify({"response": "I didn't quite catch that. Could you say something?", "movies": []})

    if "reset" in user_message or "start over" in user_message:
        session['step'] = 'industry'
        session['industry'] = None
        return jsonify({"response": "Alright, let's start over! Which industry do you prefer: **Kollywood**, **Hollywood**, or **Bollywood**?", "movies": []})

    step = session.get('step', 'industry')
    
    if step == 'industry':
        if _is_greeting(user_message):
            return jsonify({
                "response": (
                    "**Hello!** I'm **CineMatch**, your friendly movie guide. "
                    "I'll suggest films based on **industry** (Kollywood, Hollywood, or Bollywood) and **genre**. "
                    "Which industry do you prefer: **Kollywood**, **Hollywood**, or **Bollywood**?"
                ),
                "movies": [],
            })

        industries = ['kollywood', 'hollywood', 'bollywood']
        matched_industry = None
        for ind in industries:
            if ind in user_message:
                matched_industry = ind
                break
        
        if matched_industry:
            session['industry'] = matched_industry.capitalize()
            session['step'] = 'genre'
            response = f"Excellent! {matched_industry.capitalize()} has some amazing films. Now, what **genre** would you like to explore? (e.g., Action, Drama, Comedy, Sci-Fi)"
            return jsonify({"response": response, "movies": []})
        else:
            return jsonify({
                "response": "I'm sorry, I specialize in **Kollywood**, **Hollywood**, and **Bollywood**. Which one do you prefer?",
                "movies": []
            })

    elif step == 'genre':
        industry = session.get('industry')
        industry_movies = [m for m in MOVIES if m.get('industry') == industry]

        if _is_greeting(user_message):
            ind = industry or "this industry"
            return jsonify({
                "response": (
                    f"**Hey!** You're browsing **{ind}**. "
                    "Tell me a **genre**—for example **Action**, **Drama**, **Horror**, **Romance**, or **Sci-Fi**."
                ),
                "movies": [],
            })

        matched_genres = _find_matched_genres(user_message, industry_movies)

        if not matched_genres:
            alias_lc = _detect_genre_alias(user_message)
            if alias_lc:
                has_genre = any(m.get("genre", "").lower() == alias_lc for m in industry_movies)
                if not has_genre:
                    seen: dict[str, str] = {}
                    for m in industry_movies:
                        g = m.get("genre", "")
                        k = g.lower()
                        if k and k not in seen:
                            seen[k] = g
                    display_genres = ", ".join(sorted(seen.values(), key=str.lower)) if seen else "none available"
                    ind = industry or "this industry"
                    label = "Sci-Fi" if alias_lc == "sci-fi" else alias_lc.title()
                    return jsonify({
                        "response": (
                            f"We don't have **{label}** movies in our list for **{ind}** right now. "
                            f"Try choosing a genre available here: **{display_genres}**."
                        ),
                        "movies": [],
                    })
        
        if matched_genres:
            matching_movies = []
            for m in industry_movies:
                if m.get('genre') in matched_genres:
                    matching_movies.append(m)
                    
            random.shuffle(matching_movies)
            recommendations = matching_movies[:5]

            for m in recommendations:
                enrich_movie_data(m)
            
            industry_str = str(industry) if industry else "Unknown Industry"
            
            if len(matched_genres) == 1:
                genre_str = matched_genres[0]
            else:
                genre_str = ", ".join(matched_genres[:-1]) + " and " + matched_genres[-1]
                
            response = f"Here are some top {genre_str} movies from {industry_str}:"
            return jsonify({
                "response": response, 
                "movies": [{
                    "title": m.get('title', ''),
                    "genre": m.get('genre', ''),
                    "rating": m.get('rating', 'N/A'),
                    "description": m.get('description', 'No description available.'),
                    "poster": m.get('poster', ''),
                    "link": m.get('link', '#')
                } for m in recommendations]
            })
        else:
            seen: dict[str, str] = {}
            for m in industry_movies:
                g = m.get("genre", "")
                k = g.lower()
                if k and k not in seen:
                    seen[k] = g
            display_list = sorted(seen.values(), key=str.lower)
            display_genres = ", ".join(display_list)
            industry_str = str(industry) if industry else "this industry"
            return jsonify({
                "response": (
                    f"I couldn't match that to a genre in {industry_str}. "
                    f"Try one of these: **{display_genres}**."
                ),
                "movies": [],
            })

    return jsonify({"response": "Something went wrong. Let's start over.", "movies": []})

if __name__ == '__main__':
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5001"))
    csv_path = os.path.join(os.path.dirname(__file__), 'data', 'movies.csv')
    app.run(debug=True, host=host, port=port, extra_files=[csv_path])
