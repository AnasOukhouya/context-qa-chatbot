import streamlit as st
from qa_bot import QAChatbot
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Question Answering Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling and fixed input
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    
    .chat-container {
        height: 400px;
        overflow-y: auto;
        padding: 20px;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #e9ecef;
    }
    
    .question-bubble {
        background-color: #007bff;
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 10px 0 5px auto;
        max-width: 80%;
        word-wrap: break-word;
        text-align: right;
        margin-left: 20%;
    }
    
    .answer-bubble {
        background-color: #e9ecef;
        color: #333;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 5px auto 10px 0;
        max-width: 80%;
        word-wrap: break-word;
        margin-right: 20%;
    }
    
    .confidence-info {
        font-size: 0.8rem;
        color: #666;
        margin-top: 5px;
        font-style: italic;
    }
    
    .high-confidence { color: #28a745; }
    .medium-confidence { color: #ffc107; }
    .low-confidence { color: #dc3545; }
    
    .timestamp {
        font-size: 0.7rem;
        color: #999;
        text-align: center;
        margin: 15px 0 5px 0;
    }
    
    .fixed-bottom {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: white;
        padding: 20px;
        border-top: 2px solid #e9ecef;
        z-index: 1000;
    }
    
    .context-section {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border: 1px solid #e9ecef;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
    
    .main-content {
        padding-bottom: 150px;
    }
    
    /* Hide streamlit footer and header */
    .stApp > footer {display: none;}
    .stApp > header {display: none;}
    
    /* Adjust main container */
    .main .block-container {
        padding-top: 2rem;
        max-width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = QAChatbot()  # Load model immediately
if 'context' not in st.session_state:
    st.session_state.context = ""
if 'qa_history' not in st.session_state:
    st.session_state.qa_history = []
if 'question_input' not in st.session_state:
    st.session_state.question_input = ""

def clear_chat():
    """Clear the chat history."""
    st.session_state.qa_history = []
    st.success("🗑️ Chat history cleared!")
    time.sleep(1)
    st.rerun()

def get_confidence_class(confidence):
    """Get CSS class based on confidence level."""
    if confidence >= 0.7:
        return "high-confidence"
    elif confidence >= 0.4:
        return "medium-confidence"
    else:
        return "low-confidence"

def get_confidence_text(confidence):
    """Get confidence level text."""
    if confidence >= 0.7:
        return "High Confidence"
    elif confidence >= 0.4:
        return "Medium Confidence"
    else:
        return "Low Confidence"

def handle_question_submit():
    """Handle question submission."""
    question = st.session_state.question_input_widget
    if question and st.session_state.context.strip():
        result = st.session_state.chatbot.answer_question(
            st.session_state.context, 
            question
        )
        
        # Add to history
        qa_entry = {
            'question': question,
            'answer': result['answer'],
            'confidence': result['confidence'],
            'timestamp': datetime.now().strftime("%H:%M:%S"),
            'error': result.get('error', False)
        }
        st.session_state.qa_history.append(qa_entry)
        
        # Clear input
        st.session_state.question_input_widget = ""

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Question Answering Chatbot</h1>', unsafe_allow_html=True)
    
    # Main content container
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Context input section
    st.markdown("### 📝 Context")
    context_input = st.text_area(
        "Enter or paste your context here:",
        value=st.session_state.context,
        height=120,
        placeholder="Paste your context here... (e.g., a paragraph, article, or document excerpt)",
        key="context_input"
    )
    
    # Update context
    if context_input != st.session_state.context:
        st.session_state.context = context_input
    
    # Sidebar for controls
    with st.sidebar:
        st.markdown("### 📋 Instructions")
        st.markdown("""
        1. **Enter your context** - the text containing information
        2. **Ask questions** about the context
        3. **Press Enter** or click Ask to submit
        4. **Clear chat** to start fresh conversation
        """)
        
        # Statistics
        if st.session_state.qa_history:
            st.markdown("### 📊 Session Stats")
            total_questions = len(st.session_state.qa_history)
            avg_confidence = sum(qa['confidence'] for qa in st.session_state.qa_history) / total_questions
            
            st.metric("Questions Asked", total_questions)
            st.metric("Avg. Confidence", f"{avg_confidence:.1%}")
        
        # Clear chat button
        if st.session_state.qa_history:
            st.markdown("### 🗑️ Chat Management")
            if st.button("Clear Chat History", type="secondary"):
                clear_chat()
    
    # Chat conversation display
    if st.session_state.qa_history:
        st.markdown("### 💬 Conversation")
        
        # Create scrollable chat container
        chat_html = '<div class="chat-container">'
        
        for qa in st.session_state.qa_history:
            # Timestamp
            chat_html += f'<div class="timestamp">{qa["timestamp"]}</div>'
            
            # Question bubble
            chat_html += f'<div class="question-bubble">🙋 {qa["question"]}</div>'
            
            # Answer bubble with confidence
            confidence_class = get_confidence_class(qa['confidence'])
            confidence_text = get_confidence_text(qa['confidence'])
            
            chat_html += f'''
            <div class="answer-bubble">
                🤖 {qa["answer"]}
                <div class="confidence-info {confidence_class}">
                    {confidence_text} ({qa["confidence"]:.1%})
                </div>
            </div>
            '''
        
        chat_html += '</div>'
        st.markdown(chat_html, unsafe_allow_html=True)
        
        # Auto-scroll to bottom using JavaScript
        st.markdown("""
        <script>
        var chatContainer = document.querySelector('.chat-container');
        if (chatContainer) {
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        </script>
        """, unsafe_allow_html=True)
    
    else:
        if st.session_state.context:
            st.info("💡 Context is ready! Ask your first question below.")
        else:
            st.info("📝 Please enter a context above, then ask questions about it.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Fixed bottom input section
    st.markdown("""
    <style>
    .element-container:has(> .stTextInput) {
        position: fixed;
        bottom: 20px;
        left: 20px;
        right: 20px;
        background-color: white;
        padding: 20px;
        border-top: 2px solid #e9ecef;
        border-radius: 10px;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        z-index: 1000;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Question input at bottom
    col1, col2 = st.columns([5, 1])
    
    with col1:
        question = st.text_input(
            "Ask a question:",
            placeholder="What would you like to know about the context?",
            key="question_input_widget",
            on_change=None,
            label_visibility="collapsed"
        )
    
    with col2:
        ask_button = st.button("🚀 Ask", type="primary", use_container_width=True)
    
    # Handle Enter key press or button click
    if ask_button or (question and question != st.session_state.get('last_question', '')):
        if not st.session_state.context.strip():
            st.error("⚠️ Please provide a context first!")
        elif not question.strip():
            st.error("⚠️ Please enter a question!")
        else:
            st.session_state.last_question = question
            handle_question_submit()
            time.sleep(0.1)  # Small delay for smooth UX
            st.rerun()
    
    # JavaScript for Enter key handling
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const questionInput = document.querySelector('input[aria-label="Ask a question:"]');
        if (questionInput) {
            questionInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const askButton = document.querySelector('button[kind="primary"]');
                    if (askButton) {
                        askButton.click();
                    }
                }
            });
        }
    });
    </script>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
