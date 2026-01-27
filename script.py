import os
from openai import OpenAI
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class PersonaChat:
    """
    A chat system that allows users to interact with AI personas.
    The persona is set based on user input about who they want to talk to
    and how that person communicates.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the PersonaChat with OpenAI API key.
        
        Args:
            api_key: OpenAI API key. If None, will use OPENAI_API_KEY env variable.
        """
        if api_key:
            self.client = OpenAI(api_key=api_key)
        else:
            self.client = OpenAI()  # Uses OPENAI_API_KEY env variable
        
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt: str = ""
        self.persona_name: str = ""
    
    def set_persona_environment(self, persona_name: str, persona_description: str):
        """
        Set the AI environment based on the persona the user wants to talk to.
        
        Args:
            persona_name: Name/relationship of the persona (e.g., "father", "mother", "best friend")
            persona_description: Description of how this persona talks and behaves
        """
        self.persona_name = persona_name
        
        # Create a detailed system prompt based on the persona
        self.system_prompt = f"""You are now role-playing as the user's {persona_name}.

Persona Description:
{persona_description}

Important Instructions:
- Stay in character as the {persona_name} at all times
- Match the communication style described above
- Be authentic and natural in your responses
- Show care and concern appropriate to this relationship
- Only reference information explicitly shared by the user - do NOT invent memories, past events, or experiences
- Respond as this person would actually respond

Remember: You ARE the {persona_name}. Respond directly as them, not as an AI describing them."""
        
        # Initialize conversation with system prompt
        self.conversation_history = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        print(f"\n✓ Environment set successfully! You are now chatting with your {persona_name}.")
        print(f"{'='*60}\n")
    
    def chat(self, user_message: str) -> str:
        """
        Send a message and get a response from the persona.
        
        Args:
            user_message: The message from the user
            
        Returns:
            The AI's response as the persona
        """
        if not self.system_prompt:
            return "Error: Please set up a persona environment first using set_persona_environment()"
        
        # Add user message to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Get response from OpenAI
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # You can change to "gpt-3.5-turbo" for faster/cheaper responses
            messages=self.conversation_history,
            temperature=0.8,  # Slightly higher for more natural, varied responses
            max_tokens=500
        )
        
        # Extract the assistant's reply
        assistant_message = response.choices[0].message.content
        
        # Add assistant's response to conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    
    def reset_conversation(self):
        """Reset the conversation while keeping the same persona."""
        if self.system_prompt:
            self.conversation_history = [
                {"role": "system", "content": self.system_prompt}
            ]
            print(f"\n✓ Conversation reset. Still chatting with your {self.persona_name}.\n")
        else:
            self.conversation_history = []
            print("\n✓ Conversation reset.\n")
    
    def change_persona(self):
        """Clear the current persona to set up a new one."""
        self.conversation_history = []
        self.system_prompt = ""
        self.persona_name = ""
        print("\n✓ Persona cleared. Ready to set up a new environment.\n")


def setup_persona_interactive() -> tuple:
    """
    Interactive setup to gather persona information from the user.
    
    Returns:
        Tuple of (persona_name, persona_description)
    """
    print("\n" + "="*60)
    print("PERSONA SETUP")
    print("="*60)
    print("\nI'll ask a few short questions to set up the persona environment.\n")

    # 1) Who would you like to talk to?
    persona_name = input("Who would you like to talk to? (e.g., father, mother, best friend, coach, etc.): ").strip()
    if not persona_name:
        persona_name = "friend"

    # 2) Some characteristics / mannerisms
    characteristics = input(
        "List a few characteristics or mannerisms for this person (tone, common phrases, attitude).\n" 
        "Example: warm, uses humour, short direct answers, supportive, formal: \n> "
    ).strip()
    if not characteristics:
        characteristics = f"A caring and supportive {persona_name} who communicates warmly and genuinely."

    # 3) What would you like to talk about?
    topic = input("What would you like to talk about with them? (e.g., career advice, family, celebration, breakup): ").strip()
    if not topic:
        topic = "a general conversation"

    # 4) Set the situation/environment
    situation = input(
        "Set the situation/environment for the conversation (optional).\n" 
        "Example: 'at a family dinner', 'late-night call', 'supportive message after a setback' (press Enter to skip): \n> "
    ).strip()
    if not situation:
        situation = "a casual conversation"

    # Build a clear persona description combining the inputs
    persona_description_parts = [
        f"Relationship: {persona_name}",
        f"Characteristics: {characteristics}",
        f"Topic: {topic}",
        f"Situation: {situation}",
    ]

    persona_description = (
        "\n".join(persona_description_parts)
        + "\n\nInstructions: Stay in character as the person described above.\n"
        "Speak in a way that matches the listed characteristics, keep responses relevant to the stated topic, "
        "and reflect the situation/environment when appropriate."
    )

    return persona_name, persona_description


def main():
    """
    Main function to run the interactive persona chat.
    """
    print("\n" + "="*60)
    print("WELCOME TO PERSONA CHAT")
    print("="*60)
    print("\nThis application lets you chat with AI personas based on")
    print("people in your life. The AI will adapt its communication")
    print("style to match the person you want to talk to.\n")
    
    # Initialize the chat system
    try:
        chat_system = PersonaChat()
    except Exception as e:
        print(f"\n❌ Error: Could not initialize OpenAI client.")
        print(f"Make sure you have set the OPENAI_API_KEY environment variable.")
        print(f"Error details: {e}")
        return
    
    # Setup persona
    persona_name, persona_description = setup_persona_interactive()
    chat_system.set_persona_environment(persona_name, persona_description)
    
    # Chat loop
    print(f"Start chatting with your {persona_name}!")
    print("Commands: 'quit' to exit, 'reset' to clear conversation, 'new' for new persona\n")
    
    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print(f"\nGoodbye! Thanks for chatting.\n")
                break
            
            elif user_input.lower() == 'reset':
                chat_system.reset_conversation()
                continue
            
            elif user_input.lower() == 'new':
                chat_system.change_persona()
                persona_name, persona_description = setup_persona_interactive()
                chat_system.set_persona_environment(persona_name, persona_description)
                continue
            
            # Get and display response
            response = chat_system.chat(user_input)
            print(f"\n{persona_name.title()}: {response}\n")
            
        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            print("Please try again or type 'quit' to exit.\n")


# Example usage for integration into a larger application
def create_persona_session(persona_name: str, persona_description: str, api_key: str = None) -> PersonaChat:
    """
    Programmatic way to create a persona chat session.
    Use this when integrating into a larger application where you already
    have the persona information from your user flow.
    
    Args:
        persona_name: Name/relationship of the persona
        persona_description: Description of the persona's communication style
        api_key: Optional OpenAI API key
        
    Returns:
        Configured PersonaChat instance ready to use
        
    Example:
        >>> chat = create_persona_session(
        ...     persona_name="father",
        ...     persona_description="Wise, supportive, uses dad jokes, gives practical advice"
        ... )
        >>> response = chat.chat("Hey, how are you doing?")
        >>> print(response)
    """
    chat = PersonaChat(api_key=api_key)
    chat.set_persona_environment(persona_name, persona_description)
    return chat


if __name__ == "__main__":
    main()
