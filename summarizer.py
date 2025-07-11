from transformers import pipeline

# Load BART summarizer pipeline
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def generate_summary(text):
    if len(text) < 200:
        return text  # skip summarization if text is too short
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
    return summary[0]['summary_text']
