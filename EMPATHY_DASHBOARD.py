#!/usr/bin/env python3
"""
Interactive Empathy Testing Dashboard

A real-time dashboard for testing empathy features with live visualization.

Usage:
    python EMPATHY_DASHBOARD.py
"""

import asyncio
import httpx
import json
from datetime import datetime
from typing import Optional, Dict, Any
import sys

# Colors
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
    DIM = '\033[2m'


class TestResult:
    """Store result of a single test"""
    def __init__(self, name: str):
        self.name = name
        self.status = "pending"
        self.time = 0.0
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None

    def format_status(self) -> str:
        """Format status for display"""
        if self.status == "pending":
            return f"{Colors.YELLOW}⏳ PENDING{Colors.END}"
        elif self.status == "running":
            return f"{Colors.CYAN}🔄 RUNNING{Colors.END}"
        elif self.status == "pass":
            return f"{Colors.GREEN}✓ PASS{Colors.END}"
        elif self.status == "fail":
            return f"{Colors.RED}✗ FAIL{Colors.END}"
        elif self.status == "skip":
            return f"{Colors.DIM}⊘ SKIP{Colors.END}"
        else:
            return f"{Colors.DIM}UNKNOWN{Colors.END}"


class Dashboard:
    """Test dashboard for empathy feature"""

    def __init__(self):
        self.results: Dict[str, TestResult] = {}
        self.start_time = None
        self.api_url = "http://localhost:8000"
        self.empathy_url = f"{self.api_url}/api/empathy"

    def register_test(self, name: str) -> TestResult:
        """Register a new test"""
        result = TestResult(name)
        self.results[name] = result
        return result

    def clear_screen(self):
        """Clear terminal screen"""
        sys.stdout.write('\033[2J\033[H')
        sys.stdout.flush()

    def print_header(self):
        """Print dashboard header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}╔═══════════════════════════════════════════════════════════════╗{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}║          AI Desk - Empathy Feature Testing Dashboard           ║{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}╚═══════════════════════════════════════════════════════════════╝{Colors.END}\n")

    def print_tests(self):
        """Print all test results"""
        print(f"{Colors.BOLD}Test Results:{Colors.END}")
        print("-" * 65)

        for name, result in self.results.items():
            status = result.format_status()
            time_str = f"{result.time:.2f}s" if result.time > 0 else ""
            print(f"  {name:<40} {status:<20} {time_str:>5}")

        print("-" * 65)

    def print_details(self):
        """Print detailed results"""
        print(f"\n{Colors.BOLD}Details:{Colors.END}")
        print("-" * 65)

        for name, result in self.results.items():
            if result.status == "pass" and result.result:
                print(f"\n{Colors.GREEN}{name}{Colors.END}")
                if isinstance(result.result, dict):
                    for key, value in result.result.items():
                        if isinstance(value, (dict, list)):
                            print(f"  {key}: {Colors.YELLOW}[complex]{Colors.END}")
                        else:
                            print(f"  {key}: {Colors.YELLOW}{value}{Colors.END}")
            elif result.status == "fail":
                print(f"\n{Colors.RED}{name}{Colors.END}")
                print(f"  Error: {result.error}")

        print("-" * 65)

    def print_summary(self):
        """Print test summary"""
        total = len(self.results)
        passed = sum(1 for r in self.results.values() if r.status == "pass")
        failed = sum(1 for r in self.results.values() if r.status == "fail")
        skipped = sum(1 for r in self.results.values() if r.status == "skip")

        elapsed = datetime.now().timestamp() - self.start_time if self.start_time else 0

        print(f"\n{Colors.BOLD}Summary:{Colors.END}")
        print(f"  Total Tests:  {total}")
        print(f"  {Colors.GREEN}Passed:{Colors.END}        {passed}")
        print(f"  {Colors.RED}Failed:{Colors.END}        {failed}")
        print(f"  {Colors.DIM}Skipped:{Colors.END}       {skipped}")
        print(f"  Time:         {elapsed:.1f}s")

        if failed == 0 and passed > 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All tests passed!{Colors.END}")
        elif failed > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ Some tests failed{Colors.END}")

    async def run_health_check(self) -> bool:
        """Test API health"""
        result = self.register_test("API Health Check")
        result.status = "running"
        self.clear_screen()
        self.print_header()

        start = datetime.now().timestamp()
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.api_url}/")
                result.time = datetime.now().timestamp() - start
                if response.status_code == 200:
                    result.status = "pass"
                    result.result = response.json()
                    return True
                else:
                    result.status = "fail"
                    result.error = f"Status {response.status_code}"
                    return False
        except Exception as e:
            result.time = datetime.now().timestamp() - start
            result.status = "fail"
            result.error = str(e)
            return False

    async def run_get_tones(self) -> bool:
        """Test getting available tones"""
        result = self.register_test("Get Available Tones")
        result.status = "running"

        start = datetime.now().timestamp()
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.empathy_url}/tones")
                result.time = datetime.now().timestamp() - start
                if response.status_code == 200:
                    result.status = "pass"
                    result.result = response.json()
                    return True
                else:
                    result.status = "fail"
                    result.error = f"Status {response.status_code}"
                    return False
        except Exception as e:
            result.time = datetime.now().timestamp() - start
            result.status = "fail"
            result.error = str(e)
            return False

    async def run_tone_analysis(self, message: str, tone_name: str) -> bool:
        """Test tone analysis"""
        result = self.register_test(f"Analyze Tone - {tone_name}")
        result.status = "running"

        start = datetime.now().timestamp()
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    f"{self.empathy_url}/analyze",
                    json={"user_message": message},
                    timeout=15.0
                )
                result.time = datetime.now().timestamp() - start
                if response.status_code == 200:
                    result.status = "pass"
                    result.result = response.json()
                    return True
                else:
                    result.status = "fail"
                    result.error = f"Status {response.status_code}"
                    return False
        except httpx.TimeoutException:
            result.status = "fail"
            result.error = "Request timeout"
            return False
        except Exception as e:
            result.time = datetime.now().timestamp() - start
            result.status = "fail"
            result.error = str(e)
            return False

    async def run_response_generation(self, message: str, scenario: str) -> bool:
        """Test response generation"""
        result = self.register_test(f"Generate Response - {scenario}")
        result.status = "running"

        start = datetime.now().timestamp()
        try:
            async with httpx.AsyncClient(timeout=70.0) as client:
                response = await client.post(
                    f"{self.empathy_url}/response",
                    json={"user_message": message, "conversation_history": []},
                    timeout=70.0
                )
                result.time = datetime.now().timestamp() - start
                if response.status_code == 200:
                    result.status = "pass"
                    result.result = response.json()
                    return True
                else:
                    result.status = "fail"
                    result.error = f"Status {response.status_code}"
                    return False
        except httpx.TimeoutException:
            result.time = datetime.now().timestamp() - start
            result.status = "fail"
            result.error = "Request timeout (>70s)"
            return False
        except Exception as e:
            result.time = datetime.now().timestamp() - start
            result.status = "fail"
            result.error = str(e)
            return False

    def display(self):
        """Display dashboard"""
        self.clear_screen()
        self.print_header()
        self.print_tests()
        self.print_details()
        self.print_summary()

    async def run_all_quick_tests(self):
        """Run all quick tests"""
        self.start_time = datetime.now().timestamp()

        # Health check
        if not await self.run_health_check():
            print(f"\n{Colors.RED}Backend not running. Start it with:{Colors.END}")
            print(f"  cd backend && uv run uvicorn main:app --reload")
            return

        self.display()

        # Get available tones
        await self.run_get_tones()
        self.display()

        # Tone analysis tests
        tests = [
            ("I've been trying for hours!", "Frustrated"),
            ("I'm worried I'll break it", "Anxious"),
            ("I don't understand", "Confused"),
            ("This is amazing!", "Excited"),
            ("This will never work", "Negative"),
        ]

        for message, tone in tests:
            await self.run_tone_analysis(message, tone)
            self.display()
            await asyncio.sleep(0.5)  # Small delay between requests


async def interactive_menu():
    """Interactive menu for testing"""
    dashboard = Dashboard()

    print(f"\n{Colors.BOLD}{Colors.CYAN}AI Desk - Empathy Testing Menu{Colors.END}\n")
    print("1. Run all quick tests (tone analysis)")
    print("2. Test tone analysis (custom message)")
    print("3. Generate empathetic response")
    print("4. Test conversation analysis")
    print("5. Exit")

    while True:
        choice = input(f"\n{Colors.BOLD}Select option (1-5): {Colors.END}").strip()

        if choice == "1":
            await dashboard.run_all_quick_tests()
            print(f"\n{Colors.GREEN}Tests completed!{Colors.END}")

        elif choice == "2":
            message = input(f"\n{Colors.BOLD}Enter message to analyze: {Colors.END}")
            dashboard.register_test("Custom Analysis")
            await dashboard.run_tone_analysis(message, "Custom")
            dashboard.display()

        elif choice == "3":
            print(f"\n{Colors.YELLOW}Note: This may take 30-60 seconds...{Colors.END}")
            message = input(f"{Colors.BOLD}Enter message: {Colors.END}")
            await dashboard.run_response_generation(message, "Custom")
            dashboard.display()

        elif choice == "4":
            print(f"\n{Colors.YELLOW}Not yet implemented{Colors.END}")

        elif choice == "5":
            print(f"\n{Colors.CYAN}Goodbye!{Colors.END}\n")
            break

        else:
            print(f"{Colors.RED}Invalid option{Colors.END}")


async def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--quick":
            # Run quick tests automatically
            dashboard = Dashboard()
            await dashboard.run_all_quick_tests()
        else:
            print(f"Usage: python EMPATHY_DASHBOARD.py [--quick]")
    else:
        # Interactive mode
        await interactive_menu()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}Interrupted{Colors.END}")
