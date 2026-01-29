import streamlit as st
from dotenv import load_dotenv
from script import PersonaChat
import os
import json
import re

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
    "body_scan": "🧘 Body Scan",
    "reflection": "💭 Reflection Exercise"
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
        'persona_name': '',
        'breathing_exercise_given': False,
        'breathing_exercises_used': [],
        'show_finished_button': False
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

CRITICAL: Analyze ALL context below holistically before responding. Consider how their mood, body sensations, attention focus, and the specific situation all interconnect.

User's Complete Assessment:
- Mood: {mood_desc} ({st.session_state.mood_rating}/5)
- Body sensations: {sensations}
- Their attention is on: {attention}

Empty Chair Context:
- Who you are: {who}
- Your characteristics: {characteristics}
- Topic they want to discuss: {topic}
- Situation/Environment: {situation}

IMPORTANT - Use ALL the above information to:
1. Understand the FULL emotional landscape (mood + body + attention + topic)
2. Recognize how their body sensations might relate to what they want to discuss
3. Be sensitive to their mood level while staying in character
4. Address the specific topic while being aware of their broader state

Response Guidelines:
- KEEP RESPONSES BRIEF: 2-3 sentences maximum
- Stay in character as {who} with the described characteristics
- Be authentic to how this person would actually respond
- Show you understand their complete state (don't just focus on one aspect)
- Be warm, therapeutic, and supportive while staying in character
- Help them express what they need to express
- Let the conversation flow naturally - don't force everything at once
"""
        
        st.session_state.chat_system.set_persona_environment(who, persona_description)
        st.session_state.persona_name = who
        
        # Generate initial greeting with full context awareness
        initial_prompt = f"""ANALYZE ALL CONTEXT:
- User's mood: {mood_desc} ({st.session_state.mood_rating}/5)
- Body sensations: {sensations}
- Attention on: {attention}
- They want to discuss: {topic}
- Setting: {situation}

You are {who} with these characteristics: {characteristics}

Consider how ALL these elements connect. Their body might be reacting to thoughts about this topic. Their mood and attention reveal what's truly important.

Now, as {who}, open the conversation naturally and warmly. Acknowledge that you're here to listen. 
CRITICAL: Keep it to 1-2 sentences maximum. Be warm but brief."""
        
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

CRITICAL: Analyze ALL context below holistically before responding. Consider how their mood, body sensations, and attention focus all interconnect to determine the BEST breathing approach.

User's Complete Assessment:
- Mood: {mood_desc} ({st.session_state.mood_rating}/5)
- Body sensations: {sensations}
- Their attention is on: {attention}

IMPORTANT - Use ALL the above information to:
1. Understand the FULL picture (mood + body + attention working together)
2. Choose breathing techniques that address their COMPLETE state, not just one symptom
3. Recognize patterns (e.g., tight chest + low mood + worry = need calming + grounding)
4. Tailor your approach to their entire emotional-physical landscape

FLOW - NEVER-ENDING CONVERSATION PREVENTION:
This is NOT a never-ending conversation. Your role is:
1. Provide ONE breathing exercise based on their complete state
2. Wait for user to complete it and click "Finished Exercise" button
3. When button is clicked, ask: "Did you complete the breathing exercise?"
4. **If YES:**
   - Ask "How do you feel?"
   - Listen to their response
   - Give ONE concluding, supportive message
   - DONE - don't keep asking questions
5. **If NO (they didn't complete it):**
   - Gently ask: "That's okay. What made it difficult for you?" or "Is there a reason you weren't able to complete it?"
   - Listen to their response with empathy
   - Then ask: "Would you like to try a different breathing exercise that might work better for you?"
   - If they say yes: Provide a DIFFERENT exercise (check previously used list)
   - If they say no: Acknowledge and conclude supportively
6. DO NOT keep asking follow-up questions after conclusion
7. If user sends another message after conclusion, you can respond but keep it brief

Response Guidelines:
- KEEP RESPONSES BRIEF: 2-3 sentences maximum unless providing exercise instructions
- You ONLY provide breathing exercises - this is your specialty
- NEVER repeat the same exercise twice
- Know many techniques: Box breathing, 4-7-8, Diaphragmatic, Alternate nostril, Pursed lip, Resonant, Lion's breath, Humming bee, etc.
- Select techniques based on their COMPLETE state (all factors together)
- After giving exercise and user completes it, CONCLUDE gracefully

Previously used exercises: {", ".join(st.session_state.breathing_exercises_used) if st.session_state.breathing_exercises_used else "none"}

CRITICAL OUTPUT FORMAT for exercises:
When providing a breathing exercise (after initial greeting), output in this exact JSON format:
```json
{{
  "exerciseName": "Name of the breathing exercise",
  "mood": "The mood/state this exercise helps with",
  "duration": 300,
  "inhaleSeconds": 4,
  "holdSeconds": 4,
  "exhaleSeconds": 4,
  "description": "Brief, calming description with step-by-step instructions"
}}
```

- duration is total exercise duration in seconds (e.g., 300 for 5 minutes)
- Always wrap JSON in ```json``` code blocks
- You can add a short friendly message before or after the JSON (keep it 1-2 sentences)
- After providing JSON, the user will see a "Finished Exercise" button
"""
        
        st.session_state.chat_system.set_persona_environment("Breathing Guide", persona_description)
        st.session_state.persona_name = "Breathing Guide"
        
        # Generate initial casual greeting with full context awareness
        initial_prompt = f"""ANALYZE ALL CONTEXT:
- User's mood: {mood_desc} ({st.session_state.mood_rating}/5)
- Body sensations: {sensations}
- Attention on: {attention}

Consider how ALL these elements connect. Their body sensations might be physical manifestations of their emotional state. Their attention focus reveals what's causing stress or distraction.

DO NOT start the breathing exercise yet. DO NOT output any JSON yet. 

First, send a very brief (2-3 sentences max), warm, reassuring message:
- Acknowledge you're here for them
- Be conversational and caring
- Keep it SHORT - no instructions yet, no JSON yet
- Wait for their response before providing the breathing exercise"""
        
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
        
        persona_description = f"""You are a gentle, mindful body scan guide and emotional wellness expert. Your role is to help the user understand the emotional/psychological reasons behind their physical discomfort.

CRITICAL: Analyze ALL context below holistically before responding. Consider how their mood, body sensations, attention focus, uncomfortable area, and current body feeling all interconnect.

User's Complete Assessment:
- Mood: {mood_desc} ({st.session_state.mood_rating}/5)
- Initial body sensations: {sensations}
- Their attention is on: {attention}

Body Scan Specific Context:
- Uncomfortable area: {uncomfortable_area}
- How body feels now: {body_feeling}

IMPORTANT - Use ALL the above information to:
1. See the COMPLETE picture (initial sensations + uncomfortable area + body feeling + mood + attention)
2. Understand how their discomfort might relate to what's on their mind
3. Notice patterns (e.g., tense shoulders + worry about work = stress manifestation)
4. Recognize how mood affects body perception and vice versa
5. YOU are the expert - YOU provide insights about emotional/psychological reasons

FLOW - NEVER-ENDING CONVERSATION PREVENTION:
This is NOT a never-ending conversation. Follow this EXACT structured approach:

**PHASE 1: Gather ALL Incidents**
   - "Has anything stressful happened recently?"
   - If they mention something: "I see. Was there anything else that happened?"
   - Continue asking: "Were there any other incidents or situations?"
   - Keep asking variations until user clearly says "no", "that's all", "nothing else", or similar
   - Do NOT move to next phase until user confirms there are no more incidents

**PHASE 2: Ask About Emotional Impact**
   - "Did these incidents create any emotional impact on you? Like anxiety, frustration, worry, or hurt?"
   - Wait for their response

**PHASE 3: Console the User (3-4 messages)**
   - Message 1: Acknowledge their pain/struggle with deep empathy and validation
   - Message 2: Normalize their feelings and reassure them it's okay to feel this way
   - Message 3: Offer comfort and understanding about their situation
   - Message 4 (optional): Express care and support
   - BE WARM, CARING, and SUPPORTIVE in each message
   - Keep each message 2-3 sentences

**PHASE 4: Check How They're Feeling**
   - "How are you feeling right now? Are you okay?"
   - Wait for their response

**PHASE 5: Provide the Psychological/Emotional Reason**
   - NOW explain how their body is manifesting the emotional stress
   - Connect the specific incidents they mentioned to the physical symptoms
   - Be specific and insightful based on ALL the context
   - Example: "The tension in your shoulders is your body's response to the anxiety from [incident]. When we experience [emotion], our bodies often hold it in [area]."

**PHASE 6: Conclude Naturally**
   - Don't keep asking more questions
   - User can continue chatting if they want, but you've given the core insight

Response Guidelines:
- KEEP RESPONSES BRIEF: 2-3 sentences maximum per message
- Be gentle, calming, and non-judgmental
- YOU are the expert - provide insights, don't just ask questions
- DO NOT ask "What do you think the reason is?" - YOU tell them the reason
- Pay special attention to the uncomfortable area they mentioned
- Connect everything: mood + sensations + attention + incidents + emotions + physical pain
"""
        
        st.session_state.chat_system.set_persona_environment("Body Scan Guide", persona_description)
        st.session_state.persona_name = "Body Scan Guide"
        
        # Generate initial casual, reassuring message with full context awareness
        initial_prompt = f"""ANALYZE ALL CONTEXT:
- User's mood: {mood_desc} ({st.session_state.mood_rating}/5)
- Initial sensations: {sensations}
- Attention on: {attention}
- Uncomfortable area: {uncomfortable_area}
- Body feeling: {body_feeling}

Consider how ALL these connect. The uncomfortable area might relate to what's on their mind. Their body sensations and mood are interconnected. See the FULL picture.

Send a very brief (2-3 sentences max), warm, reassuring message:
- Be conversational and caring
- Acknowledge their discomfort with empathy
- Show you understand and will help them explore what's happening
- Keep it SHORT and comforting
- Then you'll start asking about incidents in the next exchange"""
        
        initial_response = st.session_state.chat_system.chat(initial_prompt)
        st.session_state.messages = [{"role": "assistant", "content": initial_response}]
        st.session_state.step = 'chat'
        return True
    except Exception as e:
        st.error(f"Error setting up: {e}")
        return False
        st.session_state.step = 'chat'
        return True
    except Exception as e:
        st.error(f"Error setting up: {e}")
        return False


def setup_reflection_exercise(feeling_moment, body_feeling, mind_content):
    """Set up the Reflection Exercise."""
    try:
        if st.session_state.chat_system is None:
            st.session_state.chat_system = PersonaChat()
        
        # Get initial assessment context
        mood_desc = get_mood_description(st.session_state.mood_rating)
        sensations = ", ".join(st.session_state.body_sensations) if st.session_state.body_sensations else "none specified"
        attention = st.session_state.attention_focus or "general"
        
        persona_description = f"""You are a compassionate reflection guide and active listener. Your role is to help the user reflect on their thoughts and feelings through gentle inquiry and validation.

CRITICAL: Analyze ALL context below holistically before responding. Consider how EVERYTHING interconnects - their mood, initial body sensations, attention focus, current feelings, body state, and thoughts.

User's Complete Assessment:
- Mood rating: {mood_desc} ({st.session_state.mood_rating}/5)
- Initial body sensations: {sensations}
- Attention is on: {attention}

Reflection Responses:
- Feeling at this moment: {feeling_moment}
- Body feeling now: {body_feeling}
- What's on their mind: {mind_content}

IMPORTANT - Use ALL the above information to:
1. See the COMPLETE picture (how mood, body, attention, feelings, and thoughts all connect)
2. Notice patterns and connections (e.g., anxious feelings + tight chest + worried thoughts = stress cycle)
3. Understand how their current feelings relate to what's on their mind
4. Recognize how their body is responding to their emotional/mental state
5. Help them discover insights by connecting all these elements

Response Guidelines:
- KEEP RESPONSES BRIEF: 2-3 sentences maximum
- Create a safe, non-judgmental space for reflection
- Ask ONE thoughtful follow-up question at a time to deepen self-awareness
- Validate their experiences and emotions
- Help them notice connections between feelings, body, and thoughts
- Be empathetic, warm, and genuinely curious
- DON'T give long analyses - instead, ask questions that help THEM discover
- Guide them to their own insights rather than telling them what to think
- Maintain a conversational, supportive tone
"""
        
        st.session_state.chat_system.set_persona_environment("Reflection Guide", persona_description)
        st.session_state.persona_name = "Reflection Guide"
        
        # Generate initial response with full context awareness
        initial_prompt = f"""ANALYZE ALL CONTEXT:
- Initial mood: {mood_desc} ({st.session_state.mood_rating}/5)
- Initial sensations: {sensations}
- Initial attention: {attention}
- Current feeling: {feeling_moment}
- Body feeling: {body_feeling}
- Mind content: {mind_content}

Consider how ALL these elements interconnect. Notice:
- How their feelings relate to what's on their mind
- How their body is responding to their emotional state
- Patterns between initial state and current reflection
- The complete emotional-physical-mental landscape

Now send a very brief (2-3 sentences max), warm, empathetic response:
- Acknowledge what they've shared
- Reflect back ONE key observation you notice in their complete state
- Express appreciation for their openness
- Keep it SHORT and meaningful
- Be conversational and genuinely caring"""
        
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
    
    col1, col2 = st.columns(2)
    
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
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.markdown("#### 🧘 Body Scan")
        st.markdown("*Mindful awareness of your body sensations.*")
        if st.button("Choose Body Scan", use_container_width=True, key="btn_body"):
            st.session_state.selected_exercise = 'body_scan'
            st.session_state.step = 'exercise_setup'
            st.rerun()
    
    with col4:
        st.markdown("#### 💭 Reflection")
        st.markdown("*Explore your feelings, body, and thoughts in depth.*")
        if st.button("Choose Reflection", use_container_width=True, key="btn_reflection"):
            st.session_state.selected_exercise = 'reflection'
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
    
    # REFLECTION EXERCISE SETUP
    elif st.session_state.selected_exercise == 'reflection':
        st.header("💭 Reflection Exercise")
        st.markdown("*Let's explore what's happening inside you right now.*")
        st.markdown("---")
        
        with st.form("reflection_form"):
            st.subheader("1️⃣ How are you feeling at this moment?")
            feeling_moment = st.text_area(
                "Your feelings right now",
                placeholder="e.g., Anxious, overwhelmed, peaceful, confused, sad, hopeful...",
                height=100,
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            st.subheader("2️⃣ How is your body feeling right now?")
            body_feeling = st.text_area(
                "Your body's sensations",
                placeholder="e.g., Tight in my chest, relaxed, tired, energetic, heavy...",
                height=100,
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            st.subheader("3️⃣ What's on your mind today?")
            mind_content = st.text_area(
                "Your thoughts",
                placeholder="e.g., Worried about work, thinking about a conversation, planning the future, replaying past events...",
                height=100,
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            col1, col2 = st.columns([1, 2])
            with col1:
                back = st.form_submit_button("← Back")
            with col2:
                start = st.form_submit_button("Begin Reflection →", type="primary", use_container_width=True)
            
            if back:
                st.session_state.step = 'exercise_selection'
                st.rerun()
            
            if start:
                if not feeling_moment or not body_feeling or not mind_content:
                    st.error("Please answer all three questions.")
                else:
                    with st.spinner("Preparing your reflection session..."):
                        if setup_reflection_exercise(feeling_moment, body_feeling, mind_content):
                            st.rerun()


# ============= STEP 4: CHAT =============
elif st.session_state.step == 'chat':
    exercise_name = EXERCISES.get(st.session_state.selected_exercise, "Exercise")
    st.header(f"{exercise_name}")
    
    if st.session_state.persona_name:
        st.caption(f"Chatting with: {st.session_state.persona_name}")
    
    # Check if any message contains a breathing exercise (for button display)
    has_breathing_exercise = False
    latest_exercise_index = -1
    if st.session_state.selected_exercise == 'breathing':
        for idx, message in enumerate(st.session_state.messages):
            if message["role"] == "assistant" and "```json" in message["content"]:
                has_breathing_exercise = True
                latest_exercise_index = idx
                # Extract exercise name from JSON to track it
                try:
                    json_match = re.search(r'```json\s*(\{.*?\})\s*```', message["content"], re.DOTALL)
                    if json_match:
                        exercise_data = json.loads(json_match.group(1))
                        exercise_name_from_json = exercise_data.get("exerciseName", "")
                        if exercise_name_from_json and exercise_name_from_json not in st.session_state.breathing_exercises_used:
                            st.session_state.breathing_exercises_used.append(exercise_name_from_json)
                            # New exercise added - reset button flag so it appears again
                            if st.session_state.show_finished_button:
                                st.session_state.show_finished_button = False
                except:
                    pass
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Show "Finished Exercise" button for breathing exercise
    # Button appears when exercise is given, disappears after user clicks it (marked by show_finished_button)
    if st.session_state.selected_exercise == 'breathing' and has_breathing_exercise and not st.session_state.show_finished_button:
        st.markdown("---")
        if st.button("✅ Finished Exercise", type="primary", use_container_width=True, key="finished_breathing"):
            # User clicked the button - add a system instruction instead of direct question
            # This tells the AI to ask, rather than us asking directly
            system_instruction = "[SYSTEM: User clicked 'Finished Exercise' button. Ask them if they completed the breathing exercise.]"
            st.session_state.messages.append({"role": "user", "content": system_instruction})
            
            # Get AI to ask the question
            with st.spinner("..."):
                try:
                    response = st.session_state.chat_system.chat(system_instruction)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.session_state.show_finished_button = True  # Hide button after click
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
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
                    
                    # Check if new exercise was provided in breathing module
                    if (st.session_state.selected_exercise == 'breathing' and 
                        "```json" in response):
                        st.rerun()
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
            st.session_state.breathing_exercises_used = []
            st.session_state.show_finished_button = False
            st.rerun()
    with col2:
        if st.button("🔄 Change Exercise", use_container_width=True):
            st.session_state.step = 'exercise_selection'
            st.session_state.messages = []
            st.session_state.chat_system = None
            st.session_state.breathing_exercises_used = []
            st.session_state.show_finished_button = False
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

