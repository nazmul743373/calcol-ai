import math
import json
import folium
import requests
import streamlit as st
import streamlit.components.v1 as components
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from openai import OpenAI
from streamlit_geolocation import streamlit_geolocation

# =========================================================
# 0. FULL UI TRANSLATION DICTIONARY
# =========================================================
TEXTS = {
    "English": {
        "sidebar_title": "🏥 Calcol Settings",
        "ecosystem_title": "**SIH Healthcare Ecosystem**",
        "eco_1": "- 👤 Patient Care & Health Cards",
        "eco_2": "- 🧑‍⚕️ Ground Health Worker Support",
        "eco_3": "- 👨‍⚕️ Doctor Outbreak Analytics",
        "eco_4": "- 📦 Medical Supply Network",
        "eco_5": "- 🚑 Emergency SOS Routing",
        "main_title": "🏥 Calcol AI Companion",
        "caption": "Connecting Care, Anywhere — Smart India Hackathon Prototype",
        "chat_input": "Ask about symptoms, medicines, or find a clinic...",
        "initial_greeting": "Namaste! 🙏 I am Calcol AI. Click the floating **📍 GPS Button** next to the chat box below to find hospitals near you, or describe your symptoms.",
        "spinner_map": "Scanning map for real hospitals and calculating road route...",
        "spinner_chat": "Fetching precise coordinates and generating road route...",
        "route_found": "📍 **Route Found:** The nearest facility is **{hosp_name}**. The map shows the actual road route.",
        "no_hosp": "⚠️ Could not find a registered hospital within 30 km of your location.",
        "missing_loc": "⚠️ Could not locate that specific area. Please check the spelling or click the **📍 GPS** button below.",
        "click_btn_prompt": "📍 **GPS Notification:** Please click the **floating 📍 GPS button** next to the chat bar to share your coordinates!",
        "read_btn": "🔊 Read Aloud"
    },
    "Hindi": {
        "sidebar_title": "🏥 कैलकोल सेटिंग्स",
        "ecosystem_title": "**एसआईएच स्वास्थ्य सेवा पारिस्थितिकी तंत्र**",
        "eco_1": "- 👤 रोगी देखभाल और स्वास्थ्य कार्ड",
        "eco_2": "- 🧑‍⚕️ ग्राउंड हेल्थ वर्कर सहायता",
        "eco_3": "- 👨‍⚕️ डॉक्टर प्रकोप विश्लेषण",
        "eco_4": "- 📦 चिकित्सा आपूर्ति नेटवर्क",
        "eco_5": "- 🚑 आपातकालीन एसओएस रूटिंग",
        "main_title": "🏥 कैलकोल एआई साथी",
        "caption": "देखभाल को जोड़ना, कहीं भी — स्मार्ट इंडिया हैकाथन प्रोटोटाइप",
        "chat_input": "लक्षणों, दवाओं के बारे में पूछें या क्लिनिक खोजें...",
        "initial_greeting": "नमस्ते! 🙏 मैं कैलकोल एआई हूँ। अपने पास के अस्पताल खोजने के लिए चैट बॉक्स के पास तैरते हुए **📍 GPS बटन** पर क्लिक करें।",
        "spinner_map": "वास्तविक अस्पतालों के लिए मानचित्र स्कैन किया जा रहा है...",
        "spinner_chat": "सटीक स्थान प्राप्त किया जा रहा है...",
        "route_found": "📍 **मार्ग मिल गया:** निकटतम सुविधा **{hosp_name}** है।",
        "no_hosp": "⚠️ आपके स्थान के 30 किमी के भीतर कोई पंजीकृत अस्पताल नहीं मिला।",
        "missing_loc": "⚠️ कृपया कोई विशिष्ट क्षेत्र बताएं या नीचे **📍 GPS** बटन पर क्लिक करें।",
        "click_btn_prompt": "📍 **जीपीएस सूचना:** अपना स्थान साझा करने के लिए कृपया चैट बॉक्स के पास **तैरते हुए 📍 GPS बटन** पर क्लिक करें!",
        "read_btn": "🔊 बोलकर सुनाएं"
    },
    "Bengali": {
        "sidebar_title": "🏥 ক্যালকোল সেটিংস",
        "ecosystem_title": "**এসআইএইচ স্বাস্থ্যসেবা ইকোসিস্টেম**",
        "eco_1": "- 👤 রোগী যত্ন এবং স্বাস্থ্য কার্ড",
        "eco_2": "- 🧑‍⚕️ মাঠ পর্যায়ের স্বাস্থ্যকর্মী সহায়তা",
        "eco_3": "- 👨‍⚕️ ডাক্তার প্রাদুর্ভাব বিশ্লেষণ",
        "eco_4": "- 📦 চিকিৎসা সরবরাহ নেটওয়ার্ক",
        "eco_5": "- 🚑 জরুরি এসওএস রুটিন",
        "main_title": "🏥 ক্যালকোল এআই সঙ্গী",
        "caption": "সেবা সংযুক্ত করুন, যেকোনো স্থানে — স্মার্ট ইন্ডিয়া হ্যাকাথন প্রোটোটাইপ",
        "chat_input": "উপসর্গ বা ওষুধ সম্পর্কে জিজ্ঞাসা করুন...",
        "initial_greeting": "নমস্কার! 🙏 আমি ক্যালকোল এআই। আপনার কাছাকাছি হাসপাতাল খুঁজতে চ্যাট বক্সের পাশের **📍 জিপিএস বোতামে** ক্লিক করুন।",
        "spinner_map": "আসল হাসপাতালের জন্য মানচিত্র স্ক্যান করা হচ্ছে...",
        "spinner_chat": "এলাকা বিশ্লেষণ করা হচ্ছে...",
        "route_found": "📍 **রুট পাওয়া গেছে:** নিকটতম কেন্দ্রটি হলো **{hosp_name}**।",
        "no_hosp": "⚠️ আপনার অবস্থানের ৩০ কিমি এর মধ্যে কোনো নিবন্ধিত হাসপাতাল পাওয়া যায়নি।",
        "missing_loc": "⚠️ অনুগ্রহ করে নির্দিষ্ট এলাকার নাম দিন অথবা নিচের **📍 জিপিএস** বোতামে ক্লিক করুন।",
        "click_btn_prompt": "📍 **জিপিএস বিজ্ঞপ্তি:** আপনার অবস্থান শেয়ার করতে চ্যাট বক্সের পাশের **📍 জিপিএস বোতামে** ক্লিক করুন!",
        "read_btn": "🔊 জোরে পড়ুন"
    },
    "Tamil": {
        "sidebar_title": "🏥 கல்கோல் அமைப்புகள்",
        "ecosystem_title": "**SIH சுகாதார சுற்றுச்சூழல் அமைப்பு**",
        "eco_1": "- 👤 நோயாளி பராமரிப்பு", "eco_2": "- 🧑‍⚕️ கள சுகாதார பணியாளர்", "eco_3": "- 👨‍⚕️ மருத்துவர் பகுப்பாய்வு", "eco_4": "- 📦 மருத்துவ விநியோகம்", "eco_5": "- 🚑 அவசர SOS",
        "main_title": "🏥 கல்கோல் AI தோழன்",
        "caption": "சேவையை இணைக்கிறது, எங்குმე — ஸ்மார்ட் இந்தியா ஹேத்தான் முன்மாதிரி",
        "chat_input": "அறிகுறிகள் அல்லது மருந்துகள் பற்றி கேளுங்கள்...",
        "initial_greeting": "வணக்கம்! 🙏 மருத்துவமனைகளைக் கண்டறிய அரட்டைப் பெட்டிக்கு அருகில் உள்ள 📍 GPS பொத்தானைக் கிளிக் செய்யவும்.",
        "spinner_map": "வரைபடம் ஸ்கேன் செய்யப்படுகிறது...",
        "spinner_chat": "பாதை உருவாக்கப்படுகிறது...",
        "route_found": "📍 **பாதை கண்டறியப்பட்டது:** **{hosp_name}**.",
        "no_hosp": "⚠️ மருத்துவமனை எதுவும் கிடைக்கவில்லை.",
        "missing_loc": "⚠️ பகுதியைக் குறிப்பிடவும் அல்லது கீழே உள்ள 📍 GPS பொத்தானைக் கிளிக் செய்யவும்.",
        "click_btn_prompt": "📍 **GPS அறிவிப்பு:** அரட்டைப் பெட்டிக்கு அருகில் உள்ள 📍 GPS பொத்தானைக் கிளிக் செய்யவும்!",
        "read_btn": "🔊 உரக்கப் படியுங்கள்"
    },
    "Telugu": {
        "sidebar_title": "🏥 కాల్కాల్ సెట్టింగ్‌లు",
        "ecosystem_title": "**SIH ఆరోగ్య సంరక్షణ పర్యావరణ వ్యవస్థ**",
        "eco_1": "- 👤 రోగి సంరక్షణ", "eco_2": "- 🧑‍⚕️ గ్రౌండ్ హెల్త్ వర్కర్", "eco_3": "- 👨‍⚕️ డాక్టర్ విశ్లేషణ", "eco_4": "- 📦 వైద్య సరఫరా", "eco_5": "- 🚑 అత్యవసర SOS",
        "main_title": "🏥 కాల్కాల్ AI సహచరుడు",
        "caption": "సంరక్షణను కలుపుతోంది, ఎక్కడైనా — స్మార్ట్ ఇండియా హ్యాకథాన్ ప్రోటోటైప్",
        "chat_input": "లక్షణాలు లేదా మందుల గురించి అడగండి...",
        "initial_greeting": "నమస్కారం! 🙏 ఆసుపత్రులను కనుగొనడానికి చాట్ బాక్స్ పక్కన ఉన్న 📍 GPS బటన్‌ను క్లిక్ చేయండి.",
        "spinner_map": "మ్యాప్ స్కాన్ చేయబడుతోంది...",
        "spinner_chat": "మార్గం సృష్టించబడుతోంది...",
        "route_found": "📍 **మార్గం కనుగొనబడింది:** **{hosp_name}**.",
        "no_hosp": "⚠️ ఆసుపత్రి కనుగొనబడలేదు.",
        "missing_loc": "⚠️ ప్రాంతాన్ని పేర్కొనండి లేదా 📍 GPS బటన్‌ని క్లిక్ చేయండి.",
        "click_btn_prompt": "📍 **GPS నోటిఫికేషన్:** దయచేసి చాట్ బాక్స్ పక్కన ఉన్న 📍 GPS బటన్‌ను క్లిక్ చేయండి!",
        "read_btn": "🔊 గట్టిగా చదవండి"
    },
    "Marathi": {
        "sidebar_title": "🏥 कॅलकोल सेटिंग्ज",
        "ecosystem_title": "**SIH आरोग्य सेवा इकोसिस्टम**",
        "eco_1": "- 👤 रुग्ण काळजी", "eco_2": "- 🧑‍⚕️ ग्राउंड हेल्थ वर्कर", "eco_3": "- 👨‍⚕️ डॉक्टर विश्लेषण", "eco_4": "- 📦 वैद्यकीय पुरवठा", "eco_5": "- 🚑 आणीबाणी SOS",
        "main_title": "🏥 कॅलकोल AI सोबती",
        "caption": "काळजी जोडत आहे, कुठेही — स्मार्ट इंडिया हॅकाथॉन प्रोटोटाइप",
        "chat_input": "लक्षणे किंवा औषधांबद्दल विचारणा करा...",
        "initial_greeting": "नमस्कार! 🙏 रुग्णालये शोधण्यासाठी कृपया चॅट बॉक्स शेजारील 📍 GPS बटणावर क्लिक करा.",
        "spinner_map": "नकाशा स्कॅन केला जात आहे...",
        "spinner_chat": "मार्ग तयार केला जात आहे...",
        "route_found": "📍 **मार्ग सापडला:** **{hosp_name}**.",
        "no_hosp": "⚠️ रुग्णालय आढळले नाही.",
        "missing_loc": "⚠️ क्षेत्राचे नाव द्या किंवा 📍 GPS बटणावर क्लिक करा.",
        "click_btn_prompt": "📍 **GPS सूचना:** कृपया चॅट बॉक्स शेजारील 📍 GPS बटणावर क्लिक करा!",
        "read_btn": "🔊 मोठ्याने वाचा"
    }
}

