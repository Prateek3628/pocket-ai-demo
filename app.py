import streamlit as st
from dotenv import load_dotenv
from script import PersonaChat
import os

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Pocket AI - Persona Chat",
    page_icon="💬",
    layout="centered"
)

# Initialize session state
if 'chat_system' not in st.session_state:
    st.session_state.chat_system = None
if 'persona_set' not in st.session_state:
    st.session_state.persona_set = False
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'persona_name' not in st.session_state:
    st.session_state.persona_name = ""


def reset_persona():
    """Reset the persona and clear chat history."""
    st.session_state.chat_system = None
    st.session_state.persona_set = False
    st.session_state.messages = []
    st.session_state.persona_name = ""


def setup_persona(who, characteristics, topic, situation):
    """Set up the persona based on the four questions."""
    try:
        # Initialize chat system if not already done
        if st.session_state.chat_system is None:
            st.session_state.chat_system = PersonaChat()
        
        # Create comprehensive persona description
        persona_description = f"""Characteristics and Personality:
{characteristics}

Context for this conversation:
- The user wants to talk about: {topic}
- Current situation/environment: {situation}

Communication Style:
- Respond naturally as this person would
- Keep the conversation topic and situation in mind
- Be authentic to the characteristics described above
"""
        
        # Set the persona environment
        st.session_state.chat_system.set_persona_environment(who, persona_description)
        st.session_state.persona_set = True
        st.session_state.persona_name = who
        st.session_state.messages = []
        
        # Generate initial greeting message from the persona
        initial_prompt = f"Start the conversation naturally. Given the situation ({situation}) and the topic they want to discuss ({topic}), greet them warmly and show you're ready to talk."
        initial_response = st.session_state.chat_system.chat(initial_prompt)
        
        # Add the initial message to chat history
        st.session_state.messages.append({"role": "assistant", "content": initial_response})
        
        return True
    except Exception as e:
        st.error(f"Error setting up persona: {e}")
        return False


# App Title
st.title("💬 Pocket AI - Persona Chat")
st.markdown("---")

# Sidebar for persona setup
with st.sidebar:
    st.header("🎭 Persona Setup")
    
    if st.session_state.persona_set:
        st.success(f"✓ Currently chatting with: **{st.session_state.persona_name}**")
        if st.button("🔄 Change Persona", use_container_width=True):
            reset_persona()
            st.rerun()
    else:
        st.info("Set up who you want to talk to")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("This app lets you chat with AI personas based on people in your life.")

# Main content area
if not st.session_state.persona_set:
    # Persona Setup Form
    st.header("🎯 Let's Set Up Your Conversation")
    st.markdown("Answer these questions to personalize your chat experience:")
    
    with st.form("persona_form"):
        st.subheader("1️⃣ Who would you like to talk to?")
        who = st.text_input(
            "Enter the person or relationship",
            placeholder="e.g., father, mother, best friend, mentor, etc.",
            help="Who do you want to have a conversation with?"
        )
        
        st.markdown("---")
        st.subheader("2️⃣ Some characteristics of the person")
        characteristics = st.text_area(
            "Describe their personality and communication style",
            placeholder="e.g., Caring and supportive, uses humor often, gives practical advice, speaks directly but kindly...",
            height=120,
            help="How does this person talk? What's their personality like?"
        )
        
        st.markdown("---")
        st.subheader("3️⃣ What would you like to talk about?")
        topic = st.text_input(
            "Enter the topic or subject",
            placeholder="e.g., career advice, life updates, seeking comfort, casual chat...",
            help="What's the main topic you want to discuss?"
        )
        
        st.markdown("---")
        st.subheader("4️⃣ Set the situation/environment")
        situation = st.text_area(
            "Describe the current situation or context",
            placeholder="e.g., It's late evening and I'm feeling stressed about work. I need someone to talk to who understands me...",
            height=120,
            help="What's the context or setting for this conversation?"
        )
        
        st.markdown("---")
        submitted = st.form_submit_button("🚀 Start Chatting", use_container_width=True, type="primary")
        
        if submitted:
            if not who or not characteristics or not topic or not situation:
                st.error("⚠️ Please fill in all fields before starting the chat.")
            else:
                with st.spinner("Setting up your persona..."):
                    if setup_persona(who, characteristics, topic, situation):
                        st.success("✓ Persona set up successfully!")
                        st.rerun()

else:
    # Chat Interface
    st.header(f"💬 Chatting with your {st.session_state.persona_name}")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.chat_system.chat(prompt)
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    if "OPENAI_API_KEY" in str(e) or "api_key" in str(e).lower():
                        st.warning("⚠️ Make sure your OPENAI_API_KEY is set in the .env file")
    
    # Clear conversation button
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.chat_system:
                st.session_state.chat_system.reset_conversation()
            st.rerun()
    with col2:
        if st.button("🔄 New Persona", use_container_width=True):
            reset_persona()
            st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.8em;'>"
    "Powered by OpenAI • Built with Streamlit"
    "</div>",
    unsafe_allow_html=True
)
