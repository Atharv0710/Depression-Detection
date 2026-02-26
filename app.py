# app.py - Streamlit Depression Prediction App

import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime
import sqlite3
from sqlite3 import Error
import matplotlib.pyplot as plt
import seaborn as sns
from chatbot import render_chatbot
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Depression Diagnosis Assistant",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #2563EB;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .section-box {
        background-color: #F0F9FF;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 1.5rem;
    }
    .symptom-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        transition: transform 0.2s;
    }
    .symptom-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .prediction-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
    }
    .precaution-card {
        background-color: #EFF6FF;
        border: 1px solid #BFDBFE;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .emergency-box {
        background-color: #FEF2F2;
        border: 2px solid #DC2626;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stat-box {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    /* Chatbot specific styling */
    .stChatMessage {
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
    }
    .stChatMessage[data-testid="user-message"] {
        background-color: #3B82F6;
        color: white;
    }
    .stChatMessage[data-testid="assistant-message"] {
        background-color: #F0F9FF;
        color: #1F2937;
        border-left: 3px solid #3B82F6;
    }
    .stChatInput {
        border: 2px solid #3B82F6;
        border-radius: 20px;
    }
    .emergency-box-chat {
        background-color: #FEF2F2;
        border: 2px solid #DC2626;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Database setup
def create_connection():
    """Create a database connection"""
    conn = None
    try:
        conn = sqlite3.connect('depression_data.db')
        return conn
    except Error as e:
        st.error(f"Error connecting to database: {e}")
    return conn

def create_tables(conn):
    """Create necessary tables if they don't exist"""
    try:
        cursor = conn.cursor()
        
        # Patients table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT UNIQUE,
            age_group TEXT,
            gender TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Symptoms table
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
        
        # Predictions table
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
        
        # Precautions table (pre-populated)
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS precautions (
            depression_type TEXT PRIMARY KEY,
            immediate_actions TEXT,
            lifestyle_changes TEXT,
            professional_help TEXT,
            emergency_contacts TEXT
        )
        ''')
        
        # Pre-populate precautions table
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
        
    except Error as e:
        st.error(f"Error creating tables: {e}")

def save_prediction_to_db(patient_id, symptoms_dict, prediction, confidence, probabilities):
    """Save prediction data to database"""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Check if patient exists
            cursor.execute("SELECT id FROM patients WHERE patient_id = ?", (patient_id,))
            patient = cursor.fetchone()
            
            if not patient:
                # Create new patient
                cursor.execute('''
                INSERT INTO patients (patient_id, age_group, gender, timestamp)
                VALUES (?, ?, ?, ?)
                ''', (patient_id, symptoms_dict.get('Age', 'unknown'), 
                     symptoms_dict.get('gender', 'unknown'), datetime.now()))
            
            # Save symptoms
            cursor.execute('''
            INSERT INTO symptoms 
            (patient_id, feeling_hopeless, loss_of_interest, appetite_change, 
             disturbed_sleep, low_energy, lack_concentration, suicidal_thoughts,
             temper_outburst, panic_attack, mood_swing, medical_issue, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                patient_id,
                symptoms_dict.get('Feelinghopeless', 0),
                symptoms_dict.get('lossofinterest', 0),
                symptoms_dict.get('appetitechange', 0),
                symptoms_dict.get('distrubedsleepcycle', 0),
                symptoms_dict.get('low energy', 0),
                symptoms_dict.get('lackofconcentration', 0),
                symptoms_dict.get('suicidalthoughts', 0),
                symptoms_dict.get('temperoutburst', 0),
                symptoms_dict.get('panicattack', 0),
                symptoms_dict.get('moodswing', 0),
                symptoms_dict.get('medicalissue', 0),
                datetime.now()
            ))
            
            # Save prediction
            cursor.execute('''
            INSERT INTO predictions 
            (patient_id, predicted_type, confidence, probabilities, timestamp)
            VALUES (?, ?, ?, ?, ?)
            ''', (patient_id, prediction, confidence, str(probabilities), datetime.now()))
            
            conn.commit()
            conn.close()
            return True
            
        except Error as e:
            st.error(f"Error saving to database: {e}")
            return False
    return False

def get_precautions(depression_type):
    """Get precautions for a specific depression type"""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM precautions WHERE depression_type = ?", (depression_type,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'depression_type': result[0],
                    'immediate_actions': result[1],
                    'lifestyle_changes': result[2],
                    'professional_help': result[3],
                    'emergency_contacts': result[4]
                }
        except Error as e:
            st.error(f"Error fetching precautions: {e}")
    return None

