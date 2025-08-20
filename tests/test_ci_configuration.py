"""
Continuous Integration Configuration Tests
Tests for CI/CD pipeline configuration and automated testing setup
"""

import pytest
import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List


@pytest.mark.ci
class TestCIConfiguration:
    """Tests for CI configuration files"""
    
    def test_github_actions_workflow_exists(self):
        """Test GitHub Actions workflow file exists"""
        workflow_path = Path('.github/workflows/ci.yml')
        assert workflow_path.exists(), "GitHub Actions CI workflow should exist"
    
    def test_github_actions_workflow_valid(self):
        """Test GitHub Actions workflow is valid YAML"""
        workflow_path = Path('.github/workflows/ci.yml')
        
        if workflow_path.exists():
            with open(workflow_path, 'r') as f:
                try:
                    workflow = yaml.safe_load(f)
                    assert isinstance(workflow, dict), "Workflow should be valid YAML dict"
                    assert 'name' in workflow, "Workflow should have a name"
                    assert ('on' in workflow or True in workflow), "Workflow should have triggers"
                    assert 'jobs' in workflow, "Workflow should have jobs"
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in workflow file: {e}")
    
    def test_github_actions_has_test_job(self):
        """Test GitHub Actions workflow has test job"""
        workflow_path = Path('.github/workflows/ci.yml')
        
        if workflow_path.exists():
            with open(workflow_path, 'r') as f:
                workflow = yaml.safe_load(f)
                
                jobs = workflow.get('jobs', {})
                
                # Should have at least one job that runs tests
                test_job_found = False
                for job_name, job_config in jobs.items():
                    steps = job_config.get('steps', [])
                    for step in steps:
                        if 'pytest' in str(step).lower() or 'test' in str(step).lower():
                            test_job_found = True
                            break
                    if test_job_found:
                        break
                
                assert test_job_found, "Workflow should have a job that runs tests"
    
    def test_requirements_dev_exists(self):
        """Test development requirements file exists"""
        req_path = Path('requirements-dev.txt')
        assert req_path.exists(), "Development requirements file should exist"
    
    def test_requirements_dev_has_testing_deps(self):
        """Test development requirements includes testing dependencies"""
        req_path = Path('requirements-dev.txt')
        
        if req_path.exists():
            with open(req_path, 'r') as f:
                content = f.read().lower()
                
                required_deps = ['pytest', 'pytest-cov', 'pytest-mock']
                
                for dep in required_deps:
                    assert dep in content, f"Development requirements should include {dep}"
    
    def test_pytest_config_exists(self):
        """Test pytest configuration exists"""
        config_files = ['pytest.ini', 'pyproject.toml', 'setup.cfg']
        
        config_found = any(Path(config_file).exists() for config_file in config_files)
        assert config_found, "Pytest configuration should exist in one of: pytest.ini, pyproject.toml, setup.cfg"
    
    def test_coverage_config_exists(self):
        """Test coverage configuration exists"""
        coverage_files = ['.coveragerc', 'pyproject.toml', 'setup.cfg']
        
        # Check if coverage config exists in any of these files
        coverage_config_found = False
        
        for config_file in coverage_files:
            if Path(config_file).exists():
                with open(config_file, 'r') as f:
                    content = f.read()
                    if 'coverage' in content.lower() or '[tool.coverage' in content:
                        coverage_config_found = True
                        break
        
        # Coverage config is optional but recommended
        if not coverage_config_found:
            pytest.skip("Coverage configuration not found (optional)")


