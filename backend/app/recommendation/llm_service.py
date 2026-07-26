"""
MandiSense LLM Service — Natural Language Recommendation Generator
===================================================================
Converts structured price recommendations into natural-language
explanations that vendors can understand.

Two modes:
    1. TEMPLATE MODE (default, no API key needed):
       Uses pre-written templates in English, Hindi, and Tamil.
       Fast, free, and works offline.
    
    2. LLM MODE (optional, requires ANTHROPIC_API_KEY):
       Sends structured data to Claude API for richer, more natural
       explanations. Falls back to template mode on any failure.

The frontend renders whichever output is returned — both use the
same JSON structure.
"""

import os
import json
import httpx
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATE-BASED EXPLANATIONS (works offline, no API needed)
# ═══════════════════════════════════════════════════════════════════════════════

TEMPLATES = {
    "en": {
        "reduce": {
            "HIGH_SPOILAGE": "Reduce {item} price by {pct}% today — spoilage risk is {risk}/100. High {factor} will cause stock to go bad quickly. Sell at Rs.{price}/kg to clear stock fast.",
            "MODERATE_SPOILAGE": "Consider reducing {item} price by {pct}% — moderate spoilage risk ({risk}/100). Selling faster at Rs.{price}/kg will reduce waste.",
            "DEMAND_DROP": "Demand for {item} is expected to drop {demand_pct}% over the next 3 days. Lower price to Rs.{price}/kg to maintain sales volume.",
            "OVERSUPPLY": "There's more {item} in the market than buyers need. Reduce price to Rs.{price}/kg to avoid unsold stock spoiling.",
            "default": "Reduce {item} price to Rs.{price}/kg ({pct}% lower) based on current market conditions.",
        },
        "increase": {
            "DEMAND_SPIKE": "Good news! Demand for {item} is rising {demand_pct}% — you can increase price to Rs.{price}/kg and still sell well.",
            "WEATHER_DISRUPTION": "{item} supply may be disrupted due to {weather}. You can hold or raise price to Rs.{price}/kg.",
            "default": "Market conditions favor increasing {item} price to Rs.{price}/kg ({pct}% higher).",
        },
        "hold": {
            "STABLE": "No major changes for {item} today. Keep selling at Rs.{price}/kg — market is stable.",
            "default": "{item} pricing looks fine at Rs.{price}/kg. No changes recommended today.",
        },
    },
    "hi": {
        "reduce": {
            "HIGH_SPOILAGE": "{item} का दाम {pct}% कम करें — खराब होने का खतरा {risk}/100 है। ज़्यादा {factor} से माल जल्दी खराब होगा। Rs.{price}/kg पर बेचें।",
            "MODERATE_SPOILAGE": "{item} का दाम {pct}% कम करने पर विचार करें — खराबी का मध्यम खतरा ({risk}/100)। Rs.{price}/kg पर जल्दी बेचें।",
            "DEMAND_DROP": "{item} की मांग अगले 3 दिनों में {demand_pct}% गिरने की उम्मीद है। बिक्री बनाए रखने के लिए दाम Rs.{price}/kg करें।",
            "OVERSUPPLY": "बाज़ार में {item} ज़रूरत से ज़्यादा है। माल खराब होने से बचाने के लिए दाम Rs.{price}/kg करें।",
            "default": "बाज़ार की स्थिति के अनुसार {item} का दाम Rs.{price}/kg ({pct}% कम) करें।",
        },
        "increase": {
            "DEMAND_SPIKE": "अच्छी खबर! {item} की मांग {demand_pct}% बढ़ रही है — दाम Rs.{price}/kg तक बढ़ा सकते हैं।",
            "WEATHER_DISRUPTION": "{weather} के कारण {item} की आपूर्ति प्रभावित हो सकती है। दाम Rs.{price}/kg रख सकते हैं।",
            "default": "बाज़ार की स्थिति {item} का दाम Rs.{price}/kg ({pct}% ज़्यादा) बढ़ाने के अनुकूल है।",
        },
        "hold": {
            "STABLE": "{item} में आज कोई बड़ा बदलाव नहीं। Rs.{price}/kg पर बेचते रहें — बाज़ार स्थिर है।",
            "default": "{item} का दाम Rs.{price}/kg ठीक है। आज कोई बदलाव की ज़रूरत नहीं।",
        },
    },
    "ta": {
        "reduce": {
            "HIGH_SPOILAGE": "{item} விலையை {pct}% குறைக்கவும் — கெட்டுப்போகும் ஆபத்து {risk}/100. அதிக {factor} காரணமாக சரக்கு விரைவில் கெட்டுவிடும். Rs.{price}/kg இல் விற்கவும்.",
            "MODERATE_SPOILAGE": "{item} விலையை {pct}% குறைக்க யோசிக்கவும் — மிதமான கெடும் ஆபத்து ({risk}/100). Rs.{price}/kg இல் விரைவாக விற்கவும்.",
            "DEMAND_DROP": "{item} தேவை அடுத்த 3 நாட்களில் {demand_pct}% குறையும் என எதிர்பார்க்கப்படுகிறது. Rs.{price}/kg ஆக விலை குறைக்கவும்.",
            "OVERSUPPLY": "சந்தையில் {item} அதிகமாக உள்ளது. விற்கப்படாத சரக்கு கெட்டுப்போவதைத் தவிர்க்க Rs.{price}/kg ஆக குறைக்கவும்.",
            "default": "சந்தை நிலையின் அடிப்படையில் {item} விலையை Rs.{price}/kg ({pct}% குறைவு) ஆக்கவும்.",
        },
        "increase": {
            "DEMAND_SPIKE": "நல்ல செய்தி! {item} தேவை {demand_pct}% உயர்கிறது — விலையை Rs.{price}/kg ஆக உயர்த்தலாம்.",
            "WEATHER_DISRUPTION": "{weather} காரணமாக {item} விநியோகம் பாதிக்கப்படலாம். விலையை Rs.{price}/kg ஆக வைக்கலாம்.",
            "default": "சந்தை நிலை {item} விலையை Rs.{price}/kg ({pct}% அதிகம்) உயர்த்த ஏற்றது.",
        },
        "hold": {
            "STABLE": "{item} இல் இன்று பெரிய மாற்றம் இல்லை. Rs.{price}/kg இல் விற்கவும் — சந்தை நிலையானது.",
            "default": "{item} விலை Rs.{price}/kg சரியாக உள்ளது. இன்று மாற்றம் தேவையில்லை.",
        },
    },
}