def get_statistics():
    """Get statistics from database"""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Total predictions
            cursor.execute("SELECT COUNT(*) FROM predictions")
            total_result = cursor.fetchone()
            total_predictions = total_result[0] if total_result and total_result[0] is not None else 0
            
            # Predictions by type
            cursor.execute("""
                SELECT predicted_type, COUNT(*) as count 
                FROM predictions 
                GROUP BY predicted_type 
                ORDER BY count DESC
            """)
            predictions_by_type = cursor.fetchall()
            
            # Most common symptoms - using COALESCE to handle NULL values
            cursor.execute("""
                SELECT 
                    COALESCE(SUM(feeling_hopeless), 0) as hopeless,
                    COALESCE(SUM(loss_of_interest), 0) as interest_loss,
                    COALESCE(SUM(appetite_change), 0) as appetite,
                    COALESCE(SUM(disturbed_sleep), 0) as sleep,
                    COALESCE(SUM(low_energy), 0) as energy,
                    COALESCE(SUM(lack_concentration), 0) as concentration,
                    COALESCE(SUM(suicidal_thoughts), 0) as suicidal,
                    COALESCE(SUM(temper_outburst), 0) as temper,
                    COALESCE(SUM(panic_attack), 0) as panic,
                    COALESCE(SUM(mood_swing), 0) as mood,
                    COALESCE(SUM(medical_issue), 0) as medical
                FROM symptoms
            """)
            symptom_counts = cursor.fetchone()
            
            conn.close()
            
            # Ensure symptom_counts is a tuple of integers
            if symptom_counts:
                symptom_counts = tuple(int(x) for x in symptom_counts)
            else:
                symptom_counts = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            
            return {
                'total_predictions': total_predictions,
                'predictions_by_type': predictions_by_type if predictions_by_type else [],
                'symptom_counts': symptom_counts
            }
            
        except Error as e:
            st.error(f"Error fetching statistics: {e}")
            return None
    return None

# Load model
@st.cache_resource
def load_model():
    """Load the trained model"""
    try:
        model_package = joblib.load('depression_prediction_model.pkl')
        return model_package
    except:
        st.warning("Model file not found. Please ensure 'depression_prediction_model.pkl' is in the same directory.")
        return None

def predict_depression(symptoms_dict, model_package):
    """Predict depression type based on symptoms"""
    if not model_package:
        return "Model not loaded", {}, 0.0
    
    model = model_package['model']
    scaler = model_package['scaler']
    label_encoder = model_package['label_encoder']
    
    # Create a dataframe with all possible columns
    all_columns = model_package['feature_names']
    input_data = pd.DataFrame(0, index=[0], columns=all_columns)
    
    # Fill in the provided symptoms
    for symptom, value in symptoms_dict.items():
        if symptom in input_data.columns:
            if isinstance(value, str):
                input_data[symptom] = 1 if value.upper() == 'Y' else 0
            else:
                input_data[symptom] = value
        elif symptom == 'Age':
            age_col = f'Age_{symptoms_dict["Age"]}'
            if age_col in input_data.columns:
                input_data[age_col] = 1
    
    # Scale the input
    input_scaled = scaler.transform(input_data)
    
    # Make prediction
    prediction_encoded = model.predict(input_scaled)[0]
    prediction_prob = model.predict_proba(input_scaled)[0]
    
    # Decode the prediction
    prediction = label_encoder.inverse_transform([prediction_encoded])[0]
    confidence = prediction_prob[prediction_encoded]
    
    # Get probabilities for all classes
    probabilities = {}
    for i, prob in enumerate(prediction_prob):
        class_name = label_encoder.inverse_transform([i])[0]
        probabilities[class_name] = float(prob)
    
    return prediction, probabilities, confidence

