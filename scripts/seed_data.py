"""Seed database with sample data for development.

Usage: python -m scripts.seed_data
"""

import os
import sys
import random
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import db
from app.services.exam_service import create_exam, create_question_with_choices
from app.models.student import Student
from app.models.result import Result
from app.models.exam import Exam


EXAMS = [
    {
        "title": "Mathematics - Algebra",
        "subject": "Mathematics",
        "total_marks": 20,
        "questions": [
            {"text": "What is 2 + 2?", "marks": 5, "choices": [
                {"label": "A", "text": "3", "is_correct": False},
                {"label": "B", "text": "4", "is_correct": True},
                {"label": "C", "text": "5", "is_correct": False},
                {"label": "D", "text": "6", "is_correct": False},
            ]},
            {"text": "What is 5 x 3?", "marks": 5, "choices": [
                {"label": "A", "text": "8", "is_correct": False},
                {"label": "B", "text": "15", "is_correct": True},
                {"label": "C", "text": "20", "is_correct": False},
            ]},
            {"text": "Solve: x + 3 = 7", "marks": 5, "choices": [
                {"label": "A", "text": "x = 3", "is_correct": False},
                {"label": "B", "text": "x = 4", "is_correct": True},
                {"label": "C", "text": "x = 10", "is_correct": False},
                {"label": "D", "text": "x = 7", "is_correct": False},
            ]},
            {"text": "What is the square root of 16?", "marks": 5, "choices": [
                {"label": "A", "text": "2", "is_correct": False},
                {"label": "B", "text": "4", "is_correct": True},
                {"label": "C", "text": "8", "is_correct": False},
            ]},
        ],
    },
    {
        "title": "Biology - Cell Biology",
        "subject": "Biology",
        "total_marks": 20,
        "questions": [
            {"text": "What is the powerhouse of the cell?", "marks": 4, "choices": [
                {"label": "A", "text": "Nucleus", "is_correct": False},
                {"label": "B", "text": "Mitochondria", "is_correct": True},
                {"label": "C", "text": "Ribosome", "is_correct": False},
                {"label": "D", "text": "Golgi apparatus", "is_correct": False},
            ]},
            {"text": "Which organelle contains DNA?", "marks": 4, "choices": [
                {"label": "A", "text": "Nucleus", "is_correct": True},
                {"label": "B", "text": "Lysosome", "is_correct": False},
                {"label": "C", "text": "Vacuole", "is_correct": False},
            ]},
            {"text": "What is the function of ribosomes?", "marks": 4, "choices": [
                {"label": "A", "text": "Energy production", "is_correct": False},
                {"label": "B", "text": "Protein synthesis", "is_correct": True},
                {"label": "C", "text": "Cell division", "is_correct": False},
                {"label": "D", "text": "Waste removal", "is_correct": False},
            ]},
            {"text": "Cell membrane is made of:", "marks": 4, "choices": [
                {"label": "A", "text": "Carbohydrates", "is_correct": False},
                {"label": "B", "text": "Phospholipid bilayer", "is_correct": True},
                {"label": "C", "text": "Cellulose", "is_correct": False},
            ]},
            {"text": "Which process converts glucose to energy?", "marks": 4, "choices": [
                {"label": "A", "text": "Photosynthesis", "is_correct": False},
                {"label": "B", "text": "Cellular respiration", "is_correct": True},
                {"label": "C", "text": "Fermentation", "is_correct": False},
                {"label": "D", "text": "Osmosis", "is_correct": False},
            ]},
        ],
    },
    {
        "title": "Physics - Mechanics",
        "subject": "Physics",
        "total_marks": 25,
        "questions": [
            {"text": "Newton's first law describes:", "marks": 5, "choices": [
                {"label": "A", "text": "Inertia", "is_correct": True},
                {"label": "B", "text": "Acceleration", "is_correct": False},
                {"label": "C", "text": "Action-reaction", "is_correct": False},
            ]},
            {"text": "F = ma is Newton's ___ law", "marks": 5, "choices": [
                {"label": "A", "text": "First", "is_correct": False},
                {"label": "B", "text": "Second", "is_correct": True},
                {"label": "C", "text": "Third", "is_correct": False},
                {"label": "D", "text": "Fourth", "is_correct": False},
            ]},
            {"text": "Unit of force is:", "marks": 5, "choices": [
                {"label": "A", "text": "Joule", "is_correct": False},
                {"label": "B", "text": "Newton", "is_correct": True},
                {"label": "C", "text": "Watt", "is_correct": False},
            ]},
            {"text": "Acceleration due to gravity is approximately:", "marks": 5, "choices": [
                {"label": "A", "text": "9.8 m/s\u00b2", "is_correct": True},
                {"label": "B", "text": "10.2 m/s\u00b2", "is_correct": False},
                {"label": "C", "text": "8.5 m/s\u00b2", "is_correct": False},
                {"label": "D", "text": "11.0 m/s\u00b2", "is_correct": False},
            ]},
            {"text": "Work is defined as:", "marks": 5, "choices": [
                {"label": "A", "text": "Force \u00d7 Distance", "is_correct": True},
                {"label": "B", "text": "Mass \u00d7 Velocity", "is_correct": False},
                {"label": "C", "text": "Power \u00d7 Time", "is_correct": False},
            ]},
        ],
    },
    {
        "title": "Chemistry - Organic",
        "subject": "Chemistry",
        "total_marks": 20,
        "questions": [
            {"text": "Carbon can form how many bonds?", "marks": 5, "choices": [
                {"label": "A", "text": "2", "is_correct": False},
                {"label": "B", "text": "4", "is_correct": True},
                {"label": "C", "text": "6", "is_correct": False},
            ]},
            {"text": "Methane's formula is:", "marks": 5, "choices": [
                {"label": "A", "text": "CH4", "is_correct": True},
                {"label": "B", "text": "C2H6", "is_correct": False},
                {"label": "C", "text": "CO2", "is_correct": False},
                {"label": "D", "text": "C2H4", "is_correct": False},
            ]},
            {"text": "An alcohol contains which functional group?", "marks": 5, "choices": [
                {"label": "A", "text": "-OH", "is_correct": True},
                {"label": "B", "text": "-COOH", "is_correct": False},
                {"label": "C", "text": "-NH2", "is_correct": False},
            ]},
            {"text": "Benzene has how many carbon atoms?", "marks": 5, "choices": [
                {"label": "A", "text": "4", "is_correct": False},
                {"label": "B", "text": "6", "is_correct": True},
                {"label": "C", "text": "8", "is_correct": False},
                {"label": "D", "text": "12", "is_correct": False},
            ]},
        ],
    },
    {
        "title": "Computer Science - Algorithms",
        "subject": "Computer Science",
        "total_marks": 25,
        "questions": [
            {"text": "Time complexity of binary search:", "marks": 5, "choices": [
                {"label": "A", "text": "O(n)", "is_correct": False},
                {"label": "B", "text": "O(log n)", "is_correct": True},
                {"label": "C", "text": "O(n\u00b2)", "is_correct": False},
                {"label": "D", "text": "O(1)", "is_correct": False},
            ]},
            {"text": "Which data structure uses FIFO?", "marks": 5, "choices": [
                {"label": "A", "text": "Stack", "is_correct": False},
                {"label": "B", "text": "Queue", "is_correct": True},
                {"label": "C", "text": "Array", "is_correct": False},
            ]},
            {"text": "A stack uses which principle?", "marks": 5, "choices": [
                {"label": "A", "text": "FIFO", "is_correct": False},
                {"label": "B", "text": "LIFO", "is_correct": True},
                {"label": "C", "text": "Random", "is_correct": False},
                {"label": "D", "text": "Priority", "is_correct": False},
            ]},
            {"text": "Worst case of bubble sort:", "marks": 5, "choices": [
                {"label": "A", "text": "O(n)", "is_correct": False},
                {"label": "B", "text": "O(n log n)", "is_correct": False},
                {"label": "C", "text": "O(n\u00b2)", "is_correct": True},
            ]},
            {"text": "Which is a divide-and-conquer algorithm?", "marks": 5, "choices": [
                {"label": "A", "text": "Bubble sort", "is_correct": False},
                {"label": "B", "text": "Merge sort", "is_correct": True},
                {"label": "C", "text": "Insertion sort", "is_correct": False},
                {"label": "D", "text": "Selection sort", "is_correct": False},
            ]},
        ],
    },
    {
        "title": "English - Grammar & Vocabulary",
        "subject": "English",
        "total_marks": 32,
        "questions": [
            {"text": "Which word is a noun in the sentence: 'The quick fox jumps over the lazy dog'?", "marks": 2, "choices": [
                {"label": "A", "text": "quick", "is_correct": False},
                {"label": "B", "text": "fox", "is_correct": True},
                {"label": "C", "text": "jumps", "is_correct": False},
                {"label": "D", "text": "lazy", "is_correct": False},
            ]},
            {"text": "Choose the correct past tense of 'go':", "marks": 2, "choices": [
                {"label": "A", "text": "goed", "is_correct": False},
                {"label": "B", "text": "gone", "is_correct": False},
                {"label": "C", "text": "went", "is_correct": True},
                {"label": "D", "text": "going", "is_correct": False},
            ]},
            {"text": "What part of speech is the word 'beautiful'?", "marks": 2, "choices": [
                {"label": "A", "text": "Noun", "is_correct": False},
                {"label": "B", "text": "Verb", "is_correct": False},
                {"label": "C", "text": "Adjective", "is_correct": True},
                {"label": "D", "text": "Adverb", "is_correct": False},
            ]},
            {"text": "Which sentence uses the present perfect tense correctly?", "marks": 2, "choices": [
                {"label": "A", "text": "She go to the market yesterday.", "is_correct": False},
                {"label": "B", "text": "She has gone to the market.", "is_correct": True},
                {"label": "C", "text": "She will go to the market.", "is_correct": False},
                {"label": "D", "text": "She going to the market.", "is_correct": False},
            ]},
            {"text": "What is the synonym of 'happy'?", "marks": 2, "choices": [
                {"label": "A", "text": "Sad", "is_correct": False},
                {"label": "B", "text": "Angry", "is_correct": False},
                {"label": "C", "text": "Joyful", "is_correct": True},
                {"label": "D", "text": "Tired", "is_correct": False},
            ]},
            {"text": "Identify the verb in: 'The students studied hard for the exam.'", "marks": 2, "choices": [
                {"label": "A", "text": "students", "is_correct": False},
                {"label": "B", "text": "hard", "is_correct": False},
                {"label": "C", "text": "exam", "is_correct": False},
                {"label": "D", "text": "studied", "is_correct": True},
            ]},
            {"text": "Which word correctly completes: 'She sings _____ than her sister.'?", "marks": 2, "choices": [
                {"label": "A", "text": "more beautifully", "is_correct": True},
                {"label": "B", "text": "most beautifully", "is_correct": False},
                {"label": "C", "text": "beautifuller", "is_correct": False},
                {"label": "D", "text": "beautifullier", "is_correct": False},
            ]},
            {"text": "What is the antonym of 'ancient'?", "marks": 2, "choices": [
                {"label": "A", "text": "Old", "is_correct": False},
                {"label": "B", "text": "Historic", "is_correct": False},
                {"label": "C", "text": "Modern", "is_correct": True},
                {"label": "D", "text": "Classical", "is_correct": False},
            ]},
            {"text": "Which sentence is in passive voice?", "marks": 2, "choices": [
                {"label": "A", "text": "The chef cooked the meal.", "is_correct": False},
                {"label": "B", "text": "The meal was cooked by the chef.", "is_correct": True},
                {"label": "C", "text": "The chef is cooking the meal.", "is_correct": False},
                {"label": "D", "text": "The chef will cook the meal.", "is_correct": False},
            ]},
            {"text": "What does the word 'benevolent' mean?", "marks": 2, "choices": [
                {"label": "A", "text": "Cruel and harsh", "is_correct": False},
                {"label": "B", "text": "Kind and generous", "is_correct": True},
                {"label": "C", "text": "Lazy and careless", "is_correct": False},
                {"label": "D", "text": "Loud and boisterous", "is_correct": False},
            ]},
            {"text": "Choose the correct article: '___ university is a place of learning.'", "marks": 2, "choices": [
                {"label": "A", "text": "A", "is_correct": True},
                {"label": "B", "text": "An", "is_correct": False},
                {"label": "C", "text": "The", "is_correct": False},
                {"label": "D", "text": "No article needed", "is_correct": False},
            ]},
            {"text": "Which of the following is a compound sentence?", "marks": 2, "choices": [
                {"label": "A", "text": "She runs every morning.", "is_correct": False},
                {"label": "B", "text": "Because it rained, we stayed home.", "is_correct": False},
                {"label": "C", "text": "He studied hard, and he passed the exam.", "is_correct": True},
                {"label": "D", "text": "The tall, dark stranger arrived.", "is_correct": False},
            ]},
            {"text": "What is the plural form of 'criterion'?", "marks": 2, "choices": [
                {"label": "A", "text": "criterions", "is_correct": False},
                {"label": "B", "text": "criterias", "is_correct": False},
                {"label": "C", "text": "criteria", "is_correct": True},
                {"label": "D", "text": "criterium", "is_correct": False},
            ]},
            {"text": "Identify the preposition in: 'The book is on the table.'", "marks": 2, "choices": [
                {"label": "A", "text": "book", "is_correct": False},
                {"label": "B", "text": "is", "is_correct": False},
                {"label": "C", "text": "on", "is_correct": True},
                {"label": "D", "text": "table", "is_correct": False},
            ]},
            {"text": "Which sentence contains a grammatical error?", "marks": 2, "choices": [
                {"label": "A", "text": "They are going to the park.", "is_correct": False},
                {"label": "B", "text": "She don't like coffee.", "is_correct": True},
                {"label": "C", "text": "We have finished our work.", "is_correct": False},
                {"label": "D", "text": "He was tired after the race.", "is_correct": False},
            ]},
            {"text": "What is the meaning of the idiom 'break the ice'?", "marks": 2, "choices": [
                {"label": "A", "text": "To literally crack frozen water", "is_correct": False},
                {"label": "B", "text": "To cause an accident", "is_correct": False},
                {"label": "C", "text": "To initiate conversation in an awkward situation", "is_correct": True},
                {"label": "D", "text": "To end a friendship", "is_correct": False},
            ]},
        ],
    },
    {
        "title": "History - World History",
        "subject": "History",
        "total_marks": 40,
        "questions": [
            {"text": "Which ancient civilization built the Great Pyramids of Giza?", "marks": 2, "choices": [
                {"label": "A", "text": "Mesopotamian", "is_correct": False},
                {"label": "B", "text": "Egyptian", "is_correct": True},
                {"label": "C", "text": "Greek", "is_correct": False},
                {"label": "D", "text": "Roman", "is_correct": False},
            ]},
            {"text": "The French Revolution began in which year?", "marks": 2, "choices": [
                {"label": "A", "text": "1776", "is_correct": False},
                {"label": "B", "text": "1789", "is_correct": True},
                {"label": "C", "text": "1804", "is_correct": False},
                {"label": "D", "text": "1815", "is_correct": False},
            ]},
            {"text": "Who was the first Emperor of unified China?", "marks": 2, "choices": [
                {"label": "A", "text": "Confucius", "is_correct": False},
                {"label": "B", "text": "Sun Tzu", "is_correct": False},
                {"label": "C", "text": "Qin Shi Huang", "is_correct": True},
                {"label": "D", "text": "Kublai Khan", "is_correct": False},
            ]},
            {"text": "World War I started in which year?", "marks": 2, "choices": [
                {"label": "A", "text": "1912", "is_correct": False},
                {"label": "B", "text": "1914", "is_correct": True},
                {"label": "C", "text": "1916", "is_correct": False},
                {"label": "D", "text": "1918", "is_correct": False},
            ]},
            {"text": "The Magna Carta was signed in:", "marks": 2, "choices": [
                {"label": "A", "text": "1066", "is_correct": False},
                {"label": "B", "text": "1215", "is_correct": True},
                {"label": "C", "text": "1415", "is_correct": False},
                {"label": "D", "text": "1603", "is_correct": False},
            ]},
            {"text": "Which empire was ruled by Genghis Khan?", "marks": 2, "choices": [
                {"label": "A", "text": "Ottoman Empire", "is_correct": False},
                {"label": "B", "text": "Roman Empire", "is_correct": False},
                {"label": "C", "text": "Mongol Empire", "is_correct": True},
                {"label": "D", "text": "Persian Empire", "is_correct": False},
            ]},
            {"text": "The American Declaration of Independence was adopted in:", "marks": 2, "choices": [
                {"label": "A", "text": "1774", "is_correct": False},
                {"label": "B", "text": "1775", "is_correct": False},
                {"label": "C", "text": "1776", "is_correct": True},
                {"label": "D", "text": "1783", "is_correct": False},
            ]},
            {"text": "Which ancient Greek city-state was known for its military culture?", "marks": 2, "choices": [
                {"label": "A", "text": "Athens", "is_correct": False},
                {"label": "B", "text": "Corinth", "is_correct": False},
                {"label": "C", "text": "Sparta", "is_correct": True},
                {"label": "D", "text": "Thebes", "is_correct": False},
            ]},
            {"text": "The Renaissance period originated in which country?", "marks": 2, "choices": [
                {"label": "A", "text": "France", "is_correct": False},
                {"label": "B", "text": "England", "is_correct": False},
                {"label": "C", "text": "Italy", "is_correct": True},
                {"label": "D", "text": "Spain", "is_correct": False},
            ]},
            {"text": "World War II ended in Europe in which year?", "marks": 2, "choices": [
                {"label": "A", "text": "1943", "is_correct": False},
                {"label": "B", "text": "1944", "is_correct": False},
                {"label": "C", "text": "1945", "is_correct": True},
                {"label": "D", "text": "1946", "is_correct": False},
            ]},
            {"text": "The Industrial Revolution first began in:", "marks": 2, "choices": [
                {"label": "A", "text": "France", "is_correct": False},
                {"label": "B", "text": "Germany", "is_correct": False},
                {"label": "C", "text": "Great Britain", "is_correct": True},
                {"label": "D", "text": "United States", "is_correct": False},
            ]},
            {"text": "Which civilization developed the first writing system (cuneiform)?", "marks": 2, "choices": [
                {"label": "A", "text": "Egyptian", "is_correct": False},
                {"label": "B", "text": "Sumerian", "is_correct": True},
                {"label": "C", "text": "Chinese", "is_correct": False},
                {"label": "D", "text": "Indus Valley", "is_correct": False},
            ]},
            {"text": "The Cold War was primarily between which two superpowers?", "marks": 2, "choices": [
                {"label": "A", "text": "USA and China", "is_correct": False},
                {"label": "B", "text": "USA and USSR", "is_correct": True},
                {"label": "C", "text": "UK and USSR", "is_correct": False},
                {"label": "D", "text": "USA and Germany", "is_correct": False},
            ]},
            {"text": "Napoleon Bonaparte was exiled to which island after Waterloo?", "marks": 2, "choices": [
                {"label": "A", "text": "Elba", "is_correct": False},
                {"label": "B", "text": "Corsica", "is_correct": False},
                {"label": "C", "text": "Saint Helena", "is_correct": True},
                {"label": "D", "text": "Madagascar", "is_correct": False},
            ]},
            {"text": "The Roman Republic transitioned to an Empire under:", "marks": 2, "choices": [
                {"label": "A", "text": "Julius Caesar", "is_correct": False},
                {"label": "B", "text": "Augustus Caesar", "is_correct": True},
                {"label": "C", "text": "Marcus Aurelius", "is_correct": False},
                {"label": "D", "text": "Nero", "is_correct": False},
            ]},
            {"text": "The Berlin Wall fell in:", "marks": 2, "choices": [
                {"label": "A", "text": "1987", "is_correct": False},
                {"label": "B", "text": "1989", "is_correct": True},
                {"label": "C", "text": "1991", "is_correct": False},
                {"label": "D", "text": "1993", "is_correct": False},
            ]},
            {"text": "Which explorer is credited with first reaching the Americas in 1492?", "marks": 2, "choices": [
                {"label": "A", "text": "Vasco da Gama", "is_correct": False},
                {"label": "B", "text": "Ferdinand Magellan", "is_correct": False},
                {"label": "C", "text": "Christopher Columbus", "is_correct": True},
                {"label": "D", "text": "Amerigo Vespucci", "is_correct": False},
            ]},
            {"text": "The Algerian War of Independence ended in:", "marks": 2, "choices": [
                {"label": "A", "text": "1958", "is_correct": False},
                {"label": "B", "text": "1960", "is_correct": False},
                {"label": "C", "text": "1962", "is_correct": True},
                {"label": "D", "text": "1965", "is_correct": False},
            ]},
            {"text": "The United Nations was founded after which world event?", "marks": 2, "choices": [
                {"label": "A", "text": "World War I", "is_correct": False},
                {"label": "B", "text": "World War II", "is_correct": True},
                {"label": "C", "text": "The Cold War", "is_correct": False},
                {"label": "D", "text": "The Korean War", "is_correct": False},
            ]},
            {"text": "Which revolution in Russia in 1917 led to the establishment of the Soviet Union?", "marks": 2, "choices": [
                {"label": "A", "text": "The February Revolution", "is_correct": False},
                {"label": "B", "text": "The October Revolution", "is_correct": True},
                {"label": "C", "text": "The Bolshevik Uprising", "is_correct": False},
                {"label": "D", "text": "The Tsarist Revolt", "is_correct": False},
            ]},
        ],
    },
]

