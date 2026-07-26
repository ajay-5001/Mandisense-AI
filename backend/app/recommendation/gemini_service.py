"""
MandiSense Gemini AI Service — AI Assistant and Explanation Generator
===================================================================
Uses Google Gemini API to generate structured pricing recommendations,
chat responses, and daily business summaries. Falls back to offline templates if API key is missing or calls fail.
"""

import os
import json
import httpx
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

# We default to gemini-1.5-flash for speed, cost-effectiveness, and reliability.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
CANDIDATE_MODELS = [GEMINI_MODEL, "gemini-1.5-flash", "gemini-2.0-flash", "gemini-2.5-flash", "gemini-1.5-pro"]
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"

def get_api_key(headers_api_key: Optional[str] = None) -> str:
    """Retrieve Gemini API key from headers or local environment."""
    return headers_api_key or os.getenv("GEMINI_API_KEY", "")

async def call_gemini_api(
    prompt: str,
    system_instruction: Optional[str] = None,
    response_json: bool = False,
    api_key: Optional[str] = None
) -> str:
    """
    Sends a request to the Google Gemini API with candidate model fallbacks.
    """
    key = api_key or os.getenv("GEMINI_API_KEY", "")
    if not key:
        raise ValueError("Gemini API key is missing.")
        
    seen = set()
    models_to_try = [m for m in CANDIDATE_MODELS if not (m in seen or seen.add(m))]
    
    last_exception = None
    for model_name in models_to_try:
        url = f"{GEMINI_API_URL}/{model_name}:generateContent?key={key}"
        
        payload: Dict[str, Any] = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }
        
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [
                    {"text": system_instruction}
                ]
            }
            
        generation_config = {}
        if response_json:
            generation_config["responseMimeType"] = "application/json"
            
        if generation_config:
            payload["generationConfig"] = generation_config
            
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                res_data = response.json()
                try:
                    return res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                except (KeyError, IndexError):
                    raise Exception(f"Unexpected response structure from Gemini API: {res_data}")
            else:
                last_exception = Exception(f"Gemini API Error ({response.status_code}) for {model_name}: {response.text}")
                if response.status_code in (400, 403):
                    # Invalid key or unauthorized, no need to retry other models
                    break
                    
    raise last_exception or Exception("Gemini API call failed.")

