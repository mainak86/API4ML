"""
Empathy Examples for AI Desk Chat Application

This file contains example scenarios and empathetic responses to help guide
the implementation and testing of empathy features in the chat system.
"""

# Example 1: Frustrated User
FRUSTRATED_SCENARIO = {
    "user_messages": [
        "I've been trying to get this to work for hours and nothing is working!",
        "The documentation is so confusing. Nothing makes sense.",
        "I just want to give up right now.",
    ],
    "empathetic_responses": [
        "I can really hear your frustration, and I completely understand why you'd feel that way after hours of troubleshooting. That's exhausting.",
        "Documentation can definitely be overwhelming sometimes. Let's break this down together step by step - we'll figure this out.",
        "I get it - hitting a wall like this is super discouraging. But you've already invested time, which shows you care about solving this. Let's turn this around.",
    ],
    "tone": "frustrated",
    "empathy_score": 0.85,
}

# Example 2: Anxious User
ANXIOUS_SCENARIO = {
    "user_messages": [
        "I'm worried I'm going to mess something up. What if I break it?",
        "Should I even be attempting this? I'm not sure I'm qualified.",
        "What if I get this wrong and it causes problems?",
    ],
    "empathetic_responses": [
        "Your concern about accuracy shows you care about doing things right. That's actually a strength. And don't worry - we can take this carefully.",
        "Imposter syndrome is real, and your concerns are valid. But let's remember: every expert started exactly where you are right now.",
        "It's totally normal to feel uncertain. Most experienced developers have worried about the same thing. We'll go through this together, and I'll help you verify each step.",
    ],
    "tone": "anxious",
    "empathy_score": 0.78,
}

# Example 3: Confused User
CONFUSED_SCENARIO = {
    "user_messages": [
        "I don't understand what this error message means.",
        "There are so many options here. Which one should I choose?",
        "Can you explain this in simpler terms? I'm lost.",
    ],
    "empathetic_responses": [
        "Error messages can definitely be cryptic! Let me help decode that for you. This particular message actually means...",
        "That's a lot of choices! Let's simplify this. For your use case, you'll want to focus on just these two key options.",
        "Absolutely - I'll break this down into simpler terms. Think of it like... [analogy]. Does that make more sense?",
    ],
    "tone": "confused",
    "empathy_score": 0.72,
}

# Example 4: Excited User
EXCITED_SCENARIO = {
    "user_messages": [
        "This is amazing! I just got it working!",
        "I love how intuitive this is. I never thought I could do this!",
        "I'm so motivated to keep learning more!",
    ],
    "empathetic_responses": [
        "That's wonderful! Your excitement is contagious! You should feel proud - you solved it!",
        "Right? That 'aha' moment feels incredible, doesn't it? You absolutely can do this, and you're proving it right now.",
        "That's the spirit! Your enthusiasm is exactly what you need to keep progressing. Keep riding this momentum!",
    ],
    "tone": "excited",
    "empathy_score": 0.65,
}

# Example 5: Negative/Discouraged User
NEGATIVE_SCENARIO = {
    "user_messages": [
        "This will never work. I'm wasting my time.",
        "I'm not smart enough for this.",
        "What's the point? I'll just fail anyway.",
    ],
    "empathetic_responses": [
        "I hear the discouragement. It's heavy, I know. But I've seen people who felt exactly this way turn it around. Let's focus on one small win first.",
        "That voice in your head is lying to you. Intelligence comes in many forms, and problem-solving is something you can absolutely develop. You're already trying, which matters.",
        "The fact that you're still here, still asking questions, tells me you haven't given up yet. That's worth something. Let's find one thing that works.",
    ],
    "tone": "negative",
    "empathy_score": 0.88,
}

# Example 6: Positive/Confident User
POSITIVE_SCENARIO = {
    "user_messages": [
        "This approach seems logical. What do you think?",
        "I got this part working. Moving on to the next.",
        "Let's tackle this efficiently.",
    ],
    "empathetic_responses": [
        "I like your logical thinking! Your approach is solid. Building on that, here's what we could consider next...",
        "Excellent progress! You're moving through this nicely. That confidence is well-placed.",
        "Your efficiency is impressive. Let's channel that momentum into the next challenge.",
    ],
    "tone": "positive",
    "empathy_score": 0.55,
}

# Example 7: Multi-Message Conversation (Tracking Emotional Journey)
EMOTIONAL_JOURNEY = {
    "conversation": [
        {
            "role": "user",
            "content": "I tried to implement this feature but I don't think it's working right.",
            "detected_tone": "uncertain",
            "empathy_score": 0.6,
        },
        {
            "role": "assistant",
            "content": "Let's debug this together. Can you tell me what's happening?",
        },
        {
            "role": "user",
            "content": "When I click the button, nothing happens. This is so frustrating!",
            "detected_tone": "frustrated",
            "empathy_score": 0.8,
        },
        {
            "role": "assistant",
            "content": "I can hear your frustration. Silent failures are the worst because there's no error to work from. Let's trace through this step by step.",
        },
        {
            "role": "user",
            "content": "Actually, I found the issue! I forgot to wire up the event listener. It works now!",
            "detected_tone": "excited",
            "empathy_score": 0.7,
        },
        {
            "role": "assistant",
            "content": "That's awesome! Great debugging - you found it yourself, which means you'll remember this next time. You should feel proud!",
        },
    ],
    "emotional_journey": "Uncertain → Frustrated → Excited",
    "summary": {
        "sentiment": "positive_resolution",
        "key_moments": [
            "Initial uncertainty",
            "Frustration peak",
            "Issue identification",
            "Success and pride",
        ],
        "empathy_level_needed": "Moderate - user showed resilience",
    },
}

