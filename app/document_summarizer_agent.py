import nltk
from typing import Optional

from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse

from .config import LENGTH_MAP
from .helpers import is_semantically_consistent, get_text_from_file, extractive_summary, abstractive_summary


nltk.download('punkt')
app = FastAPI(title="AI Document Summarizer")


@app.post("/summarize")
async def summarize_document(
    file: UploadFile,
    summary_type: str = Form(...),
    length: str = Form(...),
    topics: Optional[str] = Form(None),
    check: Optional[bool] = Form(None)
):
    ext = file.filename.split(".")[-1].lower()
    content = await file.read()

    try:
        text = get_text_from_file(ext, content)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    if topics:
        topics = [t.strip() for t in topics.split(",")]
        topic_summaries = {}
        for topic in topics:
            segment = "\n".join([s for s in text.split("\n") if topic.lower() in s.lower()]) or text
            summary = extractive_summary(segment, num_sentences=3) if summary_type == "extractive" \
                else abstractive_summary(segment, max_tokens=LENGTH_MAP.get(length, 120))
            if check and summary_type == "abstractive" and not is_semantically_consistent(summary, segment):
                return JSONResponse({"error": f"Generated summary for topic '{topic}' may contain hallucinations."},
                                    status_code=422)
            topic_summaries[topic] = summary
        return topic_summaries
    else:
        summary = extractive_summary(text, num_sentences=3) if summary_type == "extractive" \
                  else abstractive_summary(text, max_tokens=LENGTH_MAP.get(length, 120))
        if check and summary_type == "abstractive" and not is_semantically_consistent(summary, text):
            return JSONResponse({"error": "Generated summary may contain hallucinations."},
                                status_code=422)
        return {"summary": summary}


@app.get("/")
def root():
    return {"message": "AI Document Summarizer is running."}