def _get_primary_factor(recommendation: dict) -> str:
    """Extract the dominant weather/risk factor from the recommendation."""
    factors = recommendation.get("risk_level", {})
    # Check risk factors
    risk_data = recommendation.get("reasons", [])
    for reason in risk_data:
        if "humidity" in reason.get("detail", "").lower():
            return "humidity (moisture)"
        if "temperature" in reason.get("detail", "").lower() or "heat" in reason.get("detail", "").lower():
            return "temperature (heat)"
    return "weather conditions"


def generate_explanation_template(recommendation: dict, language: str = "en") -> str:
    """
    Generate a natural-language explanation using pre-built templates.
    
    Args:
        recommendation: Output from price_advisor.generate_recommendation()
        language: Language code — 'en', 'hi', or 'ta'
    
    Returns:
        A human-readable explanation string in the selected language.
    """
    lang_templates = TEMPLATES.get(language, TEMPLATES["en"])
    action = recommendation["action"]
    action_templates = lang_templates.get(action, lang_templates.get("hold", {}))
    
    # Find the best template based on reason codes
    primary_reason = recommendation["reasons"][0]["code"] if recommendation["reasons"] else "STABLE"
    template = action_templates.get(primary_reason, action_templates.get("default", ""))
    
    # Build template variables
    demand_pct = 0
    weather = ""
    for reason in recommendation["reasons"]:
        if "demand" in reason["code"].lower():
            demand_pct = abs(reason.get("impact_pct", 0)) * 3  # Approximate
        if reason["code"] == "WEATHER_DISRUPTION":
            weather = reason.get("detail", "bad weather")
    
    explanation = template.format(
        item=recommendation["item_name"],
        pct=abs(recommendation["price_change_pct"]),
        price=recommendation["suggested_price"],
        risk=recommendation.get("risk_score", 0),
        factor=_get_primary_factor(recommendation),
        demand_pct=f"{abs(demand_pct):.0f}",
        weather=weather,
    )
    
    return explanation


async def generate_explanation_llm(recommendation: dict, language: str = "en") -> str:
    """
    Generate a natural-language explanation using Claude API.
    
    Falls back to template mode if API key is missing or call fails.
    
    Args:
        recommendation: Output from price_advisor.generate_recommendation()
        language: Language code — 'en', 'hi', or 'ta'
    
    Returns:
        A human-readable explanation string.
    """
    if not ANTHROPIC_API_KEY:
        return generate_explanation_template(recommendation, language)
    
    lang_names = {"en": "English", "hi": "Hindi", "ta": "Tamil"}
    lang_name = lang_names.get(language, "English")
    
    # Build a structured prompt — NOT freeform
    prompt = f"""You are a pricing advisor for a small vegetable/fruit vendor in India.
Convert this structured recommendation into ONE clear, actionable sentence in {lang_name}.

Recommendation data:
- Item: {recommendation['item_name']}
- Current price: Rs.{recommendation['current_price']}/kg
- Suggested price: Rs.{recommendation['suggested_price']}/kg  
- Price change: {recommendation['price_change_pct']:+.1f}%
- Action: {recommendation['action']}
- Risk score: {recommendation.get('risk_score', 0)}/100
- Reasons: {json.dumps([r['label'] + ': ' + r['detail'] for r in recommendation['reasons']])}

Rules:
1. Output ONLY the recommendation sentence, nothing else
2. Use simple language a street vendor would understand
3. Include the specific price in Rupees
4. Keep it under 2 sentences
5. Output in {lang_name} language"""

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                ANTHROPIC_API_URL,
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 200,
                    "messages": [{"role": "user", "content": prompt}],
                },
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["content"][0]["text"].strip()
            else:
                # API error — fall back to template
                return generate_explanation_template(recommendation, language)
    
    except Exception:
        # Network error, timeout, etc. — fall back to template
        return generate_explanation_template(recommendation, language)


def generate_explanation(recommendation: dict, language: str = "en") -> str:
    """
    Synchronous wrapper — always uses template mode.
    Use generate_explanation_llm() for async LLM mode.
    """
    return generate_explanation_template(recommendation, language)