# Main app
def main():
    # Initialize database
    conn = create_connection()
    if conn:
        create_tables(conn)
        conn.close()
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/brain.png", width=100)
        st.title("🧠 Depression Diagnosis")
        
        menu = st.selectbox(
            "Navigation",
            ["🏠 Home", "📋 Self-Assessment", "📊 Statistics", "📚 Precautions Database", "⚙️ Admin"]
        )
        
        st.markdown("---")
        st.markdown("### About")
        st.info("""
        This tool helps identify potential depression types based on symptoms.
        **Not a substitute for professional medical advice.**
        """)
        
        # Emergency resources
        with st.expander("🚨 Emergency Resources"):
            st.markdown("""
            **If you're in crisis:**
            - National Suicide Prevention Lifeline: **1-800-273-8255**
            - Crisis Text Line: Text **HOME** to **741741**
            - Emergency Services: **911**
            
            **International Helplines:**
            - International Association for Suicide Prevention: [Find a Helpline](https://www.iasp.info/resources/Crisis_Centres/)
            """)
        with st.sidebar:
            st.image("https://img.icons8.com/color/96/000000/brain.png", width=100)
            st.title("🧠 Depression Diagnosis")
    
    menu = st.selectbox(
        "Navigation",
        ["🏠 Home", "📋 Self-Assessment", "💬 Chat with Dr. Sara", "📊 Statistics", "📚 Precautions Database", "⚙️ Admin"]
    )
    # ... baaki sidebar code
    
    # Home page
    if menu == "🏠 Home":
        st.markdown('<h1 class="main-header">🧠 Depression Diagnosis Assistant</h1>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            <div class="section-box">
            <h3>Welcome to the Depression Diagnosis Assistant</h3>
            <p>This tool uses machine learning to help identify potential types of depression based on symptoms.</p>
            <p>It is designed to:</p>
            <ul>
                <li>Provide preliminary assessment based on symptoms</li>
                <li>Offer information about different depression types</li>
                <li>Suggest appropriate precautions and next steps</li>
                <li>Track symptoms over time (with user consent)</li>
            </ul>
            <p><strong>Important:</strong> This is not a substitute for professional medical diagnosis or treatment.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="emergency-box">', unsafe_allow_html=True)
            st.markdown("### 🚨 Emergency")
            st.markdown("""
            If you or someone you know is in immediate danger:
            
            **Call 911** or go to the nearest emergency room
            
            **Suicide Prevention Lifeline:**
            1-800-273-8255
            """)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick symptom checker
        st.markdown('<h3 class="sub-header">Quick Symptom Check</h3>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            hopeless = st.selectbox("Feeling hopeless?", ["Select", "Yes", "No"], key="quick1")
        
        with col2:
            interest = st.selectbox("Loss of interest?", ["Select", "Yes", "No"], key="quick2")
        
        with col3:
            sleep = st.selectbox("Sleep disturbances?", ["Select", "Yes", "No"], key="quick3")
        
        if st.button("Quick Check", type="primary"):
            if any(x == "Yes" for x in [hopeless, interest, sleep]):
                st.warning("⚠️ You're experiencing some symptoms associated with depression. Consider taking the full assessment or consulting a professional.")
            else:
                st.success("✅ No concerning symptoms detected in this quick check.")
    
    # Self-Assessment page
    elif menu == "📋 Self-Assessment":
        st.markdown('<h1 class="main-header">Self-Assessment Questionnaire</h1>', unsafe_allow_html=True)
        
        # Generate patient ID
        patient_id = f"PAT{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Personal information
        with st.expander("👤 Personal Information", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                age_group = st.selectbox(
                    "Age Group",
                    ["youth", "middel-aged", "adult", "elderly"],
                    help="Select your age group"
                )
            with col2:
                gender = st.selectbox(
                    "Gender",
                    ["Male", "Female", "Other", "Prefer not to say"],
                    help="For statistical purposes only"
                )
        
        # Symptoms questionnaire
        st.markdown('<h3 class="sub-header">Symptoms Assessment</h3>', unsafe_allow_html=True)
        st.markdown("Please answer the following questions about symptoms experienced in the last 2 weeks:")
        
        symptoms = {}
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="symptom-card">', unsafe_allow_html=True)
            symptoms['Feelinghopeless'] = st.radio(
                "1. Feeling hopeless or pessimistic?",
                ["Yes", "No"],
                key="hopeless"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="symptom-card">', unsafe_allow_html=True)
            symptoms['lossofinterest'] = st.radio(
                "2. Loss of interest or pleasure in activities?",
                ["Yes", "No"],
                key="interest"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="symptom-card">', unsafe_allow_html=True)
            symptoms['appetitechange'] = st.radio(
                "3. Significant appetite or weight changes?",
                ["Yes", "No"],
                key="appetite"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="symptom-card">', unsafe_allow_html=True)
            symptoms['distrubedsleepcycle'] = st.radio(
                "4. Sleep disturbances (insomnia or oversleeping)?",
                ["Yes", "No"],
                key="sleep"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="symptom-card">', unsafe_allow_html=True)
            symptoms['low energy'] = st.radio(
                "5. Low energy or fatigue?",
                ["Yes", "No"],
                key="energy"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="symptom-card">', unsafe_allow_html=True)
            symptoms['lackofconcentration'] = st.radio(
                "6. Difficulty concentrating or making decisions?",
                ["Yes", "No"],
                key="concentration"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="symptom-card">', unsafe_allow_html=True)
            symptoms['suicidalthoughts'] = st.radio(
                "7. Thoughts of death or suicide?",
                ["Yes", "No"],
                key="suicidal"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="symptom-card">', unsafe_allow_html=True)
            symptoms['temperoutburst'] = st.radio(
                "8. Frequent temper outbursts or irritability?",
                ["Yes", "No"],
                key="temper"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="symptom-card">', unsafe_allow_html=True)
            symptoms['panicattack'] = st.radio(
                "9. Panic attacks or severe anxiety?",
                ["Yes", "No"],
                key="panic"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="symptom-card">', unsafe_allow_html=True)
            symptoms['moodswing'] = st.radio(
                "10. Frequent mood swings?",
                ["Yes", "No"],
                key="mood"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="symptom-card">', unsafe_allow_html=True)
        symptoms['medicalissue'] = st.radio(
            "11. Known medical conditions that might affect mood?",
            ["Yes", "No"],
            key="medical"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        symptoms['Age'] = age_group
        
        
        
        # Prediction button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 Analyze Symptoms", type="primary", use_container_width=True):
                with st.spinner("Analyzing symptoms..."):
                    # Load model
                    model_package = load_model()
                    
                    if model_package:
                        # Make prediction
                        prediction, probabilities, confidence = predict_depression(symptoms, model_package)
                        
                        # Display results
                        st.markdown(f'<div class="prediction-card">', unsafe_allow_html=True)
                        st.markdown(f"## Predicted: {prediction}")
                        st.markdown(f"### Confidence: {confidence:.1%}")
                        st.markdown(f"**Patient ID:** {patient_id}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Probability chart
                        fig = go.Figure(data=[
                            go.Bar(
                                x=list(probabilities.keys()),
                                y=list(probabilities.values()),
                                marker_color=['#3B82F6' if x == prediction else '#94A3B8' for x in probabilities.keys()]
                            )
                        ])
                        fig.update_layout(
                            title="Prediction Probabilities",
                            xaxis_title="Depression Type",
                            yaxis_title="Probability",
                            yaxis_tickformat=".0%",
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Get and display precautions
                        precautions = get_precautions(prediction)
                        if precautions:
                            st.markdown('<h3 class="sub-header">📋 Recommended Precautions</h3>', unsafe_allow_html=True)
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown('<div class="precaution-card">', unsafe_allow_html=True)
                                st.markdown("#### 🚨 Immediate Actions")
                                for action in precautions['immediate_actions'].split(', '):
                                    st.markdown(f"• {action}")
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                st.markdown('<div class="precaution-card">', unsafe_allow_html=True)
                                st.markdown("#### 🏥 Professional Help")
                                for help_item in precautions['professional_help'].split(', '):
                                    st.markdown(f"• {help_item}")
                                st.markdown('</div>', unsafe_allow_html=True)
                            
                            with col2:
                                st.markdown('<div class="precaution-card">', unsafe_allow_html=True)
                                st.markdown("#### 🏃 Lifestyle Changes")
                                for change in precautions['lifestyle_changes'].split(', '):
                                    st.markdown(f"• {change}")
                                st.markdown('</div>', unsafe_allow_html=True)
                                
                                st.markdown('<div class="precaution-card">', unsafe_allow_html=True)
                                st.markdown("#### 📞 Emergency Contacts")
                                for contact in precautions['emergency_contacts'].split(', '):
                                    st.markdown(f"• {contact}")
                                st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Save to database
                        if st.checkbox("Save assessment to database (anonymous)"):
                            symptoms_dict = {k: 1 if v == "Yes" else 0 for k, v in symptoms.items() if k != 'Age'}
                            symptoms_dict['Age'] = age_group
                            symptoms_dict['gender'] = gender
                            
                            if save_prediction_to_db(patient_id, symptoms_dict, prediction, confidence, probabilities):
                                st.success("✅ Assessment saved successfully!")
                                st.info(f"Your Patient ID: **{patient_id}** - Save this for future reference")
                        
                        # Warning message
                        st.markdown("""
                        <div class="emergency-box">
                        <h4>⚠️ Important Disclaimer</h4>
                        <p>This prediction is based on machine learning algorithms and should not be considered a medical diagnosis. 
                        Always consult with qualified healthcare professionals for proper diagnosis and treatment.</p>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Statistics page
    elif menu == "📊 Statistics":
        st.markdown('<h1 class="main-header">📊 Statistics Dashboard</h1>', unsafe_allow_html=True)
        
        stats = get_statistics()
        
        if stats and stats['total_predictions'] > 0:
            # Key metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown('<div class="stat-box">', unsafe_allow_html=True)
                st.metric("Total Assessments", stats['total_predictions'])
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="stat-box">', unsafe_allow_html=True)
                if stats['predictions_by_type']:
                    most_common = stats['predictions_by_type'][0]
                    st.metric("Most Common Type", most_common[0])
                else:
                    st.metric("Most Common Type", "No data")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="stat-box">', unsafe_allow_html=True)
                if stats['symptom_counts']:
                    symptom_counts_list = list(stats['symptom_counts'])
                    # Find the index of the maximum value safely
                    if any(x > 0 for x in symptom_counts_list):
                        max_symptom_index = max(range(len(symptom_counts_list)), key=lambda i: symptom_counts_list[i])
                        symptom_names = ['Hopeless', 'Interest Loss', 'Appetite', 'Sleep', 'Energy', 
                                        'Concentration', 'Suicidal', 'Temper', 'Panic', 'Mood', 'Medical']
                        st.metric("Most Common Symptom", symptom_names[max_symptom_index])
                    else:
                        st.metric("Most Common Symptom", "No data")
                else:
                    st.metric("Most Common Symptom", "No data")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                # Predictions by type chart
                if stats['predictions_by_type']:
                    types, counts = zip(*stats['predictions_by_type'])
                    fig = px.pie(
                        names=types, 
                        values=counts,
                        title="Distribution of Predicted Types",
                        color_discrete_sequence=px.colors.sequential.RdBu
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No prediction data available for chart.")
            
            with col2:
                # Symptoms chart
                if stats['symptom_counts']:
                    symptom_counts_list = list(stats['symptom_counts'])
                    if any(x > 0 for x in symptom_counts_list):
                        symptom_names = ['Hopeless', 'Interest Loss', 'Appetite', 'Sleep', 'Energy', 
                                        'Concentration', 'Suicidal', 'Temper', 'Panic', 'Mood', 'Medical']
                        fig = px.bar(
                            x=symptom_names,
                            y=symptom_counts_list,
                            title="Most Common Symptoms",
                            labels={'x': 'Symptom', 'y': 'Count'},
                            color=symptom_counts_list,
                            color_continuous_scale='Blues'
                        )
                        fig.update_layout(xaxis_tickangle=45)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No symptom data available for chart.")
                else:
                    st.info("No symptom data available for chart.")
            
            # Raw data
            with st.expander("View Raw Data"):
                if stats['predictions_by_type']:
                    df_stats = pd.DataFrame(stats['predictions_by_type'], columns=['Type', 'Count'])
                    st.dataframe(df_stats, use_container_width=True)
                else:
                    st.info("No data available.")
        else:
            st.info("No statistics available yet. Complete some assessments first.")
    
    # Precautions Database page
    elif menu == "📚 Precautions Database":
        st.markdown('<h1 class="main-header">📚 Precautions Database</h1>', unsafe_allow_html=True)
        
        depression_types = ['Clinical Depression', 'PDD', 'Medical Depression', 'DMDD', 'PMDD']
        selected_type = st.selectbox("Select Depression Type", depression_types)
        
        precautions = get_precautions(selected_type)
        
        if precautions:
            st.markdown(f'<h3 class="sub-header">Precautions for {selected_type}</h3>', unsafe_allow_html=True)
            
            tabs = st.tabs(["🚨 Immediate Actions", "🏃 Lifestyle Changes", "🏥 Professional Help", "📞 Emergency Contacts"])
            
            with tabs[0]:
                st.markdown('<div class="section-box">', unsafe_allow_html=True)
                actions = precautions['immediate_actions'].split(', ')
                for action in actions:
                    st.markdown(f"• **{action}**")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tabs[1]:
                st.markdown('<div class="section-box">', unsafe_allow_html=True)
                changes = precautions['lifestyle_changes'].split(', ')
                for change in changes:
                    st.markdown(f"• **{change}**")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tabs[2]:
                st.markdown('<div class="section-box">', unsafe_allow_html=True)
                help_items = precautions['professional_help'].split(', ')
                for item in help_items:
                    st.markdown(f"• **{item}**")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tabs[3]:
                st.markdown('<div class="section-box">', unsafe_allow_html=True)
                contacts = precautions['emergency_contacts'].split(', ')
                for contact in contacts:
                    st.markdown(f"• **{contact}**")
                st.markdown('</div>', unsafe_allow_html=True)
        
        # General mental health tips
        st.markdown('<h3 class="sub-header">General Mental Health Tips</h3>', unsafe_allow_html=True)
        
        tips = [
            "Practice regular physical exercise (30 minutes, 3-5 times per week)",
            "Maintain a consistent sleep schedule",
            "Eat a balanced diet rich in fruits, vegetables, and omega-3 fatty acids",
            "Practice mindfulness or meditation daily",
            "Stay connected with supportive friends and family",
            "Limit alcohol and avoid recreational drugs",
            "Set realistic goals and break tasks into smaller steps",
            "Seek professional help when needed - it's a sign of strength",
            "Keep a gratitude journal",
            "Spend time in nature regularly"
        ]
        
        for i, tip in enumerate(tips, 1):
            st.markdown(f"{i}. {tip}")
            
    # Chatbot page
    elif menu == "💬 Chat with Dr. Sara":
        st.markdown('<h1 class="main-header">💬 Chat with Dr. Sara</h1>', unsafe_allow_html=True)
        
        # Create two columns
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Chatbot interface
            render_chatbot()
        
        with col2:
            # Quick resources sidebar
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h3 style="margin-top:0;">✨ Quick Tips</h3>
                <ul style="list-style-type: none; padding-left: 0;">
                    <li>✓ Be honest about your feelings</li>
                    <li>✓ Take deep breaths if overwhelmed</li>
                    <li>✓ Remember you're not alone</li>
                    <li>✓ Professional help is available</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            # What you can ask about
            with st.expander("💡 What can I ask?", expanded=True):
                st.markdown("""
                **You can ask Dr. Sara about:**
                - Depression symptoms
                - Treatment options
                - Different depression types
                - Self-care tips
                - Coping strategies
                - Emergency resources
                - Just share how you're feeling
                
                **Example questions:**
                - "What are depression symptoms?"
                - "How is depression treated?"
                - "Tell me about Clinical Depression"
                - "I'm feeling sad today"
                - "What is CBT therapy?"
                """)
            
            # Disclaimer
            with st.expander("⚠️ Important Disclaimer"):
                st.markdown("""
                Dr. Sara is an AI assistant designed to provide information and support. 
                She is **NOT** a replacement for:
                - Professional medical diagnosis
                - Licensed therapist or psychiatrist
                - Emergency medical services
                
                Always consult with qualified healthcare providers for proper diagnosis and treatment.
                """)
    
    # Admin page
    elif menu == "⚙️ Admin":
        st.markdown('<h1 class="main-header">⚙️ Admin Panel</h1>', unsafe_allow_html=True)
        
        password = st.text_input("Enter Admin Password", type="password")
        
        # Simple password check (in production, use proper authentication)
        if password == "admin123":  # Change this in production
            st.success("✅ Admin access granted")
            
            tab1, tab2, tab3 = st.tabs(["📊 Database Stats", "📥 Export Data", "🔄 Update Precautions"])
            
            with tab1:
                conn = create_connection()
                if conn:
                    cursor = conn.cursor()
                    
                    # Table statistics
                    tables = ['patients', 'symptoms', 'predictions', 'precautions']
                    for table in tables:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        count = cursor.fetchone()[0]
                        st.metric(f"{table.capitalize()} Records", count)
                    
                    # Recent predictions
                    cursor.execute("""
                        SELECT p.patient_id, pr.predicted_type, pr.confidence, pr.timestamp
                        FROM predictions pr
                        JOIN patients p ON pr.patient_id = p.patient_id
                        ORDER BY pr.timestamp DESC
                        LIMIT 10
                    """)
                    recent = cursor.fetchall()
                    
                    if recent:
                        st.subheader("Recent Predictions")
                        df_recent = pd.DataFrame(recent, columns=['Patient ID', 'Type', 'Confidence', 'Timestamp'])
                        st.dataframe(df_recent, use_container_width=True)
                    
                    conn.close()
            
            with tab2:
                st.subheader("Export Data")
                
                conn = create_connection()
                if conn:
                    export_option = st.selectbox("Select data to export", 
                                                ["All Predictions", "Symptoms Data", "Patient Demographics"])
                    
                    if export_option == "All Predictions":
                        query = """
                            SELECT p.*, s.*, pr.*
                            FROM predictions pr
                            JOIN patients p ON pr.patient_id = p.patient_id
                            JOIN symptoms s ON pr.patient_id = s.patient_id
                        """
                    elif export_option == "Symptoms Data":
                        query = "SELECT * FROM symptoms"
                    else:
                        query = "SELECT * FROM patients"
                    
                    df_export = pd.read_sql_query(query, conn)
                    conn.close()
                    
                    st.dataframe(df_export, use_container_width=True)
                    
                    csv = df_export.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"depression_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            
            with tab3:
                st.subheader("Update Precautions")
                
                conn = create_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT depression_type FROM precautions")
                    existing_types = [row[0] for row in cursor.fetchall()]
                    
                    update_type = st.selectbox("Select type to update", existing_types)
                    
                    if update_type:
                        cursor.execute("SELECT * FROM precautions WHERE depression_type = ?", (update_type,))
                        current = cursor.fetchone()
                        
                        if current:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                immediate = st.text_area("Immediate Actions", 
                                                        value=current[1], 
                                                        height=150)
                                lifestyle = st.text_area("Lifestyle Changes", 
                                                        value=current[2], 
                                                        height=150)
                            
                            with col2:
                                professional = st.text_area("Professional Help", 
                                                          value=current[3], 
                                                          height=150)
                                emergency = st.text_area("Emergency Contacts", 
                                                        value=current[4], 
                                                        height=150)
                            
                            if st.button("Update Precautions", type="primary"):
                                cursor.execute("""
                                    UPDATE precautions 
                                    SET immediate_actions = ?, 
                                        lifestyle_changes = ?, 
                                        professional_help = ?, 
                                        emergency_contacts = ?
                                    WHERE depression_type = ?
                                """, (immediate, lifestyle, professional, emergency, update_type))
                                conn.commit()
                                st.success("✅ Precautions updated successfully!")
                    
                    conn.close()

if __name__ == "__main__":
    main()