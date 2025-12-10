#!/usr/bin/env python3
"""
Test script for empathy feature.

Run this to verify empathy endpoints are working correctly.

Usage:
    python TEST_EMPATHY.py
    
Or from backend directory:
    uv run python TEST_EMPATHY.py
"""

import asyncio
import httpx
import json
from EMPATHY_EXAMPLES import (
    FRUSTRATED_SCENARIO,
    ANXIOUS_SCENARIO,
    CONFUSED_SCENARIO,
    EXCITED_SCENARIO,
    NEGATIVE_SCENARIO,
    EMOTIONAL_JOURNEY,
)

# API Base URL
BASE_URL = "http://localhost:8000"
EMPATHY_ENDPOINT = f"{BASE_URL}/api/empathy"

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(text):
    """Print a section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"{text:^60}")
    print(f"{'='*60}{Colors.END}\n")


def print_subheader(text):
    """Print a subsection header"""
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'-'*len(text)}{Colors.END}")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


def print_json(data):
    """Pretty print JSON data"""
    print(f"{Colors.YELLOW}{json.dumps(data, indent=2)}{Colors.END}")


async def test_health_check():
    """Test if API is running"""
    print_header("1. Health Check")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/")
            if response.status_code == 200:
                print_success("API is running")
                print_json(response.json())
                return True
            else:
                print_error(f"API returned status {response.status_code}")
                return False
    except Exception as e:
        print_error(f"Cannot connect to API: {e}")
        print_info(f"Make sure backend is running: uv run uvicorn main:app --reload")
        return False


async def test_empathy_available_tones():
    """Test getting available emotional tones"""
    print_header("2. Available Emotional Tones")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{EMPATHY_ENDPOINT}/tones")
            if response.status_code == 200:
                print_success("Retrieved available tones")
                print_json(response.json())
                return True
            else:
                print_error(f"Failed with status {response.status_code}")
                return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


async def test_analyze_tone(message, scenario_name):
    """Test emotional tone analysis"""
    print_subheader(f"Testing: {scenario_name}")
    print_info(f"Message: \"{message}\"")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{EMPATHY_ENDPOINT}/analyze",
                json={"user_message": message},
                timeout=30.0
            )
            if response.status_code == 200:
                analysis = response.json()
                print_success("Tone analysis completed")
                print(f"  {Colors.YELLOW}Tone:{Colors.END} {analysis.get('tone', 'N/A')}")
                print(f"  {Colors.YELLOW}Empathy Score:{Colors.END} {analysis.get('empathy_score', 0):.2f}")
                print(f"  {Colors.YELLOW}Context:{Colors.END} {analysis.get('context', 'N/A')}")
                if 'keywords' in analysis:
                    print(f"  {Colors.YELLOW}Keywords:{Colors.END} {', '.join(analysis['keywords'])}")
                return True
            else:
                print_error(f"Failed with status {response.status_code}")
                print(f"  {response.text}")
                return False
    except httpx.TimeoutException:
        print_error("Request timed out (30 seconds)")
        print_info("This might indicate the empathy service is processing...")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


async def test_analyze_scenarios():
    """Test emotional analysis on different scenarios"""
    print_header("3. Emotional Tone Analysis")
    print_info("Testing various emotional scenarios...\n")
    
    scenarios = [
        (FRUSTRATED_SCENARIO["user_messages"][0], "Frustrated User"),
        (ANXIOUS_SCENARIO["user_messages"][0], "Anxious User"),
        (CONFUSED_SCENARIO["user_messages"][0], "Confused User"),
        (EXCITED_SCENARIO["user_messages"][0], "Excited User"),
        (NEGATIVE_SCENARIO["user_messages"][0], "Negative User"),
    ]
    
    results = []
    for message, name in scenarios:
        result = await test_analyze_tone(message, name)
        results.append(result)
        print()  # Add spacing between tests
    
    return all(results)


async def test_empathetic_response(message, scenario_name):
    """Test empathetic response generation"""
    print_subheader(f"Testing: {scenario_name}")
    print_info(f"Message: \"{message}\"")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{EMPATHY_ENDPOINT}/response",
                json={
                    "user_message": message,
                    "conversation_history": []
                },
                timeout=60.0
            )
            if response.status_code == 200:
                result = response.json()
                print_success("Empathetic response generated")
                print(f"  {Colors.YELLOW}Tone:{Colors.END} {result.get('emotional_tone', 'N/A')}")
                print(f"  {Colors.YELLOW}Empathy Score:{Colors.END} {result.get('empathy_score', 0):.2f}")
                print(f"  {Colors.YELLOW}Response:{Colors.END}\n{Colors.YELLOW}{result.get('response', 'N/A')}{Colors.END}")
                return True
            else:
                print_error(f"Failed with status {response.status_code}")
                print(f"  {response.text}")
                return False
    except httpx.TimeoutException:
        print_error("Request timed out (60 seconds)")
        print_info("Response generation may take longer for complex empathy analysis")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


async def test_empathetic_responses():
    """Test empathetic response generation"""
    print_header("4. Empathetic Response Generation")
    print_info("Testing response generation for various scenarios...\n")
    print_info("Note: This may take 30-60 seconds per request as responses are AI-generated\n")
    
    scenarios = [
        (FRUSTRATED_SCENARIO["user_messages"][0], "Frustrated User"),
        (ANXIOUS_SCENARIO["user_messages"][0], "Anxious User"),
    ]
    
    results = []
    for message, name in scenarios:
        result = await test_empathetic_response(message, name)
        results.append(result)
        print()  # Add spacing between tests
    
    return all(results)


async def test_conversation_summary():
    """Test conversation emotional summary"""
    print_header("5. Conversation Emotional Summary")
    
    # Build conversation history from emotional journey example
    conversation = EMOTIONAL_JOURNEY["conversation"]
    print_info(f"Analyzing conversation with {len(conversation)} messages...")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{EMPATHY_ENDPOINT}/summary",
                json={"conversation_history": conversation},
                timeout=60.0
            )
            if response.status_code == 200:
                summary = response.json()
                print_success("Conversation summary generated")
                print(f"  {Colors.YELLOW}Overall Sentiment:{Colors.END} {summary.get('sentiment', 'N/A')}")
                print(f"  {Colors.YELLOW}Emotional Journey:{Colors.END} {summary.get('emotional_journey', 'N/A')}")
                print(f"  {Colors.YELLOW}Key Concerns:{Colors.END} {', '.join(summary.get('key_concerns', []))}")
                print(f"  {Colors.YELLOW}Empathy Level Needed:{Colors.END} {summary.get('empathy_level_needed', 0):.2f}")
                print(f"  {Colors.YELLOW}Recommendation:{Colors.END} {summary.get('recommendation', 'N/A')}")
                return True
            else:
                print_error(f"Failed with status {response.status_code}")
                print(f"  {response.text}")
                return False
    except httpx.TimeoutException:
        print_error("Request timed out (60 seconds)")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


async def test_with_history():
    """Test response generation with conversation history"""
    print_header("6. Response with Conversation Context")
    print_info("Testing how empathy adapts to conversation history...\n")
    
    # Use the emotional journey conversation
    conversation = EMOTIONAL_JOURNEY["conversation"][:4]  # First 4 messages
    last_user_message = "Can you help me debug this?"
    
    print_subheader("Conversation Context")
    for msg in conversation:
        print(f"  {msg['role'].upper()}: {msg['content'][:80]}...")
    
    print()
    print_info(f"New message: \"{last_user_message}\"")
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{EMPATHY_ENDPOINT}/response",
                json={
                    "user_message": last_user_message,
                    "conversation_history": conversation
                },
                timeout=60.0
            )
            if response.status_code == 200:
                result = response.json()
                print_success("Response generated with context awareness")
                print(f"  {Colors.YELLOW}Tone:{Colors.END} {result.get('emotional_tone', 'N/A')}")
                print(f"  {Colors.YELLOW}Empathy Score:{Colors.END} {result.get('empathy_score', 0):.2f}")
                print(f"  {Colors.YELLOW}Response:{Colors.END}\n{Colors.YELLOW}{result.get('response', 'N/A')}{Colors.END}")
                return True
            else:
                print_error(f"Failed with status {response.status_code}")
                return False
    except httpx.TimeoutException:
        print_error("Request timed out (60 seconds)")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def print_summary(results):
    """Print test summary"""
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(results)
    
    if passed == total:
        print_success(f"All {total} test groups passed! ✓")
    else:
        print_error(f"{passed}/{total} test groups passed")
    
    # Show recommendations
    print()
    print_subheader("Next Steps")
    if passed == total:
        print_info("Empathy feature is working correctly!")
        print_info("")
        print("You can now:")
        print("  1. Send messages in the chat UI and observe empathetic responses")
        print("  2. Check the browser DevTools to see the emotional tone analysis")
        print("  3. Try different emotional scenarios (frustrated, anxious, excited, etc.)")
        print("  4. Integrate empathy analysis into the main chat flow")
    else:
        print_info("Some tests failed. Check the errors above.")
        print_info("")
        print("Troubleshooting:")
        print("  1. Ensure backend is running: uv run uvicorn main:app --reload")
        print("  2. Verify GEMINI_API_KEY is set in .env file")
        print("  3. Check network connectivity to API endpoints")
        print("  4. Review detailed error messages above")


async def main():
    """Run all tests"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}AI Desk - Empathy Feature Test Suite{Colors.END}\n")
    print(f"Testing empathy endpoints at: {BASE_URL}\n")
    
    results = []
    
    # Test 1: Health check
    results.append(await test_health_check())
    
    # If API is not running, stop here
    if not results[0]:
        print_summary([False])
        return
    
    # Test 2: Available tones
    results.append(await test_empathy_available_tones())
    
    # Test 3: Analyze emotional tones
    results.append(await test_analyze_scenarios())
    
    # Test 4: Generate empathetic responses
    print_info("WARNING: Response generation uses AI (Gemini) and may take 30-60 seconds per request")
    response = input(f"\n{Colors.BOLD}Continue with full empathy response tests? (y/n): {Colors.END}").lower()
    
    if response == 'y':
        results.append(await test_empathetic_responses())
        results.append(await test_conversation_summary())
        results.append(await test_with_history())
    else:
        print_info("Skipping full response tests\n")
        results.extend([None, None, None])  # Mark as skipped
    
    # Print summary
    results_filtered = [r for r in results if r is not None]
    print_summary(results_filtered)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}Test interrupted by user{Colors.END}")
    except Exception as e:
        print(f"\n\n{Colors.RED}Unexpected error: {e}{Colors.END}")