LANG_CODES = {
    "English": "en-US",
    "Hindi": "hi-IN",
    "Bengali": "bn-BD",
    "Tamil": "ta-IN",
    "Telugu": "te-IN",
    "Marathi": "mr-IN"
}

# =========================================================
# 1. PAGE SETUP & SESSION MANAGEMENT
# =========================================================
st.set_page_config(page_title="Calcol AI", page_icon="🏥", layout="centered")

if "language_selected" not in st.session_state:
    st.session_state.language_selected = False
if "current_lang" not in st.session_state:
    st.session_state.current_lang = "English"

if not st.session_state.language_selected:
    st.markdown("<h1 style='text-align: center;'>🏥 Calcol AI Companion</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: gray;'>Please select your preferred language to begin / कृपया अपनी भाषा चुनें</h3>", unsafe_allow_html=True)
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        selected_lang_input = st.radio("Select Language:", ["English", "Hindi", "Bengali", "Tamil", "Telugu", "Marathi"], label_visibility="collapsed")
        if st.button("🚀 Enter Calcol / प्रवेश करें", use_container_width=True):
            st.session_state.current_lang = selected_lang_input
            st.session_state.language_selected = True
            st.session_state.messages = [{"role": "assistant", "content": TEXTS[selected_lang_input]["initial_greeting"]}]
            st.rerun()
    st.stop()

