# Contributing to ReconMaster

First off, thank you for considering contributing to ReconMaster! We appreciate all contributions from the community.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

### Our Pledge

In the interest of fostering an open and welcoming environment, we as contributors and maintainers pledge to making participation in our project and our community a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual orientation.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing opinions, viewpoints, and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find one that matches your concern.

When creating a bug report, please include:

- **Clear descriptive title**
- **Detailed description** of the issue
- **Steps to reproduce** the issue
- **Expected behavior** and actual behavior
- **Screenshots or logs** (if applicable)
- **Environment details**:
  - OS and version
  - Python version (`python3 --version`)
  - ReconMaster version
  - Relevant tool versions

**Bug Report Template**:
```
### Description
Brief description of the bug

### Steps to Reproduce
1. First step
2. Second step
3. Result

### Expected Behavior
What should happen

### Actual Behavior
What actually happens

### Environment
- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.9.2]
- ReconMaster: [version or commit]
- Go Tools: [e.g., subfinder 2.5.0]

### Logs
```
$ python3 reconmaster.py -d example.com
[error message here]
```
```

### Requesting Features

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

- **Clear descriptive title**
- **Detailed description** of the suggested enhancement
- **Use cases** and examples
- **Possible implementation approach** (optional)
- **Related issues or discussion** (if any)

**Feature Request Template**:
```
### Description
Describe the feature in detail

### Motivation
Why would this feature be useful?

### Implementation Ideas
How could this be implemented?

### Examples
Show how the feature would be used
```

### Pull Requests

When submitting a pull request:

1. **Fork the repository** and create your branch from `main`
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes** following the coding standards
4. **Add tests** for new functionality
5. **Update documentation** as necessary
6. **Commit with meaningful messages**: `git commit -m "feat: add feature description"`
7. **Push to your fork**: `git push origin feature/your-feature-name`
8. **Submit pull request** with clear description
9. **Respond to review** comments promptly

**PR Template**:
```markdown
## Description
Describe the changes you made

## Related Issues
Fixes #123

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How have you tested these changes?

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have added tests
- [ ] All tests pass
- [ ] I have updated documentation
- [ ] No new warnings generated
```

## Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/VIPHACKER100/ReconMaster.git
cd ReconMaster
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Additional dev tools
```

### 4. Install Pre-commit Hooks (Recommended)

```bash
pip install pre-commit
pre-commit install
```

### 5. Verify Installation

```bash
python3 reconmaster.py --help
./scripts/import_smoke_check.py  # Verify all imports
```

## Coding Standards

### Style Guide

- **Python Version**: 3.9+
- **Style**: PEP 8 compliant
- **Linting**: flake8
  ```bash
  flake8 --config=.flake8 reconmaster.py utils.py
  ```
- **Formatting**: Black
  ```bash
  black --line-length 100 *.py
  ```
- **Type Hints**: Required for all functions
  ```python
  def process_domain(domain: str, threads: int = 10) -> dict:
      pass
  ```

### Code Structure

- **Classes**: Use meaningful names (e.g., `ReconMaster`, not `RM`)
- **Methods**: Lowercase with underscores (`passive_subdomain_enum`)
- **Constants**: UPPERCASE (`MAX_THREADS`, `DEFAULT_TIMEOUT`)
- **Variables**: Lowercase with underscores (`output_dir`, not `outputDir`)
- **Private Members**: Prefix with underscore (`_private_method`)

### Documentation

- **Module Docstrings**: Explain purpose at top of each file
- **Class Docstrings**: Describe class and main attributes
- **Method Docstrings**: Use Google style format
  ```python
  def method_name(param1: str, param2: int) -> bool:
      """Brief one-line description.
      
      Longer description explaining the method's behavior,
      any side effects, and important details.
      
      Args:
          param1: Description of param1
          param2: Description of param2
          
      Returns:
          Description of return value
          
      Raises:
          ValueError: When validation fails
          FileNotFoundError: When file not found
      """
  ```
- **Inline Comments**: Explain WHY, not WHAT (code should be clear)

### Error Handling

- **Custom Exceptions**: Create for domain-specific errors
  ```python
  class ToolNotFoundError(Exception):
      """Raised when external tool not in PATH"""
      pass
  ```
- **Always Log Errors**: Include context for debugging
  ```python
  try:
      result = safe_run(cmd)
  except FileNotFoundError as e:
      logger.error(f"Tool not found: {cmd[0]}", exc_info=True)
      raise ToolNotFoundError(f"{cmd[0]} must be installed") from e
  ```
- **Graceful Degradation**: Continue scan if non-critical tool fails

## Commit Message Format

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, missing semicolons, etc.)
- **refactor**: Code refactoring without feature changes
- **perf**: Performance improvements
- **test**: Test additions/changes
- **chore**: Build process, dependencies, tools

### Examples

```
feat(subdomain-enum): add async execution support
fix(httpx): handle connection timeouts gracefully
docs(readme): update installation instructions
refactor(core): extract utility functions to utils module
test(reconmaster): add unit tests for domain validation
perf(wordlist): optimize memory usage for large files
```

## Testing

### Running Tests

```bash
# All tests
python -m pytest tests/

