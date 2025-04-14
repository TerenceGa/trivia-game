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
        /* Animation applied via class below */
    }
    .incorrect {
        background-color: #f44336;
        color: white;
        padding: 10px;
        border-radius: 5px;
    }
    .score-counter {
        position: fixed;
        top: 20px;  /* Increased from 10px */
        right: 20px; /* Increased from 10px */
        padding: 10px;
        background-color: #2196F3;
        color: white;
        border-radius: 5px;
        font-weight: bold;
        z-index: 99; /* Ensure it stays on top */
        text-align: right; /* Align text to the right within the box */
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); } /* Start invisible and slightly down */
        to { opacity: 1; transform: translateY(0); }   /* Fade to visible and original position */
    }
    .fade-in {
        animation: fadeIn 0.5s ease-out forwards; /* Apply the animation */
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
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'current_streak' not in st.session_state:
    st.session_state.current_streak = 0

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
# Function to start a new game
def start_game():
    # ... (fetch questions logic remains the same) ...
    st.session_state.questions = fetch_questions(st.session_state.category, st.session_state.difficulty, st.session_state.question_type)
    st.session_state.game_started = True
    st.session_state.current_question = 0
    # RESET score and streak
    st.session_state.score = 0
    st.session_state.current_streak = 0
    # RESET other relevant states
    st.session_state.correct_answers = 0 # Keep this if you still want the simple count/rate
    st.session_state.answered = False
    st.session_state.selected_option = None
    st.session_state.correct_option = None
    st.session_state.current_options_order = [] # Reset options order

# Function to restart the game with the same settings
def restart_game():
    st.session_state.game_started = True
    st.session_state.current_question = 0
    # RESET score and streak
    st.session_state.score = 0
    st.session_state.current_streak = 0
    # RESET other relevant states
    st.session_state.correct_answers = 0
    st.session_state.answered = False
    st.session_state.selected_option = None
    st.session_state.correct_option = None
    st.session_state.current_options_order = []

# Function to return to the settings page
def return_to_settings():
    st.session_state.game_started = False
    st.session_state.current_question = 0
    # RESET score and streak
    st.session_state.score = 0
    st.session_state.current_streak = 0
    # RESET other relevant states
    st.session_state.correct_answers = 0 # Resetting just in case
    st.session_state.questions = []
    st.session_state.answered = False
    st.session_state.selected_option = None
    st.session_state.correct_option = None
    st.session_state.current_options_order = []
    # Optionally reset token too if desired:
    # st.session_state.pop('token', None)

# Function to check the answer
# Function to check the answer
def check_answer(selected_option, correct_answer):
    st.session_state.answered = True
    st.session_state.selected_option = selected_option
    st.session_state.correct_option = correct_answer

    points = 0 # Points for this question
    difficulty = st.session_state.get('difficulty', 'Easy') # Get current difficulty

    if selected_option == correct_answer:
        # --- Dynamic Scoring ---
        if difficulty == "Easy":
            points = 10
        elif difficulty == "Medium":
            points = 20
        elif difficulty == "Hard":
            points = 30
        else:
            points = 10 # Default points

        st.session_state.score += points
        st.session_state.correct_answers += 1 # Keep track of raw count too

        st.session_state.current_streak += 1

    else:
        st.session_state.current_streak = 0 

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
# Make sure you have also updated the check_answer function as previously discussed!

# Main application logic
def display_settings():
    """Displays the game configuration settings (category, difficulty, type) and the start button."""
    st.markdown("### Configure Your Game")

    # --- Instructions Expander ---
    with st.expander("How to Play", expanded=False): # Set expanded=True to show by default
        st.markdown("""
        1.  **Choose your challenge:** Select a Category, Difficulty, and Question Type (Multiple Choice or True/False).
        2.  **Start the game:** Hit the "START" button.
        3.  **Answer questions:** Select your answer for each of the 10 questions presented.
        4.  **Check feedback:** See if you were correct or incorrect. Correct answers earn points based on difficulty and build your 🔥 Streak!
        5.  **Continue:** Click "Next Question" to move on.
        6.  **Finish:** See your final score after 10 questions! Good luck!
        """)
        st.markdown("---") # Optional separator inside expander
    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state.category = st.selectbox(
            "Select Category", options=list(category_mapping.keys()), index=0, key="settings_category"
        )
    with col2:
        st.session_state.difficulty = st.selectbox(
            "Select Difficulty", options=["Easy", "Medium", "Hard"], index=0, key="settings_difficulty"
        )
    with col3:
        st.session_state.question_type = st.selectbox(
            "Select Type", options=["multiple", "boolean"], index=0, key="settings_type"
        )

    st.markdown(
        """
        <div style="display: flex; justify-content: center; margin-top: 50px;">
            <div>Click Start to begin the game!</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    if st.button("START", key="start_button", use_container_width=True, type="primary"):
        start_game() # Assumes start_game() is defined elsewhere
        st.rerun()

# --- Helper Function: Display Game Header (Score, Streak, Progress) ---
def display_game_header():
    """Displays the score, streak, question progress, and progress bar."""
    if not st.session_state.game_started or not st.session_state.questions:
        return # Don't display if game hasn't started or no questions

    total_questions_in_round = len(st.session_state.questions)
    current_q_display_num = min(st.session_state.current_question + 1, total_questions_in_round)

    score_text = f"Score: {st.session_state.score}"
    streak_text = f"Streak: {st.session_state.current_streak} 🔥" if st.session_state.current_streak > 0 else "Streak: 0"
    question_progress_text = f"Question: {current_q_display_num}/{total_questions_in_round}"

    st.markdown(
        f"""
        <div class="score-counter">
            {score_text} | {streak_text} <br> {question_progress_text}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Visual Progress Bar
    progress_value = (st.session_state.current_question) / total_questions_in_round
    st.progress(progress_value)
    st.markdown("---") # Separator

# --- Helper Function: Display Question Area ---
def display_question_area(current_q):
    """Displays the current question text, difficulty, and category."""
    st.markdown(f'<div class="question-text fade-in">Question {st.session_state.current_question + 1}: {html.unescape(current_q["question"])}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="fade-in">*(Difficulty: {current_q["difficulty"].capitalize()}, Category: {html.unescape(current_q["category"])})*</div>', unsafe_allow_html=True)
    st.markdown("---")

# --- Helper Function: Display Answer Buttons ---
def display_answer_buttons(current_q):
    """Displays the True/False or Multiple Choice answer buttons."""
    if current_q["type"] == "boolean":
        col1, col2 = st.columns(2)
        with col1:
            if st.button("True", key="true_btn", type="primary", use_container_width=True):
                check_answer("True", current_q["correct_answer"]) # Assumes check_answer is defined
                st.rerun()
        with col2:
            if st.button("False", key="false_btn", type="primary", use_container_width=True):
                check_answer("False", current_q["correct_answer"])
                st.rerun()
    else: # Multiple Choice Buttons
        correct_answer_unescaped = html.unescape(current_q["correct_answer"])
        options = [correct_answer_unescaped] + [html.unescape(ans) for ans in current_q["incorrect_answers"]]
        random.shuffle(options) # Assumes random is imported
        st.session_state.current_options_order = options # Store order for feedback

        for option in options:
            # Ensure unique keys if options can be numerically similar (e.g., '1' vs 1)
            button_key = f"option_{option}_{st.session_state.current_question}"
            if st.button(option, key=button_key, use_container_width=True):
                check_answer(option, correct_answer_unescaped)
                st.rerun()

# --- Helper Function: Display Feedback Area ---
def display_feedback_area(current_q):
    """Displays feedback (correct/incorrect styles), points message, streak message,
       and Next button with fade-in animations.
    """
    correct_answer_unescaped = html.unescape(current_q["correct_answer"])
    # Retrieve the order options were displayed in, needed for consistent feedback.
    # Assumes 'current_options_order' was set in session_state when buttons were created.
    options_in_order_displayed = st.session_state.get('current_options_order', [])

    st.markdown("---") # Separator before feedback

    # --- Display styled feedback for the options ---
    if current_q["type"] == "boolean":
        col1, col2 = st.columns(2)
        # Determine styles based on correctness and user selection
        true_style = "correct" if "True" == correct_answer_unescaped else "incorrect" if st.session_state.selected_option == "True" else ""
        false_style = "correct" if "False" == correct_answer_unescaped else "incorrect" if st.session_state.selected_option == "False" else ""

        with col1:
            # Apply fade-in class to the markdown div
            st.markdown(f'<div class="{true_style} fade-in" style="padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 10px;">True</div>', unsafe_allow_html=True)
        with col2:
             # Apply fade-in class to the markdown div
            st.markdown(f'<div class="{false_style} fade-in" style="padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 10px;">False</div>', unsafe_allow_html=True)

    else: # Multiple Choice Feedback
        # Fallback if options order wasn't stored (feedback order might not match button order)
        if not options_in_order_displayed:
             options_in_order_displayed = [correct_answer_unescaped] + [html.unescape(ans) for ans in current_q["incorrect_answers"]]
             st.warning("Option order for feedback might be inconsistent.", icon="⚠️") # Warn user if fallback is used

        for i, option in enumerate(options_in_order_displayed):
            # Determine style based on correctness and user selection
            option_style = "correct" if option == correct_answer_unescaped else "incorrect" if option == st.session_state.selected_option else ""
            # Apply fade-in class to the markdown div
            # You could add a staggered delay using CSS style='animation-delay: {i * 0.05}s' but keeping it simple here.
            st.markdown(f'<div class="{option_style} fade-in" style="padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 10px;">{option}</div>', unsafe_allow_html=True)

    st.markdown("---") # Separator after option feedback

    # --- Display points/streak message ---
    if st.session_state.selected_option == correct_answer_unescaped:
        # Calculate points earned (ensure difficulty is in session stacounter te)
        difficulty = st.session_state.get('difficulty', 'Easy')
        points_earned = 10 if difficulty == "Easy" else 20 if difficulty == "Medium" else 30
        # Use st.success for positive feedback (includes icon and subtle animation)
        st.success(f"Correct! +{points_earned} points", icon="✅")
        # Display streak info if streak is greater than 1
        if st.session_state.current_streak > 1:
             # Use st.info for neutral supplementary info
             st.info(f"Streak: {st.session_state.current_streak} 🔥")
    else:
        # Use st.error for negative feedback (includes icon and subtle animation)
        st.error(f"Incorrect! The answer was: {correct_answer_unescaped}", icon="❌")
        # Optionally mention if a streak was broken


    # --- Next Question Button ---
    # This button appears after feedback is shown.
    # Assumes 'next_question' function is defined elsewhere and handles state update.
    if st.button("Next Question", on_click=next_question, type="primary", use_container_width=True):
        # Streamlit handles the rerun automatically after the on_click callback finishes.
        pass


# --- Helper Function: Display Results Screen ---
def display_results():
    """Displays the final score and options to play again or change settings."""
    total_questions_in_round = len(st.session_state.questions)
    st.progress(1.0) # Show full progress bar

    st.markdown(
        f"""
        <div style="text-align: center; margin: 50px 0;">
            <h2>Game Completed!</h2>
            <h3>Final Score: {st.session_state.score} points</h3>
            <p>({st.session_state.correct_answers} / {total_questions_in_round} correct answers)</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Play Again", type="primary", use_container_width=True):
            restart_game() # Assumes restart_game is defined
            st.rerun()
    with col2:
        if st.button("Change Settings", type="secondary", use_container_width=True):
            return_to_settings() # Assumes return_to_settings is defined
            st.rerun()

# --- Helper Function: Display Loading/Error State ---
def display_loading_error():
     """Displays an error message if questions couldn't be loaded."""
     st.error("Failed to load questions. Please check your settings or try again later.")
     if st.button("Back to Settings", type="primary"):
         return_to_settings()
         st.rerun()
def main():
    st.title("🎮 Trivia Game 🎮")
    st.markdown("Test your knowledge with fun trivia questions!")

    # --- Game State Controller ---

    # State 1: Settings Screen
    if not st.session_state.game_started:
        display_settings()

    # State 2: Game In Progress
    elif st.session_state.game_started and st.session_state.questions and st.session_state.current_question < len(st.session_state.questions):
        display_game_header()
        current_q = st.session_state.questions[st.session_state.current_question]
        display_question_area(current_q)

        if st.session_state.answered:
            display_feedback_area(current_q)
        else:
            display_answer_buttons(current_q)

    # State 3: Results Screen
    elif st.session_state.game_started and st.session_state.questions and st.session_state.current_question >= len(st.session_state.questions):
        display_game_header() # Show final header state
        display_results()

    # State 4: Loading Error (No questions fetched)
    elif st.session_state.game_started and not st.session_state.questions:
        display_loading_error()

# --- Entry Point ---
if __name__ == "__main__":
    # Make sure necessary imports (streamlit, html, random, requests, time) are at the top
    # Make sure function definitions (fetch_questions, check_answer, next_question, etc.)
    # and category_mapping are defined before main() is called.
    main()