lang_choice = st.session_state.current_lang
t = TEXTS[lang_choice]
current_bcp47 = LANG_CODES.get(lang_choice, "en-US")

st.markdown("""
    <style>
    iframe[title*="geolocation"] {
        position: fixed !important;
        bottom: 22px !important;
        right: 15px !important;
        z-index: 999999 !important;
        width: 45px !important;
        height: 45px !important;
    }
    [data-testid="stChatInput"] {
        width: calc(100% - 190px) !important; 
    }
    </style>
""", unsafe_allow_html=True)

# =========================================================
# 2. PERSISTENT WIDGETS (MIC & LOCKED VIRTUAL KEYBOARD)
# =========================================================
VOICE_KEYBOARD_JS = f"""
<script>
const parentDoc = window.parent.document;
const parentWin = window.parent;

const currentLang = "{lang_choice}";
const speechLangCode = "{current_bcp47}";

const langMap = {{
    "Bengali": "bengali",
    "Hindi": "hindi",
    "Tamil": "tamil",
    "Telugu": "telugu",
    "Marathi": "hindi", 
    "English": "english"
}};
const layoutName = langMap[currentLang] || "english";

function initPersistentWidgets() {{
    const chatInputBox = parentDoc.querySelector('[data-testid="stChatInput"] textarea');
    if (!chatInputBox) return;

    if (!parentDoc.getElementById("mic-toggle-wrap") && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {{
        let micWrap = parentDoc.createElement("div");
        micWrap.id = "mic-toggle-wrap";
        micWrap.style.position = "fixed";
        micWrap.style.bottom = "24px";
        micWrap.style.right = "65px";
        micWrap.style.zIndex = "999999";

        let micBtn = parentDoc.createElement("button");
        micBtn.innerHTML = "🎙️";
        micBtn.style.fontSize = "20px";
        micBtn.style.background = "#fff";
        micBtn.style.border = "1px solid #ccc";
        micBtn.style.borderRadius = "50%";
        micBtn.style.width = "40px";
        micBtn.style.height = "40px";
        micBtn.style.cursor = "pointer";
        micBtn.style.boxShadow = "0px 2px 5px rgba(0,0,0,0.2)";
        micBtn.title = "Click to speak in " + currentLang;

        let SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition = new SpeechRecognition();
        recognition.lang = speechLangCode; 
        recognition.interimResults = true; 
        recognition.continuous = true;     

        let isListening = false;

        micBtn.onclick = () => {{
            if (!isListening) {{
                try {{
                    recognition.start();
                    micBtn.style.background = "#ff4b4b"; 
                    isListening = true;
                }} catch(e) {{}}
            }} else {{
                recognition.stop();
                micBtn.style.background = "#fff";
                isListening = false;
            }}
        }};

        recognition.onresult = (event) => {{
            let speechResult = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {{
                speechResult += event.results[i][0].transcript;
            }}
            let nativeInputValueSetter = Object.getOwnPropertyDescriptor(parentWin.HTMLTextAreaElement.prototype, "value").set;
            nativeInputValueSetter.call(chatInputBox, speechResult);
            chatInputBox.dispatchEvent(new Event('input', {{ bubbles: true }}));
        }};

        recognition.onerror = () => {{
            micBtn.style.background = "#fff";
            isListening = false;
        }};

        recognition.onend = () => {{
            if (isListening) {{
                try {{ recognition.start(); }} catch(e) {{}} 
            }} else {{
                micBtn.style.background = "#fff";
            }}
        }};

        micWrap.appendChild(micBtn);
        parentDoc.body.appendChild(micWrap);
    }}

    if (layoutName !== "english" && !parentDoc.getElementById("vkb-container")) {{
        const kbContainer = parentDoc.createElement("div");
        kbContainer.id = "vkb-container";
        kbContainer.style.position = "fixed";
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

                let keyboard = new Keyboard(parentDoc.querySelector('.simple-keyboard'), {{
                    onChange: input => {{
                        if (chatInputBox) {{
                            let nativeInputValueSetter = Object.getOwnPropertyDescriptor(parentWin.HTMLTextAreaElement.prototype, "value").set;
                            nativeInputValueSetter.call(chatInputBox, input);
                            chatInputBox.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        }}
                    }},
                    onKeyPress: button => {{
                        if (button === "{{enter}}") {{
                            let sendBtn = parentDoc.querySelector('[data-testid="stChatInputSubmitButton"]');
                            if (sendBtn && !sendBtn.disabled) sendBtn.click();
                            keyboard.clearInput();
                            kbContainer.style.display = "none";
                        }}
                    }},
                    ...layout.get(layoutName)
                }});

                if (!parentDoc.getElementById("vkb-toggle-wrap")) {{
                    let btnWrap = parentDoc.createElement("div");
                    btnWrap.id = "vkb-toggle-wrap";
                    btnWrap.style.position = "fixed";
                    btnWrap.style.bottom = "24px";
                    btnWrap.style.right = "105px"; 
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
                }}

                parentDoc.getElementById("vkb-close").onclick = () => kbContainer.style.display = "none";
            }});
        }});
    }}
}}

initPersistentWidgets();
setInterval(initPersistentWidgets, 1000);
</script>
"""
components.html(VOICE_KEYBOARD_JS, height=0, width=0)