@pytest.mark.ci
class TestTestStructure:
    """Tests for test structure and organization"""
    
    def test_test_directory_structure(self):
        """Test test directory has proper structure"""
        test_dir = Path('tests')
        assert test_dir.exists(), "Tests directory should exist"
        assert test_dir.is_dir(), "Tests should be a directory"
    
    def test_conftest_exists(self):
        """Test conftest.py exists for shared fixtures"""
        conftest_path = Path('tests/conftest.py')
        assert conftest_path.exists(), "conftest.py should exist for shared fixtures"
    
    def test_test_files_naming_convention(self):
        """Test test files follow naming convention"""
        test_dir = Path('tests')
        
        if test_dir.exists():
            test_files = list(test_dir.glob('test_*.py'))
            
            assert len(test_files) > 0, "Should have test files following test_*.py convention"
            
            for test_file in test_files:
                assert test_file.name.startswith('test_'), f"Test file {test_file.name} should start with 'test_'"
                assert test_file.suffix == '.py', f"Test file {test_file.name} should have .py extension"
    
    def test_test_categories_exist(self):
        """Test different categories of tests exist"""
        test_dir = Path('tests')
        
        if test_dir.exists():
            test_files = [f.name for f in test_dir.glob('test_*.py')]
            
            # Check for different test categories
            categories = {
                'unit': ['unit', 'test_comprehensive_unit'],
                'integration': ['integration', 'test_comprehensive_integration'],
                'ui': ['ui', 'test_comprehensive_ui'],
                'performance': ['performance', 'test_comprehensive_performance'],
                'e2e': ['e2e', 'test_comprehensive_e2e']
            }
            
            found_categories = []
            for category, patterns in categories.items():
                for pattern in patterns:
                    if any(pattern in test_file for test_file in test_files):
                        found_categories.append(category)
                        break
            
            assert len(found_categories) >= 3, f"Should have at least 3 test categories, found: {found_categories}"
    
    def test_test_markers_defined(self):
        """Test pytest markers are properly defined"""
        # Check if markers are defined in pytest configuration
        config_files = ['pytest.ini', 'pyproject.toml', 'setup.cfg']
        
        markers_found = False
        expected_markers = ['unit', 'integration', 'ui', 'performance', 'e2e']
        
        for config_file in config_files:
            config_path = Path(config_file)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    content = f.read()
                    
                    # Check for marker definitions
                    if 'markers' in content:
                        markers_found = True
                        for marker in expected_markers:
                            if marker in content:
                                assert True  # Marker found
        
        # If no explicit marker config found, check conftest.py
        if not markers_found:
            conftest_path = Path('tests/conftest.py')
            if conftest_path.exists():
                with open(conftest_path, 'r') as f:
                    content = f.read()
                    if 'pytest_configure' in content and 'markers' in content:
                        markers_found = True
        
        assert markers_found, "Pytest markers should be defined in configuration"


@pytest.mark.ci
class TestTestExecution:
    """Tests for test execution and commands"""
    
    def test_pytest_runs_without_errors(self):
        """Test pytest can run without import errors"""
        import subprocess
        import sys
        
        # Run pytest with --collect-only to check for import errors
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/', '--collect-only', '-q'
        ], capture_output=True, text=True, cwd='.')
        
        # Should not have import errors
        if result.returncode != 0:
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
        
        # Allow some test collection issues but not import errors
        assert 'ImportError' not in result.stderr, f"Import errors found: {result.stderr}"
        assert 'ModuleNotFoundError' not in result.stderr, f"Module not found errors: {result.stderr}"
    
    def test_test_markers_work(self):
        """Test pytest markers work correctly"""
        import subprocess
        import sys
        
        # Test running specific marker
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/', '-m', 'unit', '--collect-only', '-q'
        ], capture_output=True, text=True, cwd='.')
        
        # Should collect some tests or give appropriate message
        assert result.returncode == 0 or 'no tests ran' in result.stdout.lower()
    
    def test_coverage_can_run(self):
        """Test coverage can run with pytest"""
        import subprocess
        import sys
        
        # Try to run pytest with coverage
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            'tests/', '--cov=src', '--cov-report=term-missing', 
            '--collect-only', '-q'
        ], capture_output=True, text=True, cwd='.')
        
        # Should not fail due to coverage setup issues
        if 'coverage' in result.stderr.lower() and 'error' in result.stderr.lower():
            pytest.skip("Coverage not properly configured")
        
        assert 'ImportError' not in result.stderr


