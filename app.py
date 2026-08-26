import math
import folium
import requests
import streamlit as st
import streamlit.components.v1 as components
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from google import genai
from google.genai import types
from streamlit_geolocation import streamlit_geolocation

# =========================================================
# 0. FULL UI TRANSLATION DICTIONARY
# =========================================================
TEXTS = {
    "English": {
        "sidebar_title": "🏥 ArogyaMitra Settings",
        "api_label": "Enter Gemini API Key",
        "ecosystem_title": "**SIH Healthcare Ecosystem**",
        "eco_1": "- 👤 Patient Care & Health Cards",
        "eco_2": "- 🧑‍⚕️ Ground Health Worker Support",
        "eco_3": "- 👨‍⚕️ Doctor Outbreak Analytics",
        "eco_4": "- 📦 Medical Supply Network",
        "eco_5": "- 🚑 Emergency SOS Routing",
        "main_title": "🏥 ArogyaMitra AI Companion",
        "caption": "Connecting Care, Anywhere — Smart India Hackathon Prototype",
        "chat_input": "Ask about symptoms, medicines, or find a clinic...",
        "initial_greeting": "Namaste! 🙏 I am ArogyaMitra AI. Click the floating **📍 GPS Button** next to the chat box below to find hospitals near you, or describe your symptoms.",
        "api_warning": "⚠️ Please enter your Gemini API Key in the sidebar.",
        "spinner_map": "Scanning map for real hospitals and calculating road route...",
        "spinner_chat": "Fetching precise coordinates and generating road route...",
        "route_found": "📍 **Route Found:** The nearest facility is **{hosp_name}**. The map shows the actual road route.",
        "no_hosp": "⚠️ Could not find a registered hospital within 30 km of your location.",
        "missing_loc": "⚠️ Could not locate that specific area. Please check the spelling or click the **📍 GPS** button below.",
        "click_btn_prompt": "📍 **GPS Notification:** Please click the **floating 📍 GPS button** next to the chat bar to share your coordinates!"
    },
    "Hindi": {
        "sidebar_title": "🏥 आरोग्यमित्र सेटिंग्स",
        "api_label": "जेमिनी एपीआई कुंजी दर्ज करें",
        "ecosystem_title": "**एसआईएच स्वास्थ्य सेवा पारिस्थितिकी तंत्र**",
        "eco_1": "- 👤 रोगी देखभाल और स्वास्थ्य कार्ड",
        "eco_2": "- 🧑‍⚕️ ग्राउंड हेल्थ वर्कर सहायता",
        "eco_3": "- 👨‍⚕️ डॉक्टर प्रकोप विश्लेषण",
        "eco_4": "- 📦 चिकित्सा आपूर्ति नेटवर्क",
        "eco_5": "- 🚑 आपातकालीन एसओएस रूटिंग",
        "main_title": "🏥 आरोग्यमित्र एआई साथी",
        "caption": "देखभाल को जोड़ना, कहीं भी — स्मार्ट इंडिया हैकाथन प्रोटोटाइप",
        "chat_input": "लक्षणों, दवाओं के बारे में पूछें या क्लिनिक खोजें...",
        "initial_greeting": "नमस्ते! 🙏 मैं आरोग्यमित्र एआई हूँ। अपने पास के अस्पताल खोजने के लिए चैट बॉक्स के पास तैरते हुए **📍 GPS बटन** पर क्लिक करें।",
        "api_warning": "⚠️ कृपया अपनी जेमिनी एपीआई कुंजी साइडबार में दर्ज करें।",
        "spinner_map": "वास्तविक अस्पतालों के लिए मानचित्र स्कैन किया जा रहा है...",
        "spinner_chat": "सटीक स्थान प्राप्त किया जा रहा है...",
        "route_found": "📍 **मार्ग मिल गया:** निकटतम सुविधा **{hosp_name}** है।",
        "no_hosp": "⚠️ आपके स्थान के 30 किमी के भीतर कोई पंजीकृत अस्पताल नहीं मिला।",
        "missing_loc": "⚠️ कृपया कोई विशिष्ट क्षेत्र बताएं या नीचे **📍 GPS** बटन पर क्लिक करें।",
        "click_btn_prompt": "📍 **जीपीएस सूचना:** अपना स्थान साझा करने के लिए कृपया चैट बॉक्स के पास **तैरते हुए 📍 GPS बटन** पर क्लिक करें!"
    },
    "Bengali": {
        "sidebar_title": "🏥 আরোগ্যমিত্র সেটিংস",
        "api_label": "জেমিনি এপিআই কী লিখুন",
        "ecosystem_title": "**এসআইএইচ স্বাস্থ্যসেবা ইকোসিস্টেম**",
        "eco_1": "- 👤 রোগী যত্ন এবং স্বাস্থ্য কার্ড",
        "eco_2": "- 🧑‍⚕️ মাঠ পর্যায়ের স্বাস্থ্যকর্মী সহায়তা",
        "eco_3": "- 👨‍⚕️ ডাক্তার প্রাদুর্ভাব বিশ্লেষণ",
        "eco_4": "- 📦 চিকিৎসা সরবরাহ নেটওয়ার্ক",
        "eco_5": "- 🚑 জরুরি এসওএস রুটিন",
        "main_title": "🏥 আরোগ্যমিত্র এআই সঙ্গী",
        "caption": "সেবা সংযুক্ত করুন, যেকোনো স্থানে — স্মার্ট ইন্ডিয়া হ্যাকাথন প্রোটোটাইপ",
        "chat_input": "উপসর্গ বা ওষুধ সম্পর্কে জিজ্ঞাসা করুন...",
        "initial_greeting": "নমস্কার! 🙏 আমি আরোগ্যমিত্র এআই। আপনার কাছাকাছি হাসপাতাল খুঁজতে চ্যাট বক্সের পাশের **📍 জিপিএস বোতামে** ক্লিক করুন।",
        "api_warning": "⚠️ অনুগ্রহ করে সাইডবারে আপনার জেমিনি এপিআই কী লিখুন।",
        "spinner_map": "আসল হাসপাতালের জন্য মানচিত্র স্ক্যান করা হচ্ছে...",
        "spinner_chat": "এলাকা বিশ্লেষণ করা হচ্ছে...",
        "route_found": "📍 **রুট পাওয়া গেছে:** নিকটতম কেন্দ্রটি হলো **{hosp_name}**।",
        "no_hosp": "⚠️ আপনার অবস্থানের ৩০ কিমি এর মধ্যে কোনো নিবন্ধিত হাসপাতাল পাওয়া যায়নি।",
        "missing_loc": "⚠️ অনুগ্রহ করে নির্দিষ্ট এলাকার নাম দিন অথবা নিচের **📍 জিপিএস** বোতামে ক্লিক করুন।",
        "click_btn_prompt": "📍 **জিপিএস বিজ্ঞপ্তি:** আপনার অবস্থান শেয়ার করতে চ্যাট বক্সের পাশের **📍 জিপিএস বোতামে** ক্লিক করুন!"
    },
    "Tamil": {
        "sidebar_title": "🏥 ஆரோக்கியமித்ரா அமைப்புகள்",
        "api_label": "ஜெமினி API விசையை உள்ளிடவும்",
        "ecosystem_title": "**SIH சுகாதார சுற்றுச்சூழல் அமைப்பு**",
        "eco_1": "- 👤 நோயாளி பராமரிப்பு", "eco_2": "- 🧑‍⚕️ கள சுகாதார பணியாளர்", "eco_3": "- 👨‍⚕️ மருத்துவர் பகுப்பாய்வு", "eco_4": "- 📦 மருத்துவ விநியோகம்", "eco_5": "- 🚑 அவசர SOS",
        "main_title": "🏥 ஆரோக்கியமித்ரா AI தோழன்",
        "caption": "சேவையை இணைக்கிறது, எங்குმე — ஸ்மார்ட் இந்தியா ஹேத்தான் முன்மாதிரி",
        "chat_input": "அறிகுறிகள் அல்லது மருந்துகள் பற்றி கேளுங்கள்...",
        "initial_greeting": "வணக்கம்! 🙏 மருத்துவமனைகளைக் கண்டறிய அரட்டைப் பெட்டிக்கு அருகில் உள்ள 📍 GPS பொத்தானைக் கிளிக் செய்யவும்.",
        "api_warning": "⚠️ தயவுசெய்து பக்கவாட்டுப் பட்டையில் விசையை உள்ளிடவும்.",
        "spinner_map": "வரைபடம் ஸ்கேன் செய்யப்படுகிறது...",
        "spinner_chat": "பாதை உருவாக்கப்படுகிறது...",
        "route_found": "📍 **பாதை கண்டறியப்பட்டது:** **{hosp_name}**.",
        "no_hosp": "⚠️ மருத்துவமனை எதுவும் கிடைக்கவில்லை.",
        "missing_loc": "⚠️ பகுதியைக் குறிப்பிடவும் அல்லது கீழே உள்ள 📍 GPS பொத்தானைக் கிளிக் செய்யவும்.",
        "click_btn_prompt": "📍 **GPS அறிவிப்பு:** அரட்டைப் பெட்டிக்கு அருகில் உள்ள 📍 GPS பொத்தானைக் கிளிக் செய்யவும்!"
    },
    "Telugu": {
        "sidebar_title": "🏥 ఆరోగ్యమిత్ర సెట్టింగ్‌లు",
        "api_label": "జెమిని API కీని నమోదు చేయండి",
        "ecosystem_title": "**SIH ఆరోగ్య సంరక్షణ పర్యావరణ వ్యవస్థ**",
        "eco_1": "- 👤 రోగి సంరక్షణ", "eco_2": "- 🧑‍⚕️ గ్రౌండ్ హెల్త్ వర్కర్", "eco_3": "- 👨‍⚕️ డాక్టర్ విశ్లేషణ", "eco_4": "- 📦 వైద్య సరఫరా", "eco_5": "- 🚑 అత్యవసర SOS",
        "main_title": "🏥 ఆరోగ్యమిత్ర AI సహచరుడు",
        "caption": "సంరక్షణను కలుపుతోంది, ఎక్కడైనా — స్మార్ట్ ఇండియా హ్యాకథాన్ ప్రోటోటైప్",
        "chat_input": "లక్షణాలు లేదా మందుల గురించి అడగండి...",
        "initial_greeting": "నమస్కారం! 🙏 ఆసుపత్రులను కనుగొనడానికి చాట్ బాక్స్ పక్కన ఉన్న 📍 GPS బటన్‌ను క్లిక్ చేయండి.",
        "api_warning": "⚠️ దయచేసి సైడ్‌బార్‌లో కీని నమోదు చేయండి.",
        "spinner_map": "మ్యాప్ స్కాన్ చేయబడుతోంది...",
        "spinner_chat": "మార్గం సృష్టించబడుతోంది...",
        "route_found": "📍 **మార్గం కనుగొనబడింది:** **{hosp_name}**.",
        "no_hosp": "⚠️ ఆసుపత్రి కనుగొనబడలేదు.",
        "missing_loc": "⚠️ ప్రాంతాన్ని పేర్కొనండి లేదా 📍 GPS బటన్‌ని క్లిక్ చేయండి.",
        "click_btn_prompt": "📍 **GPS నోటిఫికేషన్:** దయచేసి చాట్ బాక్స్ పక్కన ఉన్న 📍 GPS బటన్‌ను క్లిక్ చేయండి!"
    },
    "Marathi": {
        "sidebar_title": "🏥 आरोग्यमित्र सेटिंग्ज",
        "api_label": "जेमिनी एपीआय की प्रविष्ट करा",
        "ecosystem_title": "**SIH आरोग्य सेवा इकोसिस्टम**",
        "eco_1": "- 👤 रुग्ण काळजी", "eco_2": "- 🧑‍⚕️ ग्राउंड हेल्थ वर्कर", "eco_3": "- 👨‍⚕️ डॉक्टर विश्लेषण", "eco_4": "- 📦 वैद्यकीय पुरवठा", "eco_5": "- 🚑 आणीबाणी SOS",
        "main_title": "🏥 आरोग्यमित्र AI सोबती",
        "caption": "काळजी जोडत आहे, कुठेही — स्मार्ट इंडिया हॅकाथॉन प्रोटोटाइप",
        "chat_input": "लक्षणे किंवा औषधांबद्दल विचारणा करा...",
        "initial_greeting": "नमस्कार! 🙏 रुग्णालये शोधण्यासाठी कृपया चॅट बॉक्स शेजारील 📍 GPS बटणावर क्लिक करा.",
        "api_warning": "⚠️ कृपया साइडबारमध्ये की प्रविष्ट करा.",
        "spinner_map": "नकाशा स्कॅन केला जात आहे...",
        "spinner_chat": "मार्ग तयार केला जात आहे...",
        "route_found": "📍 **मार्ग सापडला:** **{hosp_name}**.",
        "no_hosp": "⚠️ रुग्णालय आढळले नाही.",
        "missing_loc": "⚠️ क्षेत्राचे नाव द्या किंवा 📍 GPS बटणावर क्लिक करा.",
        "click_btn_prompt": "📍 **GPS सूचना:** कृपया चॅट बॉक्स शेजारील 📍 GPS बटणावर क्लिक करा!"
    }
}