# Example 8: Support Trigger Scenarios
SUPPORT_TRIGGERS = {
    "low_empathy_needed": {
        "scenario": "User is confident and making progress",
        "trigger_condition": "empathy_score < 0.4",
        "support_offer": None,  # Don't offer extra support
    },
    "moderate_empathy_needed": {
        "scenario": "User is facing challenges but handling well",
        "trigger_condition": "0.4 <= empathy_score < 0.65",
        "support_offer": "Would you like some suggestions, or would you prefer to explore this yourself?",
    },
    "high_empathy_needed": {
        "scenario": "User is frustrated or anxious",
        "trigger_condition": "0.65 <= empathy_score < 0.8",
        "support_offer": "I'm here to help. Would it help to break this down into smaller steps?",
    },
    "critical_empathy_needed": {
        "scenario": "User is highly discouraged or overwhelmed",
        "trigger_condition": "empathy_score >= 0.8",
        "support_offer": "It sounds like this is really challenging right now. Let's take a step back - what's one small thing we can tackle first?",
    },
}

# Example 9: Empathy Indicators for UI
EMPATHY_INDICATORS = {
    "positive": {
        "emoji": "😊",
        "color": "#4CAF50",
        "message": "Great enthusiasm!",
        "tone": "positive",
    },
    "neutral": {
        "emoji": "😐",
        "color": "#2196F3",
        "message": "Working through it",
        "tone": "neutral",
    },
    "confused": {
        "emoji": "🤔",
        "color": "#FF9800",
        "message": "Let me clarify that",
        "tone": "confused",
    },
    "frustrated": {
        "emoji": "😤",
        "color": "#F44336",
        "message": "I understand your frustration",
        "tone": "frustrated",
    },
    "anxious": {
        "emoji": "😟",
        "color": "#FF5722",
        "message": "You've got this!",
        "tone": "anxious",
    },
    "excited": {
        "emoji": "🎉",
        "color": "#9C27B0",
        "message": "Your enthusiasm is great!",
        "tone": "excited",
    },
}

# Example 10: Phrases Bank by Emotional Tone
EMPATHETIC_PHRASES = {
    "opening": {
        "frustrated": [
            "I can really hear your frustration here.",
            "That sounds incredibly frustrating.",
            "I totally get why you're feeling this way.",
        ],
        "anxious": [
            "Your concerns are completely valid.",
            "I can sense your uncertainty, and that's okay.",
            "Let's work through this carefully together.",
        ],
        "confused": [
            "That's a great question, and you're not alone in wondering.",
            "Let me help clarify that.",
            "No worries - this can be confusing at first.",
        ],
        "excited": [
            "Your enthusiasm is fantastic!",
            "I love your energy!",
            "That's an awesome observation!",
        ],
        "negative": [
            "I hear you, and I want to help change this.",
            "Those feelings are understandable.",
            "Let's find a way forward together.",
        ],
    },
    "middle": {
        "frustrated": [
            "Let's break this down into smaller, manageable pieces.",
            "I'm here to help untangle this with you.",
            "We'll get through this - one step at a time.",
        ],
        "anxious": [
            "Every expert started exactly where you are now.",
            "Take your time - there's no rush.",
            "You're doing better than you think you are.",
        ],
        "confused": [
            "Think of it like this...",
            "Here's a simpler way to look at it...",
            "Let me walk you through this step by step.",
        ],
        "excited": [
            "This is just the beginning - there's so much more you can do!",
            "Keep that momentum going!",
            "Your progress is impressive!",
        ],
        "negative": [
            "Here's what I know: you're still here, trying.",
            "Small wins count - let's find one.",
            "You have more capability than you're giving yourself credit for.",
        ],
    },
    "closing": {
        "frustrated": [
            "You've made real progress here. That matters.",
            "Don't hesitate to reach out if you hit another wall.",
            "You're handling this better than you think.",
        ],
        "anxious": [
            "You're going to do great - I'm confident in you.",
            "Remember: it's okay to take breaks when you need them.",
            "You've got this, and I'm here if you need me.",
        ],
        "confused": [
            "Now that makes more sense, right?",
            "Feel free to ask if anything else needs clarification.",
            "You're on the right track now!",
        ],
        "excited": [
            "I can't wait to see what you build next!",
            "Keep up this amazing work!",
            "Your journey is inspiring!",
        ],
        "negative": [
            "You took a step today - that's progress.",
            "Come back anytime you need support.",
            "I believe in your ability to get through this.",
        ],
    },
}

if __name__ == "__main__":
    print("Empathy Examples loaded successfully!")
    print(f"\nAvailable examples:")
    print(f"- FRUSTRATED_SCENARIO")
    print(f"- ANXIOUS_SCENARIO")
    print(f"- CONFUSED_SCENARIO")
    print(f"- EXCITED_SCENARIO")
    print(f"- NEGATIVE_SCENARIO")
    print(f"- POSITIVE_SCENARIO")
    print(f"- EMOTIONAL_JOURNEY")
    print(f"- SUPPORT_TRIGGERS")
    print(f"- EMPATHY_INDICATORS")
    print(f"- EMPATHETIC_PHRASES")
