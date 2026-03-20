# Context Q&A Chatbot

A lightweight extractive question-answering app built with a fine-tuned DistilBERT model and a Streamlit interface. You paste any text as context, ask questions about it, and the model extracts the most relevant answer span directly from that text.

**Live demo**: [context-qna-chatbot.streamlit.app](https://context-qna-chatbot.streamlit.app)

---

## How it works

The app uses `distilbert-base-cased-distilled-squad`, a distilled version of BERT fine-tuned on the SQuAD dataset (Stanford Question Answering Dataset). Rather than generating answers, it performs **extractive QA** — it identifies the start and end token positions of the answer within the provided context. A confidence score is derived from the softmax probabilities of those positions.

This makes it fast, interpretable, and grounded: it will never hallucinate an answer that isn't in the text.

---

## Features

- Paste any text as context (articles, paragraphs, documents)
- Ask natural language questions about that context
- Answers returned with a confidence score (High / Medium / Low)
- Full session history with timestamps
- Warnings for low-confidence answers

---

## Run locally

```bash
git clone https://github.com/AnasOukhouya/context-qa-chatbot.git
cd context-qa-chatbot
pip install -r requirements.txt
streamlit run app.py
```

The model (~250MB) is downloaded automatically from Hugging Face on first run and cached locally.

---

## Stack

| Component | Library |
|---|---|
| QA Model | `distilbert-base-cased-distilled-squad` via Hugging Face Transformers |
| Inference | PyTorch (no-grad, CPU-compatible) |
| Interface | Streamlit |

---

## Known limitation

This is an extractive model — it can only return spans of text that exist verbatim in the context. It cannot synthesize, summarize, or answer questions that require reasoning beyond what is explicitly stated.
