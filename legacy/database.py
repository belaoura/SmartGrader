import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "smart_grader.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_database():
    """Initialize database with schema"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Read and execute schema.sql
    schema_path = os.path.join(BASE_DIR, "schema.sql")
    with open(schema_path, 'r') as f:
        schema = f.read()
        cursor.executescript(schema)
    
    conn.commit()
    conn.close()

# =========================
# EXAM OPERATIONS
# =========================

def insert_exam(title, subject, date=None, total_marks=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO exams (title, subject, date, total_marks)
        VALUES (?, ?, ?, ?)
    """, (title, subject, date, total_marks))
    conn.commit()
    exam_id = cur.lastrowid
    conn.close()
    return exam_id

def get_exams():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, subject, date, total_marks FROM exams ORDER BY id DESC")
    data = cur.fetchall()
    conn.close()
    return data

def get_exam_details(exam_id):
    """Get detailed information about a specific exam"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, subject, date, total_marks 
        FROM exams 
        WHERE id = ?
    """, (exam_id,))
    data = cur.fetchone()
    conn.close()
    return data

def update_exam(exam_id, title=None, subject=None, date=None, total_marks=None):
    """Update exam details"""
    conn = get_connection()
    cur = conn.cursor()
    
    updates = []
    params = []
    
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if subject is not None:
        updates.append("subject = ?")
        params.append(subject)
    if date is not None:
        updates.append("date = ?")
        params.append(date)
    if total_marks is not None:
        updates.append("total_marks = ?")
        params.append(total_marks)
    
    if updates:
        query = f"UPDATE exams SET {', '.join(updates)} WHERE id = ?"
        params.append(exam_id)
        cur.execute(query, params)
        conn.commit()
    
    conn.close()

def delete_exam(exam_id):
    """Delete an exam and all related data (cascade delete)"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
    conn.commit()
    conn.close()

# =========================
# QUESTION OPERATIONS
# =========================

def insert_question(exam_id, text, choices_number, marks):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO questions (exam_id, question_text, question_choices_number, marks)
        VALUES (?, ?, ?, ?)
    """, (exam_id, text, choices_number, marks))
    conn.commit()
    q_id = cur.lastrowid
    conn.close()
    return q_id

def get_questions_by_exam(exam_id):
    """Get all questions for a specific exam"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, question_text, question_choices_number, marks 
        FROM questions 
        WHERE exam_id = ?
        ORDER BY id
    """, (exam_id,))
    data = cur.fetchall()
    conn.close()
    return data

def update_question(question_id, text=None, marks=None):
    """Update a question's text and/or marks"""
    conn = get_connection()
    cur = conn.cursor()
    
    updates = []
    params = []
    
    if text is not None:
        updates.append("question_text = ?")
        params.append(text)
    
    if marks is not None:
        updates.append("marks = ?")
        params.append(marks)
    
    if updates:
        query = f"UPDATE questions SET {', '.join(updates)} WHERE id = ?"
        params.append(question_id)
        cur.execute(query, params)
        conn.commit()
    
    conn.close()

def delete_question(question_id):
    """Delete a question and all its choices (cascade delete)"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()

# =========================
# CHOICE OPERATIONS
# =========================

def insert_choice(question_id, label, text, is_correct):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO choices (question_id, choice_label, choice_text, is_correct)
        VALUES (?, ?, ?, ?)
    """, (question_id, label, text, is_correct))
    conn.commit()
    choice_id = cur.lastrowid
    conn.close()
    return choice_id

def get_choices_by_question(question_id):
    """Get all choices for a specific question"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, choice_label, choice_text, is_correct 
        FROM choices 
        WHERE question_id = ?
        ORDER BY choice_label
    """, (question_id,))
    data = cur.fetchall()
    conn.close()
    return data

def update_choice(choice_id, text=None, is_correct=None):
    """Update a choice's text and/or correct status"""
    conn = get_connection()
    cur = conn.cursor()
    
    updates = []
    params = []
    
    if text is not None:
        updates.append("choice_text = ?")
        params.append(text)
    
    if is_correct is not None:
        updates.append("is_correct = ?")
        params.append(is_correct)
    
    if updates:
        query = f"UPDATE choices SET {', '.join(updates)} WHERE id = ?"
        params.append(choice_id)
        cur.execute(query, params)
        conn.commit()
    
    conn.close()

