import streamlit as st

# Set up the Streamlit app
def main():
    st.title("Chatbot Interface")

    # Display a container for the chatbot conversation
    st.markdown("### Conversation")
    conversation_container = st.container()

    with conversation_container:
        st.markdown("**Bot:** Hello! How can I assist you today?")
        st.markdown("**You:** Enter your message below or record your voice.")

    # Display a button to record voice
    if st.button("Record Voice"):
        st.write("Voice recording started...")

    # Display a text input for user to type messages
    user_input = st.text_input("Type your message:", placeholder="Enter your message here...")

    # Display a send button
    if st.button("Send Message"):
        with conversation_container:
            st.markdown(f"**You:** {user_input}")
            st.markdown("**Bot:** (Bot's response will appear here)")

if __name__ == "__main__":
    main()