async def generate_explanation_gemini(
    recommendation: Dict[str, Any],
    language: str = "en",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates a premium pricing explanation, risks, and suggestions from Gemini.
    Workflow: Weather + Forecast + Spoilage Risk + Price Advisor -> Gemini -> Output.
    """
    lang_names = {"en": "English", "hi": "Hindi", "ta": "Tamil"}
    lang_name = lang_names.get(language, "English")
    
    # Structure input data for Gemini
    structured_data = {
        "product": recommendation.get("item_name", "Perishable Item"),
        "stock": recommendation.get("stock_kg", 50),
        "expectedDemand": recommendation.get("forecast_demand_today", 0),
        "humidity": recommendation.get("humidity", 50),
        "temperature": recommendation.get("temperature", 30),
        "mandiPrice": recommendation.get("current_price", 0),
        "sellingPrice": recommendation.get("suggested_price", 0),
        "spoilageRisk": recommendation.get("risk_score", 0)
    }
    
    system_instruction = (
        "You are an expert AI Price Assistant for local vegetable and fruit vendors in India. "
        "Your task is to review the structured input data for a perishable product and generate a detailed recommendation report. "
        "You must respond in a valid JSON format with the keys: 'business_explanation', 'recommendation', 'risks', and 'suggestions'. "
        f"All text fields in the JSON response must be in the {lang_name} language. "
        "Keep language simple, direct, vendor-friendly, and practical."
    )
    
    prompt = (
        f"Input Data:\n{json.dumps(structured_data, indent=2)}\n\n"
        "Generate the recommendations, risks, and suggestions in JSON format. Ensure all text values are written in "
        f"{lang_name} so that a local vendor speaking {lang_name} can understand them."
    )
    
    try:
        raw_res = await call_gemini_api(prompt, system_instruction, response_json=True, api_key=api_key)
        return json.loads(raw_res)
    except Exception as e:
        # Graceful fallback: return structure formatted for standard offline display
        print(f"Gemini Explanation generation failed: {e}. Falling back.")
        return {
            "business_explanation": recommendation.get("explanation", ""),
            "recommendation": f"Adjust price to Rs. {recommendation.get('suggested_price')} / kg ({recommendation.get('price_change_pct'):+.1f}%)",
            "risks": "Spoilage risk based on local weather and stock levels.",
            "suggestions": "Review weather patterns and monitor shelf storage moisture levels."
        }

async def generate_daily_summary_gemini(
    summary_data: Dict[str, Any],
    language: str = "en",
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generates a premium business summary widget output for the vendor dashboard.
    """
    lang_names = {"en": "English", "hi": "Hindi", "ta": "Tamil"}
    lang_name = lang_names.get(language, "English")
    
    system_instruction = (
        "You are MandiSense AI, a senior business advisor for Indian vegetable and fruit vendors. "
        "Review today's consolidated store data and output a daily report summary. "
        "You must respond in a valid JSON format with the keys: "
        "'overall_performance', 'expected_demand', 'high_risk_products', 'suggested_discounts', "
        "'weather_impact', 'estimated_profit', and 'stock_warnings'. "
        f"All values must be written in the {lang_name} language. "
        "Write in a highly professional, encouraging, and supportive tone, providing concrete suggestions and figures."
    )
    
    prompt = (
        f"Today's Business Data Summary:\n{json.dumps(summary_data, indent=2)}\n\n"
        f"Generate the daily business summary in JSON format. All values must be in the {lang_name} language."
    )
    
    try:
        raw_res = await call_gemini_api(prompt, system_instruction, response_json=True, api_key=api_key)
        return json.loads(raw_res)
    except Exception as e:
        print(f"Gemini Daily Summary failed: {e}. Falling back.")
        return {
            "overall_performance": "Market conditions remain stable. Keep checking demand indicators.",
            "expected_demand": f"Expected demand is healthy for key seasonal items.",
            "high_risk_products": "No critical risk items. Monitor leafy vegetables for humidity decay.",
            "suggested_discounts": "Reduce pricing for items showing slow demand movements.",
            "weather_impact": "Weather is normal. No supply line disruptions expected.",
            "estimated_profit": "Expected profits remain on track with daily projections.",
            "stock_warnings": "Keep inventory aligned to 3-day forecasted demand levels."
        }

def get_offline_chat_response(
    query: str,
    region_name: str,
    language: str = "en",
    data_context: Optional[Dict[str, Any]] = None
) -> str:
    """Generates smart data-driven responses offline when Gemini API key is unconfigured or unavailable."""
    q_lower = query.lower().strip()
    products = (data_context or {}).get("products", [])
    weather = (data_context or {}).get("weather", {})
    temp = weather.get("temp", 30.0)
    humidity = weather.get("humidity", 65.0)

    # 1. Greetings
    greeting_words = ["hello", "hi", "hey", "namaste", "vanakkam", "नमस्ते", "வணக்கம்", "good morning", "good evening"]
    if any(g in q_lower for g in greeting_words):
        if language == "hi":
            return f"नमस्ते! मैं मंडीसेंस AI हूँ। {region_name} मंडी के लिए आज का तापमान {temp}°C है। मैं आपकी मूल्य निर्धारण, स्टॉक और बिक्री में कैसे मदद कर सकता हूँ?"
        elif language == "ta":
            return f"வணக்கம்! நான் மண்டிசென்ஸ் AI. {region_name} சந்தையின் இன்றைய வெப்பநிலை {temp}°C. உங்கள் விலை மற்றும் இருப்பு பற்றிய தகவல்களுக்கு நான் உதவ முடியும்."
        else:
            return f"Hello! I am MandiSense AI, your virtual assistant for {region_name}. Current temperature is {temp}°C with {humidity}% humidity. How can I help your mandi business today?"

    # 2. Specific Crop / Tomato
    if any(k in q_lower for k in ["tomato", "टमाटर", "தக்காளி"]):
        tom = next((p for p in products if "tomato" in p.get("name", "").lower()), None)
        if tom:
            s_price = tom.get("suggested_price", 0)
            m_price = tom.get("mandi_price", 0)
            risk = tom.get("risk_score", 0)
            stock = tom.get("stock", 0)
            if language == "hi":
                return f"टमाटर का अनुशंसित मूल्य ₹{s_price}/किग्रा है (थोक भाव ₹{m_price}/किग्रा)। स्टॉक {stock:.1f}किग्रा और खराबी जोखिम {risk:.0f}/100 है।"
            elif language == "ta":
                return f"தக்காளி பரிந்துரைக்கப்பட்ட விலை ₹{s_price}/கிலோ (மொத்த விலை ₹{m_price}/கிலோ). கெட்டுப்போகும் ஆபத்து {risk:.0f}/100."
            else:
                return f"Tomato is recommended at ₹{s_price}/kg (wholesale mandi price: ₹{m_price}/kg). Stock is {stock:.1f}kg with a spoilage risk score of {risk:.0f}/100."

    # 3. Buy / Restock / Purchase
    if any(k in q_lower for k in ["buy", "purchase", "restock", "खरीद", "खरीदना", "வாங்க"]):
        low_stock = [p["name"] for p in products if p.get("stock", 0) < p.get("forecast_demand_today", 0) * 1.5]
        items_str = ", ".join(low_stock[:3]) if low_stock else "None (Stock is sufficient)"
        if language == "hi":
            return f"पूर्वानुमानित मांग के आधार पर, आपको जल्द ही इन वस्तुओं को रीस्टॉक करना चाहिए: {items_str}।"
        elif language == "ta":
            return f"தேவையின் அடிப்படையில், நீங்கள் விரைவில் இவற்றை வாங்க வேண்டும்: {items_str}."
        else:
            return f"Based on forecasted demand, consider restocking: {items_str}. Keep stock aligned with 2-day projected sales."

    # 4. Spoilage / Risk
    if any(k in q_lower for k in ["spoilage", "risk", "decay", "spoil", "खराब", "जोखिम", "ஆபத்து"]):
        high_risk = sorted(products, key=lambda x: x.get("risk_score", 0), reverse=True)[:3]
        risk_strs = [f"{p['name']} ({p.get('risk_score', 0):.0f}/100)" for p in high_risk]
        items_str = ", ".join(risk_strs) if risk_strs else "None"
        if language == "hi":
            return f"सबसे अधिक खराबी जोखिम वाले उत्पाद: {items_str}। इन्हें तेजी से बेचने के लिए 5-10% छूट देने पर विचार करें।"
        elif language == "ta":
            return f"அதிக ஆபத்துள்ள தயாரிப்புகள்: {items_str}. தள்ளுபடி வழங்கி விரைவில் விற்பனை செய்யவும்."
        else:
            return f"Highest spoilage risk items: {items_str}. Consider offering small discounts to clear inventory faster."

    # 5. Profitable / Revenue / Profit
    if any(k in q_lower for k in ["profit", "profitable", "margin", "revenue", "लाभ", "मुनाफा", "லாபம்"]):
        top_items = sorted(products, key=lambda x: x.get("forecast_demand_today", 0), reverse=True)[:3]
        items_str = ", ".join([p["name"] for p in top_items]) if top_items else "Key inventory"
        if language == "hi":
            return f"आज के उच्चतम मांग वाले उत्पाद हैं: {items_str}। अनुशंसित कीमतों पर बिक्री करके अपना लाभ अधिकतम करें।"
        elif language == "ta":
            return f"இன்றைய அதிக லாபம் மற்றும் தேவை உள்ள தயாரிப்புகள்: {items_str}."
        else:
            return f"Highest demand products today: {items_str}. Selling at recommended retail prices maximizes total daily revenue."

    # 6. General queries
    if language == "hi":
        return f"{region_name} मंडी के लिए मंडीसेंस AI सक्रिय है। मौसम: {temp}°C, आर्द्रता: {humidity}%। लाइव ऑनलाइन AI चैट उत्तरों के लिए सेटिंग्स में अपनी Gemini API Key की जांच करें।"
    elif language == "ta":
        return f"{region_name} மண்டிசென்ஸ் AI நேரலை. வெப்பநிலை: {temp}°C, ஈரப்பதம்: {humidity}%. ஆன்லைன் AI பதில்களுக்கு API விசையை சரிபார்க்கவும்."
    else:
        return f"MandiSense AI is active for {region_name} (Temp: {temp}°C, Humidity: {humidity}%). For customized AI generative responses, configure your Google Gemini API Key in Settings."

async def generate_chat_response_gemini(
    query: str,
    region_name: str,
    history: List[Dict[str, str]],
    language: str = "en",
    data_context: Optional[Dict[str, Any]] = None,
    api_key: Optional[str] = None
) -> str:
    """
    Generates chat assistant responses based on the vendor's dashboard context.
    Falls back gracefully to data-driven smart offline response if API key is missing or call fails.
    """
    lang_names = {"en": "English", "hi": "Hindi", "ta": "Tamil"}
    lang_name = lang_names.get(language, "English")
    
    system_instruction = (
        "You are MandiSense AI Assistant, a helpful and highly knowledgeable virtual business partner for small "
        "retail vegetable, fruit, and kirana vendors in India. "
        f"You converse naturally and output responses ONLY in the {lang_name} language. "
        "You have complete access to the vendor's live dashboard data, weather, stock, and demand forecasts. "
        "Always use the provided data context to answer queries accurately, using actual numbers, prices, and suggestions. "
        "Be concise, warm, practical, and clear. Avoid sounding too technical — explain concepts like a friendly partner. "
        "Limit response to 2-3 short, clear sentences or bullet points."
    )
    
    # Format message history
    formatted_messages = []
    for msg in history:
        role = "user" if msg.get("sender") == "user" else "model"
        formatted_messages.append(f"{role.capitalize()}: {msg.get('text')}")
    
    chat_history_str = "\n".join(formatted_messages)
    
    prompt = (
        f"Vendor Location/Market: {region_name}\n"
        f"Live Dashboard Data Context:\n{json.dumps(data_context, indent=2) if data_context else 'No data'}\n\n"
        f"Conversation History:\n{chat_history_str}\n\n"
        f"Vendor Query: {query}\n\n"
        f"Response (written in {lang_name}):"
    )
    
    try:
        return await call_gemini_api(prompt, system_instruction, response_json=False, api_key=api_key)
    except Exception as e:
        print(f"Gemini Chat assistant call failed: {e}. Falling back to smart contextual response.")
        return get_offline_chat_response(query, region_name, language, data_context)