# Specific test file
python -m pytest tests/test_utils.py

# Specific test
python -m pytest tests/test_utils.py::TestSafeRun::test_valid_command

# With coverage
pytest --cov=. tests/
```

### Writing Tests

```python
import unittest
from unittest.mock import patch, MagicMock

class TestReconMaster(unittest.TestCase):
    """Test cases for ReconMaster class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.target = "example.com"
        self.output_dir = "/tmp/test"
        
    def test_passive_subdomain_enum(self):
        """Test passive subdomain enumeration"""
        # Arrange
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                stdout="www.example.com\n",
                stderr="",
                returncode=0
            )
            
            # Act
            recon = ReconMaster(self.target, self.output_dir)
            result = recon.passive_subdomain_enum()
            
            # Assert
            self.assertIn("www.example.com", result)
            
    def tearDown(self):
        """Clean up after tests"""
        # Remove test files
        pass
```

### Test Coverage Requirements

- New features: ≥80% coverage
- Bug fixes: Tests for the specific issue
- Critical code: 100% coverage expected

## Documentation

### README

- Clear feature descriptions
- Quick start instructions
- Installation steps
- Usage examples
- Troubleshooting section

### Code Comments

- **Why**, not **What**: Comments explain reasoning
- **One-liners**: For obvious code
- **Multi-line**: For complex logic
- **TODO Comments**: Use sparingly, link to issues

Example:
```python
# Skip YAML files - they're config, not code
if filename.endswith('.yaml'):
    continue

# Use ThreadPoolExecutor for I/O bound operations instead of
# asyncio since we're making subprocess calls that block
executor = ThreadPoolExecutor(max_workers=self.threads)
```

### Docstring Examples

```python
def validate_domain(domain: str) -> bool:
    """Validate domain format using regex.
    
    Args:
        domain: Domain name to validate (e.g., "example.com")
        
    Returns:
        True if valid domain format, False otherwise
        
    Examples:
        >>> validate_domain("example.com")
        True
        >>> validate_domain("invalid domain with spaces")
        False
    """
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]...'
    return bool(re.match(pattern, domain))
```

## Pull Request Review Process

1. **Automated Checks**: CI/CD pipeline must pass
   - All tests pass
   - Linting passes
   - Coverage not decreased
   - No new warnings

2. **Code Review**: Maintainers review for:
   - Code quality and standards
   - Security considerations
   - Performance impact
   - Documentation adequacy
   - Backwards compatibility

3. **Feedback**: Authors expected to address comments within 2 weeks

4. **Approval**: At least 1 maintainer approval required

5. **Merge**: Squash merge to keep history clean

## Release Process

1. **Version Bump**: Update `__version__` in `reconmaster.py`
2. **Changelog**: Update `CHANGELOG.md`
3. **Tag**: Create git tag `v{version}`
4. **Build**: Create wheel and source distributions
5. **PyPI**: Upload to PyPI
6. **GitHub**: Create release with notes
7. **Docker**: Build and push Docker image

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Questions and general discussion
- **Security**: security@example.com (private vulnerability reports)

### Code Review Expectations

- Be constructive and respectful
- Focus on code, not person
- Provide rationale for suggestions
- Ask questions rather than assert incorrectness

### Contributor Recognition

- **README**: Added to contributors list
- **CHANGELOG**: Credited in relevant releases
- **GitHub**: Automatically tracked in repository

## Additional Resources

- [Python Style Guide (PEP 8)](https://pep8.org)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

---

Thank you for contributing to ReconMaster! Your efforts help make this tool better for everyone.

**Questions?** Open an issue or reach out to the community!

**Last Updated:** February 10, 2026  
**Version:** 3.2.0-Elite