@pytest.mark.ci
class TestCodeQuality:
    """Tests for code quality tools configuration"""
    
    def test_precommit_config_exists(self):
        """Test pre-commit configuration exists"""
        precommit_path = Path('.pre-commit-config.yaml')
        
        if precommit_path.exists():
            with open(precommit_path, 'r') as f:
                try:
                    config = yaml.safe_load(f)
                    assert isinstance(config, dict), "Pre-commit config should be valid YAML"
                    assert 'repos' in config, "Pre-commit config should have repos"
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in pre-commit config: {e}")
        else:
            pytest.skip("Pre-commit configuration not found (optional)")
    
    def test_linting_config_exists(self):
        """Test linting configuration exists"""
        linting_configs = [
            '.flake8', 'setup.cfg', 'pyproject.toml', 
            '.pylintrc', 'pylint.ini'
        ]
        
        config_found = any(Path(config).exists() for config in linting_configs)
        
        if not config_found:
            pytest.skip("Linting configuration not found (optional)")
    
    def test_formatting_config_exists(self):
        """Test code formatting configuration exists"""
        formatting_configs = [
            'pyproject.toml', '.black', 'setup.cfg'
        ]
        
        config_found = False
        for config_file in formatting_configs:
            if Path(config_file).exists():
                with open(config_file, 'r') as f:
                    content = f.read()
                    if 'black' in content.lower() or 'isort' in content.lower():
                        config_found = True
                        break
        
        if not config_found:
            pytest.skip("Code formatting configuration not found (optional)")


@pytest.mark.ci
class TestDocumentation:
    """Tests for documentation and README"""
    
    def test_readme_exists(self):
        """Test README file exists"""
        readme_files = ['README.md', 'README.rst', 'README.txt']
        
        readme_found = any(Path(readme).exists() for readme in readme_files)
        assert readme_found, "README file should exist"
    
    def test_readme_has_testing_section(self):
        """Test README includes testing information"""
        readme_files = ['README.md', 'README.rst', 'README.txt']
        
        for readme_file in readme_files:
            readme_path = Path(readme_file)
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    
                    # Should mention testing
                    testing_keywords = ['test', 'pytest', 'testing', 'unit test']
                    has_testing_info = any(keyword in content for keyword in testing_keywords)
                    
                    if has_testing_info:
                        assert True
                        return
        
        pytest.skip("No testing information found in README (optional)")
    
    def test_contributing_guide_exists(self):
        """Test contributing guide exists"""
        contributing_files = ['CONTRIBUTING.md', 'CONTRIBUTING.rst', 'CONTRIBUTING.txt']
        
        contributing_found = any(Path(contrib).exists() for contrib in contributing_files)
        
        if not contributing_found:
            pytest.skip("Contributing guide not found (optional)")
    
    def test_changelog_exists(self):
        """Test changelog exists"""
        changelog_files = ['CHANGELOG.md', 'CHANGELOG.rst', 'CHANGELOG.txt', 'HISTORY.md']
        
        changelog_found = any(Path(changelog).exists() for changelog in changelog_files)
        
        if not changelog_found:
            pytest.skip("Changelog not found (optional)")


@pytest.mark.ci
class TestSecurityConfiguration:
    """Tests for security configuration in CI"""
    
    def test_security_scanning_config(self):
        """Test security scanning configuration"""
        # Check for security tools in CI or pre-commit
        security_tools = ['bandit', 'safety', 'semgrep']
        
        config_files = [
            '.github/workflows/ci.yml',
            '.pre-commit-config.yaml',
            'pyproject.toml'
        ]
        
        security_tool_found = False
        
        for config_file in config_files:
            config_path = Path(config_file)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    content = f.read().lower()
                    
                    for tool in security_tools:
                        if tool in content:
                            security_tool_found = True
                            break
                
                if security_tool_found:
                    break
        
        if not security_tool_found:
            pytest.skip("Security scanning tools not configured (optional)")
    
    def test_dependency_scanning_config(self):
        """Test dependency scanning configuration"""
        # Check for dependency scanning in CI
        workflow_path = Path('.github/workflows/ci.yml')
        
        if workflow_path.exists():
            with open(workflow_path, 'r') as f:
                content = f.read().lower()
                
                dependency_tools = ['safety', 'pip-audit', 'dependabot']
                
                has_dependency_scanning = any(tool in content for tool in dependency_tools)
                
                if not has_dependency_scanning:
                    pytest.skip("Dependency scanning not configured (optional)")
        else:
            pytest.skip("GitHub Actions workflow not found")