# =========================================================
# 1. PAGE SETUP & CSS INJECTION FOR BUTTON LAYOUT
# =========================================================
st.set_page_config(page_title="ArogyaMitra AI", page_icon="🏥", layout="centered")

st.markdown("""
    <style>
    /* GPS Button Location */
    iframe[title*="geolocation"] {
        position: fixed !important;
        bottom: 22px !important;
        right: 15px !important;
        z-index: 999999 !important;
        width: 45px !important;
        height: 45px !important;
    }
    /* Shrink Chat Input so buttons don't block text */
    [data-testid="stChatInput"] {
        width: calc(100% - 110px) !important; 
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
lang_choice = st.sidebar.selectbox(
    "🌐 Select Language / भाषा चुनें",
    ["English", "Hindi", "Bengali", "Tamil", "Telugu", "Marathi"]
)
t = TEXTS[lang_choice]

if "current_lang" not in st.session_state:
    st.session_state.current_lang = lang_choice

if st.session_state.current_lang != lang_choice:
    st.session_state.current_lang = lang_choice
    st.session_state.messages = [{"role": "assistant", "content": t["initial_greeting"]}]

# =========================================================
# 2. VIRTUAL KEYBOARD JAVASCRIPT INJECTION (FIXED HEIGHT)
# =========================================================
VIRTUAL_KEYBOARD_JS = f"""
<script>
const parentDoc = window.parent.document;
const parentWin = window.parent;

const existingKb = parentDoc.getElementById("vkb-container");
if(existingKb) existingKb.remove();
const existingToggle = parentDoc.getElementById("vkb-toggle-wrap");
if(existingToggle) existingToggle.remove();

const langMap = {{
    "Bengali": "bengali",
    "Hindi": "hindi",
    "Tamil": "tamil",
    "Telugu": "telugu",
    "Marathi": "hindi", 
    "English": "english"
}};
const currentLang = "{lang_choice}";
const layoutName = langMap[currentLang] || "english";

if (layoutName !== "english") {{
    const kbContainer = parentDoc.createElement("div");
    kbContainer.id = "vkb-container";
    kbContainer.style.position = "fixed";
    /* MOVED HIGHER SO IT NEVER COVERS THE CHAT BAR */
    kbContainer.style.bottom = "140px";
    kbContainer.style.left = "50%";
    kbContainer.style.transform = "translateX(-50%)";
    kbContainer.style.width = "95%";
    kbContainer.style.maxWidth = "800px";
    kbContainer.style.zIndex = "9999999";
    kbContainer.style.display = "none";
    kbContainer.style.boxShadow = "0px -4px 15px rgba(0,0,0,0.3)";
    kbContainer.style.borderRadius = "10px";
    kbContainer.style.padding = "10px";
    kbContainer.style.backgroundColor = "#f5f5f5";
    
    kbContainer.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; padding: 0 5px;">
            <strong style="color: #333; font-family: sans-serif;">${{currentLang}} Virtual Keyboard</strong>
            <button id="vkb-close" style="background:#ff4b4b; color:white; border:none; border-radius:5px; padding:5px 15px; cursor:pointer; font-weight:bold;">Close ❌</button>
        </div>
        <div class="simple-keyboard" style="color: black;"></div>
    `;
    parentDoc.body.appendChild(kbContainer);

    if (!parentDoc.getElementById("vkb-css")) {{
        const css = parentDoc.createElement("link");
        css.id = "vkb-css";
        css.rel = "stylesheet";
        css.href = "https://cdn.jsdelivr.net/npm/simple-keyboard@latest/build/css/index.css";
        parentDoc.head.appendChild(css);
    }}

    function loadScript(src, id, callback) {{
        if (parentDoc.getElementById(id)) {{ callback(); return; }}
        const script = parentDoc.createElement("script");
        script.id = id;
        script.src = src;
        script.onload = callback;
        parentDoc.head.appendChild(script);
    }}

    loadScript("https://cdn.jsdelivr.net/npm/simple-keyboard@latest/build/index.js", "vkb-script-1", () => {{
        loadScript("https://cdn.jsdelivr.net/npm/simple-keyboard-layouts@latest/build/index.js", "vkb-script-2", () => {{
            
            const Keyboard = parentWin.SimpleKeyboard.default;
            const KeyboardLayouts = parentWin.SimpleKeyboardLayouts.default;
            const layout = new KeyboardLayouts();
            const chatInput = parentDoc.querySelector('[data-testid="stChatInput"] textarea');

            let keyboard = new Keyboard(parentDoc.querySelector('.simple-keyboard'), {{
                onChange: input => {{
                    if (chatInput) {{
                        let nativeInputValueSetter = Object.getOwnPropertyDescriptor(parentWin.HTMLTextAreaElement.prototype, "value").set;
                        nativeInputValueSetter.call(chatInput, input);
                        chatInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    }}
                }},
                onKeyPress: button => {{
                    if (button === "{{shift}}" || button === "{{lock}}") {{
                        let currentL = keyboard.options.layoutName;
                        let shiftToggle = currentL === "default" ? "shift" : "default";
                        keyboard.setOptions({{ layoutName: shiftToggle }});
                    }}
                    if (button === "{{enter}}") {{
                        keyboard.clearInput();
                        kbContainer.style.display = "none";
                    }}
                }},
                ...layout.get(layoutName)
            }});

            if (chatInput) {{
                chatInput.addEventListener("input", (e) => {{
                    keyboard.setInput(e.target.value);
                }});
                
                let btnWrap = parentDoc.createElement("div");
                btnWrap.id = "vkb-toggle-wrap";
                btnWrap.style.position = "fixed";
                btnWrap.style.bottom = "24px";
                btnWrap.style.right = "65px"; 
                btnWrap.style.zIndex = "999999";
                
                let toggleBtn = parentDoc.createElement("button");
                toggleBtn.innerHTML = "⌨️";
                toggleBtn.style.fontSize = "22px";
                toggleBtn.style.background = "#fff";
                toggleBtn.style.border = "1px solid #ccc";
                toggleBtn.style.borderRadius = "50%";
                toggleBtn.style.width = "40px";
                toggleBtn.style.height = "40px";
                toggleBtn.style.cursor = "pointer";
                toggleBtn.style.boxShadow = "0px 2px 5px rgba(0,0,0,0.2)";
                toggleBtn.title = `Open ${{currentLang}} Keyboard`;
                
                toggleBtn.onclick = () => {{
                    kbContainer.style.display = kbContainer.style.display === "none" ? "block" : "none";
                }};
                
                btnWrap.appendChild(toggleBtn);
                parentDoc.body.appendChild(btnWrap);

                parentDoc.getElementById("vkb-close").onclick = () => {{
                    kbContainer.style.display = "none";
                }};
            }}
        }});
    }});
}}
</script>
"""
components.html(VIRTUAL_KEYBOARD_JS, height=0, width=0)

# =========================================================
# 3. SIDEBAR AND MAIN HEADER CONFIGURATION
# =========================================================
st.sidebar.title(t["sidebar_title"])
api_key = st.sidebar.text_input(t["api_label"], value="", type="password", help="Paste your Gemini API key here")

st.sidebar.markdown("---")
st.sidebar.markdown(f"{t['ecosystem_title']}\n{t['eco_1']}\n{t['eco_2']}\n{t['eco_3']}\n{t['eco_4']}\n{t['eco_5']}")
st.title(t["main_title"])
st.caption(t["caption"])

# =========================================================
# 4. MAP HELPER FUNCTIONS
# =========================================================
def get_coordinates_from_text(place_name):
    geolocator = Nominatim(user_agent="arogyamitra_sih_app")
    try:
        location = geolocator.geocode(f"{place_name}, India", timeout=10)
        if location: return location.latitude, location.longitude
    except: pass
    return None, None

def get_real_nearest_hospital(lat, lon):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""[out:json];(nwr["amenity"="hospital"](around:30000, {lat}, {lon});nwr["amenity"="clinic"](around:30000, {lat}, {lon});nwr["healthcare"="hospital"](around:30000, {lat}, {lon});nwr["amenity"="doctors"](around:30000, {lat}, {lon}););out center;"""
    try:
        response = requests.get(overpass_url, params={"data": query}, headers={'User-Agent': 'ArogyaMitra/1.0'}, timeout=15)
        data = response.json()
        if data.get("elements"):
            closest, min_dist = None, float("inf")
            for el in data["elements"]:
                h_lat = el.get("lat") or el.get("center", {}).get("lat")
                h_lon = el.get("lon") or el.get("center", {}).get("lon")
                if not h_lat: continue
                name = el.get("tags", {}).get("name", "Healthcare Facility")
                dist = geodesic((lat, lon), (h_lat, h_lon)).kilometers
                if dist < min_dist:
                    min_dist, closest = dist, (h_lat, h_lon, name)
            return closest
    except: pass
    return None

def get_real_road_route(lat1, lon1, lat2, lon2):
    url = f"https://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    try:
        res = requests.get(url, headers={'User-Agent': 'ArogyaMitra/1.0'}, timeout=10)
        if res.json().get("code") == "Ok":
            return [(coord[1], coord[0]) for coord in res.json()["routes"][0]["geometry"]["coordinates"]]
    except: pass
    return [(lat1, lon1), (lat2, lon2)]

def get_directions_url(destination_lat, destination_lon):
    return (
        "https://www.google.com/maps/dir/?api=1"
        f"&destination={destination_lat},{destination_lon}&travelmode=driving"
    )

# =========================================================
# 5. FLOATING GPS BUTTON AND CHAT ENGINE
# =========================================================
location = streamlit_geolocation()
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": t["initial_greeting"]}]

if location and location.get("latitude"):
    user_lat, user_lon = location["latitude"], location["longitude"]
    with st.spinner(t["spinner_map"]):
        m = folium.Map(location=[user_lat, user_lon], zoom_start=14)
        folium.Marker([user_lat, user_lon], popup="Your Location", icon=folium.Icon(color="blue", icon="user")).add_to(m)
        nearest_hosp = get_real_nearest_hospital(user_lat, user_lon)
        if nearest_hosp:
            hosp_lat, hosp_lon, hosp_name = nearest_hosp
            folium.Marker([hosp_lat, hosp_lon], popup=hosp_name, icon=folium.Icon(color="red", icon="plus-square", prefix="fa")).add_to(m)
            folium.PolyLine(get_real_road_route(user_lat, user_lon, hosp_lat, hosp_lon), color="#EF4444", weight=5).add_to(m)
            m.fit_bounds([[user_lat, user_lon], [hosp_lat, hosp_lon]])
            directions_url = get_directions_url(hosp_lat, hosp_lon)
            reply_text = t["route_found"].format(hosp_name=hosp_name) + f"\n\n[Open navigation](<{directions_url}>)"
        else:
            reply_text = t["no_hosp"]
        map_html = m._repr_html_()
        if not any(msg.get("content") == reply_text for msg in st.session_state.messages):
            st.session_state.messages.append({"role": "assistant", "content": reply_text, "map_html": map_html})
            st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "map_html" in msg and msg["map_html"]: components.html(msg["map_html"], height=400)

prompt = st.chat_input(t["chat_input"])

if prompt:
    if not api_key:
        st.warning(t["api_warning"])
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        try:
            client = genai.Client(api_key=api_key)
            is_map_query = any(k in prompt.lower() for k in ["map", "route", "way", "hospital", "clinic", "nearest", "where", "location"])
            is_my_location = any(k in prompt.lower() for k in ["my address", "my location", "near me", "from me", "around me"])

            if is_map_query and is_my_location:
                reply_text = t["click_btn_prompt"]
                st.session_state.messages.append({"role": "assistant", "content": reply_text})
                with st.chat_message("assistant"): st.warning(reply_text)
                st.stop()

            elif is_map_query and not is_my_location:
                with st.spinner(t["spinner_chat"]):
                    place_name = client.models.generate_content(model="gemini-3.5-flash", contents=f"Extract EXACT place name. Fix typos. Return ONLY name. Query: '{prompt}'").text.strip()
                    user_lat, user_lon = get_coordinates_from_text(place_name)
                    if user_lat and user_lon:
                        m = folium.Map(location=[user_lat, user_lon], zoom_start=14)
                        folium.Marker([user_lat, user_lon], popup=place_name, icon=folium.Icon(color="blue", icon="user")).add_to(m)
                        nearest_hosp = get_real_nearest_hospital(user_lat, user_lon)
                        if nearest_hosp:
                            hosp_lat, hosp_lon, hosp_name = nearest_hosp
                            folium.Marker([hosp_lat, hosp_lon], popup=hosp_name, icon=folium.Icon(color="red", icon="plus-square", prefix="fa")).add_to(m)
                            folium.PolyLine(get_real_road_route(user_lat, user_lon, hosp_lat, hosp_lon), color="#EF4444", weight=5).add_to(m)
                            m.fit_bounds([[user_lat, user_lon], [hosp_lat, hosp_lon]])
                            directions_url = get_directions_url(hosp_lat, hosp_lon)
                            reply_text = t["route_found"].format(hosp_name=hosp_name) + f"\n\n[Open navigation](<{directions_url}>)"
                        else:
                            reply_text = t["no_hosp"]
                        map_html = m._repr_html_()
                        st.session_state.messages.append({"role": "assistant", "content": reply_text, "map_html": map_html})
                        with st.chat_message("assistant"):
                            st.markdown(reply_text)
                            components.html(map_html, height=400)
                        st.stop()
                    else:
                        st.warning(t["missing_loc"])
                        st.stop()

            system_instruction = f"You are ArogyaMitra AI. Reply in {lang_choice}. Provide safe home care and mention OTC meds for illnesses. Add disclaimer: 'ArogyaMitra AI is not a doctor. Consult a physician for serious issues.'"
            reply = client.models.generate_content(model="gemini-3.5-flash", contents=prompt, config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.3)).text
            
            st.session_state.messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"): st.markdown(reply)

        except Exception as e:
            st.error(f"Error: {e}")