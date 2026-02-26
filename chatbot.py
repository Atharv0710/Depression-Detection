# chatbot.py - Simple Depression Support Chatbot

import streamlit as st
from datetime import datetime
import random
import re

class DepressionChatbot:
    def __init__(self):
        """Initialize the chatbot with responses"""
        self.bot_name = "Dr. Sara"
        self.user_name = "Friend"
        
        # Response database - categorized by intent
        self.responses = {
            "greeting": [
                "Hello! I'm Dr. Sara, your mental health assistant. How are you feeling today? 💙",
                "Hi there! I'm here to support you. What's on your mind?",
                "Welcome! I'm Dr. Sara. Feel free to share what you're going through.",
                "Namaste! I'm here to listen and help. How can I support you today?"
            ],
            
            "how_are_you": [
                "I'm here and ready to listen to you. How are you doing today?",
                "I'm doing well, thank you for asking! More importantly, how are you feeling?",
                "I'm here to support you. Tell me about your day."
            ],
            
            "feeling_sad": [
                "I'm sorry you're feeling sad. It's okay to not be okay. Would you like to talk about what's making you feel this way?",
                "Sadness is a valid emotion. Remember that you're not alone in this feeling. Can you tell me more about what's happening?",
                "It takes courage to acknowledge your feelings. I'm here to listen. What's been on your mind lately?"
            ],
            
            "feeling_hopeless": [
                "I hear that you're feeling hopeless. These feelings can be overwhelming, but they don't last forever. Have you considered talking to a professional who can help?",
                "Hopelessness can make everything feel dark. Please remember that there is help available. Would you like me to share some resources?",
                "Your feelings are valid. Sometimes hopelessness can be a symptom of depression. Would you like to take our assessment to understand better?"
            ],
            
            "symptoms": [
                "Common symptoms of depression include:\n\n• Persistent sadness or empty mood\n• Loss of interest in activities\n• Changes in appetite/weight\n• Sleep disturbances\n• Fatigue or low energy\n• Difficulty concentrating\n• Feelings of worthlessness\n• Thoughts of death or suicide\n\nWould you like to take our assessment to check your symptoms?",
                "Depression affects everyone differently. Some people experience physical symptoms like fatigue and sleep changes, while others feel emotional symptoms like sadness and hopelessness. Our assessment can help identify your specific symptoms."
            ],
            
            "treatment": [
                "Depression is very treatable! Common treatment options include:\n\n1. **Psychotherapy** - Like Cognitive Behavioral Therapy (CBT)\n2. **Medication** - Antidepressants prescribed by psychiatrists\n3. **Lifestyle changes** - Exercise, healthy diet, good sleep\n4. **Support groups** - Connecting with others\n\nWould you like more information about any of these?",
                "The best treatment depends on your specific type of depression. After taking our assessment, you'll get personalized recommendations. Would you like to try it?"
            ],
            
            "cbt": [
                "Cognitive Behavioral Therapy (CBT) is a very effective therapy for depression. It helps you identify and change negative thought patterns. Would you like to learn some simple CBT techniques?",
                "CBT focuses on the connection between thoughts, feelings, and behaviors. A therapist can help you develop coping strategies. I can share some basic techniques if you're interested."
            ],
            
            "medication": [
                "Antidepressants can be helpful for many people with depression. They work by balancing brain chemicals. Important points:\n\n• Only psychiatrists can prescribe them\n• They take 2-4 weeks to start working\n• Different types work for different people\n• Always consult a doctor before starting\n\nWould you like more information about specific medications?",
                "Medication is often combined with therapy for best results. If you're considering medication, please consult a psychiatrist who can guide you based on your specific situation."
            ],
            
            "lifestyle": [
                "Lifestyle changes can make a big difference:\n\n• **Exercise**: Even 15-30 minutes daily helps\n• **Sleep**: Try to maintain a regular sleep schedule\n• **Diet**: Eat balanced meals, stay hydrated\n• **Social connection**: Talk to trusted friends/family\n• **Stress reduction**: Try meditation or deep breathing\n\nWould you like specific tips for any of these?",
                "Small changes add up! Start with one small goal, like a short walk or calling a friend. What do you think would help you most?"
            ],
            
            "assessment": [
                "Our assessment asks 11 questions about symptoms you may have experienced in the last 2 weeks. It can help identify potential depression types. Click the **'Self-Assessment'** tab in the menu to start! 📋",
                "The assessment is quick (about 3 minutes) and completely anonymous. It will give you immediate results with confidence scores. Ready to try it? Go to the Self-Assessment section!"
            ],
            
            "precautions": [
                "I can provide precautions for different depression types. Which one would you like to know about?\n\n• **Clinical Depression**\n• **PDD** (Persistent Depressive Disorder)\n• **Medical Depression**\n• **DMDD** (Disruptive Mood Dysregulation)\n• **PMDD** (Premenstrual Dysphoric)\n\nJust type the name!",
                "Visit the **'Precautions Database'** section for detailed information about each depression type, including immediate actions, lifestyle changes, and professional help options."
            ],
            
            "clinical_depression": [
                "**Precautions for Clinical Depression:**\n\n🚨 **Immediate Actions:**\n• Consult psychiatrist immediately\n• Start therapy sessions\n• Consider medication if prescribed\n\n🏃 **Lifestyle Changes:**\n• Regular exercise\n• Balanced diet\n• Consistent sleep schedule\n• Mindfulness meditation\n\n🏥 **Professional Help:**\n• Cognitive Behavioral Therapy (CBT)\n• Psychiatrist consultation\n• Support groups\n\n📞 **Emergency Contacts:**\n• National Suicide Prevention Lifeline: 1-800-273-8255\n• Crisis Text Line: Text HOME to 741741"
            ],
            
            "pdd": [
                "**Precautions for PDD (Persistent Depressive Disorder):**\n\n🚨 **Immediate Actions:**\n• Schedule regular therapy sessions\n• Monitor symptom patterns\n• Keep a mood journal\n\n🏃 **Lifestyle Changes:**\n• Establish daily routine\n• Social engagement activities\n• Stress management techniques\n\n🏥 **Professional Help:**\n• Long-term psychotherapy\n• Regular psychiatric follow-ups\n• Group therapy\n\n📞 **Emergency Contacts:**\n• Therapist contact info\n• Trusted family member\n• Local mental health services"
            ],
            
            "medical_depression": [
                "**Precautions for Medical Depression:**\n\n🚨 **Immediate Actions:**\n• Consult with primary physician\n• Review current medications\n• Address underlying medical conditions\n\n🏃 **Lifestyle Changes:**\n• Manage underlying health condition\n• Regular medical checkups\n• Medication adherence\n\n🏥 **Professional Help:**\n• Collaborative care with physicians\n• Psychiatrist for comorbid conditions\n\n📞 **Emergency Contacts:**\n• Primary care physician\n• Emergency medical services: 911"
            ],
            
            "dmdd": [
                "**Precautions for DMDD (Disruptive Mood Dysregulation Disorder):**\n\n🚨 **Immediate Actions:**\n• Behavioral therapy for children\n• Parent management training\n• School intervention if needed\n\n🏃 **Lifestyle Changes:**\n• Consistent daily structure\n• Clear behavioral expectations\n• Positive reinforcement\n\n🏥 **Professional Help:**\n• Child psychologist\n• Family therapy\n• School counselor involvement\n\n📞 **Emergency Contacts:**\n• Pediatrician\n• Child mental health services\n• School counselor"
            ],
            
            "pmdd": [
                "**Precautions for PMDD (Premenstrual Dysphoric Disorder):**\n\n🚨 **Immediate Actions:**\n• Track menstrual cycle symptoms\n• Consult gynecologist\n• Consider hormonal treatment\n\n🏃 **Lifestyle Changes:**\n• Dietary changes (reduce salt/caffeine)\n• Regular exercise\n• Stress reduction techniques\n\n🏥 **Professional Help:**\n• Gynecologist consultation\n• Psychiatrist for symptom management\n\n📞 **Emergency Contacts:**\n• Gynecologist contact\n• Women's health clinic\n• Local support groups"
            ],
            
            "emergency": [
                "🚨 **IMMEDIATE HELP AVAILABLE** 🚨\n\nIf you're in crisis, please reach out right now:\n\n📞 **National Suicide Prevention Lifeline:**\n**1-800-273-8255** (24/7, Free, Confidential)\n\n📱 **Crisis Text Line:**\nText **HOME** to **741741**\n\n🚑 **Emergency Services:**\nCall **911** or go to nearest emergency room\n\nYou are not alone. Help is available and you matter! ❤️",
                "⚠️ **CRISIS RESOURCES** ⚠️\n\n• **Lifeline:** 1-800-273-8255\n• **Crisis Text:** HOME to 741741\n• **Emergency:** 911\n\nPlease reach out - people care about you!"
            ],
            
            "suicidal": [
                "🚨 **Please reach out for help immediately** 🚨\n\nThese thoughts are serious and you deserve support:\n\n📞 **988 Suicide & Crisis Lifeline:** 988\n📞 **National Suicide Prevention:** 1-800-273-8255\n📱 **Crisis Text Line:** Text HOME to 741741\n\nYou are valuable and this feeling won't last forever. Help is available 24/7! ❤️"
            ],
            
            "anxiety": [
                "Anxiety often co-occurs with depression. Some coping strategies:\n\n• Deep breathing: Inhale 4 counts, hold 4, exhale 6\n• Grounding technique: Name 5 things you see, 4 you feel, 3 you hear, 2 you smell, 1 you taste\n• Progressive muscle relaxation\n• Limit caffeine and alcohol\n\nWould you like more anxiety management tips?"
            ],
            
            "sleep": [
                "Sleep problems are common in depression. Tips for better sleep:\n\n• Go to bed same time each night\n• No screens 1 hour before bed\n• Keep bedroom dark and cool\n• Avoid caffeine after 2 PM\n• Try relaxation techniques before bed\n\nWould you like a guided relaxation exercise?"
            ],
            
            "stress": [
                "Stress management is important for mental health:\n\n• Take short breaks throughout the day\n• Practice mindfulness or meditation\n• Talk to someone you trust\n• Write in a journal\n• Do something you enjoy, even for 10 minutes\n\nWhat usually helps you relax?"
            ],
            
            "self_care": [
                "Self-care isn't selfish - it's necessary! Ideas:\n\n• Take a warm bath\n• Read a book\n• Listen to calming music\n• Spend time in nature\n• Connect with a friend\n• Practice gratitude\n• Do a hobby you enjoy\n\nWhat self-care activity appeals to you most?"
            ],
            
            "thanks": [
                "You're very welcome! Remember, I'm here whenever you need to talk. Take care of yourself! 💙",
                "Happy to help! Feel free to chat anytime. You're doing great by reaching out! 🌟",
                "You're welcome! Remember that seeking help is a sign of strength, not weakness. Proud of you! 💪"
            ],
            
            "goodbye": [
                "Take care of yourself! Remember, you're not alone in this journey. Come back anytime you need support. 💙",
                "Wishing you peace and healing. Feel free to reach out again. Goodbye for now! 🌸",
                "Take care! If things get difficult, remember help is available 24/7. You matter! ❤️"
            ],
            
            "name": [
                "I'm Dr. Sara, your mental health assistant! What's your name?",
                "My name is Dr. Sara. And you are?",
                "You can call me Dr. Sara! What should I call you?"
            ],
            
            "introduce": [
                "I'm Dr. Sara, a mental health assistant designed to provide support and information about depression. I can help with:\n\n• Information about depression symptoms\n• Guidance about treatment options\n• Precautions for different depression types\n• Self-care tips and coping strategies\n• Emergency resources\n\nHow can I help you today?"
            ],
            
            "capabilities": [
                "I can help you with:\n\n✅ Information about depression symptoms\n✅ Treatment options explained\n✅ Precautions for 5 depression types\n✅ Self-care and coping tips\n✅ Emergency resources\n✅ Gentle support and listening\n\nI cannot:\n❌ Provide medical diagnosis\n❌ Prescribe medication\n❌ Replace professional therapy\n\nWhat would you like to know more about?"
            ],
            
            "age_group": [
                "Depression affects people of all ages - youth, middle-aged adults, and elderly. Our assessment works for all age groups! What's your age group?",
                "Different age groups may experience depression differently. Our assessment considers your age group for more accurate results."
            ],
            
            "default": [
                "I'm here to listen and support you. Could you tell me more about how you're feeling?",
                "That sounds challenging. Would you like to talk about it, or would you prefer information about depression symptoms or treatments?",
                "I want to help. You can ask me about symptoms, treatments, precautions, or just share how you're feeling.",
                "I'm here for you. Would you like to take our assessment, learn about depression, or just talk?"
            ]
        }
        
        # Keywords mapping for intent detection
        self.keywords = {
            "greeting": ["hi", "hello", "hey", "namaste", "good morning", "good afternoon", "good evening"],
            "how_are_you": ["how are you", "how do you do", "what's up", "kaise ho"],
            "feeling_sad": ["sad", "unhappy", "down", "blue", "crying", "tears", "depressed"],
            "feeling_hopeless": ["hopeless", "worthless", "no hope", "give up", "meaningless"],
            "symptoms": ["symptom", "signs", "indicator", "how to know", "identify"],
            "treatment": ["treatment", "cure", "therapy", "medication", "medicine", "help"],
            "cbt": ["cbt", "cognitive", "behavioral", "therapy", "psychotherapy"],
            "medication": ["medication", "medicine", "antidepressant", "pill", "drug", "prescription"],
            "lifestyle": ["lifestyle", "exercise", "diet", "sleep", "routine", "habit"],
            "assessment": ["assessment", "test", "quiz", "questionnaire", "evaluate", "check"],
            "precautions": ["precaution", "advice", "suggest", "recommend", "what to do", "guide"],
            "clinical_depression": ["clinical", "major depression", "mdd"],
            "pdd": ["pdd", "persistent", "dysthymia"],
            "medical_depression": ["medical depression", "secondary depression"],
            "dmdd": ["dmdd", "disruptive", "mood dysregulation", "children", "child"],
            "pmdd": ["pmdd", "premenstrual", "period", "menstrual"],
            "emergency": ["emergency", "urgent", "crisis", "immediate", "help now"],
            "suicidal": ["suicide", "kill myself", "end my life", "die", "death", "self harm"],
            "anxiety": ["anxiety", "anxious", "worry", "panic", "nervous", "stress"],
            "sleep": ["sleep", "insomnia", "tired", "fatigue", "energy"],
            "stress": ["stress", "pressure", "overwhelmed", "burnout"],
            "self_care": ["self care", "self-care", "care for myself", "relax", "calm"],
            "thanks": ["thank", "thanks", "appreciate", "grateful"],
            "goodbye": ["bye", "goodbye", "see you", "tata", "exit", "quit"],
            "name": ["your name", "who are you", "aap kaun"],
            "introduce": ["introduce", "about you", "tell me about yourself"],
            "capabilities": ["can you do", "capabilities", "what can you", "help with"],
            "age_group": ["age", "age group", "youth", "adult", "elderly"]
        }
    
    def detect_intent(self, user_input):
        """Detect user intent from input text"""
        user_input = user_input.lower().strip()
        
        # Check each keyword category
        for intent, words in self.keywords.items():
            for word in words:
                if word in user_input:
                    return intent
        
        # Default intent if no match
        return "default"
    
    def get_response(self, user_input):
        """Generate response based on user input"""
        intent = self.detect_intent(user_input)
        
        # Special handling for name
        if intent == "name":
            return random.choice(self.responses["name"])
        
        # Special handling for greeting
        if intent == "greeting" and hasattr(self, 'user_name') and self.user_name != "Friend":
            return f"Hello again, {self.user_name}! How are you feeling today?"
        
        # Get random response from the intent category
        if intent in self.responses:
            return random.choice(self.responses[intent])
        else:
            return random.choice(self.responses["default"])
    
    def set_user_name(self, name):
        """Set user's name for personalized responses"""
        if name and name.strip():
            self.user_name = name.strip()

