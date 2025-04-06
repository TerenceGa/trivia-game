import streamlit as st
import requests
import html
import random
import time
# Set page configuration
st.set_page_config(
    page_title="Trivia Game",
    page_icon="❓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Custom CSS for styling
st.markdown("""
<style>
    .big-button {
        font-size: 30px !important;
        height: 100px !important;
        margin: 50px 0px !important;
        background-color: #4CAF50 !important;
        color: white !important;
    }
    .correct {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 5px;
        animation: fadeOut 1s ease forwards;
        animation-delay: 1s;
    }
    .incorrect {
        background-color: #f44336;
        color: white;
        padding: 10px;
        border-radius: 5px;
    }
    .score-counter {
        position: fixed;
        top: 10px;
        right: 10px;
        padding: 10px;
        background-color: #2196F3;
        color: white;
        border-radius: 5px;
        font-weight: bold;
    }
    @keyframes fadeOut {
        from {opacity: 1;}
        to {opacity: 0.5;}
    }
    .question-text {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    
    /* New CSS for green START button */
    .stButton > button[data-baseweb="button"][kind="primary"] {
        background-color: #4CAF50 !important;
        border-color: #4CAF50 !important;
    }
    
    .stButton > button[data-baseweb="button"][kind="primary"]:hover,
    .stButton > button[data-baseweb="button"][kind="primary"]:focus {
        background-color: #3d9140 !important;
        border-color: #3d9140 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables if they don't exist
if 'game_started' not in st.session_state:
    st.session_state.game_started = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'correct_answers' not in st.session_state:
    st.session_state.correct_answers = 0
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'answered' not in st.session_state:
    st.session_state.answered = False
if 'selected_option' not in st.session_state:
    st.session_state.selected_option = None
if 'correct_option' not in st.session_state:
    st.session_state.correct_option = None

# Function to get a session token
def get_session_token():
    if 'token' not in st.session_state:
        token_url = "https://opentdb.com/api_token.php?command=request"
        try:
            response = requests.get(token_url)
            data = response.json()
            if data["response_code"] == 0:
                st.session_state.token = data["token"]
            else:
                st.error(f"Error getting token: {data['response_code']}")
                return None
        except Exception as e:
            st.error(f"Error connecting to API: {e}")
            return None
    return st.session_state.token

# Function to reset session token if needed
def reset_token():
    if 'token' in st.session_state:
        reset_url = f"https://opentdb.com/api_token.php?command=reset&token={st.session_state.token}"
        try:
            response = requests.get(reset_url)
            data = response.json()
            if data["response_code"] == 0:
                st.session_state.token = data["token"]
                return True
            else:
                st.error(f"Error resetting token: {data['response_code']}")
                return False
        except Exception as e:
            st.error(f"Error connecting to API: {e}")
            return False
    return False

# Function to fetch trivia questions from API
def fetch_questions(category, difficulty, question_type):
    # Get a session token
    token = get_session_token()
    if not token:
        return []
    
    # Convert category name to ID
    category_id = category_mapping.get(category, "")
    
    # Construct the API URL with the specified parameters
    url = f"https://opentdb.com/api.php?amount=10&category={category_id}&difficulty={difficulty.lower()}&type={question_type.lower()}&token={token}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # Handle response codes
        if data["response_code"] == 0:
            # Success
            return data["results"]
        elif data["response_code"] == 1:
            st.error("No Results: Not enough questions available for your criteria. Try different settings.")
            return []
        elif data["response_code"] == 2:
            st.error("Invalid Parameter: Check your settings and try again.")
            return []
        elif data["response_code"] == 3:
            # Token not found, try to get a new one
            st.session_state.pop('token', None)
            st.warning("Session token not found. Getting a new token...")
            return fetch_questions(category, difficulty, question_type)  # Recursive call with new token
        elif data["response_code"] == 4:
            # Token empty, reset it
            st.warning("All questions for this token have been used. Resetting token...")
            if reset_token():
                return fetch_questions(category, difficulty, question_type)  # Recursive call with reset token
            else:
                return []
        elif data["response_code"] == 5:
            st.error("Rate Limit: Please wait a few seconds and try again.")
            time.sleep(5)  # Wait 5 seconds
            return fetch_questions(category, difficulty, question_type)  # Try again
        else:
            st.error(f"Unknown error: Response code {data['response_code']}")
            return []
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {e}")
        return []
    except ValueError as e:
        st.error(f"Invalid response from API: {e}")
        return []
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return []

# Function to start a new game
def start_game():
    category = st.session_state.category
    difficulty = st.session_state.difficulty
    question_type = st.session_state.question_type
    
    st.session_state.questions = fetch_questions(category, difficulty, question_type)
    st.session_state.game_started = True
    st.session_state.current_question = 0
    st.session_state.correct_answers = 0
    st.session_state.answered = False
    st.session_state.selected_option = None
    st.session_state.correct_option = None

# Function to restart the game with the same settings
def restart_game():
    st.session_state.game_started = True
    st.session_state.current_question = 0
    st.session_state.correct_answers = 0
    st.session_state.answered = False
    st.session_state.selected_option = None
    st.session_state.correct_option = None

# Function to return to the settings page
def return_to_settings():
    st.session_state.game_started = False
    st.session_state.current_question = 0
    st.session_state.correct_answers = 0
    st.session_state.questions = []
    st.session_state.answered = False
    st.session_state.selected_option = None
    st.session_state.correct_option = None

# Function to check the answer
def check_answer(selected_option, correct_answer):
    st.session_state.answered = True
    st.session_state.selected_option = selected_option
    st.session_state.correct_option = correct_answer
    
    if selected_option == correct_answer:
        st.session_state.correct_answers += 1
        time.sleep(1)  # Small delay to show the feedback
        st.session_state.current_question += 1
        st.session_state.answered = False
        st.session_state.selected_option = None
        st.session_state.correct_option = None
    else:
        # For incorrect answer, wait for user to proceed
        pass

# Function to proceed to next question
def next_question():
    st.session_state.current_question += 1
    st.session_state.answered = False
    st.session_state.selected_option = None
    st.session_state.correct_option = None

# Category mapping (name to ID)
category_mapping = {
    "🧠 General Knowledge": 9,
    "📚 Books": 10,
    "🎬 Film": 11,
    "🎵 Music": 12,
    "📺 Television": 14,
    "🎮 Video Games": 15,
    "🔬 Science & Nature": 17,
    "💻 Computers": 18,
    "🔢 Mathematics": 19,
    "⚽ Sports": 21,
    "🗺️ Geography": 22,
    "📜 History": 23,
    "🏛️ Politics": 24,
    "🎨 Art": 25,
    "🐾 Animals": 27,
    "🚗 Vehicles": 28,
    "📕 Comics": 29,
    "🔌 Gadgets": 30,
    "🇯🇵 Anime & Manga": 31,
    "🎭 Cartoon & Animations": 32,
}

# Main application logic
def main():
    # Title and header
    st.title("🎮 Trivia Game 🎮")
    st.markdown("Test your knowledge with fun trivia questions!")
    
    # Display score counter if the game is in progress
    if st.session_state.game_started and len(st.session_state.questions) > 0:
        st.markdown(
            f"""
            <div class="score-counter">
                Correct: {st.session_state.correct_answers} / {st.session_state.current_question} 
                (Questions: {st.session_state.current_question + 1}/10)
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    # Settings screen
    if not st.session_state.game_started:
        # Create three columns for the dropdowns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.session_state.category = st.selectbox(
                "Select Category", 
                options=list(category_mapping.keys()),
                index=0
            )
        
        with col2:
            st.session_state.difficulty = st.selectbox(
                "Select Difficulty", 
                options=["Easy", "Medium", "Hard"],
                index=0
            )
        
        with col3:
            st.session_state.question_type = st.selectbox(
                "Select Type", 
                options=["multiple", "boolean"],
                index=0
            )
        
        # Create a big green "Start" button
        st.markdown(
            """
            <div style="display: flex; justify-content: center; margin-top: 50px;">
                <div>Click Start to begin the game!</div>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        if st.button("START", key="start_button", use_container_width=True, type="primary"):
            start_game()
            st.rerun()
    
    # Game screen
    elif st.session_state.game_started and st.session_state.current_question < 10 and len(st.session_state.questions) > 0:
        # Get the current question
        current_q = st.session_state.questions[st.session_state.current_question]
        
        # Display the question
        st.markdown(f'<div class="question-text">Question {st.session_state.current_question + 1}: {html.unescape(current_q["question"])}</div>', unsafe_allow_html=True)
        
        # For True/False questions
        if current_q["type"] == "boolean":
            col1, col2 = st.columns(2)
            
            # Check if already answered
            if st.session_state.answered:
                true_style = "correct" if "True" == current_q["correct_answer"] else "incorrect" if st.session_state.selected_option == "True" else ""
                false_style = "correct" if "False" == current_q["correct_answer"] else "incorrect" if st.session_state.selected_option == "False" else ""
                
                with col1:
                    st.markdown(f'<div class="{true_style}">True</div>', unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f'<div class="{false_style}">False</div>', unsafe_allow_html=True)
                
                # Show next button for incorrect answers
                if st.session_state.selected_option != current_q["correct_answer"]:
                    st.button("Next Question", on_click=next_question, type="primary")
            else:
                with col1:
                    if st.button("True", key="true_btn", type="primary", use_container_width=True):
                        check_answer("True", current_q["correct_answer"])
                        st.rerun()
                
                with col2:
                    if st.button("False", key="false_btn", type="primary", use_container_width=True):
                        check_answer("False", current_q["correct_answer"])
                        st.rerun()
        
        # For Multiple Choice questions
        else:
            # Create a list of all options
            options = [html.unescape(current_q["correct_answer"])] + [html.unescape(ans) for ans in current_q["incorrect_answers"]]
            random.shuffle(options)  # Shuffle to randomize the order
            
            # Check if already answered
            if st.session_state.answered:
                for option in options:
                    option_style = ""
                    if option == html.unescape(current_q["correct_answer"]):
                        option_style = "correct"
                    elif option == st.session_state.selected_option:
                        option_style = "incorrect"
                    
                    st.markdown(f'<div class="{option_style}">{option}</div>', unsafe_allow_html=True)
                
                # Show next button for incorrect answers
                if st.session_state.selected_option != html.unescape(current_q["correct_answer"]):
                    st.button("Next Question", on_click=next_question, type="primary")
            else:
                # Display option buttons
                for option in options:
                    if st.button(option, key=f"option_{option}", use_container_width=True):
                        check_answer(option, html.unescape(current_q["correct_answer"]))
                        st.rerun()
    
    # Results screen (after 10 questions)
    elif st.session_state.game_started and st.session_state.current_question >= 10:
        st.markdown(
            f"""
            <div style="text-align: center; margin: 50px 0;">
                <h2>Game Completed!</h2>
                <h3>Your Score: {st.session_state.correct_answers} / 10</h3>
                <p>Correctness Rate: {st.session_state.correct_answers / 10 * 100:.1f}%</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Play Again", type="primary", use_container_width=True):
                restart_game()
                st.rerun()
        
        with col2:
            if st.button("Change Settings", type="secondary", use_container_width=True):
                return_to_settings()
                st.rerun()
    
    # Error message if no questions were fetched
    elif st.session_state.game_started and len(st.session_state.questions) == 0:
        st.error("Failed to load questions. Please try again or select different options.")
        if st.button("Back to Settings", type="primary"):
            return_to_settings()
            st.rerun()

if __name__ == "__main__":
    main()