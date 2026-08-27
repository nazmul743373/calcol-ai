import os
import time
import json
from gtts import gTTS
import pygame
from geopy.geocoders import Nominatim
from openai import OpenAI

# ==========================================
# 1. SETUP OPENROUTER API KEY
# ==========================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

ai_client = (
    OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)
    if OPENROUTER_API_KEY
    else None
)

MODEL_NAME = "openrouter/free"

# ==========================================
# 2. FREE TEXT-TO-SPEECH (gTTS + Pygame)
# ==========================================
pygame.mixer.init()

def speak_text(text: str, lang_code: str = "en"):
    """Converts text to speech and plays it aloud through laptop speakers."""
    try:
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
# 3. FREE HOSPITAL / CLINIC FINDER
# ==========================================
def find_nearest_hospital(city_or_area: str, facility_type: str = "hospital") -> str:
    """Finds hospitals or clinics near the specified area in India using OpenStreetMap."""
    try:
        geolocator = Nominatim(user_agent="arogyamitra_test_bot")
        location = geolocator.geocode(f"{city_or_area}, India", timeout=10)
        
        if not location:
            return f"Could not find geographic coordinates for {city_or_area}."
        
        query = f"{facility_type} in {city_or_area}, India"
        places = geolocator.geocode(query, exactly_one=False, limit=3, timeout=10)
        
        if places:
            results = [f"• {p.address.split(',')[0]} ({p.address})" for p in places]
            return f"Found {facility_type}s in/near {city_or_area}:\n" + "\n".join(results)
        else:
            return f"Located {city_or_area} at Lat: {location.latitude:.2f}, Lng: {location.longitude:.2f}. For emergencies, call 108/112."
    except Exception as e:
        return f"Location search error: {str(e)}"

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "find_nearest_hospital",
            "description": "Finds hospitals or clinics near the specified area in India using OpenStreetMap.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city_or_area": {
                        "type": "string",
                        "description": "The city, town, or specific area name in India."
                    },
                    "facility_type": {
                        "type": "string",
                        "description": "Type of facility, e.g., 'hospital', 'clinic'."
                    }
                },
                "required": ["city_or_area"]
            }
        }
    }
]

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
# 5. RUN CHATBOT WITH TRANSLATION & AUDIO CONTROL
# ==========================================
def run_arogyamitra():
    print("=" * 60)
    print("🏥 AROGYAMITRA AI — LAPTOP TEST ENVIRONMENT (OPENROUTER)")
    print("   Connecting Care, Anywhere (SIH Prototype)")
    print("=" * 60)
    
    print("\nSelect your language / अपनी भाषा चुनें:")
    for k, v in LANGUAGES.items():
        print(f" [{k}] {v['name']}")
    
    choice = input("\nEnter choice (1-6) [default: 1]: ").strip()
    selected_lang = LANGUAGES.get(choice, LANGUAGES["1"])
    current_lang_name = selected_lang['name']
    current_lang_code = selected_lang['code']
    
    print(f"\n✅ Active Language: {current_lang_name}")
    print("💡 Tip: Type 'translate to Hindi' (or Bengali, Tamil, etc.) anytime to switch languages!")
    print("💡 Tip: Type 's' to repeat the last spoken response.")
    
    messages = []
    last_response_text = selected_lang['greeting']
    
    print(f"\n🤖 ArogyaMitra: {selected_lang['greeting']}")
    speak_text(selected_lang['greeting'], current_lang_code)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\n🤖 ArogyaMitra: Take care of your health! Goodbye.")
                speak_text("Take care of your health! Goodbye.", "en")
                break
            
            if user_input.lower() == 's':
                print(f"\n🔊 Repeating last message...")
                speak_text(last_response_text, current_lang_code)
                continue
                
            messages.append({"role": "user", "content": user_input})
            
            system_instruction = f"""
            You are ArogyaMitra AI, an intelligent digital healthcare assistant for India.
            Current primary language preference: {current_lang_name}.
            CRITICAL RULES:
            1. If the user explicitly asks to translate text or change language, fulfill the translation request immediately. Otherwise, reply primarily in {current_lang_name}.
            2. If the user asks for a hospital, clinic, or pharmacy in an area, trigger the `find_nearest_hospital` tool.
            3. For symptoms or medication advice, provide clear guidance and always end with: 
               "Disclaimer: I am an AI assistant. Please consult a qualified doctor for medical diagnoses."
            4. Keep answers concise so they sound natural when spoken aloud.
            """
            
            full_payload = [{"role": "system", "content": system_instruction}] + messages
            
            response = ai_client.chat.completions.create(
                model=MODEL_NAME,
                messages=full_payload,
                tools=tools_schema,
                temperature=0.3
            )
            
            response_message = response.choices[0].message
            messages.append(response_message)
            
            if response_message.tool_calls:
                for tool_call in response_message.tool_calls:
                    if tool_call.function.name == "find_nearest_hospital":
                        args = json.loads(tool_call.function.arguments)
                        print(f"   [🔍 Searching map for: {args.get('city_or_area')}...]")
                        
                        tool_result = find_nearest_hospital(
                            city_or_area=args.get("city_or_area"),
                            facility_type=args.get("facility_type", "hospital")
                        )
                        
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                            "content": tool_result
                        })
                
                final_response = ai_client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[{"role": "system", "content": system_instruction}] + messages,
                    temperature=0.3
                )
                
                final_text = final_response.choices[0].message.content
                messages.append({"role": "assistant", "content": final_text})
                last_response_text = final_text
                
                print(f"\n🤖 ArogyaMitra: {final_text}")
                speak_text(final_text, current_lang_code)
                
            else:
                final_text = response_message.content
                last_response_text = final_text
                print(f"\n🤖 ArogyaMitra: {final_text}")
                speak_text(final_text, current_lang_code)
            
        except Exception as e:
            print(f"\n⚠️ Error connecting to AI: {e}")
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    run_arogyamitra()