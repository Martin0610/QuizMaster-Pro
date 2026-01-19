"""
QuizMaster Pro - Advanced Quiz Platform
Beautiful UI/UX with tons of features
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
from datetime import datetime, timedelta
import json
import random
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'quizmaster-pro-2026'

DATABASE = 'quizmaster.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            avatar TEXT DEFAULT 'default.png',
            total_score INTEGER DEFAULT 0,
            games_played INTEGER DEFAULT 0,
            best_streak INTEGER DEFAULT 0,
            favorite_category TEXT DEFAULT 'General',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            icon TEXT NOT NULL,
            color TEXT NOT NULL,
            description TEXT,
            question_count INTEGER DEFAULT 0
        )
    ''')
    
    # Quizzes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            category_id INTEGER,
            difficulty TEXT DEFAULT 'Medium',
            time_limit INTEGER DEFAULT 300,
            created_by INTEGER,
            is_public BOOLEAN DEFAULT 1,
            plays_count INTEGER DEFAULT 0,
            average_score REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES categories (id),
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
    ''')
    
    # Questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            question_type TEXT DEFAULT 'multiple_choice',
            correct_answer TEXT NOT NULL,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            explanation TEXT,
            points INTEGER DEFAULT 10,
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
        )
    ''')
    
    # Game sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            quiz_id INTEGER NOT NULL,
            score INTEGER DEFAULT 0,
            total_questions INTEGER,
            correct_answers INTEGER DEFAULT 0,
            time_taken INTEGER,
            streak INTEGER DEFAULT 0,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (quiz_id) REFERENCES quizzes (id)
        )
    ''')
    
    # Achievements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT,
            condition_type TEXT,
            condition_value INTEGER,
            points_reward INTEGER DEFAULT 0
        )
    ''')
    
    # User achievements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            achievement_id INTEGER NOT NULL,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (achievement_id) REFERENCES achievements (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized!")

def seed_data():
    """Add sample data to the database"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute('SELECT COUNT(*) FROM categories')
    if cursor.fetchone()[0] > 0:
        conn.close()
        return
    
    # Add categories
    categories = [
        ('Science & Technology', '🧪', '#4CAF50', 'Test your knowledge of science and tech'),
        ('History & Geography', '🏛️', '#FF9800', 'Explore the past and places around the world'),
        ('Movies & Entertainment', '🎬', '#E91E63', 'Lights, camera, action! Test your movie knowledge'),
        ('Sports & Games', '⚽', '#2196F3', 'From football to chess, test your sports IQ'),
        ('Food & Culture', '🍕', '#FF5722', 'Delicious questions about food and culture'),
        ('Programming', '💻', '#9C27B0', 'Code your way through these programming challenges'),
        ('General Knowledge', '🧠', '#607D8B', 'A mix of everything - the ultimate brain test'),
        ('Music & Arts', '🎵', '#795548', 'Harmonize with questions about music and arts')
    ]
    
    category_ids = {}
    for name, icon, color, desc in categories:
        cursor.execute('''
            INSERT INTO categories (name, icon, color, description)
            VALUES (?, ?, ?, ?)
        ''', (name, icon, color, desc))
        category_ids[name] = cursor.lastrowid
    
    # Add sample quizzes and questions
    quiz_data = [
        {
            'category': 'Science & Technology',
            'title': 'Science Quiz',
            'description': 'Test your scientific knowledge',
            'difficulty': 'Easy',
            'questions': [
                {
                    'question': 'What is the chemical symbol for water?',
                    'correct': 'H2O',
                    'options': ['H2O', 'CO2', 'NaCl', 'O2'],
                    'explanation': 'Water is composed of two hydrogen atoms and one oxygen atom.'
                },
                {
                    'question': 'Which planet is known as the Red Planet?',
                    'correct': 'Mars',
                    'options': ['Venus', 'Mars', 'Jupiter', 'Saturn'],
                    'explanation': 'Mars appears red due to iron oxide (rust) on its surface.'
                },
                {
                    'question': 'What is the speed of light in vacuum?',
                    'correct': '299,792,458 m/s',
                    'options': ['299,792,458 m/s', '300,000,000 m/s', '186,000 miles/s', 'All of the above'],
                    'explanation': 'The speed of light in vacuum is exactly 299,792,458 meters per second.'
                },
                {
                    'question': 'Which gas makes up about 78% of Earth\'s atmosphere?',
                    'correct': 'Nitrogen',
                    'options': ['Oxygen', 'Carbon Dioxide', 'Nitrogen', 'Argon'],
                    'explanation': 'Nitrogen makes up about 78% of Earth\'s atmosphere, while oxygen is about 21%.'
                },
                {
                    'question': 'What is the smallest unit of matter?',
                    'correct': 'Atom',
                    'options': ['Molecule', 'Atom', 'Electron', 'Proton'],
                    'explanation': 'An atom is the smallest unit of ordinary matter that forms a chemical element.'
                },
                {
                    'question': 'What does DNA stand for?',
                    'correct': 'Deoxyribonucleic Acid',
                    'options': ['Deoxyribonucleic Acid', 'Dynamic Nuclear Acid', 'Dual Nuclear Acid', 'Deoxyribose Nucleic Acid'],
                    'explanation': 'DNA stands for Deoxyribonucleic Acid, which carries genetic information.'
                },
                {
                    'question': 'Which scientist developed the theory of relativity?',
                    'correct': 'Albert Einstein',
                    'options': ['Isaac Newton', 'Albert Einstein', 'Galileo Galilei', 'Stephen Hawking'],
                    'explanation': 'Albert Einstein developed both special and general theories of relativity.'
                },
                {
                    'question': 'What is the hardest natural substance on Earth?',
                    'correct': 'Diamond',
                    'options': ['Gold', 'Iron', 'Diamond', 'Platinum'],
                    'explanation': 'Diamond is the hardest naturally occurring substance, rating 10 on the Mohs scale.'
                },
                {
                    'question': 'How many bones are in an adult human body?',
                    'correct': '206',
                    'options': ['196', '206', '216', '226'],
                    'explanation': 'An adult human skeleton has 206 bones.'
                },
                {
                    'question': 'What is the largest organ in the human body?',
                    'correct': 'Skin',
                    'options': ['Liver', 'Brain', 'Skin', 'Heart'],
                    'explanation': 'The skin is the largest organ, covering the entire body surface.'
                },
                {
                    'question': 'Which blood type is known as the universal donor?',
                    'correct': 'O negative',
                    'options': ['A positive', 'B negative', 'AB positive', 'O negative'],
                    'explanation': 'O negative blood can be given to people of any blood type.'
                },
                {
                    'question': 'What is the powerhouse of the cell?',
                    'correct': 'Mitochondria',
                    'options': ['Nucleus', 'Mitochondria', 'Ribosome', 'Chloroplast'],
                    'explanation': 'Mitochondria produce energy (ATP) for cellular processes.'
                },
                {
                    'question': 'Which planet has the most moons?',
                    'correct': 'Saturn',
                    'options': ['Jupiter', 'Saturn', 'Uranus', 'Neptune'],
                    'explanation': 'Saturn has 146 confirmed moons, more than any other planet.'
                },
                {
                    'question': 'What is the study of earthquakes called?',
                    'correct': 'Seismology',
                    'options': ['Geology', 'Seismology', 'Meteorology', 'Volcanology'],
                    'explanation': 'Seismology is the scientific study of earthquakes and seismic waves.'
                },
                {
                    'question': 'Which element has the atomic number 1?',
                    'correct': 'Hydrogen',
                    'options': ['Helium', 'Hydrogen', 'Lithium', 'Carbon'],
                    'explanation': 'Hydrogen is the first element on the periodic table with atomic number 1.'
                }
            ]
        },
        {
            'category': 'Programming',
            'title': 'Programming Quiz',
            'description': 'Test your coding knowledge',
            'difficulty': 'Medium',
            'questions': [
                {
                    'question': 'Which of the following is used to define a function in Python?',
                    'correct': 'def',
                    'options': ['function', 'def', 'define', 'func'],
                    'explanation': 'The "def" keyword is used to define functions in Python.'
                },
                {
                    'question': 'What is the output of print(2 ** 3)?',
                    'correct': '8',
                    'options': ['6', '8', '9', '23'],
                    'explanation': '** is the exponentiation operator in Python, so 2**3 = 2³ = 8.'
                },
                {
                    'question': 'Which data type is mutable in Python?',
                    'correct': 'List',
                    'options': ['String', 'Tuple', 'List', 'Integer'],
                    'explanation': 'Lists are mutable in Python, meaning their contents can be changed after creation.'
                },
                {
                    'question': 'What does the len() function return?',
                    'correct': 'Length of an object',
                    'options': ['Length of an object', 'Last element', 'First element', 'Type of object'],
                    'explanation': 'The len() function returns the number of items in an object.'
                },
                {
                    'question': 'Which symbol is used for comments in Python?',
                    'correct': '#',
                    'options': ['//', '#', '/*', '--'],
                    'explanation': 'The # symbol is used for single-line comments in Python.'
                },
                {
                    'question': 'What does HTML stand for?',
                    'correct': 'HyperText Markup Language',
                    'options': ['HyperText Markup Language', 'High Tech Modern Language', 'Home Tool Markup Language', 'Hyperlink and Text Markup Language'],
                    'explanation': 'HTML stands for HyperText Markup Language, used for creating web pages.'
                },
                {
                    'question': 'Which of these is NOT a programming language?',
                    'correct': 'HTTP',
                    'options': ['Python', 'Java', 'HTTP', 'C++'],
                    'explanation': 'HTTP is a protocol for transferring data, not a programming language.'
                },
                {
                    'question': 'What does CSS stand for?',
                    'correct': 'Cascading Style Sheets',
                    'options': ['Computer Style Sheets', 'Cascading Style Sheets', 'Creative Style Sheets', 'Colorful Style Sheets'],
                    'explanation': 'CSS stands for Cascading Style Sheets, used for styling web pages.'
                },
                {
                    'question': 'Which company developed JavaScript?',
                    'correct': 'Netscape',
                    'options': ['Microsoft', 'Google', 'Netscape', 'Apple'],
                    'explanation': 'JavaScript was originally developed by Netscape in 1995.'
                },
                {
                    'question': 'What is the correct way to create an array in JavaScript?',
                    'correct': 'var arr = [];',
                    'options': ['var arr = {};', 'var arr = [];', 'var arr = ();', 'var arr = <>;'],
                    'explanation': 'Square brackets [] are used to create arrays in JavaScript.'
                },
                {
                    'question': 'Which of these is a NoSQL database?',
                    'correct': 'MongoDB',
                    'options': ['MySQL', 'PostgreSQL', 'MongoDB', 'SQLite'],
                    'explanation': 'MongoDB is a popular NoSQL document database.'
                },
                {
                    'question': 'What does API stand for?',
                    'correct': 'Application Programming Interface',
                    'options': ['Application Programming Interface', 'Advanced Programming Interface', 'Automated Programming Interface', 'Application Process Interface'],
                    'explanation': 'API stands for Application Programming Interface.'
                },
                {
                    'question': 'Which HTTP method is used to retrieve data?',
                    'correct': 'GET',
                    'options': ['POST', 'GET', 'PUT', 'DELETE'],
                    'explanation': 'GET method is used to retrieve data from a server.'
                },
                {
                    'question': 'What is the time complexity of binary search?',
                    'correct': 'O(log n)',
                    'options': ['O(n)', 'O(log n)', 'O(n²)', 'O(1)'],
                    'explanation': 'Binary search has O(log n) time complexity as it halves the search space each time.'
                },
                {
                    'question': 'Which of these is NOT a valid variable name in most programming languages?',
                    'correct': '2variable',
                    'options': ['variable2', '_variable', 'variable_name', '2variable'],
                    'explanation': 'Variable names cannot start with a number in most programming languages.'
                }
            ]
        },
        {
            'category': 'General Knowledge',
            'title': 'General Knowledge Quiz',
            'description': 'Test your general knowledge',
            'difficulty': 'Easy',
            'questions': [
                {
                    'question': 'Which is the largest ocean on Earth?',
                    'correct': 'Pacific Ocean',
                    'options': ['Atlantic Ocean', 'Indian Ocean', 'Pacific Ocean', 'Arctic Ocean'],
                    'explanation': 'The Pacific Ocean is the largest and deepest ocean on Earth.'
                },
                {
                    'question': 'How many continents are there?',
                    'correct': '7',
                    'options': ['5', '6', '7', '8'],
                    'explanation': 'There are 7 continents: Asia, Africa, North America, South America, Antarctica, Europe, and Australia.'
                },
                {
                    'question': 'What is the capital of Australia?',
                    'correct': 'Canberra',
                    'options': ['Sydney', 'Melbourne', 'Canberra', 'Perth'],
                    'explanation': 'Canberra is the capital city of Australia, not Sydney or Melbourne.'
                },
                {
                    'question': 'Which country has the most time zones?',
                    'correct': 'France',
                    'options': ['Russia', 'USA', 'China', 'France'],
                    'explanation': 'France has 12 time zones due to its overseas territories.'
                },
                {
                    'question': 'What is the smallest country in the world?',
                    'correct': 'Vatican City',
                    'options': ['Monaco', 'Vatican City', 'San Marino', 'Liechtenstein'],
                    'explanation': 'Vatican City is the smallest country in the world with an area of just 0.17 square miles.'
                },
                {
                    'question': 'Which river is the longest in the world?',
                    'correct': 'Nile River',
                    'options': ['Amazon River', 'Nile River', 'Mississippi River', 'Yangtze River'],
                    'explanation': 'The Nile River in Africa is the longest river in the world at 6,650 km.'
                },
                {
                    'question': 'What is the tallest mountain in the world?',
                    'correct': 'Mount Everest',
                    'options': ['K2', 'Mount Everest', 'Kangchenjunga', 'Lhotse'],
                    'explanation': 'Mount Everest is the tallest mountain at 8,848.86 meters above sea level.'
                },
                {
                    'question': 'Which country is known as the Land of the Rising Sun?',
                    'correct': 'Japan',
                    'options': ['China', 'Japan', 'South Korea', 'Thailand'],
                    'explanation': 'Japan is called the Land of the Rising Sun because of its location east of Asia.'
                },
                {
                    'question': 'What is the largest desert in the world?',
                    'correct': 'Antarctica',
                    'options': ['Sahara', 'Gobi', 'Antarctica', 'Arabian'],
                    'explanation': 'Antarctica is technically the largest desert as it receives very little precipitation.'
                },
                {
                    'question': 'Which language has the most native speakers?',
                    'correct': 'Mandarin Chinese',
                    'options': ['English', 'Spanish', 'Mandarin Chinese', 'Hindi'],
                    'explanation': 'Mandarin Chinese has over 900 million native speakers.'
                },
                {
                    'question': 'What is the currency of the United Kingdom?',
                    'correct': 'Pound Sterling',
                    'options': ['Euro', 'Dollar', 'Pound Sterling', 'Franc'],
                    'explanation': 'The UK uses Pound Sterling (GBP) as its currency.'
                },
                {
                    'question': 'Which planet is closest to the Sun?',
                    'correct': 'Mercury',
                    'options': ['Venus', 'Mercury', 'Earth', 'Mars'],
                    'explanation': 'Mercury is the closest planet to the Sun in our solar system.'
                },
                {
                    'question': 'What is the most spoken language in the world?',
                    'correct': 'English',
                    'options': ['Mandarin', 'English', 'Spanish', 'Hindi'],
                    'explanation': 'English is the most widely spoken language when including second-language speakers.'
                },
                {
                    'question': 'Which country invented pizza?',
                    'correct': 'Italy',
                    'options': ['Greece', 'Italy', 'France', 'Spain'],
                    'explanation': 'Pizza originated in Naples, Italy in the 18th century.'
                },
                {
                    'question': 'What is the largest mammal in the world?',
                    'correct': 'Blue Whale',
                    'options': ['African Elephant', 'Blue Whale', 'Giraffe', 'Hippopotamus'],
                    'explanation': 'The Blue Whale is the largest mammal and largest animal ever known to exist.'
                }
            ]
        },
        {
            'category': 'History & Geography',
            'title': 'History & Geography Quiz',
            'description': 'Test your knowledge of history and geography',
            'difficulty': 'Medium',
            'questions': [
                {
                    'question': 'In which year did World War II end?',
                    'correct': '1945',
                    'options': ['1944', '1945', '1946', '1947'],
                    'explanation': 'World War II ended in 1945 with the surrender of Japan in September.'
                },
                {
                    'question': 'Which ancient wonder of the world was located in Alexandria?',
                    'correct': 'Lighthouse of Alexandria',
                    'options': ['Hanging Gardens', 'Lighthouse of Alexandria', 'Colossus of Rhodes', 'Temple of Artemis'],
                    'explanation': 'The Lighthouse of Alexandria was one of the Seven Wonders of the Ancient World.'
                },
                {
                    'question': 'What is the capital of Canada?',
                    'correct': 'Ottawa',
                    'options': ['Toronto', 'Vancouver', 'Montreal', 'Ottawa'],
                    'explanation': 'Ottawa is the capital city of Canada, located in Ontario.'
                },
                {
                    'question': 'Which empire was ruled by Julius Caesar?',
                    'correct': 'Roman Empire',
                    'options': ['Greek Empire', 'Roman Empire', 'Persian Empire', 'Egyptian Empire'],
                    'explanation': 'Julius Caesar was a Roman general and statesman who ruled the Roman Empire.'
                },
                {
                    'question': 'Which country is both in Europe and Asia?',
                    'correct': 'Turkey',
                    'options': ['Russia', 'Turkey', 'Kazakhstan', 'Georgia'],
                    'explanation': 'Turkey is a transcontinental country located mainly in Anatolia in Western Asia, with a smaller portion on the Balkan Peninsula in Southeastern Europe.'
                },
                {
                    'question': 'Who was the first person to walk on the moon?',
                    'correct': 'Neil Armstrong',
                    'options': ['Buzz Aldrin', 'Neil Armstrong', 'John Glenn', 'Alan Shepard'],
                    'explanation': 'Neil Armstrong was the first human to walk on the moon on July 20, 1969.'
                },
                {
                    'question': 'Which wall was built to keep invaders out of China?',
                    'correct': 'Great Wall of China',
                    'options': ['Berlin Wall', 'Hadrian\'s Wall', 'Great Wall of China', 'Western Wall'],
                    'explanation': 'The Great Wall of China was built to protect Chinese states from invasions.'
                },
                {
                    'question': 'What is the longest river in Europe?',
                    'correct': 'Volga River',
                    'options': ['Danube River', 'Rhine River', 'Volga River', 'Thames River'],
                    'explanation': 'The Volga River is the longest river in Europe at 3,530 km.'
                },
                {
                    'question': 'Which city was the capital of the Byzantine Empire?',
                    'correct': 'Constantinople',
                    'options': ['Rome', 'Athens', 'Constantinople', 'Alexandria'],
                    'explanation': 'Constantinople (modern-day Istanbul) was the capital of the Byzantine Empire.'
                },
                {
                    'question': 'In which country would you find Machu Picchu?',
                    'correct': 'Peru',
                    'options': ['Bolivia', 'Peru', 'Ecuador', 'Colombia'],
                    'explanation': 'Machu Picchu is an ancient Incan city located in Peru.'
                }
            ]
        },
        {
            'category': 'Sports & Games',
            'title': 'Sports & Games Quiz',
            'description': 'Test your sports knowledge',
            'difficulty': 'Medium',
            'questions': [
                {
                    'question': 'How many players are on a basketball team on the court at one time?',
                    'correct': '5',
                    'options': ['4', '5', '6', '7'],
                    'explanation': 'Each basketball team has 5 players on the court at any given time.'
                },
                {
                    'question': 'In which sport would you perform a slam dunk?',
                    'correct': 'Basketball',
                    'options': ['Volleyball', 'Basketball', 'Tennis', 'Badminton'],
                    'explanation': 'A slam dunk is a basketball shot where the player jumps and scores by putting the ball directly through the basket.'
                },
                {
                    'question': 'Which country has won the most FIFA World Cups?',
                    'correct': 'Brazil',
                    'options': ['Germany', 'Brazil', 'Argentina', 'Italy'],
                    'explanation': 'Brazil has won the FIFA World Cup 5 times, more than any other country.'
                },
                {
                    'question': 'In tennis, what does "love" mean?',
                    'correct': 'Zero points',
                    'options': ['One point', 'Zero points', 'Winning point', 'Tie score'],
                    'explanation': 'In tennis scoring, "love" means zero points.'
                },
                {
                    'question': 'How many holes are played in a standard round of golf?',
                    'correct': '18',
                    'options': ['16', '18', '20', '24'],
                    'explanation': 'A standard round of golf consists of 18 holes.'
                }
            ]
        },
        {
            'category': 'Food & Culture',
            'title': 'Food & Culture Quiz',
            'description': 'Test your knowledge of food and culture',
            'difficulty': 'Easy',
            'questions': [
                {
                    'question': 'Which country is famous for inventing pizza?',
                    'correct': 'Italy',
                    'options': ['France', 'Italy', 'Greece', 'Spain'],
                    'explanation': 'Pizza was invented in Naples, Italy in the 18th century.'
                },
                {
                    'question': 'What is the main ingredient in guacamole?',
                    'correct': 'Avocado',
                    'options': ['Tomato', 'Avocado', 'Onion', 'Pepper'],
                    'explanation': 'Guacamole is primarily made from mashed avocados.'
                },
                {
                    'question': 'Which spice is derived from the Crocus flower?',
                    'correct': 'Saffron',
                    'options': ['Turmeric', 'Saffron', 'Paprika', 'Cinnamon'],
                    'explanation': 'Saffron comes from the flower of Crocus sativus and is one of the most expensive spices.'
                },
                {
                    'question': 'Which country is the origin of sushi?',
                    'correct': 'Japan',
                    'options': ['China', 'Japan', 'Korea', 'Thailand'],
                    'explanation': 'Sushi originated in Japan, though it has ancient roots in Southeast Asia.'
                },
                {
                    'question': 'What is the most consumed beverage in the world after water?',
                    'correct': 'Tea',
                    'options': ['Coffee', 'Tea', 'Soda', 'Beer'],
                    'explanation': 'Tea is the second most consumed beverage in the world after water.'
                }
            ]
        },
        {
            'category': 'Movies & Entertainment',
            'title': 'Movies & Entertainment Quiz',
            'description': 'Test your movie and entertainment knowledge',
            'difficulty': 'Medium',
            'questions': [
                {
                    'question': 'Which movie won the Academy Award for Best Picture in 2020?',
                    'correct': 'Parasite',
                    'options': ['1917', 'Parasite', 'Joker', 'Once Upon a Time in Hollywood'],
                    'explanation': 'Parasite became the first non-English language film to win Best Picture.'
                },
                {
                    'question': 'Who directed the movie "Inception"?',
                    'correct': 'Christopher Nolan',
                    'options': ['Steven Spielberg', 'Christopher Nolan', 'Martin Scorsese', 'Quentin Tarantino'],
                    'explanation': 'Christopher Nolan wrote and directed Inception (2010).'
                },
                {
                    'question': 'Which actor played Iron Man in the Marvel Cinematic Universe?',
                    'correct': 'Robert Downey Jr.',
                    'options': ['Chris Evans', 'Robert Downey Jr.', 'Mark Ruffalo', 'Chris Hemsworth'],
                    'explanation': 'Robert Downey Jr. portrayed Tony Stark/Iron Man from 2008 to 2019.'
                },
                {
                    'question': 'Which TV series features the character Walter White?',
                    'correct': 'Breaking Bad',
                    'options': ['Better Call Saul', 'Breaking Bad', 'The Sopranos', 'Mad Men'],
                    'explanation': 'Walter White is the main character in the TV series Breaking Bad.'
                },
                {
                    'question': 'Which movie features the quote "May the Force be with you"?',
                    'correct': 'Star Wars',
                    'options': ['Star Trek', 'Star Wars', 'Guardians of the Galaxy', 'Interstellar'],
                    'explanation': 'This iconic quote is from the Star Wars franchise.'
                }
            ]
        },
        {
            'category': 'Music & Arts',
            'title': 'Music & Arts Quiz',
            'description': 'Test your knowledge of music and arts',
            'difficulty': 'Medium',
            'questions': [
                {
                    'question': 'Who composed "The Four Seasons"?',
                    'correct': 'Antonio Vivaldi',
                    'options': ['Johann Bach', 'Antonio Vivaldi', 'Wolfgang Mozart', 'Ludwig Beethoven'],
                    'explanation': 'Antonio Vivaldi composed "The Four Seasons" in 1723.'
                },
                {
                    'question': 'Which artist painted "The Starry Night"?',
                    'correct': 'Vincent van Gogh',
                    'options': ['Pablo Picasso', 'Vincent van Gogh', 'Claude Monet', 'Salvador Dalí'],
                    'explanation': 'Vincent van Gogh painted "The Starry Night" in 1889.'
                },
                {
                    'question': 'How many strings does a standard guitar have?',
                    'correct': '6',
                    'options': ['4', '5', '6', '7'],
                    'explanation': 'A standard acoustic or electric guitar has 6 strings.'
                },
                {
                    'question': 'What does "forte" mean in music?',
                    'correct': 'Loud',
                    'options': ['Soft', 'Loud', 'Fast', 'Slow'],
                    'explanation': 'Forte (f) is a dynamic marking that means to play loudly.'
                },
                {
                    'question': 'Who sculpted "David"?',
                    'correct': 'Michelangelo',
                    'options': ['Leonardo da Vinci', 'Michelangelo', 'Donatello', 'Rodin'],
                    'explanation': 'Michelangelo sculpted the famous statue of David between 1501-1504.'
                }
            ]
        }
    ]
    
    for quiz_info in quiz_data:
        # Create quiz
        cursor.execute('''
            INSERT INTO quizzes (title, description, category_id, difficulty, time_limit, created_by, is_public)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (quiz_info['title'], quiz_info['description'], category_ids[quiz_info['category']], 
              quiz_info['difficulty'], 300, 1, 1))
        
        quiz_id = cursor.lastrowid
        
        # Add questions
        for q in quiz_info['questions']:
            cursor.execute('''
                INSERT INTO questions (quiz_id, question_text, correct_answer, option_a, option_b, option_c, option_d, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (quiz_id, q['question'], q['correct'], q['options'][0], q['options'][1], 
                  q['options'][2], q['options'][3], q['explanation']))
    
    # Update category question counts
    cursor.execute('''
        UPDATE categories SET question_count = (
            SELECT COUNT(q.id) 
            FROM questions q 
            JOIN quizzes qz ON q.quiz_id = qz.id 
            WHERE qz.category_id = categories.id
        )
    ''')
    
    # Add achievements
    achievements = [
        ('First Steps', 'Complete your first quiz', '🎯', 'games_played', 1, 50),
        ('Quiz Master', 'Complete 10 quizzes', '🏆', 'games_played', 10, 200),
        ('Perfect Score', 'Get 100% on any quiz', '⭐', 'perfect_score', 1, 100),
        ('Speed Demon', 'Complete a quiz in under 60 seconds', '⚡', 'speed', 60, 150),
        ('Streak Master', 'Get 5 questions right in a row', '🔥', 'streak', 5, 75),
        ('Category Expert', 'Complete all quizzes in one category', '🎓', 'category_complete', 1, 300),
        ('High Scorer', 'Reach 1000 total points', '💎', 'total_score', 1000, 250),
        ('Quiz Creator', 'Create your first quiz', '✨', 'quiz_created', 1, 100)
    ]
    
    for name, desc, icon, cond_type, cond_val, points in achievements:
        cursor.execute('''
            INSERT INTO achievements (name, description, icon, condition_type, condition_value, points_reward)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, desc, icon, cond_type, cond_val, points))
    
    conn.commit()
    conn.close()
    print("✅ Sample data added!")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this feature', 'warning')
            return redirect(url_for('auth'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'register':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not all([username, email, password]):
                flash('All fields are required', 'danger')
                return redirect(url_for('auth'))
            
            conn = get_db()
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute('SELECT id FROM users WHERE username = ? OR email = ?', (username, email))
            if cursor.fetchone():
                flash('Username or email already exists', 'danger')
                conn.close()
                return redirect(url_for('auth'))
            
            # Create user
            cursor.execute('''
                INSERT INTO users (username, email, password)
                VALUES (?, ?, ?)
            ''', (username, email, password))
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            session['user_id'] = user_id
            session['username'] = username
            flash(f'Welcome to QuizMaster Pro, {username}!', 'success')
            return redirect(url_for('dashboard'))
        
        elif action == 'login':
            username = request.form.get('username')
            password = request.form.get('password')
            
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash(f'Welcome back, {user["username"]}!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'danger')
    
    return render_template('auth.html')

@app.route('/dashboard')
@login_required
def dashboard():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get user stats
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    
    # Get recent games
    cursor.execute('''
        SELECT gs.*, q.title, c.name as category_name, c.icon
        FROM game_sessions gs
        JOIN quizzes q ON gs.quiz_id = q.id
        JOIN categories c ON q.category_id = c.id
        WHERE gs.user_id = ?
        ORDER BY gs.completed_at DESC
        LIMIT 5
    ''', (session['user_id'],))
    recent_games = cursor.fetchall()
    
    # Get categories with stats
    cursor.execute('''
        SELECT c.*, COUNT(q.id) as quiz_count
        FROM categories c
        LEFT JOIN quizzes q ON c.id = q.category_id
        GROUP BY c.id
        ORDER BY c.name
    ''')
    categories = cursor.fetchall()
    
    # Get achievements
    cursor.execute('''
        SELECT a.*, ua.earned_at
        FROM achievements a
        LEFT JOIN user_achievements ua ON a.id = ua.achievement_id AND ua.user_id = ?
        ORDER BY ua.earned_at DESC NULLS LAST
    ''', (session['user_id'],))
    achievements = cursor.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html', 
                         user=user, 
                         recent_games=recent_games, 
                         categories=categories,
                         achievements=achievements)

@app.route('/test-db')
def test_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Check categories
    cursor.execute('SELECT COUNT(*) as count FROM categories')
    cat_count = cursor.fetchone()['count']
    
    # Check quizzes
    cursor.execute('SELECT COUNT(*) as count FROM quizzes')
    quiz_count = cursor.fetchone()['count']
    
    # Check questions
    cursor.execute('SELECT COUNT(*) as count FROM questions')
    question_count = cursor.fetchone()['count']
    
    conn.close()
    
    return f"Categories: {cat_count}, Quizzes: {quiz_count}, Questions: {question_count}"

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

@app.route('/category/<category_name>')
@login_required
def category_quizzes(category_name):
    conn = get_db()
    cursor = conn.cursor()
    
    # Get category
    cursor.execute('SELECT * FROM categories WHERE name = ?', (category_name,))
    category = cursor.fetchone()
    
    if not category:
        flash('Category not found', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get quizzes in this category
    cursor.execute('''
        SELECT q.*, COUNT(qs.id) as question_count
        FROM quizzes q
        LEFT JOIN questions qs ON q.id = qs.quiz_id
        WHERE q.category_id = ?
        GROUP BY q.id
        ORDER BY q.created_at DESC
    ''', (category['id'],))
    quizzes = cursor.fetchall()
    
    conn.close()
    
    return render_template('category.html', category=category, quizzes=quizzes)

@app.route('/quiz/<int:quiz_id>')
@login_required
def start_quiz(quiz_id):
    conn = get_db()
    cursor = conn.cursor()
    
    # Get quiz details
    cursor.execute('''
        SELECT q.*, c.name as category_name, c.icon as category_icon
        FROM quizzes q
        JOIN categories c ON q.category_id = c.id
        WHERE q.id = ?
    ''', (quiz_id,))
    quiz = cursor.fetchone()
    
    if not quiz:
        flash('Quiz not found', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get ALL questions from this quiz
    cursor.execute('SELECT * FROM questions WHERE quiz_id = ? ORDER BY RANDOM()', (quiz_id,))
    all_questions = cursor.fetchall()
    
    conn.close()
    
    if not all_questions:
        flash('This quiz has no questions yet', 'warning')
        return redirect(url_for('dashboard'))
    
    # Select random 10 questions (or all if less than 10)
    import random
    questions = list(all_questions)
    if len(questions) > 10:
        questions = random.sample(questions, 10)
    
    # Store quiz session
    session['current_quiz'] = {
        'quiz_id': quiz_id,
        'questions': [dict(q) for q in questions],
        'current_question': 0,
        'score': 0,
        'correct_answers': 0,
        'start_time': datetime.now().isoformat(),
        'answers': [],
        'question_time_limit': 30  # 30 seconds per question
    }
    
    return render_template('quiz.html', quiz=quiz, questions=questions)

@app.route('/quiz/question/<int:question_num>')
@login_required
def quiz_question(question_num):
    print(f"Loading question {question_num}")
    
    if 'current_quiz' not in session:
        print("No active quiz session found")
        return jsonify({'error': 'No active quiz session. Please start a new quiz.'}), 400
    
    quiz_session = session['current_quiz']
    print(f"Quiz session found with {len(quiz_session['questions'])} questions")
    
    if question_num >= len(quiz_session['questions']):
        print(f"Question {question_num} is out of range")
        return jsonify({'error': 'Quiz completed'}), 400
    
    question = quiz_session['questions'][question_num]
    quiz_session['current_question'] = question_num
    session['current_quiz'] = quiz_session
    session.permanent = True  # Make session permanent to avoid expiry
    
    print(f"Returning question: {question['question_text'][:50]}...")
    
    return jsonify({
        'question': question,
        'question_num': question_num + 1,
        'total_questions': len(quiz_session['questions']),
        'progress': ((question_num + 1) / len(quiz_session['questions'])) * 100
    })

@app.route('/quiz/submit', methods=['POST'])
@login_required
def submit_answer():
    print("Answer submission received")
    
    if 'current_quiz' not in session:
        print("No active quiz session")
        return jsonify({'error': 'No active quiz session. Please start a new quiz.'}), 400
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data received'}), 400
            
        answer = data.get('answer', '')  # Allow empty answers
        question_num = data.get('question_num', 0)
        
        print(f"Submitting answer '{answer}' for question {question_num}")
        
        quiz_session = session['current_quiz']
        
        if question_num >= len(quiz_session['questions']):
            return jsonify({'error': 'Invalid question number'}), 400
            
        question = quiz_session['questions'][question_num]
        
        is_correct = answer == question['correct_answer'] if answer else False
        
        if is_correct:
            quiz_session['score'] += question.get('points', 10)
            quiz_session['correct_answers'] += 1
        
        quiz_session['answers'].append({
            'question_id': question['id'],
            'answer': answer if answer else 'No answer',
            'correct': is_correct,
            'correct_answer': question['correct_answer'],
            'explanation': question.get('explanation', '')
        })
        
        session['current_quiz'] = quiz_session
        session.permanent = True  # Make session permanent
        
        print(f"Answer processed. Correct: {is_correct}, Score: {quiz_session['score']}")
        
        return jsonify({
            'correct': is_correct,
            'correct_answer': question['correct_answer'],
            'explanation': question.get('explanation', ''),
            'score': quiz_session['score']
        })
        
    except Exception as e:
        print(f"Error processing answer: {str(e)}")
        return jsonify({'error': f'Error processing answer: {str(e)}'}), 500

@app.route('/quiz/results')
@login_required
def quiz_results():
    if 'current_quiz' not in session:
        flash('No quiz session found', 'warning')
        return redirect(url_for('dashboard'))
    
    quiz_session = session['current_quiz']
    
    # Calculate results
    total_questions = len(quiz_session['questions'])
    correct_answers = quiz_session['correct_answers']
    score = quiz_session['score']
    percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Calculate time taken
    start_time = datetime.fromisoformat(quiz_session['start_time'])
    time_taken = int((datetime.now() - start_time).total_seconds())
    
    # Save to database
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO game_sessions (user_id, quiz_id, score, total_questions, correct_answers, time_taken)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (session['user_id'], quiz_session['quiz_id'], score, total_questions, correct_answers, time_taken))
    
    # Update user stats
    cursor.execute('''
        UPDATE users SET 
            total_score = total_score + ?,
            games_played = games_played + 1,
            best_streak = CASE WHEN ? > best_streak THEN ? ELSE best_streak END
        WHERE id = ?
    ''', (score, correct_answers, correct_answers, session['user_id']))
    
    # Get quiz info
    cursor.execute('''
        SELECT q.title, c.name as category_name, c.icon as category_icon
        FROM quizzes q
        JOIN categories c ON q.category_id = c.id
        WHERE q.id = ?
    ''', (quiz_session['quiz_id'],))
    quiz_info = cursor.fetchone()
    
    conn.commit()
    conn.close()
    
    results = {
        'quiz_info': quiz_info,
        'score': score,
        'correct_answers': correct_answers,
        'total_questions': total_questions,
        'percentage': percentage,
        'time_taken': time_taken,
        'answers': quiz_session['answers']
    }
    
    # Clear quiz session
    session.pop('current_quiz', None)
    
    return render_template('quiz_results.html', results=results)

@app.route('/random-quiz')
@login_required
def random_quiz():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get a random quiz
    cursor.execute('SELECT id FROM quizzes ORDER BY RANDOM() LIMIT 1')
    quiz = cursor.fetchone()
    
    conn.close()
    
    if quiz:
        return redirect(url_for('start_quiz', quiz_id=quiz['id']))
    else:
        flash('No quizzes available', 'warning')
        return redirect(url_for('dashboard'))

# Initialize database on startup
if not os.path.exists(DATABASE):
    init_db()
    seed_data()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🎮 QuizMaster Pro - Advanced Quiz Platform")
    print("="*60)
    print("\n  🌐 Access at: http://localhost:5000")
    print("  🎯 Features: Quizzes, Leaderboards, Achievements")
    print("  🎨 Beautiful UI with animations and effects")
    print("  📱 Mobile-responsive design")
    print("\n" + "="*60 + "\n")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)