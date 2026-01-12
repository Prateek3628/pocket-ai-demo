import streamlit as st
from dotenv import load_dotenv
from script import PersonaChat
import os

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Pocket AI - Mental Wellness",
    page_icon="🧘",
    layout="centered"
)

# Body sensation options
BODY_SENSATIONS = [
    "Tension in body",
    "Numbness",
    "Tight chest or breathing",
    "Heavy or tired",
    "Light and energetic",
    "Restless or fidgety",
    "Emptiness",
    "Palpitations"
]

# Attention focus options
ATTENTION_OPTIONS = [
    "A conversation I need to have",
    "Personal care or self-care",
    "Work tasks or projects",
    "Expressing emotions I've held back",
    "Reaching out to someone",
    "Physical sensations"
]

# Exercise types
EXERCISES = {
    "empty_chair": "🪑 Empty Chair",
    "breathing": "🌬️ Breathing Exercise",
    "body_scan": "🧘 Body Scan"
}

# Initialize session state
def init_session_state():
    defaults = {
        'chat_system': None,
        'messages': [],
        'step': 'initial_assessment',  # initial_assessment -> exercise_selection -> exercise_setup -> chat
        'mood_rating': 3,
        'body_sensations': [],
        'attention_focus': None,
        'selected_exercise': None,
        'exercise_context': {},
        'persona_name': ''
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()


def reset_all():
    """Reset everything to start over."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    init_session_state()


def get_mood_description(rating):
    """Convert mood rating to description."""
    mood_map = {
        1: "not good at all",
        2: "not so good",
        3: "neutral/okay",
        4: "good",
        5: "very good"
    }
    return mood_map.get(rating, "neutral")


def setup_empty_chair(who, characteristics, topic, situation):
    """Set up the Empty Chair exercise."""
    try:
        if st.session_state.chat_system is None:
            st.session_state.chat_system = PersonaChat()
        
        # Get initial assessment context
        mood_desc = get_mood_description(st.session_state.mood_rating)
        sensations = ", ".join(st.session_state.body_sensations) if st.session_state.body_sensations else "none specified"
        attention = st.session_state.attention_focus or "general"
        
        persona_description = f"""You are participating in an Empty Chair therapeutic exercise. You are role-playing as the user's {who}.

User's Current State:
- Mood: {mood_desc} ({st.session_state.mood_rating}/5)
- Body sensations: {sensations}
- Their attention is on: {attention}

About the person you're playing:
- Characteristics: {characteristics}
- Topic to discuss: {topic}
- Situation/Environment: {situation}

Instructions:
- Stay in character as {who} throughout the conversation
- Be aware of the user's emotional state and respond with appropriate sensitivity
- Match the communication style described in the characteristics
- Keep responses therapeutic and supportive while staying in character
- Help the user express what they need to express
- Be authentic to how this person would actually respond
"""
        
        st.session_state.chat_system.set_persona_environment(who, persona_description)
        st.session_state.persona_name = who
        
        # Generate initial greeting
        initial_prompt = f"""You are {who} sitting in the empty chair. The user wants to talk to you about {topic}. 
The situation is: {situation}. 
Start the conversation naturally and warmly, acknowledging that you're here to listen. 
Be brief but warm - just 1-2 sentences to open the dialogue."""
        
        initial_response = st.session_state.chat_system.chat(initial_prompt)
        st.session_state.messages = [{"role": "assistant", "content": initial_response}]
        st.session_state.step = 'chat'
        return True
    except Exception as e:
        st.error(f"Error setting up: {e}")
        return False


def setup_breathing_exercise():
    """Set up the Breathing Exercise."""
    try:
        if st.session_state.chat_system is None:
            st.session_state.chat_system = PersonaChat()
        
        # Get initial assessment context
        mood_desc = get_mood_description(st.session_state.mood_rating)
        sensations = ", ".join(st.session_state.body_sensations) if st.session_state.body_sensations else "none specified"
        attention = st.session_state.attention_focus or "general"
        
        persona_description = f"""You are a gentle, calming breathing exercise guide. Your role is to help the user with breathing exercises.

User's Current State:
- Mood: {mood_desc} ({st.session_state.mood_rating}/5)
- Body sensations: {sensations}
- Their attention is on: {attention}

IMPORTANT RULES:
1. You ONLY provide breathing exercises - this is your specialty
2. If the user asks for a different type of exercise, acknowledge their request but offer a DIFFERENT breathing technique instead
3. You know many breathing techniques: Box breathing, 4-7-8 breathing, Diaphragmatic breathing, Alternate nostril breathing, Pursed lip breathing, Resonant breathing, Lion's breath, Humming bee breath, etc.
4. Adapt your breathing suggestions based on the user's mood and sensations

CRITICAL OUTPUT FORMAT:
When providing a breathing exercise (after the initial casual greeting), you MUST output in this exact JSON format:
```json
{{
  "exerciseName": "Name of the breathing exercise",
  "mood": "The mood this exercise helps with",
  "duration": 300,
  "inhaleSeconds": 4,
  "holdSeconds": 4,
  "exhaleSeconds": 4,
  "description": "A brief, calming description of the exercise and how to do it"
}}
```

- duration is total exercise duration in seconds (e.g., 300 for 5 minutes)
- inhaleSeconds, holdSeconds, exhaleSeconds are the timing for each breath cycle
- description should include step-by-step instructions in a friendly tone
- Always wrap the JSON in ```json``` code blocks
- You can add a short friendly message before or after the JSON
"""
        
        st.session_state.chat_system.set_persona_environment("Breathing Guide", persona_description)
        st.session_state.persona_name = "Breathing Guide"
        
        # Generate initial casual greeting - not jumping into exercise yet
        initial_prompt = f"""The user is feeling {mood_desc} and experiencing: {sensations}. 
Their attention is on: {attention}.

DO NOT start the breathing exercise yet. Do NOT output any JSON yet. First, send a casual, warm, reassuring message:
- Acknowledge that you're here for them
- Be conversational and friendly (2-3 sentences max)
- Say something like "Hey, I'm glad you're here. Whatever's going on, we'll work through it together. How about we start with something simple to help you feel a bit more grounded?"
- Keep it SHORT and casual - no instructions yet, no JSON yet
- Wait for their response before providing the breathing exercise JSON"""
        
        initial_response = st.session_state.chat_system.chat(initial_prompt)

        st.session_state.messages = [{"role": "assistant", "content": initial_response}]
        st.session_state.step = 'chat'
        return True
    except Exception as e:
        st.error(f"Error setting up: {e}")
        return False


def setup_body_scan(uncomfortable_area, body_feeling):
    """Set up the Body Scan exercise."""
    try:
        if st.session_state.chat_system is None:
            st.session_state.chat_system = PersonaChat()
        
        # Get initial assessment context
        mood_desc = get_mood_description(st.session_state.mood_rating)
        sensations = ", ".join(st.session_state.body_sensations) if st.session_state.body_sensations else "none specified"
        attention = st.session_state.attention_focus or "general"
        
        persona_description = f"""You are a gentle, mindful body scan guide. Your role is to help the user with a body scan meditation and awareness exercise.

User's Current State:
- Mood: {mood_desc} ({st.session_state.mood_rating}/5)
- Body sensations from initial check: {sensations}
- Their attention is on: {attention}

Body Scan Specific Information:
- Area feeling uncomfortable: {uncomfortable_area}
- How their body is feeling right now: {body_feeling}

Instructions:
1. Guide the user through a mindful body scan experience
2. Pay special attention to the area they mentioned as uncomfortable
3. Be gentle, calming, and non-judgmental
4. Help them notice sensations without trying to change them
5. Offer guidance on releasing tension if appropriate
6. Adapt your guidance based on their responses
7. Keep instructions clear and paced well
"""
        
        st.session_state.chat_system.set_persona_environment("Body Scan Guide", persona_description)
        st.session_state.persona_name = "Body Scan Guide"
        
        # Generate initial casual, reassuring message - NOT starting the exercise yet
        initial_prompt = f"""The user has indicated that their {uncomfortable_area} feels uncomfortable, and they describe their body as feeling: {body_feeling}.
Their mood is {mood_desc} and they've noticed: {sensations}.

DO NOT start the body scan exercise yet. First, send a casual, warm, reassuring message:
- Be conversational and friendly (2-3 sentences max)
- Reassure them that it's okay, you'll figure it out together
- Say something like "Hey, thanks for sharing that with me. It's okay - we'll figure this out together. Let's see what's really bothering you and take it from there."
- Keep it SHORT and casual - no meditation instructions yet
- Show you care and that you're here to help them explore what's going on
- Wait for their response before starting any body scan guidance"""
        
        initial_response = st.session_state.chat_system.chat(initial_prompt)
        st.session_state.messages = [{"role": "assistant", "content": initial_response}]
        st.session_state.step = 'chat'
        return True
    except Exception as e:
        st.error(f"Error setting up: {e}")
        return False


# ============= UI COMPONENTS =============

# App Title
st.title("🧘 Pocket AI - Mental Wellness")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("🌟 Your Session")
    
    if st.session_state.step == 'chat':
        st.success(f"**Exercise:** {EXERCISES.get(st.session_state.selected_exercise, 'Active')}")
        if st.session_state.persona_name:
            st.info(f"**With:** {st.session_state.persona_name}")
        
        st.markdown("---")
        st.markdown("**Your Check-in:**")
        st.write(f"• Mood: {st.session_state.mood_rating}/5")
        if st.session_state.body_sensations:
            st.write(f"• Sensations: {', '.join(st.session_state.body_sensations)}")
        if st.session_state.attention_focus:
            st.write(f"• Focus: {st.session_state.attention_focus}")
    
    st.markdown("---")
    if st.button("🔄 Start Over", use_container_width=True):
        reset_all()
        st.rerun()


# ============= STEP 1: INITIAL ASSESSMENT =============
if st.session_state.step == 'initial_assessment':
    st.header("📋 Let's Check In With You")
    st.markdown("Before we begin, I'd like to understand how you're feeling right now.")
    
    with st.form("initial_assessment_form"):
        # Question 1: Mood Rating
        st.subheader("1️⃣ Rate your mood")
        st.caption("1 = Not good at all, 5 = Very good")
        mood = st.slider(
            "How are you feeling right now?",
            min_value=1,
            max_value=5,
            value=3,
            help="1 being not good, 5 being very good"
        )
        
        # Visual mood indicator
        mood_emojis = {1: "😢", 2: "😕", 3: "😐", 4: "🙂", 5: "😊"}
        st.markdown(f"### {mood_emojis[mood]}")
        
        st.markdown("---")
        
        # Question 2: Body Sensations
        st.subheader("2️⃣ What sensations do you notice in your body?")
        st.caption("Select all that apply")
        sensations = st.multiselect(
            "Body sensations",
            options=BODY_SENSATIONS,
            default=None,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Question 3: Attention Focus
        st.subheader("3️⃣ Where is your attention?")
        attention = st.radio(
            "What's on your mind?",
            options=ATTENTION_OPTIONS,
            index=None,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        submitted = st.form_submit_button("Continue →", use_container_width=True, type="primary")
        
        if submitted:
            if not sensations:
                st.warning("Please select at least one body sensation.")
            elif not attention:
                st.warning("Please select where your attention is.")
            else:
                st.session_state.mood_rating = mood
                st.session_state.body_sensations = sensations
                st.session_state.attention_focus = attention
                st.session_state.step = 'exercise_selection'
                st.rerun()


# ============= STEP 2: EXERCISE SELECTION =============
elif st.session_state.step == 'exercise_selection':
    st.header("🎯 Choose Your Exercise")
    
    # Show summary of check-in
    with st.expander("📊 Your Check-in Summary", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mood", f"{st.session_state.mood_rating}/5")
        with col2:
            st.write("**Sensations:**")
            for s in st.session_state.body_sensations:
                st.write(f"• {s}")
        with col3:
            st.write("**Focus:**")
            st.write(st.session_state.attention_focus)
    
    st.markdown("---")
    st.markdown("### What would you like to do?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🪑 Empty Chair")
        st.markdown("*Talk to someone who isn't here - express what you need to say.*")
        if st.button("Choose Empty Chair", use_container_width=True, key="btn_empty"):
            st.session_state.selected_exercise = 'empty_chair'
            st.session_state.step = 'exercise_setup'
            st.rerun()
    
    with col2:
        st.markdown("#### 🌬️ Breathing")
        st.markdown("*Guided breathing exercises to calm your mind and body.*")
        if st.button("Choose Breathing", use_container_width=True, key="btn_breathing"):
            st.session_state.selected_exercise = 'breathing'
            st.session_state.step = 'exercise_setup'
            st.rerun()
    
    with col3:
        st.markdown("#### 🧘 Body Scan")
        st.markdown("*Mindful awareness of your body sensations.*")
        if st.button("Choose Body Scan", use_container_width=True, key="btn_body"):
            st.session_state.selected_exercise = 'body_scan'
            st.session_state.step = 'exercise_setup'
            st.rerun()
    
    st.markdown("---")
    if st.button("← Back to Check-in"):
        st.session_state.step = 'initial_assessment'
        st.rerun()


# ============= STEP 3: EXERCISE SETUP =============
elif st.session_state.step == 'exercise_setup':
    
    # EMPTY CHAIR SETUP
    if st.session_state.selected_exercise == 'empty_chair':
        st.header("🪑 Empty Chair Exercise")
        st.markdown("*Imagine the person you want to talk to is sitting in an empty chair in front of you.*")
        st.markdown("---")
        
        with st.form("empty_chair_form"):
            st.subheader("1️⃣ Who would you like to talk to?")
            who = st.text_input(
                "Person or relationship",
                placeholder="e.g., father, mother, best friend, my younger self, etc.",
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            st.subheader("2️⃣ Some characteristics of this person")
            characteristics = st.text_area(
                "Describe how they talk, their personality",
                placeholder="e.g., Warm and understanding, uses humor, speaks softly, always gives advice...",
                height=100,
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            st.subheader("3️⃣ What would you like to talk about?")
            topic = st.text_input(
                "Topic",
                placeholder="e.g., Something I never got to say, seeking closure, asking for advice...",
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            st.subheader("4️⃣ Set the situation/environment")
            situation = st.text_area(
                "Situation",
                placeholder="e.g., We're sitting in their living room, it's a quiet evening...",
                height=80,
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            col1, col2 = st.columns([1, 2])
            with col1:
                back = st.form_submit_button("← Back")
            with col2:
                start = st.form_submit_button("Start Conversation →", type="primary", use_container_width=True)
            
            if back:
                st.session_state.step = 'exercise_selection'
                st.rerun()
            
            if start:
                if not all([who, characteristics, topic, situation]):
                    st.error("Please fill in all fields.")
                else:
                    with st.spinner("Setting up the empty chair..."):
                        if setup_empty_chair(who, characteristics, topic, situation):
                            st.rerun()
    
    # BREATHING EXERCISE SETUP
    elif st.session_state.selected_exercise == 'breathing':
        st.header("🌬️ Breathing Exercise")
        st.markdown("*Let's begin a breathing exercise tailored to how you're feeling.*")
        st.markdown("---")
        
        # Show user's current state
        st.info(f"""
        Based on your check-in:
        - **Mood:** {st.session_state.mood_rating}/5
        - **Sensations:** {', '.join(st.session_state.body_sensations)}
        - **Focus:** {st.session_state.attention_focus}
        
        I'll suggest a breathing exercise that's right for you.
        """)
        
        col1, col2 = st.columns([1, 2])
        with col1:
            if st.button("← Back"):
                st.session_state.step = 'exercise_selection'
                st.rerun()
        with col2:
            if st.button("Begin Breathing Exercise →", type="primary", use_container_width=True):
                with st.spinner("Preparing your breathing exercise..."):
                    if setup_breathing_exercise():
                        st.rerun()
    
    # BODY SCAN SETUP
    elif st.session_state.selected_exercise == 'body_scan':
        st.header("🧘 Body Scan Exercise")
        st.markdown("*Let's bring mindful awareness to your body.*")
        st.markdown("---")
        
        with st.form("body_scan_form"):
            st.subheader("1️⃣ Which area feels uncomfortable?")
            uncomfortable_area = st.text_input(
                "Body area",
                placeholder="e.g., shoulders, chest, stomach, head, back...",
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            st.subheader("2️⃣ How is your body feeling right now?")
            body_feeling = st.text_area(
                "Describe your body's state",
                placeholder="e.g., Tense and tight, exhausted, restless, heavy...",
                height=100,
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            col1, col2 = st.columns([1, 2])
            with col1:
                back = st.form_submit_button("← Back")
            with col2:
                start = st.form_submit_button("Begin Body Scan →", type="primary", use_container_width=True)
            
            if back:
                st.session_state.step = 'exercise_selection'
                st.rerun()
            
            if start:
                if not uncomfortable_area or not body_feeling:
                    st.error("Please answer both questions.")
                else:
                    with st.spinner("Preparing your body scan..."):
                        if setup_body_scan(uncomfortable_area, body_feeling):
                            st.rerun()


# ============= STEP 4: CHAT =============
elif st.session_state.step == 'chat':
    exercise_name = EXERCISES.get(st.session_state.selected_exercise, "Exercise")
    st.header(f"{exercise_name}")
    
    if st.session_state.persona_name:
        st.caption(f"Chatting with: {st.session_state.persona_name}")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("..."):
                try:
                    response = st.session_state.chat_system.chat(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            if st.session_state.chat_system:
                st.session_state.chat_system.reset_conversation()
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("🔄 Change Exercise", use_container_width=True):
            st.session_state.step = 'exercise_selection'
            st.session_state.messages = []
            st.session_state.chat_system = None
            st.rerun()
    with col3:
        if st.button("🏠 Start Over", use_container_width=True):
            reset_all()
            st.rerun()


# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.8em;'>"
    "🧘 Pocket AI Mental Wellness • Powered by OpenAI"
    "</div>",
    unsafe_allow_html=True
)