def delete_choice(choice_id):
    """Delete a specific choice"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM choices WHERE id = ?", (choice_id,))
    conn.commit()
    conn.close()

# =========================
# STUDENT OPERATIONS
# =========================

def insert_student(name, matricule, email=None):
    """Insert a new student"""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO students (name, matricule, email)
            VALUES (?, ?, ?)
        """, (name, matricule, email))
        conn.commit()
        student_id = cur.lastrowid
        conn.close()
        return student_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_students():
    """Get all students"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, matricule, email FROM students ORDER BY name")
    data = cur.fetchall()
    conn.close()
    return data

def get_student_by_matricule(matricule):
    """Get student by matricule"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, matricule, email FROM students WHERE matricule = ?", (matricule,))
    data = cur.fetchone()
    conn.close()
    return data

# =========================
# ANSWER OPERATIONS
# =========================

def insert_student_answer(student_id, question_id, selected_choice_id):
    """Insert or update a student's answer"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Check if answer already exists
    cur.execute("""
        SELECT id FROM student_answers 
        WHERE student_id = ? AND question_id = ?
    """, (student_id, question_id))
    
    existing = cur.fetchone()
    
    if existing:
        # Update existing answer
        cur.execute("""
            UPDATE student_answers 
            SET selected_choice_id = ? 
            WHERE student_id = ? AND question_id = ?
        """, (selected_choice_id, student_id, question_id))
    else:
        # Insert new answer
        cur.execute("""
            INSERT INTO student_answers (student_id, question_id, selected_choice_id)
            VALUES (?, ?, ?)
        """, (student_id, question_id, selected_choice_id))
    
    conn.commit()
    conn.close()

def get_student_answers(student_id, exam_id):
    """Get all answers for a student in an exam"""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT sa.question_id, sa.selected_choice_id, c.is_correct, q.marks
        FROM student_answers sa
        JOIN questions q ON sa.question_id = q.id
        LEFT JOIN choices c ON sa.selected_choice_id = c.id
        WHERE sa.student_id = ? AND q.exam_id = ?
    """, (student_id, exam_id))
    data = cur.fetchall()
    conn.close()
    return data

# =========================
# RESULT OPERATIONS
# =========================

def calculate_and_save_result(student_id, exam_id):
    """Calculate student's score and save result"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Get all questions for the exam
    cur.execute("""
        SELECT q.id, q.marks
        FROM questions q
        WHERE q.exam_id = ?
    """, (exam_id,))
    
    questions = cur.fetchall()
    total_marks = sum(q[1] for q in questions)
    obtained_marks = 0
    
    # Get student's answers and check correctness
    for question in questions:
        cur.execute("""
            SELECT c.is_correct
            FROM student_answers sa
            JOIN choices c ON sa.selected_choice_id = c.id
            WHERE sa.student_id = ? AND sa.question_id = ?
        """, (student_id, question[0]))
        
        answer = cur.fetchone()
        if answer and answer[0] == 1:  # If answer is correct
            obtained_marks += question[1]
    
    # Calculate percentage
    percentage = (obtained_marks / total_marks * 100) if total_marks > 0 else 0
    
    # Insert or update result
    cur.execute("""
        INSERT OR REPLACE INTO results (student_id, exam_id, score, percentage, graded_at)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, (student_id, exam_id, obtained_marks, percentage))
    
    conn.commit()
    conn.close()
    
    return obtained_marks, percentage

def get_results(exam_id=None):
    """Get results, optionally filtered by exam"""
    conn = get_connection()
    cur = conn.cursor()
    
    if exam_id:
        cur.execute("""
            SELECT r.id, s.name, s.matricule, e.title, r.score, r.percentage, r.graded_at
            FROM results r
            JOIN students s ON r.student_id = s.id
            JOIN exams e ON r.exam_id = e.id
            WHERE r.exam_id = ?
            ORDER BY r.percentage DESC
        """, (exam_id,))
    else:
        cur.execute("""
            SELECT r.id, s.name, s.matricule, e.title, r.score, r.percentage, r.graded_at
            FROM results r
            JOIN students s ON r.student_id = s.id
            JOIN exams e ON r.exam_id = e.id
            ORDER BY r.graded_at DESC
        """)
    
    data = cur.fetchall()
    conn.close()
    return data

