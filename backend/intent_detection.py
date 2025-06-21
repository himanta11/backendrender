import re
from typing import Dict, List, Tuple, Optional
from enum import Enum

class IntentType(Enum):
    GREETING = "greeting"
    FAREWELL = "farewell"
    THANKS = "thanks"
    HELP = "help"
    EDUCATIONAL = "educational"
    GENERAL_QUESTION = "general_question"
    CLARIFICATION = "clarification"
    UNKNOWN = "unknown"

class IntentDetector:
    def __init__(self):
        # Greeting patterns
        self.greeting_patterns = [
            r'\b(hi|hello|hey|good morning|good afternoon|good evening|sup|what\'s up|howdy)\b',
            r'\b(how are you|how\'s it going|how\'s everything)\b',
            r'\b(nice to meet you|pleasure to meet you)\b'
        ]
        
        # Farewell patterns
        self.farewell_patterns = [
            r'\b(bye|goodbye|see you|take care|farewell|good night)\b',
            r'\b(see you later|talk to you later|until next time)\b'
        ]
        
        # Thanks patterns
        self.thanks_patterns = [
            r'\b(thank you|thanks|thx|thank you so much|thanks a lot)\b',
            r'\b(appreciate it|grateful|thankful)\b'
        ]
        
        # Help patterns
        self.help_patterns = [
            r'\b(help|can you help|i need help|assist|support)\b',
            r'\b(what can you do|how do you work|your capabilities)\b',
            r'\b(guide|tutorial|instructions)\b'
        ]
        
        # Educational patterns (subjects and topics)
        self.educational_patterns = [
            r'\b(math|mathematics|algebra|geometry|calculus|trigonometry)\b',
            r'\b(physics|chemistry|biology|science)\b',
            r'\b(history|geography|literature|english|grammar)\b',
            r'\b(programming|coding|computer science|python|java|javascript)\b',
            r'\b(explain|define|what is|how does|why does|when does)\b',
            r'\b(solve|calculate|find|determine|analyze)\b',
            r'\b(equation|formula|theorem|concept|theory)\b',
            r'\b(problem|question|exercise|assignment)\b'
        ]
        
        # Clarification patterns
        self.clarification_patterns = [
            r'\b(can you repeat|i don\'t understand|unclear|confused)\b',
            r'\b(what do you mean|elaborate|more details|clarify)\b',
            r'\b(sorry|pardon|excuse me|what)\b'
        ]
        
        # Response templates
        self.response_templates = {
            IntentType.GREETING: [
                "Hello! 👋 How can I help you with your studies today?",
                "Hi there! 😊 Ready to tackle some learning together?",
                "Hey! What subject would you like to explore today?",
                "Hello! I'm here to help with your educational questions. What would you like to learn about?",
                "Hi! I'm your AI study assistant. What topic can I help you with?"
            ],
            IntentType.FAREWELL: [
                "Goodbye! Feel free to come back anytime for more learning help! 👋",
                "See you later! Keep up the great work with your studies! 📚",
                "Take care! Don't hesitate to return if you have more questions!",
                "Goodbye! Happy studying! 🎓"
            ],
            IntentType.THANKS: [
                "You're welcome! 😊 Happy to help with your studies!",
                "Anytime! Keep asking great questions! 📚",
                "My pleasure! Learning together is what I'm here for!",
                "You're very welcome! Feel free to ask more questions anytime!"
            ],
            IntentType.HELP: [
                "I'm your AI study assistant! I can help you with:\n\n• **Math problems** - algebra, geometry, calculus\n• **Science concepts** - physics, chemistry, biology\n• **Language arts** - grammar, literature, writing\n• **Programming** - Python, Java, web development\n• **History & Geography** - facts, dates, locations\n\nJust ask me any educational question! 📚",
                "I'm here to help with your studies! I can explain concepts, solve problems, provide examples, and answer questions about various subjects. What would you like to learn about?",
                "I'm an AI tutor that specializes in educational content. I can help with math, science, languages, programming, and more. Just ask me anything!",
                "I'm your learning companion! I can:\n- Explain complex topics simply\n- Solve step-by-step problems\n- Provide examples and analogies\n- Answer questions about any subject\n\nWhat would you like to explore?"
            ],
            IntentType.CLARIFICATION: [
                "I'd be happy to clarify! Could you rephrase your question or let me know what specific part you'd like me to explain better?",
                "Let me try to explain that differently. What exactly would you like me to clarify?",
                "I want to make sure I understand correctly. Could you ask your question in a different way?",
                "I'm here to help! Please let me know what part you'd like me to explain more clearly."
            ]
        }
    
    def detect_intent(self, message: str) -> Tuple[IntentType, float]:
        """
        Detect the intent of a user message and return the intent type with confidence score.
        
        Args:
            message: The user's message
            
        Returns:
            Tuple of (IntentType, confidence_score)
        """
        message_lower = message.lower().strip()
        
        # Check for greetings
        for pattern in self.greeting_patterns:
            if re.search(pattern, message_lower):
                return IntentType.GREETING, 0.9
        
        # Check for farewells
        for pattern in self.farewell_patterns:
            if re.search(pattern, message_lower):
                return IntentType.FAREWELL, 0.9
        
        # Check for thanks
        for pattern in self.thanks_patterns:
            if re.search(pattern, message_lower):
                return IntentType.THANKS, 0.9
        
        # Check for help requests
        for pattern in self.help_patterns:
            if re.search(pattern, message_lower):
                return IntentType.HELP, 0.8
        
        # Check for clarification requests
        for pattern in self.clarification_patterns:
            if re.search(pattern, message_lower):
                return IntentType.CLARIFICATION, 0.8
        
        # Check for educational content
        educational_matches = 0
        for pattern in self.educational_patterns:
            if re.search(pattern, message_lower):
                educational_matches += 1
        
        if educational_matches >= 1:
            confidence = min(0.7 + (educational_matches * 0.1), 0.95)
            return IntentType.EDUCATIONAL, confidence
        
        # Check for general questions (question marks, what/how/why/when/where)
        if '?' in message or re.search(r'\b(what|how|why|when|where|who|which)\b', message_lower):
            return IntentType.GENERAL_QUESTION, 0.6
        
        return IntentType.UNKNOWN, 0.3
    
    def get_response(self, intent: IntentType, message: str = "") -> str:
        """
        Get an appropriate response based on the detected intent.
        
        Args:
            intent: The detected intent type
            message: The original user message (for context)
            
        Returns:
            Appropriate response string
        """
        if intent in self.response_templates:
            import random
            responses = self.response_templates[intent]
            return random.choice(responses)
        
        # For educational and general questions, return None to use AI
        if intent in [IntentType.EDUCATIONAL, IntentType.GENERAL_QUESTION]:
            return None
        
        # Default response for unknown intent
        return "I'm here to help with your studies! What would you like to learn about?"
    
    def should_use_ai(self, intent: IntentType) -> bool:
        """
        Determine if the message should be sent to the AI model.
        
        Args:
            intent: The detected intent type
            
        Returns:
            True if AI should be used, False if predefined response is sufficient
        """
        # Use AI for educational content and general questions
        return intent in [IntentType.EDUCATIONAL, IntentType.GENERAL_QUESTION, IntentType.UNKNOWN]
    
    def get_ai_prompt_context(self, intent: IntentType, message: str) -> str:
        """
        Get context-aware prompt for AI based on intent.
        
        Args:
            intent: The detected intent type
            message: The user's message
            
        Returns:
            Context string to add to AI prompt
        """
        if intent == IntentType.EDUCATIONAL:
            return "This appears to be an educational question. Provide a clear, well-structured explanation using appropriate markdown formatting. Keep the response focused and educational."
        elif intent == IntentType.GENERAL_QUESTION:
            return "This is a general question. Provide a helpful response that's educational and informative, but keep it concise and relevant to learning."
        elif intent == IntentType.UNKNOWN:
            return "This message is unclear. Provide a helpful response that encourages educational discussion or ask for clarification."
        
        return "Provide a helpful educational response."

# Global instance
intent_detector = IntentDetector() 