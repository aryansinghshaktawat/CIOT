#!/usr/bin/env python3
"""
Comprehensive Test Runner for Enhanced Phone Investigation
Runs all test suites with proper configuration and reporting
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
import json


class TestRunner:
    """Comprehensive test runner for the enhanced phone investigation system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_dir = self.project_root / 'tests'
        self.src_dir = self.project_root / 'src'
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def setup_environment(self):
        """Setup test environment"""
        print("Setting up test environment...")
        
        # Add src to Python path
        src_path = str(self.src_dir)
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        # Set environment variables for testing
        os.environ['TESTING'] = '1'
        os.environ['PYTHONPATH'] = src_path
        
        # Create necessary directories
        (self.project_root / 'test-results').mkdir(exist_ok=True)
        (self.project_root / 'coverage-reports').mkdir(exist_ok=True)
    
    def run_unit_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run unit tests"""
        print("\n" + "="*60)
        print("RUNNING UNIT TESTS")
        print("="*60)
        
        cmd = [
            sys.executable, '-m', 'pytest',
            str(self.test_dir / 'test_comprehensive_unit_tests.py'),
            '-m', 'unit',
            '--cov=src',
            '--cov-report=term-missing',
            '--cov-report=html:coverage-reports/unit-coverage',
            '--cov-report=xml:coverage-reports/unit-coverage.xml',
            '--junit-xml=test-results/unit-tests.xml',
            '--tb=short'
        ]
        
        if verbose:
            cmd.append('-v')
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        end_time = time.time()
        
        return {
            'name': 'Unit Tests',
            'returncode': result.returncode,
            'duration': end_time - start_time,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
    
    def run_integration_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run integration tests"""
        print("\n" + "="*60)
        print("RUNNING INTEGRATION TESTS")
        print("="*60)
        
        cmd = [
            sys.executable, '-m', 'pytest',
            str(self.test_dir / 'test_comprehensive_integration_tests.py'),
            '-m', 'integration',
            '--cov=src',
            '--cov-report=html:coverage-reports/integration-coverage',
            '--cov-report=xml:coverage-reports/integration-coverage.xml',
            '--junit-xml=test-results/integration-tests.xml',
            '--tb=short'
        ]
        
        if verbose:
            cmd.append('-v')
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        end_time = time.time()
        
        return {
            'name': 'Integration Tests',
            'returncode': result.returncode,
            'duration': end_time - start_time,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
    
    def run_ui_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run UI tests"""
        print("\n" + "="*60)
        print("RUNNING UI TESTS")
        print("="*60)
        
        cmd = [
            sys.executable, '-m', 'pytest',
            str(self.test_dir / 'test_comprehensive_ui_tests.py'),
            '-m', 'ui',
            '--junit-xml=test-results/ui-tests.xml',
            '--tb=short'
        ]
        
        if verbose:
            cmd.append('-v')
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        end_time = time.time()
        
        return {
            'name': 'UI Tests',
            'returncode': result.returncode,
            'duration': end_time - start_time,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
    
    def run_performance_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run performance tests"""
        print("\n" + "="*60)
        print("RUNNING PERFORMANCE TESTS")
        print("="*60)
        
        cmd = [
            sys.executable, '-m', 'pytest',
            str(self.test_dir / 'test_comprehensive_performance_tests.py'),
            '-m', 'performance',
            '--junit-xml=test-results/performance-tests.xml',
            '--tb=short'
        ]
        
        if verbose:
            cmd.append('-v')
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        end_time = time.time()
        
        return {
            'name': 'Performance Tests',
            'returncode': result.returncode,
            'duration': end_time - start_time,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
    
    def run_e2e_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run end-to-end tests"""
        print("\n" + "="*60)
        print("RUNNING END-TO-END TESTS")
        print("="*60)
        
        cmd = [
            sys.executable, '-m', 'pytest',
            str(self.test_dir / 'test_comprehensive_e2e_tests.py'),
            '-m', 'e2e',
            '--junit-xml=test-results/e2e-tests.xml',
            '--tb=short'
        ]
        
        if verbose:
            cmd.append('-v')
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.project_root)
        end_time = time.time()
        
        return {
            'name': 'End-to-End Tests',
            'returncode': result.returncode,
            'duration': end_time - start_time,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
    
    def run_all_tests(self, test_types: List[str], verbose: bool = False) -> Dict[str, Any]:
        """Run all specified test types"""
        print("Starting comprehensive test suite...")
        print(f"Test types: {', '.join(test_types)}")
        
        self.start_time = time.time()
        
        test_runners = {
            'unit': self.run_unit_tests,
            'integration': self.run_integration_tests,
            'ui': self.run_ui_tests,
            'performance': self.run_performance_tests,
            'e2e': self.run_e2e_tests
        }
        
        results = {}
        
        for test_type in test_types:
            if test_type in test_runners:
                try:
                    result = test_runners[test_type](verbose)
                    results[test_type] = result
                    
                    # Print immediate result
                    status = "PASSED" if result['success'] else "FAILED"
                    print(f"\n{result['name']}: {status} ({result['duration']:.2f}s)")
                    
                    if not result['success'] and verbose:
                        print("STDOUT:", result['stdout'])
                        print("STDERR:", result['stderr'])
                        
                except Exception as e:
                    results[test_type] = {
                        'name': test_type.title() + ' Tests',
                        'returncode': 1,
                        'duration': 0,
                        'stdout': '',
                        'stderr': str(e),
                        'success': False,
                        'error': str(e)
                    }
                    print(f"\n{test_type.title()} Tests: ERROR - {e}")
            else:
                print(f"Unknown test type: {test_type}")
        
        self.end_time = time.time()
        self.results = results
        
        return results
    
    def generate_summary_report(self) -> str:
        """Generate summary report"""
        if not self.results:
            return "No test results available"
        
        total_duration = self.end_time - self.start_time if self.start_time and self.end_time else 0
        
        report = []
        report.append("="*80)
        report.append("COMPREHENSIVE TEST SUITE SUMMARY")
        report.append("="*80)
        report.append(f"Total Duration: {total_duration:.2f} seconds")
        report.append("")
        
        # Test results table
        report.append(f"{'Test Suite':<20} {'Status':<10} {'Duration':<12} {'Result'}")
        report.append("-" * 60)
        
        total_tests = len(self.results)
        passed_tests = 0
        
        for test_type, result in self.results.items():
            status = "PASSED" if result['success'] else "FAILED"
            duration = f"{result['duration']:.2f}s"
            
            if result['success']:
                passed_tests += 1
            
            report.append(f"{result['name']:<20} {status:<10} {duration:<12}")
        
        report.append("-" * 60)
        report.append(f"Overall: {passed_tests}/{total_tests} test suites passed")
        
        # Overall status
        overall_success = passed_tests == total_tests
        overall_status = "SUCCESS" if overall_success else "FAILURE"
        report.append(f"Overall Status: {overall_status}")
        
        # Failed tests details
        failed_tests = [name for name, result in self.results.items() if not result['success']]
        if failed_tests:
            report.append("")
            report.append("FAILED TEST SUITES:")
            for test_name in failed_tests:
                result = self.results[test_name]
                report.append(f"  - {result['name']}")
                if 'error' in result:
                    report.append(f"    Error: {result['error']}")
        
        report.append("="*80)
        
        return "\n".join(report)
    
    def save_results(self, output_file: Optional[str] = None):
        """Save test results to file"""
        if not output_file:
            output_file = self.project_root / 'test-results' / 'comprehensive-test-results.json'
        
        results_data = {
            'timestamp': time.time(),
            'total_duration': self.end_time - self.start_time if self.start_time and self.end_time else 0,
            'results': self.results,
            'summary': {
                'total_suites': len(self.results),
                'passed_suites': sum(1 for r in self.results.values() if r['success']),
                'failed_suites': sum(1 for r in self.results.values() if not r['success']),
                'overall_success': all(r['success'] for r in self.results.values())
            }
        }
        
        with open(output_file, 'w') as f:
            json.dump(results_data, f, indent=2, default=str)
        
        print(f"\nTest results saved to: {output_file}")
    
    def run_quick_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run quick test suite (unit + integration only)"""
        return self.run_all_tests(['unit', 'integration'], verbose)
    
    def run_full_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run full test suite (all test types)"""
        return self.run_all_tests(['unit', 'integration', 'ui', 'performance', 'e2e'], verbose)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Comprehensive Test Runner for Enhanced Phone Investigation')
    
    parser.add_argument('--test-types', nargs='+', 
                       choices=['unit', 'integration', 'ui', 'performance', 'e2e', 'all', 'quick'],
                       default=['quick'],
                       help='Test types to run')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    parser.add_argument('--output', '-o', type=str,
                       help='Output file for results')
    
    parser.add_argument('--setup-only', action='store_true',
                       help='Only setup environment, don\'t run tests')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    runner.setup_environment()
    
    if args.setup_only:
        print("Environment setup complete.")
        return 0
    
    # Determine test types to run
    test_types = args.test_types
    if 'all' in test_types:
        test_types = ['unit', 'integration', 'ui', 'performance', 'e2e']
    elif 'quick' in test_types:
        test_types = ['unit', 'integration']
    
    # Run tests
    try:
        if 'quick' in args.test_types and len(args.test_types) == 1:
            results = runner.run_quick_tests(args.verbose)
        elif 'all' in args.test_types:
            results = runner.run_full_tests(args.verbose)
        else:
            results = runner.run_all_tests(test_types, args.verbose)
        
        # Generate and print summary
        summary = runner.generate_summary_report()
        print("\n" + summary)
        
        # Save results
        runner.save_results(args.output)
        
        # Return appropriate exit code
        overall_success = all(r['success'] for r in results.values())
        return 0 if overall_success else 1
        
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        return 130
    except Exception as e:
        print(f"\nError running tests: {e}")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)