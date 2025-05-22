import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import streamlit as st
import warnings
warnings.filterwarnings("ignore")

@st.cache_resource
def load_qa_model(model_name="distilbert-base-cased-distilled-squad"):
    """
    Load and cache the QA model to avoid reloading on every interaction.
    
    Args:
        model_name (str): Name of the pre-trained model from Hugging Face Hub
        
    Returns:
        tuple: (tokenizer, model)
    """
    try:
        with st.spinner("🤖 Loading AI model... Please wait a moment."):
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForQuestionAnswering.from_pretrained(model_name)
            model.eval()
        return tokenizer, model
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None, None

class QAChatbot:
    def __init__(self, model_name="distilbert-base-cased-distilled-squad"):
        """
        Initialize the chatbot with a pre-trained QA model.
        
        Args:
            model_name (str): Name of the pre-trained model from Hugging Face Hub
        """
        self.model_name = model_name
        self.tokenizer, self.model = load_qa_model(model_name)
        
    def answer_question(self, context, question, max_answer_length=100):
        """
        Answer a question based on the given context.
        
        Args:
            context (str): The context/passage containing information
            question (str): The question to answer
            max_answer_length (int): Maximum length of the answer
            
        Returns:
            dict: Contains the answer, confidence score, and positions
        """
        if not self.tokenizer or not self.model:
            return {
                'answer': "Model not loaded properly. Please refresh the page.",
                'confidence': 0.0,
                'error': True
            }
        
        try:
            # Tokenize the input
            inputs = self.tokenizer.encode_plus(
                question,
                context,
                add_special_tokens=True,
                return_tensors="pt",
                max_length=512,
                truncation=True,
                padding=True
            )
            
            # Get model predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                start_logits = outputs.start_logits
                end_logits = outputs.end_logits
            
            # Find the best answer span
            start_idx = torch.argmax(start_logits)
            end_idx = torch.argmax(end_logits)
            
            # Ensure end comes after start and within reasonable length
            if end_idx < start_idx:
                end_idx = start_idx
            if end_idx - start_idx > max_answer_length:
                end_idx = start_idx + max_answer_length
            
            # Extract answer from tokens
            answer_tokens = inputs['input_ids'][0][start_idx:end_idx+1]
            answer = self.tokenizer.decode(answer_tokens, skip_special_tokens=True)
            
            # Calculate confidence score
            start_confidence = torch.softmax(start_logits, dim=-1)[0][start_idx].item()
            end_confidence = torch.softmax(end_logits, dim=-1)[0][end_idx].item()
            confidence = (start_confidence + end_confidence) / 2
            
            return {
                'answer': answer.strip() if answer.strip() else "I couldn't find a clear answer in the context.",
                'confidence': confidence,
                'start_position': start_idx.item(),
                'end_position': end_idx.item(),
                'error': False
            }
            
        except Exception as e:
            return {
                'answer': f"Error processing question: {str(e)}",
                'confidence': 0.0,
                'error': True
            }
    
    def get_confidence_color(self, confidence):
        """
        Get color code based on confidence level.
        
        Args:
            confidence (float): Confidence score between 0 and 1
            
        Returns:
            str: Color code for styling
        """
        if confidence >= 0.7:
            return "#28a745"  # Green
        elif confidence >= 0.4:
            return "#ffc107"  # Yellow
        else:
            return "#dc3545"  # Red
    
    def get_confidence_text(self, confidence):
        """
        Get confidence level text.
        
        Args:
            confidence (float): Confidence score between 0 and 1
            
        Returns:
            str: Confidence level description
        """
        if confidence >= 0.7:
            return "High"
        elif confidence >= 0.4:
            return "Medium"
        else:
            return "Low"