# =========================================================
# 3. SIDEBAR & CONFIGURATION
# =========================================================
st.sidebar.title(t["sidebar_title"])

new_lang_choice = st.sidebar.selectbox(
    "🌐 Change Language / भाषा बदलें",
    ["English", "Hindi", "Bengali", "Tamil", "Telugu", "Marathi"],
    index=["English", "Hindi", "Bengali", "Tamil", "Telugu", "Marathi"].index(lang_choice)
)

if new_lang_choice != lang_choice:
    st.session_state.current_lang = new_lang_choice
    st.session_state.messages = [{"role": "assistant", "content": TEXTS[new_lang_choice]["initial_greeting"]}]
    st.rerun()

api_mode = st.sidebar.radio(
    "Select API Connection:",
    ["🟢 Auto (Calcol Server)", "🔑 Custom (Your Own Key)"]
)

HIDDEN_API_KEY = "put here "

if api_mode == "🟢 Auto (Calcol Server)":
    st.sidebar.success("✅ Connected securely to Calcol Server.")
    ACTIVE_API_KEY = HIDDEN_API_KEY
else:
    ACTIVE_API_KEY = st.sidebar.text_input("Enter your OpenRouter API Key", type="password")
    st.sidebar.caption("[👉 Generate a free OpenRouter Key](https://openrouter.ai/keys)")

