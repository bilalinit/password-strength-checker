import streamlit as st

import google.generativeai as genai
import re
import random
import string

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Gemini API key not found in .streamlit/secrets.toml. Please set the GEMINI_API_KEY secret.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")

def check_password_strength(password):
    score = 0
    feedback = []

    if len(password) >= 8:
        score += 1
    else:
        feedback.append("❌ Password should be at least 8 characters long.")

    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append("❌ Include at least one uppercase letter.")

    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("❌ Include at least one lowercase letter.")

    if re.search(r"\d", password):
        score += 1
    else:
        feedback.append("❌ Add at least one number (0-9).")

    if re.search(r"[!@#$%^&*]", password):
        score += 1
    else:
        feedback.append("❌ Include at least one special character (!@#$%^&*).")

    if password.lower() in ["password", "password123", "123456"]:
        score = 0
        feedback.append("❌ Avoid common passwords.")

    return score, feedback

def generate_strong_password(length=12):
    if length < 8:
        length = 8


    password = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("!@#$%^&*")
    ]
    

    remaining_length = length - len(password)
    password += random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=remaining_length)
    

    random.shuffle(password)
    
    return ''.join(password)

def get_gemini_enhanced_feedback(password, feedback, strength_category):
    if strength_category == "Strong" and len(feedback) == 0:
        prompt = f"The password '{password}' is rated as 'Strong' because it meets all key security criteria. Explain why this password is strong in simple terms within 40 words."
    elif feedback:
        prompt = f"The password '{password}' is rated as '{strength_category}' and here are the following problems '{feedback}'. Rephrase this feedback in a more encouraging and actionable way. Make it concise!"
    else:
        return ""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating feedback from Gemini: {e}"

def main():
    st.title("Password Strength Meter")
    
    password = st.text_input("Enter your password:", type="password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        check_button = st.button("Check Password")
    
    with col2:
        generate_button = st.button("Generate Password")
    
    if generate_button:
        suggested_password = generate_strong_password()
        st.subheader("Generated Strong Password:")
        st.write(suggested_password)
    
    if password and check_button:
        score, feedback = check_password_strength(password)
        
        st.subheader("Password Strength:")
        
        if score <= 2:
            strength_category = "Weak"
        elif score <= 3:
            strength_category = "Moderate"
        else:
            strength_category = "Strong"
        
        st.progress(score / 5)
        st.write(f"Strength: {strength_category} (Score: {score})")
        
        enhanced_feedback = get_gemini_enhanced_feedback(password, feedback, strength_category)
        
        if strength_category == "Strong" and score == 5:
            st.success("✅ Your password is strong!")
            st.write(enhanced_feedback)
        else:
            if feedback:
                for message in feedback:
                    st.write(message)
            st.write(enhanced_feedback)

if __name__ == "__main__":
    main()
