from nltk.tokenize import sent_tokenize

from sentence_transformers import SentenceTransformer, util
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import pipeline

import app.parsers as parsers

SBERT_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
# Load Hugging Face summarization pipeline
ABSTRACTIVE_MODEL = pipeline("summarization", model="facebook/bart-large-cnn")


def get_text_from_file(ext: str, content: bytes):
    parser_func_name = f"parse_{ext}"
    if hasattr(parsers, parser_func_name):
        parser_func = getattr(parsers, parser_func_name)
        try:
            return parser_func(content)
        except Exception as e:
            raise ValueError(f"Failed to parse {ext} file: {str(e)}")
    else:
        raise ValueError(f"Unsupported file format: .{ext}")


def is_semantically_consistent(summary: str, source: str, threshold: float = 0.75) -> bool:
    summary_embedding = SBERT_MODEL.encode(summary, convert_to_tensor=True)
    source_embedding = SBERT_MODEL.encode(source, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(summary_embedding, source_embedding).item()
    return similarity >= threshold


# Extractive summarization (basic TF-IDF scoring)
def extractive_summary(text: str, num_sentences: int = 3) -> str:
    sentences = sent_tokenize(text)
    if len(sentences) <= num_sentences:
        return text
    vect = TfidfVectorizer().fit_transform(sentences)
    scores = vect.sum(axis=1).flatten().tolist()[0]
    ranked = sorted(list(zip(sentences, scores)), key=lambda x: x[1], reverse=True)
    return " ".join([s[0] for s in ranked[:num_sentences]])


# Abstractive summarization using Hugging Face
def abstractive_summary(text: str, max_tokens: int = 120) -> str:
    result = ABSTRACTIVE_MODEL(text[:1024], max_length=max_tokens, min_length=30, do_sample=False)
    return result[0]['summary_text']