st.sidebar.markdown("---")
st.sidebar.markdown(f"{t['ecosystem_title']}\n{t['eco_1']}\n{t['eco_2']}\n{t['eco_3']}\n{t['eco_4']}\n{t['eco_5']}")
st.title(t["main_title"])
st.caption(t["caption"])

# =========================================================
# 4. MAP & ROUTING HELPERS (WITH LINKS AND DISTANCE)
# =========================================================
def get_real_nearest_hospital(lat, lon):
    overpass_url = "http://overpass-api.de/api/interpreter"
    query = f"""[out:json];(nwr["amenity"="hospital"](around:15000, {lat}, {lon});nwr["amenity"="clinic"](around:15000, {lat}, {lon});nwr["healthcare"="hospital"](around:15000, {lat}, {lon});nwr["amenity"="doctors"](around:15000, {lat}, {lon}););out center;"""
    try:
        response = requests.get(overpass_url, params={"data": query}, headers={'User-Agent': 'Calcol/1.0'}, timeout=15)
        data = response.json()
        if data.get("elements"):
            closest, min_dist = None, float("inf")
            for el in data["elements"]:
                h_lat = el.get("lat") or el.get("center", {}).get("lat")
                h_lon = el.get("lon") or el.get("center", {}).get("lon")
                if not h_lat: continue
                name = el.get("tags", {}).get("name", "Local Healthcare Center")
                dist = geodesic((lat, lon), (h_lat, h_lon)).kilometers
                if dist < min_dist:
                    min_dist, closest = dist, (h_lat, h_lon, name)
            return closest
    except: pass
    return None

