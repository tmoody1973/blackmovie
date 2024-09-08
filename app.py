import streamlit as st
import requests
import sqlite3
import time
from dotenv import load_dotenv
import os
import json
import random
#branch test
# Set custom theme
st.set_page_config(
    page_title="Black Cinema Trivia",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
OMDB_API_KEY = os.getenv('OMDB_API_KEY')
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')

# Debug: Print the API key to verify it's loaded correctly
print(f"CLAUDE_API_KEY: {CLAUDE_API_KEY}")

# Initialize session state
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'user_answer' not in st.session_state:
    st.session_state.user_answer = None
if 'question_data' not in st.session_state:
    st.session_state.question_data = None

# List of 100 movies directed by Black directors
BLACK_DIRECTED_MOVIES = [
    "Do the Right Thing", "Moonlight", "Get Out", "Boyz n the Hood", "Fruitvale Station",
    "Selma", "Black Panther", "12 Years a Slave", "Malcolm X", "Creed",
    "Straight Outta Compton", "Us", "Fences", "Precious", "Daughters of the Dust",
    "Pariah", "Killer of Sheep", "Eve's Bayou", "Menace II Society", "Love & Basketball",
    "Waiting to Exhale", "Set It Off", "Friday", "Crooklyn", "Juice",
    "The Last Black Man in San Francisco", "Mudbound", "If Beale Street Could Talk", "Dope", "Bessie",
    "Bamboozled", "Belly", "Clockers", "Chi-Raq", "Da 5 Bloods",
    "Shaft", "Candyman", "Soul Food", "The Best Man", "Higher Learning",
    "Poetic Justice", "New Jack City", "Boomerang", "Just Mercy", "Queen & Slim",
    "The Wood", "Brown Sugar", "Hustle & Flow", "Talk to Me", "Akeelah and the Bee",
    "Drumline", "ATL", "Paid in Full", "The Inevitable Defeat of Mister & Pete", "Middle of Nowhere",
    "Beyond the Lights", "The Secret Life of Bees", "Jumping the Broom", "Cadillac Records", "Southside with You",
    "The Photograph", "The Forty-Year-Old Version", "Miss Juneteenth", "Night Catches Us", "Atlantics",
    "Girlhood", "Rocks", "The Last Tree", "Rafiki", "Farming",
    "Noughts + Crosses", "The Boy Who Harnessed the Wind", "Queen of Katwe", "Beasts of No Nation", "Tsotsi",
    "Atlantique", "Yeelen", "Touki Bouki", "Black Girl", "Hyenas",
    "Moolaadé", "Bamako", "Timbuktu", "Félicité", "I Am Not a Witch",
    "Vaya", "Inxeba (The Wound)", "Kati Kati", "Supa Modo", "Rafiki",
    "Yardie", "The Kitchen", "Clemency", "The Burial of Kojo", "Eyimofe (This Is My Desire)",
    "Residue", "Nine Days", "Zola", "Passing", "The Harder They Fall"
]

# Function to fetch movie poster from OMDB API
def fetch_movie_poster(movie_title):
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data.get('Poster', None)

# Function to generate trivia question using Claude 3.5 Sonnet
def generate_trivia_question():
    api_url = 'https://api.anthropic.com/v1/messages'
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': CLAUDE_API_KEY,
        'anthropic-version': '2023-06-01'
    }
    
    # Randomly select a movie
    selected_movie = random.choice(BLACK_DIRECTED_MOVIES)
    
    prompt = f"""Generate a trivia question about Black cinema in JSON format with fields: question, options (array), answer, and movie_title. 
    Use the film "{selected_movie}" and craft a unique and challenging (but not impossibly difficult) question about its plot, characters, director, awards, or an interesting fact, along with four possible answer options including the correct one.
    Ensure the question hasn't been used before."""

    payload = {
        'model': 'claude-3-5-sonnet-20240620',
        'max_tokens': 300,
        'messages': [
            {'role': 'user', 'content': prompt}
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Extract the content from the response
        content = data['content'][0]['text'] if data.get('content') else ''
        
        # Find the JSON object within the content
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        json_str = content[json_start:json_end]
        
        # Parse the JSON from the content
        try:
            trivia_data = json.loads(json_str)
        except json.JSONDecodeError:
            st.error("Failed to parse the trivia question from the response.")
            return {
                'question': 'No question available',
                'options': [],
                'answer': 'No answer available',
                'movie_title': 'No movie title available'
            }

        # Handle missing keys
        return {
            'question': trivia_data.get('question', 'No question available'),
            'options': trivia_data.get('options', []),
            'answer': trivia_data.get('answer', 'No answer available'),
            'movie_title': trivia_data.get('movie_title', 'No movie title available')
        }

    except requests.exceptions.HTTPError as err:
        st.error(f"HTTP error occurred: {err}")
    except json.JSONDecodeError:
        st.error("Failed to parse the trivia question from the response.")
    except Exception as err:
        st.error(f"Other error occurred: {err}")

    return {
        'question': 'No question available',
        'options': [],
        'answer': 'No answer available',
        'movie_title': 'No movie title available'
    }

# Welcome screen
def welcome_screen():
    st.title("Black Cinema Trivia")
    st.write("An interactive quiz game celebrating films directed by Black filmmakers.")
    if st.button("Start Quiz"):
        st.session_state.question_index = 0
        st.session_state.score = 0
        st.session_state.streak = 0
        st.session_state.start_time = time.time()
        st.session_state.page = 'quiz'
        st.session_state.question_data = generate_trivia_question()
    if st.button("Leaderboard"):
        st.session_state.page = 'leaderboard'

# Quiz interface
def quiz_interface():
    if st.session_state.question_data is None:
        st.session_state.question_data = generate_trivia_question()
    
    question_data = st.session_state.question_data
    
    st.write(question_data['question'])
    options = question_data['options']
    answer = question_data['answer']
    
    if options:
        user_answer = st.radio("Choose your answer:", options, key='user_answer')
    else:
        st.write("No options available for this question.")
        return

    # Timer
    time_limit = 30  # 30 seconds per question
    elapsed_time = time.time() - st.session_state.start_time
    remaining_time = time_limit - elapsed_time
    st.write(f"Time remaining: {int(remaining_time)} seconds")

    if remaining_time <= 0:
        st.write("Time's up!")
        st.session_state.streak = 0
        st.session_state.question_index += 1
        st.session_state.start_time = time.time()
        st.session_state.question_data = generate_trivia_question()
        st.experimental_rerun()

    if st.button("Submit"):
        if st.session_state.user_answer == answer:
            st.session_state.streak += 1
            st.session_state.score += 10 * st.session_state.streak  # Streak multiplier
            st.success("Correct!")
        else:
            st.session_state.streak = 0
            st.error(f"Incorrect. The correct answer is: {answer}")
        
        st.session_state.question_index += 1
        st.session_state.start_time = time.time()
        st.session_state.question_data = generate_trivia_question()
        time.sleep(2)  # Give the user time to see the result
        st.experimental_rerun()

    # Progress bar
    total_questions = 10  # Assuming a total of 10 questions
    progress = st.session_state.question_index / total_questions
    st.progress(progress)

    # Display movie poster
    poster_url = fetch_movie_poster(question_data['movie_title'])
    if poster_url:
        st.image(poster_url)

# Leaderboard
def leaderboard():
    st.title("Leaderboard")
    leaderboard_data = fetch_leaderboard()
    for i, (name, score) in enumerate(leaderboard_data):
        st.write(f"{i+1}. {name} - {score}")
    if st.button("Back to Welcome"):
        st.session_state.page = 'welcome'

# Initialize SQLite database
conn = sqlite3.connect('leaderboard.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS leaderboard
             (name TEXT, score INTEGER)''')
conn.commit()

# Function to update leaderboard
def update_leaderboard(name, score):
    c.execute("INSERT INTO leaderboard (name, score) VALUES (?, ?)", (name, score))
    conn.commit()

# Function to fetch leaderboard data
def fetch_leaderboard():
    c.execute("SELECT name, score FROM leaderboard ORDER BY score DESC LIMIT 10")
    return c.fetchall()

# Function to fetch film recommendations
def fetch_film_recommendations():
    # Placeholder for film recommendations
    return ["Moonlight", "Black Panther", "Do the Right Thing", "12 Years a Slave"]

# End-of-quiz summary
def end_of_quiz_summary():
    st.title("Quiz Summary")
    st.write(f"Your final score: {st.session_state.score}")
    name = st.text_input("Enter your name for the leaderboard:")
    if st.button("Submit Score"):
        update_leaderboard(name, st.session_state.score)
        st.session_state.page = 'leaderboard'
    
    st.write("Film Recommendations:")
    recommendations = fetch_film_recommendations()
    for film in recommendations:
        st.write(film)

# Director spotlight
def director_spotlight():
    st.title("Director Spotlight")
    st.write("Learn more about influential Black filmmakers.")
    # Placeholder for director spotlight content
    if st.button("Back to Welcome"):
        st.session_state.page = 'welcome'

# Social media sharing
def social_media_sharing():
    st.title("Share Your Score")
    st.write("Share your score on social media.")
    # Placeholder for social media sharing functionality
    if st.button("Back to Welcome"):
        st.session_state.page = 'welcome'

# Theme customization
def theme_customization():
    st.title("Customize Theme")
    st.write("Choose your preferred theme.")
    # Placeholder for theme customization options
    if st.button("Back to Welcome"):
        st.session_state.page = 'welcome'

# Main app logic
if 'page' not in st.session_state:
    st.session_state.page = 'welcome'

if st.session_state.page == 'welcome':
    welcome_screen()
elif st.session_state.page == 'quiz':
    quiz_interface()
elif st.session_state.page == 'leaderboard':
    leaderboard()
elif st.session_state.page == 'summary':
    end_of_quiz_summary()
elif st.session_state.page == 'director_spotlight':
    director_spotlight()
elif st.session_state.page == 'social_media_sharing':
    social_media_sharing()
elif st.session_state.page == 'theme_customization':
    theme_customization()