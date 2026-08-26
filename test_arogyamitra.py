import os
import time
from gtts import gTTS
import pygame
from geopy.geocoders import Nominatim
from google import genai
from google.genai import types

# ==========================================
# 1. SETUP GEMINI API KEY
# ==========================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ai_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

# ==========================================
# 2. FREE TEXT-TO-SPEECH (gTTS + Pygame)
# ==========================================
pygame.mixer.init()

def speak_text(text: str, lang_code: str = "en"):
    """Converts text to speech and plays it aloud through laptop speakers."""
    try:
        # Clean text so TTS doesn't pronounce asterisks or markdown
        clean_text = text.replace("*", "").replace("#", "").strip()
        
        tts = gTTS(text=clean_text, lang=lang_code, slow=False)
        filename = "temp_voice.mp3"
        tts.save(filename)

        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.music.unload()
        if os.path.exists(filename):
            os.remove(filename)
    except Exception as e:
        print(f"🔊 Audio playback error: {e}")

# ==========================================
# 3. FREE HOSPITAL / CLINIC FINDER (No Maps Key Needed)
# ==========================================
def find_nearest_hospital(city_or_area: str, facility_type: str = "hospital") -> str:
    """Finds hospitals or clinics near the specified area in India using OpenStreetMap."""
    try:
        geolocator = Nominatim(user_agent="arogyamitra_test_bot")
        location = geolocator.geocode(f"{city_or_area}, India", timeout=10)
        
        if not location:
            return f"Could not find geographic coordinates for {city_or_area}."
        
        # Search for nearby healthcare facilities
        query = f"{facility_type} in {city_or_area}, India"
        places = geolocator.geocode(query, exactly_one=False, limit=3, timeout=10)
        
        if places:
            results = [f"• {p.address.split(',')[0]} ({p.address})" for p in places]
            return f"Found {facility_type}s in/near {city_or_area}:\n" + "\n".join(results)
        else:
            return f"Located {city_or_area} at Lat: {location.latitude:.2f}, Lng: {location.longitude:.2f}. For emergencies, please call 108/112 or visit the nearest Primary Health Center (PHC)."
    except Exception as e:
        return f"Location search error: {str(e)}"

# ==========================================
# 4. LANGUAGE CONFIGURATION
# ==========================================
LANGUAGES = {
    "1": {"name": "English", "code": "en", "greeting": "Hello! I am ArogyaMitra AI. How can I help you today?"},
    "2": {"name": "Hindi", "code": "hi", "greeting": "नमस्ते! मैं आरोग्यमित्र एआई हूँ। मैं आपकी क्या मदद कर सकता हूँ?"},
    "3": {"name": "Bengali", "code": "bn", "greeting": "নমস্কার! আমি আরোগ্যমিত্র এআই। আমি কীভাবে সাহায্য করতে পারি?"},
    "4": {"name": "Tamil", "code": "ta", "greeting": "வணக்கம்! நான் ஆரோக்கியமித்ரா AI. உங்களுக்கு எப்படி உதவ முடியும்?"},
    "5": {"name": "Telugu", "code": "te", "greeting": "నమస్కారం! నేను ఆరోగ్యమిత్ర AI. మీకు ఎలా సహాయపడగలను?"},
    "6": {"name": "Marathi", "code": "mr", "greeting": "नमस्कार! मी आरोग्यमित्र AI आहे. मी तुम्हाला कशी मदत करू शकतो?"},
}

# ==========================================
# 5. RUN CHATBOT
# ==========================================
def run_arogyamitra():
    print("=" * 60)
    print("🏥 AROGYAMITRA AI — LAPTOP TEST ENVIRONMENT")
    print("   Connecting Care, Anywhere (SIH Prototype)")
    print("=" * 60)
    
    print("\nSelect your language / अपनी भाषा चुनें:")
    for k, v in LANGUAGES.items():
        print(f" [{k}] {v['name']}")
    
    choice = input("\nEnter choice (1-6) [default: 1]: ").strip()
    selected_lang = LANGUAGES.get(choice, LANGUAGES["1"])
    
    print(f"\n✅ Active Language: {selected_lang['name']}")
    
    # Configure Gemini System Instructions
    system_instruction = f"""
    You are ArogyaMitra AI, an intelligent digital healthcare assistant for India.
    CRITICAL RULES:
    1. Reply entirely in {selected_lang['name']}.
    2. If the user asks for a hospital, clinic, or pharmacy in an area, call the `find_nearest_hospital` tool.
    3. For symptoms or medication advice, provide clear, simple guidance and always end with: 
       "Disclaimer: I am an AI assistant. Please consult a qualified doctor for medical diagnoses."
    4. Keep answers concise so they sound natural when spoken aloud.
    """
    
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.3,
        tools=[find_nearest_hospital]
    )
    
    chat = ai_client.chats.create(model="gemini-3.5-flash", config=config)
    
    # Speak and print greeting
    print(f"\n🤖 ArogyaMitra: {selected_lang['greeting']}")
    speak_text(selected_lang['greeting'], selected_lang['code'])
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\n🤖 ArogyaMitra: Take care of your health! Goodbye.")
                break
                
            response = chat.send_message(user_input)
            
            print(f"\n🤖 ArogyaMitra: {response.text}")
            speak_text(response.text, selected_lang['code'])
            
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    run_arogyamitra()