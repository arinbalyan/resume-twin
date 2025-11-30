#!/usr/bin/env python
"""
Test Runner Script for Resume Twin Platform.

This script runs all unit tests in sequence and generates a comprehensive report.

Usage:
    python run_tests.py                 # Run all tests
    python run_tests.py --verbose       # Run with verbose output
    python run_tests.py --coverage      # Run with coverage report
    python run_tests.py --service ai    # Run tests for specific service
    python run_tests.py --parallel      # Run tests in parallel (faster)
    python run_tests.py --html          # Generate HTML report
"""

import subprocess
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

# Test files in execution order
TEST_FILES = [
    "test_ai_service.py",
    "test_file_service.py",
    "test_github_service.py",
    "test_profile_service.py",
    "test_project_service.py",
    "test_resume_service.py",
    "test_resume_scorer_service.py",
    "test_s3_service.py",
    "test_template_service.py",
]

# Service name to test file mapping
SERVICE_MAP = {
    "ai": "test_ai_service.py",
    "file": "test_file_service.py",
    "github": "test_github_service.py",
    "profile": "test_profile_service.py",
    "project": "test_project_service.py",
    "resume": "test_resume_service.py",
    "scorer": "test_resume_scorer_service.py",
    "s3": "test_s3_service.py",
    "template": "test_template_service.py",
}


def get_project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_tests_dir():
    """Get the tests directory."""
    return Path(__file__).parent


def get_backend_dir():
    """Get the backend directory."""
    return Path(__file__).parent.parent / "backend"


def run_command(cmd: list, cwd: str = None) -> tuple:
    """Run a command and return exit code and output."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or str(get_backend_dir()),
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70 + "\n")


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print(f"{'─' * 50}\n")


def run_all_tests(args):
    """Run all tests with the specified options."""
    print_header("Resume Twin Platform - Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version}")
    
    # Build pytest command - use uv run from backend directory
    cmd = ["uv", "run", "pytest"]
    
    # Tests directory path relative to backend
    tests_dir = "../tests"
    
    # Determine which tests to run
    if args.service:
        if args.service in SERVICE_MAP:
            cmd.append(f"{tests_dir}/{SERVICE_MAP[args.service]}")
        else:
            print(f"Unknown service: {args.service}")
            print(f"Available services: {', '.join(SERVICE_MAP.keys())}")
            return 1
    else:
        # Run all test files
        for test_file in TEST_FILES:
            cmd.append(f"{tests_dir}/{test_file}")
    
    # Add options
    if args.verbose:
        cmd.append("-v")
    else:
        cmd.append("-v")  # Always use verbose for better output
    
    if args.coverage:
        cmd.extend([
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html:../htmlcov"
        ])
    
    if args.parallel:
        cmd.extend(["-n", "auto"])  # Requires pytest-xdist
    
    if args.html:
        cmd.extend([
            "--html=test_report.html",
            "--self-contained-html"
        ])
    
    # Add common options
    cmd.extend([
        "--tb=short",
        "--strict-markers",
        "-W", "ignore::DeprecationWarning"
    ])
    
    print(f"\nRunning: {' '.join(cmd)}\n")
    
    # Run pytest
    exit_code, stdout, stderr = run_command(cmd)
    
    # Print output
    if stdout:
        print(stdout)
    if stderr and exit_code != 0:
        print(stderr, file=sys.stderr)
    
    # Print summary
    print_header("Test Summary")
    if exit_code == 0:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. See output above for details.")
    
    print(f"\nFinished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return exit_code


def run_tests_sequentially(args):
    """Run tests file by file for detailed reporting."""
    print_header("Resume Twin Platform - Sequential Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    total_passed = 0
    total_failed = 0
    total_errors = 0
    
    test_files = [SERVICE_MAP[args.service]] if args.service else TEST_FILES
    tests_dir = "../tests"
    
    for test_file in test_files:
        print_section(f"Running {test_file}")
        
        cmd = ["uv", "run", "pytest", f"{tests_dir}/{test_file}", "-v", "--tb=short"]
        
        if args.coverage:
            cmd.extend(["--cov=app", "--cov-append"])
        
        exit_code, stdout, stderr = run_command(cmd)
        
        # Parse results from output
        passed = stdout.count(" passed")
        failed = stdout.count(" failed")
        errors = stdout.count(" error")
        
        results[test_file] = {
            "exit_code": exit_code,
            "passed": passed,
            "failed": failed,
            "errors": errors
        }
        
        total_passed += passed
        total_failed += failed
        total_errors += errors
        
        if exit_code == 0:
            print(f"✅ {test_file}: PASSED")
        else:
            print(f"❌ {test_file}: FAILED")
            if args.verbose:
                print(stdout)
    
    # Print summary
    print_header("Final Summary")
    print(f"{'Test File':<40} {'Status':<10} {'Passed':<8} {'Failed':<8}")
    print("-" * 70)
    
    for test_file, result in results.items():
        status = "✅ PASS" if result["exit_code"] == 0 else "❌ FAIL"
        print(f"{test_file:<40} {status:<10} {result['passed']:<8} {result['failed']:<8}")
    
    print("-" * 70)
    print(f"{'TOTAL':<40} {'':<10} {total_passed:<8} {total_failed:<8}")
    
    if total_failed == 0 and total_errors == 0:
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ {total_failed} tests failed, {total_errors} errors")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run Resume Twin Platform tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py --coverage         # Run with coverage
  python run_tests.py --service ai       # Test AI service only
  python run_tests.py --service github   # Test GitHub service only
  python run_tests.py --sequential       # Run tests one by one
  python run_tests.py --html             # Generate HTML report

Available services:
  ai, file, github, profile, project, resume, scorer, s3, template
        """
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Run with coverage report"
    )
    
    parser.add_argument(
        "-s", "--service",
        type=str,
        help="Run tests for specific service (ai, file, github, etc.)"
    )
    
    parser.add_argument(
        "-p", "--parallel",
        action="store_true",
        help="Run tests in parallel (requires pytest-xdist)"
    )
    
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML report (requires pytest-html)"
    )
    
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Run tests file by file with individual reporting"
    )
    
    args = parser.parse_args()
    
    # Change to backend directory to use its uv environment
    os.chdir(get_backend_dir())
    
    if args.sequential:
        exit_code = run_tests_sequentially(args)
    else:
        exit_code = run_all_tests(args)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