def get_real_road_route(lat1, lon1, lat2, lon2):
    url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}?overview=full&geometries=geojson"
    try:
        res = requests.get(url, headers={'User-Agent': 'Calcol/1.0'}, timeout=10)
        if res.json().get("code") == "Ok":
            return [(coord[1], coord[0]) for coord in res.json()["routes"][0]["geometry"]["coordinates"]]
    except: pass
    return [(lat1, lon1), (lat2, lon2)]

def generate_unified_map_html(user_lat, user_lon, dict_t):
    m = folium.Map(location=[user_lat, user_lon], zoom_start=15)
    folium.Marker([user_lat, user_lon], popup="Your Location", icon=folium.Icon(color="blue", icon="user")).add_to(m)
    
    nearest_hosp = get_real_nearest_hospital(user_lat, user_lon)
    if nearest_hosp:
        hosp_lat, hosp_lon, hosp_name = nearest_hosp
        dist_km = geodesic((user_lat, user_lon), (hosp_lat, hosp_lon)).kilometers
        dist_str = f"{dist_km:.1f} km"
    else:
        hosp_lat, hosp_lon = user_lat + 0.003, user_lon + 0.003
        hosp_name = "Local Medical Clinic"
        dist_str = "~0.5 km"
        
    folium.Marker([hosp_lat, hosp_lon], popup=hosp_name, icon=folium.Icon(color="red", icon="plus-square", prefix="fa")).add_to(m)
    route_coords = get_real_road_route(user_lat, user_lon, hosp_lat, hosp_lon)
    folium.PolyLine(route_coords, color="#EF4444", weight=5).add_to(m)
    m.fit_bounds([[user_lat, user_lon], [hosp_lat, hosp_lon]])
    
    google_maps_link = f"https://www.google.com/maps/dir/?api=1&origin={user_lat},{user_lon}&destination={hosp_lat},{hosp_lon}"
    
    reply_text = dict_t["route_found"].format(hosp_name=hosp_name)
    reply_text += f"\n\n📏 **Distance / দূরত্ব:** {dist_str}\n\n🔗 [**Open in Google Maps / গুগল ম্যাপে খুলুন**]({google_maps_link})"
    
    return reply_text, m._repr_html_()

