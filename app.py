import streamlit as st
from qa_bot import QAChatbot
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Question Answering Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    
    .context-box {
        background-color: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .question-container {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 10px 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    .answer-container {
        background-color: #f1f8e9;
        border-left: 4px solid #4caf50;
        padding: 10px 15px;
        margin: 10px 0;
        border-radius: 5px;
    }
    
    .low-confidence {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
    }
    
    .medium-confidence {
        background-color: #fff8e1;
        border-left: 4px solid #ff9800;
    }
    
    .high-confidence {
        background-color: #f1f8e9;
        border-left: 4px solid #4caf50;
    }
    
    .confidence-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
        margin-left: 10px;
    }
    
    .stats-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        text-align: center;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
    
    .sidebar-content {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    /* Fix the input box to the bottom */
    .fixed-input-box {
        position: fixed;
        bottom: 0;
        left: 0;
        width: calc(100% - 300px); /* adjust automatically with sidebar */
        padding: 10px 20px;
        background: white;
        z-index: 100;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = None
if 'context' not in st.session_state:
    st.session_state.context = ""
if 'qa_history' not in st.session_state:
    st.session_state.qa_history = []
if 'model_loaded' not in st.session_state:
    st.session_state.model_loaded = False

def load_model():
    """Load the QA model with progress indicator."""
    if not st.session_state.model_loaded:
        with st.spinner("🤖 Loading AI model... This may take a moment on first run."):
            st.session_state.chatbot = QAChatbot()
            st.session_state.model_loaded = True
        st.success("✅ Model loaded successfully!")
        time.sleep(1)
        st.rerun()

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

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Question Answering Chatbot</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown("### 📋 Instructions")
        st.markdown("""
        1. **Load the AI model** first (one-time setup)
        2. **Enter your context** - the text containing information
        3. **Ask questions** about the context
        4. **View answers** with confidence scores
        5. **Clear chat** to start fresh
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown("### 🎯 Model Information")
        st.markdown("""
        **Model:** DistilBERT-SQuAD  
        **Type:** Extractive QA  
        **Language:** English  
        **Context Limit:** 512 tokens
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Model loading
        st.markdown("### 🚀 Model Status")
        if st.session_state.model_loaded:
            st.success("✅ Model Ready!")
        else:
            if st.button("🔄 Load AI Model", type="primary"):
                load_model()
        
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

    # Main content
    if not st.session_state.model_loaded:
        st.info("👈 Please load the AI model from the sidebar to get started!")
        return
    
    # Context input
    st.markdown("### 📝 Context")
    st.markdown("Enter or paste the text that contains the information you want to ask questions about:")
    
    with st.sidebar:
        st.markdown("### 📝 Context")
        context_input = st.text_area(
            "Context",
            value=st.session_state.context,
            height=200,
            placeholder="Paste your context here...",
            label_visibility="collapsed"
        )
        if context_input != st.session_state.context:
            st.session_state.context = context_input
            if context_input:
                st.success(f"✅ Context updated! ({len(context_input)} characters)")

    # Update context
    if context_input != st.session_state.context:
        st.session_state.context = context_input
        if context_input:
            st.success(f"✅ Context updated! ({len(context_input)} characters)")

    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)

    # Question input
    st.markdown("### ❓ Ask a Question")
    
    st.markdown('<div class="fixed-input-box">', unsafe_allow_html=True)

    col1, col2 = st.columns([4, 1])
    
    with col1:
        question = st.text_input(
            "Question",
            placeholder="What would you like to know about the context?",
            key="input_question",
            label_visibility="collapsed"
        )
    
    with col2:
        ask_button = st.button("🚀 Ask", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    
    # Process question
    if ask_button or (question and st.session_state.get('enter_pressed', False)):
        if not st.session_state.context.strip():
            st.error("⚠️ Please provide a context first!")
        elif not question.strip():
            st.error("⚠️ Please enter a question!")
        else:
            with st.spinner("🤔 Thinking..."):
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
            
            # Clear the question input by rerunning
            st.rerun()
    
    # Display current context info
    if st.session_state.context:
        st.markdown("### 📄 Current Context Preview")
        with st.expander("Click to view/hide context", expanded=False):
            st.markdown(f'<div class="context-box">{st.session_state.context}</div>', unsafe_allow_html=True)
    
    # Display QA history
    if st.session_state.qa_history:
        st.markdown("### 💬 Question & Answer History")
        
        # Reverse to show latest first
        for i, qa in enumerate(reversed(st.session_state.qa_history)):
            with st.container():
                # Question
                st.markdown(f"""
                <div class="question-container">
                    <strong>🙋 Question {len(st.session_state.qa_history) - i}:</strong> {qa['question']}
                    <div style="font-size: 0.8rem; color: #666; margin-top: 5px;">
                        ⏰ {qa['timestamp']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Answer
                confidence_class = get_confidence_class(qa['confidence'])
                confidence_color = st.session_state.chatbot.get_confidence_color(qa['confidence'])
                confidence_text = st.session_state.chatbot.get_confidence_text(qa['confidence'])
                
                st.markdown(f"""
                <div class="answer-container {confidence_class}">
                    <strong>🤖 Answer:</strong> {qa['answer']}
                    <div style="margin-top: 10px;">
                        <span style="font-size: 0.9rem; color: #666;">Confidence:</span>
                        <span class="confidence-badge" style="background-color: {confidence_color};">
                            {confidence_text} ({qa['confidence']:.1%})
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Warning for low confidence
                if qa['confidence'] < 0.3:
                    st.warning("⚠️ Low confidence answer - the information might not be reliable or the answer might not be in the context.")
                
                st.markdown("---")
    
    else:
        if st.session_state.context:
            st.info("💡 Context is ready! Ask your first question above.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        Built with ❤️ using Streamlit and Hugging Face Transformers
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
