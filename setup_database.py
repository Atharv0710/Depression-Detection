# setup_database.py - Initial database setup

import sqlite3
from sqlite3 import Error

def setup_database():
    """Initial database setup"""
    conn = None
    try:
        conn = sqlite3.connect('depression_data.db')
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT UNIQUE,
            age_group TEXT,
            gender TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS symptoms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            feeling_hopeless INTEGER,
            loss_of_interest INTEGER,
            appetite_change INTEGER,
            disturbed_sleep INTEGER,
            low_energy INTEGER,
            lack_concentration INTEGER,
            suicidal_thoughts INTEGER,
            temper_outburst INTEGER,
            panic_attack INTEGER,
            mood_swing INTEGER,
            medical_issue INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            predicted_type TEXT,
            confidence REAL,
            probabilities TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS precautions (
            depression_type TEXT PRIMARY KEY,
            immediate_actions TEXT,
            lifestyle_changes TEXT,
            professional_help TEXT,
            emergency_contacts TEXT
        )
        ''')
        
        # Pre-populate precautions
        precautions_data = [
            ('Clinical Depression', 
             'Consult a psychiatrist immediately, Start therapy sessions, Consider medication if prescribed',
             'Regular exercise, Balanced diet, Consistent sleep schedule, Mindfulness meditation',
             'Cognitive Behavioral Therapy (CBT), Psychiatrist consultation, Support groups',
             'National Suicide Prevention Lifeline: 1-800-273-TALK, Crisis Text Line: Text HOME to 741741'),
            
            ('PDD', 
             'Schedule regular therapy sessions, Monitor symptom patterns, Keep a mood journal',
             'Establish daily routine, Social engagement activities, Stress management techniques',
             'Long-term psychotherapy, Regular psychiatric follow-ups, Group therapy',
             'Therapist contact info, Trusted family member, Local mental health services'),
            
            ('Medical Depression', 
             'Consult with primary physician, Review current medications, Address underlying medical conditions',
             'Manage underlying health condition, Regular medical checkups, Medication adherence',
             'Collaborative care with physicians, Psychiatrist for comorbid conditions',
             'Primary care physician, Emergency medical services: 911'),
            
            ('DMDD', 
             'Behavioral therapy for children, Parent management training, School intervention if needed',
             'Consistent daily structure, Clear behavioral expectations, Positive reinforcement',
             'Child psychologist, Family therapy, School counselor involvement',
             'Pediatrician, Child mental health services, School counselor'),
            
            ('PMDD', 
             'Track menstrual cycle symptoms, Consult gynecologist, Consider hormonal treatment',
             'Dietary changes (reduce salt/caffeine), Regular exercise, Stress reduction techniques',
             'Gynecologist consultation, Psychiatrist for symptom management',
             'Gynecologist contact, Women\'s health clinic, Local support groups')
        ]
        
        cursor.execute("SELECT COUNT(*) FROM precautions")
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
            INSERT OR REPLACE INTO precautions 
            (depression_type, immediate_actions, lifestyle_changes, professional_help, emergency_contacts)
            VALUES (?, ?, ?, ?, ?)
            ''', precautions_data)
        
        conn.commit()
        print("✅ Database setup completed successfully!")
        
    except Error as e:
        print(f"❌ Error setting up database: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    setup_database()