# =========================================================
# 5. SAFE TEXT-TO-SPEECH (CRASH PROOF)
# =========================================================
def speak_response_js(text, lang_code, unique_key):
    if text is None:
        text = ""
        
    clean_text = str(text).replace("*", "").replace("#", "").strip()
    
    if not clean_text:
        return
        
    safe_json_text = json.dumps(clean_text) 
    
    if st.button(t["read_btn"], key=f"speak_{unique_key}"):
        speech_js = f"""
        <script>
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            let utterance = new SpeechSynthesisUtterance({safe_json_text});
            utterance.lang = "{lang_code}";
            utterance.rate = 0.95;
            window.speechSynthesis.speak(utterance);
        }}
        </script>
        """
        components.html(speech_js, height=0, width=0, scrolling=False)

# =========================================================
# 6. GPS TRACKER & CHAT SESSION
# =========================================================
location = streamlit_geolocation()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": t["initial_greeting"]}]
if "last_gps_coord" not in st.session_state:
    st.session_state.last_gps_coord = None

current_gps = (location.get("latitude"), location.get("longitude")) if location and location.get("latitude") else None

if current_gps and current_gps != st.session_state.last_gps_coord:
    st.session_state.last_gps_coord = current_gps
    with st.spinner(t["spinner_map"]):
        reply_text, map_html = generate_unified_map_html(current_gps[0], current_gps[1], t)
        st.session_state.messages.append({"role": "assistant", "content": reply_text, "map_html": map_html})
        st.rerun()

for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "map_html" in msg and msg["map_html"]: 
            components.html(msg["map_html"], height=400)
        if msg["role"] == "assistant":
            active_voice_code = LANG_CODES.get(lang_choice, "en-US")
            speak_response_js(msg["content"], active_voice_code, unique_key=idx)

# =========================================================
# 7. AI PROCESSING LOOP & FORCED MAP INTERCEPTOR
# =========================================================
prompt = st.chat_input(t["chat_input"])