def render_chatbot():
    """Render the chatbot in Streamlit interface"""
    
    # Initialize session state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
        st.session_state.chatbot = DepressionChatbot()
        st.session_state.user_name_set = False
    
    # Chatbot container
    with st.container():
        # Chat header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 💬 Chat with Dr. Sara")
            st.caption("Your compassionate mental health assistant")
        with col2:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_messages = []
                st.session_state.user_name_set = False
                st.rerun()
        
        # User name input (optional)
        if not st.session_state.user_name_set:
            name_col1, name_col2 = st.columns([3, 1])
            with name_col1:
                user_name = st.text_input("What's your name? (Optional)", placeholder="Enter your name...")
            with name_col2:
                if st.button("✅ Set Name") and user_name:
                    st.session_state.chatbot.set_user_name(user_name)
                    st.session_state.user_name_set = True
                    # Add welcome message
                    st.session_state.chat_messages.append({
                        "role": "bot",
                        "content": f"Nice to meet you, {user_name}! How can I help you today? 💙"
                    })
                    st.rerun()
        
        # Chat history display
        chat_container = st.container(height=400)
        with chat_container:
            for message in st.session_state.chat_messages:
                if message["role"] == "user":
                    st.chat_message("user").write(message["content"])
                else:
                    st.chat_message("assistant").write(message["content"])
            
            # If no messages, show welcome message
            if not st.session_state.chat_messages:
                welcome_msg = """Hello! I'm Dr. Sara, your mental health assistant. 🌸

I'm here to:
• Listen to your concerns
• Provide information about depression
• Suggest coping strategies
• Share emergency resources when needed

**How can I support you today?** You can ask me about:
- Depression symptoms
- Treatment options
- Different depression types
- Self-care tips
- Or just talk about how you're feeling

Remember: I'm here to help, but for emergencies please use the crisis resources below."""
                
                st.chat_message("assistant").write(welcome_msg)
        
        # Chat input
        user_input = st.chat_input("Type your message here...")
        
        if user_input:
            # Add user message
            st.session_state.chat_messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Get bot response
            bot_response = st.session_state.chatbot.get_response(user_input)
            
            # Add bot response
            st.session_state.chat_messages.append({
                "role": "bot",
                "content": bot_response
            })
            
            # Rerun to update chat
            st.rerun()
        
        # Emergency resources at bottom
        with st.expander("🚨 Crisis Resources (Click for immediate help)", expanded=False):
            st.markdown("""
            <div style="background-color: #FEF2F2; padding: 15px; border-radius: 10px; border-left: 5px solid #DC2626;">
                <h4 style="color: #DC2626; margin-top: 0;">📞 If You're in Crisis, Call Now:</h4>
                <p style="font-size: 18px;"><b>National Suicide Prevention Lifeline:</b> <span style="color: #2563EB;">1-800-273-8255</span></p>
                <p style="font-size: 18px;"><b>Crisis Text Line:</b> Text <span style="background: #DC2626; color: white; padding: 2px 8px; border-radius: 5px;">HOME</span> to <span style="color: #2563EB;">741741</span></p>
                <p style="font-size: 18px;"><b>Emergency Services:</b> <span style="color: #2563EB;">911</span></p>
                <p style="font-size: 14px;">Available 24/7 • Free • Confidential</p>
            </div>
            """, unsafe_allow_html=True)