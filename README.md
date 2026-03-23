# CineMatch - Movie Recommendation Chatbot 🎬

CineMatch is an intelligent, interactive movie recommendation chatbot built with Flask. It allows users to discover movies by selecting their preferred film industry (Kollywood, Hollywood, or Bollywood) and genre (Action, Sci-Fi, Drama, Romance).

## Features ✨
- **Interactive Chat Interface**: A beautiful, modern chat UI built with HTML/CSS/JS.
- **Dynamic Content Support**: Starts with an intelligent base dataset of movies across multiple industries and dynamically falls back to your own custom `movies.csv` file.
- **Live OMDB Integration**: Automatically fetches real-time movie descriptions, actual IMDb ratings, and high-quality movie posters from the OMDB API.
- **Direct IMDb Links**: View full movie details directly on IMDb with one click.

## Quick Start 🚀

### 1. Clone the repository
```bash
git clone https://github.com/kathirm1323-ai/Movie-Recommendation-Chatbot.git
cd Movie-Recommendation-Chatbot
```

### 2. Install Dependencies
Make sure you have Python installed, then install the required packages:
```bash
pip install -r requirements.txt
```

### 3. Setup The Environment Variables
Create a `.env` file in the root directory and add your OMDB API Key:
```env
OMDB_API_KEY=your_api_key_here
```

### 4. Run the Application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5001/` to start chatting!

## Custom Dataset 📁
By default, CineMatch has a robust fallback list built-in. If you want to train it on your own specific list of movies, simply create a `movies.csv` file inside the `data/` directory with `title`, `industry`, and `genre` columns.

## Tech Stack 🛠️
- **Backend**: Python, Flask
- **Frontend**: HTML5, Vanilla JavaScript, CSS3
- **APIs**: OMDB API (Open Movie Database)
