"""Prompt templates for AI vision model inference."""

OCR_PROMPT = """Look at this scanned exam paper. Students wrote their answers directly on the paper.
Extract the handwritten answer for each question listed below.
The text may be in French, Arabic, or English.

Questions to extract: {question_list}

Return ONLY valid JSON, no other text:
{{"answers": [
  {{"question": <number>, "text": "<extracted text>"}},
  ...
]}}"""

EVALUATE_MODEL_ANSWER = """You are grading a student's answer.

{rag_examples}Question: {question_text}
Reference answer: {model_answer}
Student's answer: {student_text}
Maximum marks: {max_marks}

Grade the student's answer by comparing it to the reference.
Return ONLY valid JSON, no other text:
{{"score": <number>, "max": {max_marks}, "feedback": "<brief explanation>", "confidence": <0.0-1.0>}}"""

EVALUATE_KEYWORDS = """You are grading a student's answer.

{rag_examples}Question: {question_text}
Required concepts: {keywords_list}
Student's answer: {student_text}
Maximum marks: {max_marks}

Check which required concepts appear in the student's answer.
Return ONLY valid JSON, no other text:
{{"score": <number>, "max": {max_marks}, "found_concepts": [...], "missing_concepts": [...], "confidence": <0.0-1.0>}}"""

RAG_HEADER = """Here are examples of how this question was graded previously:
"""

RAG_EXAMPLE = """- Student wrote: "{student_text}" -> Score: {teacher_score}/{max_marks} because: {teacher_feedback}
"""

OCR_RETRY_PROMPT = """The previous response was not valid JSON. Please try again.
Extract the handwritten answers and return ONLY a JSON object like this:
{{"answers": [{{"question": 1, "text": "answer text"}}]}}"""