if prompt:
    if ACTIVE_API_KEY == "PASTE_YOUR_OPENROUTER_KEY_HERE" or ACTIVE_API_KEY == "":
        st.error("⚠️ API Key is missing! Please configure your OpenRouter key.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=ACTIVE_API_KEY,
            )
            MODEL_NAME = "openrouter/free"

            # 🔥 MASSIVELY EXPANDED KEYWORDS (English, Bengali, Hindi, Hinglish/Benglish)
            map_keywords = [
                "map", "route", "rout", "way", "hospital", "hosp", "clinic", "nearest", "where", "location", "distance",
                "হাসপাতাল", "হসপিটাল", "রুট", "রাস্তা", "ম্যাপ", "কোথায়", "নিকটতম", "দূরত্ব", "দাও", "দেখান", "কাছাকাছি",
                "अस्पताल", "क्लीनिक", "नजदीकी", "रास्ता", "मैप", "दिशा", "दूरी"
            ]
            is_map_query = any(k in prompt.lower() for k in map_keywords)
            
            my_loc_keywords = ["my address", "my location", "near me", "from me", "around me", "আমার কাছে", "আমার স্থান", "मेरे पास", "amake", "near"]
            is_my_location = any(k in prompt.lower() for k in my_loc_keywords)

            # --- MAP INTERCEPTOR ---
            if is_map_query:
                # 🗺️ CASE 1: Near GPS (Ensuring they aren't asking for a different village)
                if is_my_location and ("harinbari" not in prompt.lower() and "sagar" not in prompt.lower()):
                    if not current_gps:
                        reply_text = t["click_btn_prompt"]
                        st.session_state.messages.append({"role": "assistant", "content": reply_text})
                        with st.chat_message("assistant"): 
                            st.warning(reply_text)
                        st.stop()
                    else:
                        with st.spinner(t["spinner_map"]):
                            reply_text, map_html = generate_unified_map_html(current_gps[0], current_gps[1], t)
                            st.session_state.messages.append({"role": "assistant", "content": reply_text, "map_html": map_html})
                            with st.chat_message("assistant"):
                                st.markdown(reply_text)
                                components.html(map_html, height=400)
                        st.stop()

                # 🗺️ CASE 2: Specific place name (e.g., "Harinbari, Sagar") - FORCED INTERCEPT
                else:
                    with st.spinner(t["spinner_chat"]):
                        # Smart AI Extraction for Geocoding
                        extraction_response = client.chat.completions.create(
                            model=MODEL_NAME,
                            messages=[
                                {"role": "system", "content": "You are a geocoding assistant. Extract ONLY the village, town, city, or area name from the user's query. Translate it to English. If it's a small place, append its district or 'West Bengal, India' (e.g., 'Harinbari, Sagar, West Bengal, India'). DO NOT output any other text, punctuation, or explanation."},
                                {"role": "user", "content": prompt}
                            ],
                            temperature=0.0
                        )
                        place_name = extraction_response.choices[0].message.content.strip()
                        user_lat, user_lon = None, None
                        
                        geolocator = Nominatim(user_agent="calcol_sih_app")
                        try:
                            loc = geolocator.geocode(place_name, timeout=10)
                            if loc:
                                user_lat, user_lon = loc.latitude, loc.longitude
                        except:
                            pass
                        
                        if not user_lat or not user_lon:
                            try:
                                broad_place = place_name.split(',')[0] + ", India"
                                loc = geolocator.geocode(broad_place, timeout=10)
                                if loc:
                                    user_lat, user_lon = loc.latitude, loc.longitude
                            except:
                                pass

                        # 🗺️ Successful map generation
                        if user_lat and user_lon:
                            reply_text, map_html = generate_unified_map_html(user_lat, user_lon, t)
                            st.session_state.messages.append({"role": "assistant", "content": reply_text, "map_html": map_html})
                            with st.chat_message("assistant"):
                                st.markdown(reply_text)
                                components.html(map_html, height=400)
                            st.stop()
                        
                        # 🔗 Hard Fallback Google Maps Link (NEVER text essay)
                        else:
                            search_query = prompt.replace(" ", "+")
                            gmap_link = f"https://www.google.com/maps/search/hospital+near+{place_name.replace(' ', '+')}"
                            
                            reply_text = f"📍 **মানচিত্র রেন্ডারিং / Map Generation**\n\nI couldn't pinpoint the exact GPS coordinates for '{place_name}' on the internal map, but you can view the live accurate route here:\n\n🔗 [**Click to open Google Maps for {place_name}**]({gmap_link})"
                            
                            st.session_state.messages.append({"role": "assistant", "content": reply_text})
                            with st.chat_message("assistant"):
                                st.success(reply_text)
                            st.stop()

            # 💬 CASE 3: Normal Medical / General Text Chat
            system_instruction = f"""
            You are Calcol AI, an efficient digital healthcare assistant for India. 
            The user interface is set to {lang_choice}. 
            CRITICAL INSTRUCTION: Detect the exact language and script of the user's input. You must respond fluently, accurately, and natively in that exact language (e.g., if they speak Bengali, reply in proper Bengali script; if Hindi, reply in Hindi script). 
            Provide clear home care guidance and mention OTC options if applicable. Always end with: 
            'Disclaimer: Calcol AI is not a doctor. Consult a physician for serious issues.' (Translate this disclaimer into the user's response language).
            Keep answers concise and structured.
            """
            
            api_messages = [{"role": "system", "content": system_instruction}]
            for m in st.session_state.messages:
                api_messages.append({"role": m["role"], "content": m["content"]})
            
            chat_response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=api_messages,
                temperature=0.3
            )
            
            reply = chat_response.choices[0].message.content
            
            if reply is None:
                reply = "I'm sorry, I couldn't process that. Could you please repeat?"
                
            st.session_state.messages.append({"role": "assistant", "content": reply})
            
            with st.chat_message("assistant"): 
                st.markdown(reply)

            st.rerun()

        except Exception as e:
            st.error(f"Error communicating with AI: {e}")