STUDENTS = [
    {"name": "Ahmed Benali", "matricule": "2026001", "email": "ahmed@univ.dz"},
    {"name": "Fatima Zahra", "matricule": "2026002", "email": "fatima@univ.dz"},
    {"name": "Mohamed Amine", "matricule": "2026003", "email": "amine@univ.dz"},
    {"name": "Amina Boudiaf", "matricule": "2026004", "email": "amina@univ.dz"},
    {"name": "Youcef Khelifi", "matricule": "2026005", "email": "youcef@univ.dz"},
    {"name": "Sara Mebarki", "matricule": "2026006", "email": "sara@univ.dz"},
    {"name": "Rachid Hamidi", "matricule": "2026007", "email": "rachid@univ.dz"},
    {"name": "Nour El Houda", "matricule": "2026008", "email": "nour@univ.dz"},
    {"name": "Karim Zidane", "matricule": "2026009", "email": "karim@univ.dz"},
    {"name": "Lina Benmoussa", "matricule": "2026010", "email": "lina@univ.dz"},
]


def seed():
    """Insert sample data if not already present."""
    app = create_app("development")

    with app.app_context():
        db.create_all()

        # Seed exams and questions
        created_exams = []
        for exam_data in EXAMS:
            existing = Exam.query.filter_by(title=exam_data["title"]).first()
            if existing:
                print(f"  Exam '{exam_data['title']}' already exists, skipping")
                created_exams.append(existing)
                continue

            exam = create_exam(
                title=exam_data["title"],
                subject=exam_data["subject"],
                date="2026-04-06",
                total_marks=exam_data["total_marks"],
            )
            for q in exam_data["questions"]:
                create_question_with_choices(
                    exam_id=exam.id,
                    question_text=q["text"],
                    marks=q["marks"],
                    choices=q["choices"],
                )
            created_exams.append(exam)
            print(f"  Created exam: {exam_data['title']} ({len(exam_data['questions'])} questions)")

        # Seed students
        created_students = []
        for s in STUDENTS:
            existing = Student.query.filter_by(matricule=s["matricule"]).first()
            if existing:
                created_students.append(existing)
                continue
            student = Student(name=s["name"], matricule=s["matricule"], email=s["email"])
            db.session.add(student)
            created_students.append(student)
        db.session.commit()
        print(f"  Students: {len(created_students)} total")

        # Seed results
        random.seed(42)
        results_count = 0
        for exam in created_exams:
            existing_results = Result.query.filter_by(exam_id=exam.id).count()
            if existing_results > 0:
                print(f"  Results for '{exam.title}' already exist, skipping")
                continue

            num_students = random.randint(6, min(8, len(created_students)))
            selected = random.sample(created_students, num_students)

            for student in selected:
                score_pct = random.uniform(0.45, 1.0)
                score = round(exam.total_marks * score_pct, 1)
                percentage = round(score_pct * 100, 1)
                result = Result(
                    student_id=student.id,
                    exam_id=exam.id,
                    score=score,
                    percentage=percentage,
                    graded_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
                db.session.add(result)
                results_count += 1

        db.session.commit()
        print(f"  Results: {results_count} new results seeded")
        print(f"\nDone: {len(EXAMS)} exams, {len(STUDENTS)} students, {results_count} results")

        # --- Online exam seeding ---

        # 1. Create teacher user accounts
        from app.services.auth_service import create_teacher
        teachers_created = 0
        try:
            create_teacher(
                email="admin@smartgrader.dz",
                password="admin12345",
                name="Admin Teacher",
                is_admin=True,
            )
            teachers_created += 1
        except Exception:
            pass  # already exists

        try:
            create_teacher(
                email="teacher@smartgrader.dz",
                password="teacher123",
                name="Regular Teacher",
                is_admin=False,
            )
            teachers_created += 1
        except Exception:
            pass  # already exists

        print(f"  Created {teachers_created} teacher accounts (skipped if already exist)")

        # 2. Create User records for each seeded student
        from app.models.user import User
        student_users_created = 0
        for student in Student.query.all():
            existing = User.query.filter_by(student_id=student.id).first()
            if not existing:
                user = User(role="student", student_id=student.id)
                db.session.add(user)
                student_users_created += 1
        db.session.commit()
        print(f"  Created {student_users_created} student user accounts")

        # 3. Create 2 student groups
        from app.models.group import StudentGroup, StudentGroupMember
        from app.services.group_service import create_group, add_members

        students = Student.query.all()
        group_a_existing = StudentGroup.query.filter_by(name="CS Year 3 - Group A").first()
        group_b_existing = StudentGroup.query.filter_by(name="CS Year 3 - Group B").first()

        group_a = group_a_existing or create_group("CS Year 3 - Group A")
        group_b = group_b_existing or create_group("CS Year 3 - Group B")

        if not group_a_existing:
            add_members(group_a.id, [s.id for s in students[:5]])
        if not group_b_existing:
            add_members(group_b.id, [s.id for s in students[5:]])

        groups_created = (0 if group_a_existing else 1) + (0 if group_b_existing else 1)
        print(f"  Created {groups_created} student groups (Group A: 5 students, Group B: 5 students)")

        # 4. Create 3 exam sessions with different configurations
        from datetime import datetime, timezone, timedelta
        from app.services.session_service import create_session, assign_students
        from app.models.exam_session import ExamSession

        now = datetime.now(timezone.utc)

        # Session 1: Active session with proctoring (exam 1)
        s1_existing = ExamSession.query.filter_by(exam_id=1).first()
        if not s1_existing:
            s1 = create_session(
                exam_id=1,
                start_time=(now - timedelta(minutes=30)).isoformat(),
                end_time=(now + timedelta(hours=2)).isoformat(),
                display_mode="one_by_one", save_mode="auto_each",
                show_result="score_and_answers", randomize=False,
            )
            s1.proctoring_enabled = True
            s1.cheat_response = "warn_escalate"
            s1.warning_threshold = 3
            db.session.commit()
            assign_students(s1.id, student_ids=[], group_ids=[group_a.id])
        else:
            s1 = s1_existing

        # Session 2: Upcoming session (exam 2)
        s2_existing = ExamSession.query.filter_by(exam_id=2).first()
        if not s2_existing:
            s2 = create_session(
                exam_id=2,
                start_time=(now + timedelta(hours=24)).isoformat(),
                end_time=(now + timedelta(hours=25)).isoformat(),
                display_mode="all_at_once", save_mode="manual",
                show_result="score_only", randomize=True,
            )
            assign_students(s2.id, student_ids=[], group_ids=[group_a.id, group_b.id])
        else:
            s2 = s2_existing

        # Session 3: Ended session with results (exam 3)
        s3_existing = ExamSession.query.filter_by(exam_id=3).first()
        if not s3_existing:
            s3 = create_session(
                exam_id=3,
                start_time=(now - timedelta(hours=3)).isoformat(),
                end_time=(now - timedelta(hours=2)).isoformat(),
                display_mode="one_by_one", save_mode="auto_each",
                show_result="score_and_answers",
            )
            assign_students(s3.id, student_ids=[], group_ids=[group_b.id])
        else:
            s3 = s3_existing

        sessions_created = (0 if s1_existing else 1) + (0 if s2_existing else 1) + (0 if s3_existing else 1)
        print(f"  Created {sessions_created} exam sessions (active, upcoming, ended)")

        # 5. Create exam attempts + answers for the ended session (s3)
        from app.models.exam_attempt import ExamAttempt
        from app.models.online_answer import OnlineAnswer
        from app.models.exam import Question, Choice

        assignments_s3 = s3.assignments.all()
        questions_s3 = Question.query.filter_by(exam_id=3).all()

        attempts_created = 0
        for assignment in assignments_s3:
            existing_attempt = ExamAttempt.query.filter_by(
                session_id=s3.id, student_id=assignment.student_id
            ).first()
            if existing_attempt:
                continue

            total_score = 0
            total_marks = sum(q.marks for q in questions_s3)
            attempt = ExamAttempt(
                session_id=s3.id, student_id=assignment.student_id,
                status="submitted",
                started_at=(now - timedelta(hours=2, minutes=50)).isoformat(),
                submitted_at=(now - timedelta(hours=2, minutes=10)).isoformat(),
            )
            db.session.add(attempt)
            db.session.flush()

            for q in questions_s3:
                choices = q.choices.all()
                if random.random() < 0.7:
                    correct = [c for c in choices if c.is_correct]
                    selected = correct[0] if correct else choices[0]
                else:
                    selected = random.choice(choices)

                answer = OnlineAnswer(
                    attempt_id=attempt.id, question_id=q.id,
                    selected_choice_id=selected.id,
                    answered_at=(now - timedelta(hours=2, minutes=random.randint(10, 50))).isoformat(),
                )
                db.session.add(answer)

                if selected.is_correct:
                    total_score += q.marks

            attempt.score = total_score
            attempt.percentage = round((total_score / total_marks) * 100, 2) if total_marks > 0 else 0
            attempts_created += 1

        db.session.commit()
        print(f"  Created {attempts_created} exam attempts with answers for ended session")

        # 6. Create proctoring events for the active session (s1)
        from app.models.proctor import ProctorEvent

        active_attempts = ExamAttempt.query.filter_by(session_id=s1.id).all()
        event_types = [
            ("tab_switch", "high"), ("focus_lost", "medium"),
            ("copy_paste", "medium"), ("right_click", "low"),
        ]
        proctor_events_created = 0
        for attempt in active_attempts[:2]:  # first 2 students
            existing_events = ProctorEvent.query.filter_by(attempt_id=attempt.id).count()
            if existing_events > 0:
                continue
            for evt_type, severity in random.sample(event_types, 2):
                event = ProctorEvent(
                    attempt_id=attempt.id, event_type=evt_type, severity=severity,
                )
                db.session.add(event)
                proctor_events_created += 1
                if severity in ("medium", "high"):
                    attempt.warning_count += 1
        db.session.commit()
        print(f"  Created {proctor_events_created} proctoring events for active session")


if __name__ == "__main__":
    seed()