def create_ci_workflow_template():
    """Create a template CI workflow for GitHub Actions"""
    workflow_template = {
        'name': 'Enhanced Phone Investigation CI',
        'on': {
            'push': {
                'branches': ['main', 'develop']
            },
            'pull_request': {
                'branches': ['main', 'develop']
            }
        },
        'jobs': {
            'test': {
                'runs-on': 'ubuntu-latest',
                'strategy': {
                    'matrix': {
                        'python-version': ['3.8', '3.9', '3.10', '3.11']
                    }
                },
                'steps': [
                    {
                        'uses': 'actions/checkout@v3'
                    },
                    {
                        'name': 'Set up Python ${{ matrix.python-version }}',
                        'uses': 'actions/setup-python@v4',
                        'with': {
                            'python-version': '${{ matrix.python-version }}'
                        }
                    },
                    {
                        'name': 'Install dependencies',
                        'run': 'pip install -r requirements-dev.txt'
                    },
                    {
                        'name': 'Run unit tests',
                        'run': 'pytest tests/ -m unit -v --cov=src --cov-report=xml'
                    },
                    {
                        'name': 'Run integration tests',
                        'run': 'pytest tests/ -m integration -v'
                    },
                    {
                        'name': 'Run performance tests',
                        'run': 'pytest tests/ -m performance -v'
                    },
                    {
                        'name': 'Upload coverage to Codecov',
                        'uses': 'codecov/codecov-action@v3',
                        'with': {
                            'file': './coverage.xml',
                            'flags': 'unittests',
                            'name': 'codecov-umbrella'
                        }
                    }
                ]
            },
            'lint': {
                'runs-on': 'ubuntu-latest',
                'steps': [
                    {
                        'uses': 'actions/checkout@v3'
                    },
                    {
                        'name': 'Set up Python',
                        'uses': 'actions/setup-python@v4',
                        'with': {
                            'python-version': '3.10'
                        }
                    },
                    {
                        'name': 'Install dependencies',
                        'run': 'pip install -r requirements-dev.txt'
                    },
                    {
                        'name': 'Run flake8',
                        'run': 'flake8 src tests'
                    },
                    {
                        'name': 'Run black',
                        'run': 'black --check src tests'
                    },
                    {
                        'name': 'Run isort',
                        'run': 'isort --check-only src tests'
                    }
                ]
            },
            'security': {
                'runs-on': 'ubuntu-latest',
                'steps': [
                    {
                        'uses': 'actions/checkout@v3'
                    },
                    {
                        'name': 'Set up Python',
                        'uses': 'actions/setup-python@v4',
                        'with': {
                            'python-version': '3.10'
                        }
                    },
                    {
                        'name': 'Install dependencies',
                        'run': 'pip install -r requirements-dev.txt'
                    },
                    {
                        'name': 'Run bandit security scan',
                        'run': 'bandit -r src'
                    },
                    {
                        'name': 'Run safety check',
                        'run': 'safety check'
                    }
                ]
            }
        }
    }
    
    return workflow_template


if __name__ == '__main__':
    # Generate CI workflow template
    template = create_ci_workflow_template()
    
    # Save to file
    workflow_dir = Path('.github/workflows')
    workflow_dir.mkdir(parents=True, exist_ok=True)
    
    with open(workflow_dir / 'ci-template.yml', 'w') as f:
        yaml.dump(template, f, default_flow_style=False, sort_keys=False)
    
    print("CI workflow template created at .github/workflows/ci-template.yml")
    
    # Run the tests
    pytest.main([__file__, '-v'])