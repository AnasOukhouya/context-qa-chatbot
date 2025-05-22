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
    
    /* Fixed context panel at top */
    .context-panel {
        position: fixed;
        top: 80px;
        left: 50%;
        transform: translateX(-50%);
        width: calc(100vw - 340px);
        max-width: 1200px;
        background-color: #f8f9fa;
        border: 2px solid #e9ecef;
        border-radius: 10px;
        padding: 15px;
        z-index: 1000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: width 0.3s ease;
    }
    
    .context-panel.sidebar-collapsed {
        width: calc(100vw - 40px);
    }
    
    .context-text {
        max-height: 100px;
        overflow-y: auto;
        font-size: 0.9rem;
        color: #333;
        line-height: 1.4;
    }
    
    .context-controls {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    
    .context-stats {
        font-size: 0.8rem;
        color: #666;
    }
    
    /* Chat container with proper spacing */
    .chat-container {
        margin-top: 200px;
        margin-bottom: 120px;
        padding: 20px;
    }
    
    /* Fixed input at bottom */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: calc(100vw - 340px);
        max-width: 1200px;
        background-color: white;
        border-top: 2px solid #e9ecef;
        padding: 20px;
        z-index: 1000;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        transition: width 0.3s ease;
    }
    
    .input-container.sidebar-collapsed {
        width: calc(100vw - 40px);
    }
    
    .question-input-row {
        display: flex;
        gap: 10px;
        align-items: flex-end;
    }
    
    .question-input-row input {
        flex: 1;
        padding: 12px;
        border: 2px solid #e9ecef;
        border-radius: 25px;
        font-size: 1rem;
        outline: none;
        transition: border-color 0.3s ease;
    }
    
    .question-input-row input:focus {
        border-color: #1f77b4;
    }
    
    .question-input-row button {
        padding: 12px 24px;
        background-color: #1f77b4;
        color: white;
        border: none;
        border-radius: 25px;
        font-weight: bold;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    
    .question-input-row button:hover {
        background-color: #1565c0;
    }
    
    /* Chat messages */
    .question-container {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 15px 20px;
        margin: 15px 0;
        border-radius: 10px;
        margin-left: 20%;
    }
    
    .answer-container {
        background-color: #f1f8e9;
        border-left: 4px solid #4caf50;
        padding: 15px 20px;
        margin: 15px 0;
        border-radius: 10px;
        margin-right: 20%;
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
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
        color: white;
        margin-left: 10px;
    }
    
    .message-time {
        font-size: 0.8rem;
        color: #666;
        margin-top: 8px;
        text-align: right;
    }
    
    .sidebar-content {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    
    /* Hide default streamlit elements that interfere */
    .stTextInput > div > div > input {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .context-panel, .input-container {
            width: calc(100vw - 20px);
            left: 10px;
            transform: none;
        }
        
        .question-container, .answer-container {
            margin-left: 5%;
            margin-right: 5%;
        }
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
if 'context_visible' not in st.session_state:
    st.session_state.context_visible = True
if 'editing_context' not in st.session_state:
    st.session_state.editing_context = False

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

def toggle_context_visibility():
    """Toggle context panel visibility."""
    st.session_state.context_visible = not st.session_state.context_visible

def toggle_context_editing():
    """Toggle context editing mode."""
    st.session_state.editing_context = not st.session_state.editing_context

def main():
    # Header
    st.markdown('<h1 class="main-header">🤖 AI Question Answering Chatbot</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.markdown("### 📋 Instructions")
        st.markdown("""
        1. **Load the AI model** first (one-time setup)
        2. **Set your context** using the panel at the top
        3. **Ask questions** using the input at the bottom
        4. **View conversation** flowing upward
        5. **Manage context** with the controls provided
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
        
        # Context management
        st.markdown("### 📝 Context Management")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👁️ Toggle View", help="Show/hide context panel"):
                toggle_context_visibility()
        with col2:
            if st.button("✏️ Edit", help="Edit context"):
                toggle_context_editing()
        
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

    # Check if model is loaded
    if not st.session_state.model_loaded:
        st.info("👈 Please load the AI model from the sidebar to get started!")
        return

    # Fixed Context Panel at Top
    if st.session_state.context_visible:
        context_panel_html = f"""
        <div class="context-panel" id="context-panel">
            <div class="context-controls">
                <strong>📄 Context</strong>
                <div class="context-stats">
                    {len(st.session_state.context)} characters
                    {' • ' + str(len(st.session_state.context.split())) + ' words' if st.session_state.context else ''}
                </div>
            </div>
        """
        
        if st.session_state.editing_context:
            context_panel_html += f"""
                <textarea id="context-textarea" style="width: 100%; height: 80px; border: 1px solid #ccc; border-radius: 5px; padding: 8px; font-family: inherit; resize: vertical;" 
                          placeholder="Enter your context here...">{st.session_state.context}</textarea>
                <div style="margin-top: 10px; text-align: right;">
                    <button onclick="saveContext()" style="background: #4caf50; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; margin-right: 5px;">Save</button>
                    <button onclick="cancelEdit()" style="background: #666; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer;">Cancel</button>
                </div>
            """
        else:
            context_display = st.session_state.context if st.session_state.context else "No context set. Click 'Edit' to add context."
            context_panel_html += f"""
                <div class="context-text">{context_display}</div>
            """
        
        context_panel_html += """
        </div>
        
        <script>
        function saveContext() {
            const textarea = document.getElementById('context-textarea');
            if (textarea) {
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    key: 'context_update',
                    value: textarea.value
                }, '*');
            }
        }
        
        function cancelEdit() {
            window.parent.postMessage({
                type: 'streamlit:setComponentValue', 
                key: 'cancel_edit',
                value: true
            }, '*');
        }
        
        // Adjust panel width based on sidebar state
        function adjustPanelWidth() {
            const panel = document.getElementById('context-panel');
            const sidebar = document.querySelector('.css-1d391kg');
            
            if (panel) {
                if (sidebar && sidebar.style.transform === 'translateX(-100%)') {
                    panel.classList.add('sidebar-collapsed');
                } else {
                    panel.classList.remove('sidebar-collapsed');
                }
            }
        }
        
        // Check sidebar state periodically
        setInterval(adjustPanelWidth, 100);
        </script>
        """
        
        st.markdown(context_panel_html, unsafe_allow_html=True)

    # Main chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display QA history (most recent first - flowing upward)
    if st.session_state.qa_history:
        st.markdown("### 💬 Conversation")
        
        # Show latest messages first (reverse chronological order)
        for i, qa in enumerate(reversed(st.session_state.qa_history)):
            # Question
            st.markdown(f"""
            <div class="question-container">
                <div><strong>🙋 You:</strong> {qa['question']}</div>
                <div class="message-time">{qa['timestamp']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Answer
            confidence_class = get_confidence_class(qa['confidence'])
            confidence_color = st.session_state.chatbot.get_confidence_color(qa['confidence'])
            confidence_text = st.session_state.chatbot.get_confidence_text(qa['confidence'])
            
            st.markdown(f"""
            <div class="answer-container {confidence_class}">
                <div><strong>🤖 AI:</strong> {qa['answer']}</div>
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
                st.warning("⚠️ Low confidence answer - the information might not be reliable.")
    
    else:
        if st.session_state.context:
            st.markdown("### 💬 Conversation")
            st.info("💡 Context is ready! Ask your first question using the input box below.")
        else:
            st.info("📝 Please set your context using the panel above, then ask questions below.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Handle context updates from JavaScript
    context_update = st.query_params.get('context_update')
    if context_update:
        st.session_state.context = context_update
        st.session_state.editing_context = False
        st.rerun()
    
    cancel_edit = st.query_params.get('cancel_edit')
    if cancel_edit:
        st.session_state.editing_context = False
        st.rerun()
    
    # Fixed input container at bottom
    input_container_html = """
    <div class="input-container" id="input-container">
        <div style="margin-bottom: 10px; font-size: 0.9rem; color: #666; text-align: center;">
            Ask a question about your context
        </div>
    </div>
    
    <script>
    // Adjust input width based on sidebar state
    function adjustInputWidth() {
        const container = document.getElementById('input-container');
        const sidebar = document.querySelector('.css-1d391kg');
        
        if (container) {
            if (sidebar && sidebar.style.transform === 'translateX(-100%)') {
                container.classList.add('sidebar-collapsed');
            } else {
                container.classList.remove('sidebar-collapsed');
            }
        }
    }
    
    // Check sidebar state periodically
    setInterval(adjustInputWidth, 100);
    </script>
    """
    
    st.markdown(input_container_html, unsafe_allow_html=True)
    
    # Create a container for the input that will be positioned at the bottom
    with st.container():
        # Add some space at the bottom for the fixed input
        st.markdown('<div style="height: 120px;"></div>', unsafe_allow_html=True)
        
        # Question input (this will be styled to appear fixed at bottom via CSS)
        col1, col2 = st.columns([5, 1])
        
        with col1:
            question = st.text_input(
                "question_input",
                placeholder="Type your question here...",
                label_visibility="collapsed",
                key="question_input"
            )
        
        with col2:
            ask_button = st.button("🚀 Ask", type="primary", use_container_width=True)
    
    # Process question
    if ask_button and question.strip():
        if not st.session_state.context.strip():
            st.error("⚠️ Please set a context first!")
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
            
            # Clear the question input and refresh
            st.rerun()
    
    # Auto-scroll to bottom when new message is added
    if st.session_state.qa_history:
        st.markdown("""
        <script>
        setTimeout(function() {
            window.scrollTo(0, document.body.scrollHeight);
        }, 100);
        </script>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem; margin-bottom: 140px;">
        Built with ❤️ using Streamlit and Hugging Face Transformers
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