# =========================
# COMPREHENSIVE QUERIES
# =========================

def get_questions_with_choices():
    """Get all questions with their choices (for display)"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Get all questions with exam info
    cur.execute("""
        SELECT q.id, q.exam_id, q.question_text, 
               q.question_choices_number, q.marks, e.title as exam_title
        FROM questions q
        JOIN exams e ON q.exam_id = e.id
        ORDER BY q.exam_id, q.id
    """)
    
    questions = cur.fetchall()
    result = []
    
    for q in questions:
        # Get choices for this question
        cur.execute("""
            SELECT id, choice_label, choice_text, is_correct
            FROM choices
            WHERE question_id = ?
            ORDER BY choice_label
        """, (q[0],))
        
        choices = cur.fetchall()
        
        result.append({
            'question_id': q[0],
            'exam_id': q[1],
            'question_text': q[2],
            'choices_number': q[3],
            'marks': q[4],
            'exam_name': q[5],
            'choices': [{'id': c[0], 'label': c[1], 'text': c[2], 'is_correct': c[3]} for c in choices]
        })
    
    conn.close()
    return result

def get_question_details(question_id):
    """Get detailed information about a specific question with its choices"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Get question details
    cur.execute("""
        SELECT q.id, q.exam_id, q.question_text, 
               q.question_choices_number, q.marks, e.title as exam_title
        FROM questions q
        JOIN exams e ON q.exam_id = e.id
        WHERE q.id = ?
    """, (question_id,))
    
    question = cur.fetchone()
    
    if not question:
        conn.close()
        return None
    
    # Get choices for this question
    cur.execute("""
        SELECT id, choice_label, choice_text, is_correct
        FROM choices
        WHERE question_id = ?
        ORDER BY choice_label
    """, (question_id,))
    
    choices = cur.fetchall()
    
    conn.close()
    
    return {
        'question_id': question[0],
        'exam_id': question[1],
        'question_text': question[2],
        'choices_number': question[3],
        'marks': question[4],
        'exam_name': question[5],
        'choices': [{'id': c[0], 'label': c[1], 'text': c[2], 'is_correct': c[3]} for c in choices]
    }

def search_questions(search_term):
    """Search questions by text content"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT q.id, q.exam_id, q.question_text, 
               q.marks, e.title as exam_title
        FROM questions q
        JOIN exams e ON q.exam_id = e.id
        WHERE q.question_text LIKE ?
        ORDER BY q.exam_id, q.id
    """, (f'%{search_term}%',))
    
    questions = cur.fetchall()
    result = []
    
    for q in questions:
        # Get choices for each question
        cur.execute("""
            SELECT id, choice_label, choice_text, is_correct
            FROM choices
            WHERE question_id = ?
            ORDER BY choice_label
        """, (q[0],))
        
        choices = cur.fetchall()
        
        result.append({
            'question_id': q[0],
            'exam_id': q[1],
            'question_text': q[2],
            'marks': q[3],
            'exam_name': q[4],
            'choices': [{'id': c[0], 'label': c[1], 'text': c[2], 'is_correct': c[3]} for c in choices]
        })
    
    conn.close()
    return result

def get_exam_statistics(exam_id):
    """Get statistics about an exam"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Question statistics
    cur.execute("""
        SELECT 
            COUNT(*) as question_count,
            SUM(marks) as total_marks,
            AVG(marks) as average_marks
        FROM questions
        WHERE exam_id = ?
    """, (exam_id,))
    
    stats = cur.fetchone()
    
    # Student participation
    cur.execute("""
        SELECT COUNT(DISTINCT student_id) as student_count
        FROM results
        WHERE exam_id = ?
    """, (exam_id,))
    
    participation = cur.fetchone()
    
    # Average score
    cur.execute("""
        SELECT AVG(percentage) as avg_percentage
        FROM results
        WHERE exam_id = ?
    """, (exam_id,))
    
    avg_score = cur.fetchone()
    
    conn.close()
    
    return {
        'question_count': stats[0] or 0,
        'total_marks': stats[1] or 0,
        'average_marks': stats[2] or 0,
        'student_count': participation[0] or 0,
        'average_score': avg_score[0] or 0
    }

# Initialize database when module is imported
if not os.path.exists(DB_PATH):
    init_database()