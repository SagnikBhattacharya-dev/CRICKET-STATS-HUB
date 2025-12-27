import streamlit as st
import google.generativeai as genai
import json

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Cricket Insight AI", page_icon="🏏")

# ==========================================
# 🔑 PASTE YOUR GEMINI API KEY BELOW
# ==========================================
GEMINI_API_KEY =  st.secrets["GOOGLE_API_KEY"]
# ==========================================

genai.configure(api_key=GEMINI_API_KEY)

# --- 2. AI FUNCTION ---
def get_player_stats(name):
    """
    Asks Gemini to act as a cricket database and return clean JSON data.
    """
    model = genai.GenerativeModel('gemini-flash-latest')
    
    prompt = f"""
    Return a valid JSON object for the cricket player "{name}".
    The JSON must have these exact keys:
    - "full_name": Name of the player
    - "country": Country they play for
    - "role": e.g. Right-hand Bat / Right-arm Offbreak
    - "batting_stats": A string summarizing their batting (e.g. "Matches: 200, Runs: 8000")
    - "bowling_stats": A string summarizing their bowling (e.g. "Wickets: 150")
    - "interesting_fact": One short, unique fact about them.
    
    Do NOT use Markdown formatting. Just return the raw JSON string.
    """
    
    try:
        response = model.generate_content(prompt)
        # CLEANUP: Remove ```json and ``` if the AI adds them
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        print(f"AI Error: {e}")
        return None

# --- 3. THE UI (Streamlit) ---
st.title("🏏 AI Cricket Analyzer")

# Input
player_name = st.text_input("Enter Player Name", placeholder="e.g. Rohit Sharma")

if st.button("Analyze Player"):
    if not player_name:
        st.warning("Please enter a name first!")
    elif "PASTE_YOUR_KEY" in GEMINI_API_KEY:
        st.error("⚠️ You forgot to paste your Gemini API key in the code!")
    else:
        with st.spinner(f"Scouting data for {player_name}..."):
            
            # 1. Fetch Stats from AI
            stats = get_player_stats(player_name)
            
            if stats:
                st.success(f"Data Found: {stats['full_name']}")
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    # --- FIX: HANDLE URL SPACES ---
                    # 1. Replace spaces with '+' so the link doesn't break
                    safe_name = player_name.replace(" ", "+")
                    
                    # 2. Create the URL
                    image_url = f"https://tse4.mm.bing.net/th?q={safe_name}+cricket+profile&w=300&h=300&c=7"
                    
                    # 3. SAFETY NET: Try to show image, fallback to text if it fails
                    try:
                        st.image(image_url, caption=stats['full_name'], use_container_width=True)
                    except Exception:
                        # If Bing fails, use a simple text placeholder
                        fallback_url = f"https://placehold.co/300x300?text={safe_name}"
                        st.image(fallback_url, caption="Image Unavailable", use_container_width=True)
                
                with col2:
                    st.subheader(stats['country'])
                    st.write(f"**Role:** {stats['role']}")
                    st.info(f"💡 **Fact:** {stats['interesting_fact']}")
                    
                    # Display Stats
                    st.markdown("### 📊 Statistics")
                    st.text_area("Batting Details", stats['batting_stats'], height=70)
                    st.text_area("Bowling Details", stats['bowling_stats'], height=70)
            else:
                st.error("Could not find data. Try a different spelling.")