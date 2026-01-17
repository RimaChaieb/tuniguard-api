"""
Google Gemini AI Integration Service
Handles threat detection and chatbot interactions
"""
import google.generativeai as genai
import json
import os
from flask import current_app

class GeminiService:
    """Service for interacting with Google Gemini API"""
    
    def __init__(self):
        """Initialize Gemini with API key"""
        api_key = current_app.config.get('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in configuration")
        
        genai.configure(api_key=api_key)
        self.model_name = current_app.config.get('GEMINI_MODEL', 'gemini-1.5-flash')  # Updated default model name
        self.model = genai.GenerativeModel(self.model_name)  # Instantiate the model here
        self.temperature = current_app.config.get('GEMINI_TEMPERATURE', 0.3)
    
    def analyze_threat(self, content, content_type='sms'):
        """
        Analyze content for threats using Gemini AI
        
        Args:
            content (str): The message/call/content to analyze
            content_type (str): Type of content (sms, call, app_message)
        
        Returns:
            dict: Threat analysis result
        """
        
        # Construct Tunisia-specific threat detection prompt
        prompt = f"""You are TuniGuard, an expert cybersecurity AI specializing in Tunisian telecommunications fraud detection.

Analyze this {content_type} for security threats:

CONTENT: "{content}"

TUNISIA-SPECIFIC SCAM PATTERNS TO CHECK:
1. Fake telecom operator messages (Tunisie Telecom, Ooredoo, Orange Tunisia)
2. Mobile money fraud (D17, Flouci, Sobflous payment scams)
3. Banking phishing (Zitouna Bank, Attijari, BIAT, BNA)
4. Premium rate call scams
5. SIM swap social engineering
6. Fake prize/recharge offers
7. Government subsidy exploitation
8. Currency exchange scams
9. Fake delivery/e-commerce (Jumia, Tayara)
10. COVID/health emergency scams

ANALYSIS CRITERIA:
- Language mixing (French-Arabic typical of Tunisian scams)
- Urgency tactics ("URGENT", "Immédiatement", "فوراً")
- Suspicious links (shortened URLs, misspelled domains)
- Request for personal data (CIN, passwords, OTP codes)
- Too-good-to-be-true offers
- Impersonation of trusted entities
- Payment pressure tactics

Respond ONLY with valid JSON (no markdown, no code blocks):
{{
  "threat_detected": true or false,
  "score": 0-100 (threat probability),
  "threat_type": "Phishing" or "Impersonation" or "Premium Fraud" or "Social Engineering" or "Safe",
  "severity": "Low" or "Medium" or "High" or "Critical",
  "explanation": "Brief technical explanation of why this is/isn't a threat",
  "red_flags": ["flag1", "flag2"],
  "safe_actions": ["action1", "action2", "action3"],
  "cultural_context": "Tunisia-specific context if relevant"
}}"""

        try:
            # Generate response using corrected API
            response = self.model.generate_content(prompt)  # Corrected call
            
            # Parse JSON response
            result_text = response.text.strip()
            
            # Clean up response (remove markdown if present)
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            result = json.loads(result_text.strip())
            return result
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                'threat_detected': False,
                'score': 0,
                'threat_type': 'Analysis Error',
                'severity': 'Low',
                'explanation': 'Unable to parse AI response. Content appears safe.',
                'red_flags': [],
                'safe_actions': ['Review content manually', 'Contact official channels if suspicious'],
                'cultural_context': ''
            }
        except Exception as e:
            current_app.logger.error(f"Gemini API error: {str(e)}")
            raise
    
    def chat_interaction(self, user_message, scan_context=None, conversation_history=None):
        """
        Handle multi-turn chatbot conversation
        
        Args:
            user_message (str): User's question/message
            scan_context (dict): Original scan result for context
            conversation_history (list): Previous messages
        
        Returns:
            str: AI response
        """
        
        # Build conversation context
        context = "You are TuniGuard Security Assistant, helping Tunisian users understand cybersecurity threats.\n\n"
        
        if scan_context:
            context += f"PREVIOUS THREAT SCAN:\n"
            context += f"- Content: {scan_context.get('input_text', 'N/A')}\n"
            context += f"- Threat Detected: {scan_context.get('threat_detected', False)}\n"
            context += f"- Score: {scan_context.get('detection_score', 0)}/100\n\n"
        
        if conversation_history:
            context += "CONVERSATION HISTORY:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg.get('role', 'user')
                content = msg.get('message', '')
                context += f"{role.upper()}: {content}\n"
            context += "\n"
        
        prompt = context + f"""USER QUESTION: {user_message}

Provide a helpful, concise response in French or English (match user's language). 
Focus on:
- Practical security advice
- Tunisia-specific guidance
- Clear action steps
- Empowering the user

Keep response under 200 words and friendly in tone."""

        try:
            response = self.model.generate_content(prompt)  # Corrected call
            
            if response and response.text:
                return response.text.strip()
            else:
                return "To protect yourself: Never click suspicious links, verify sender authenticity, don't share personal data via SMS, contact official channels directly. Stay vigilant!"
            
        except Exception as e:
            current_app.logger.error(f"Gemini chat error: {str(e)}")
            # Return helpful fallback instead of error message
            if scan_context and scan_context.get('threat_detected'):
                return "🛡️ This message is dangerous! Do NOT click any links. Delete immediately. Block the sender. If you shared information, contact your telecom provider and bank. Report to cybercrime authorities."
            else:
                return "✅ Stay safe! Always verify sender identity, avoid clicking unknown links, never share passwords or OTP codes. When in doubt, contact official channels directly."