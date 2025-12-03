# Contributing to NBA Predictor

Thank you for considering contributing to NBA Predictor! This document provides guidelines and instructions for contributing.

## 🎯 Ways to Contribute

- **Bug Reports**: Report issues you encounter
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit pull requests
- **Documentation**: Improve or add documentation
- **Testing**: Write or improve tests

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Detailed steps to reproduce the issue
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**: Python version, OS, database version
6. **Logs**: Relevant log output (check `logs/nba_predictor.log`)

Example:
```markdown
**Bug**: Scraper fails on games with overtime

**Steps to Reproduce**:
1. Run `python -m nba_predictor.cli scrape-games 2024 january`
2. Error occurs when processing game with 5+ overtime periods

**Expected**: All games scraped successfully
**Actual**: Script crashes with IndexError

**Environment**: Python 3.11, Ubuntu 22.04, MySQL 8.0
```

## 💡 Feature Requests

For feature requests, please describe:

1. **Use Case**: Why is this feature needed?
2. **Proposed Solution**: How should it work?
3. **Alternatives**: Other approaches considered
4. **Implementation Ideas**: Technical approach (optional)

## 🔧 Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/nbaPredictor.git
cd nbaPredictor
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install all dependencies including dev tools
pip install -r requirements.txt
```

### 4. Set Up Pre-commit Hooks

```bash
pre-commit install
```

### 5. Configure Environment

```bash
cp .env.example .env
# Edit .env with your local settings
```

### 6. Initialize Database

```bash
# Create test database
mysql -u root -p
CREATE DATABASE sportbet_test;
EXIT;

# Initialize tables
python -m nba_predictor.cli init
```

## 📝 Code Style

We use the following tools to maintain code quality:

### Black (Code Formatting)

```bash
# Format all code
black src/ tests/

# Check formatting
black --check src/ tests/
```

### Ruff (Linting)

```bash
# Lint code
ruff check src/ tests/

# Auto-fix issues
ruff check --fix src/ tests/
```

### MyPy (Type Checking)

```bash
# Type check
mypy src/
```

### Style Guidelines

- **Line Length**: 100 characters
- **Type Hints**: Required for all functions
- **Docstrings**: Required for all public functions and classes
- **Imports**: Organized and sorted (black + isort)

Example:

```python
from typing import Optional

def calculate_average(values: list[int]) -> Optional[float]:
    """Calculate the average of a list of integers.

    Args:
        values: List of integers to average

    Returns:
        Average value or None if list is empty
    """
    if not values:
        return None
    return sum(values) / len(values)
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=nba_predictor --cov-report=html

# Run specific test file
pytest tests/test_scraper.py

# Run specific test
pytest tests/test_scraper.py::test_import_games
```

### Writing Tests

- Place tests in the `tests/` directory
- Mirror the structure of `src/nba_predictor/`
- Use descriptive test names
- Test both success and failure cases

Example:

```python
import pytest
from nba_predictor.scraper import BasketballReferenceScraper, ScraperError

def test_import_games_success():
    """Test successful game import."""
    scraper = BasketballReferenceScraper()
    count = scraper.import_games("2024", "january")
    assert count > 0

def test_import_games_invalid_month():
    """Test import fails with invalid month."""
    scraper = BasketballReferenceScraper()
    with pytest.raises(ValueError):
        scraper.import_games("2024", "invalid")
```

## 📤 Submitting Pull Requests

### Branch Naming

Use descriptive branch names:

- `feature/add-player-stats` - New features
- `fix/scraper-timeout` - Bug fixes
- `docs/update-readme` - Documentation
- `refactor/database-queries` - Refactoring

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:

```
feat(predictor): add multi-model ensemble predictions

Implemented ensemble prediction using multiple AI models for
improved accuracy. Combines Claude Sonnet and Opus predictions
with configurable weights.

Closes #123
```

```
fix(scraper): handle overtime periods correctly

Fixed IndexError when processing games with 5+ overtime periods.
Now correctly handles unlimited overtime scenarios.

Fixes #456
```

### Pull Request Process

1. **Create Branch**

```bash
git checkout -b feature/your-feature-name
```

2. **Make Changes**

- Write code following style guidelines
- Add tests for new functionality
- Update documentation if needed

3. **Run Checks**

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/

# Test
pytest
```

4. **Commit Changes**

```bash
git add .
git commit -m "feat(module): description"
```

5. **Push to Fork**

```bash
git push origin feature/your-feature-name
```

6. **Create Pull Request**

- Go to GitHub and create a PR
- Fill out the PR template
- Link related issues
- Wait for review

### Pull Request Checklist

- [ ] Code follows style guidelines (black, ruff, mypy)
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] PR description is clear and complete

## 🏗️ Architecture Guidelines

### Adding New Features

#### New Scraper Source

1. Create new file in `src/nba_predictor/scraper/`
2. Implement scraper class with error handling
3. Add configuration options to `config.py`
4. Add CLI commands in `cli.py`
5. Add tests

#### New Database Model

1. Create model in `src/nba_predictor/models/`
2. Use SQLAlchemy declarative base
3. Add relationships if needed
4. Create Alembic migration
5. Update documentation

#### New Prediction Model

1. Create predictor in `src/nba_predictor/prediction/`
2. Follow `ClaudePredictor` interface
3. Add configuration options
4. Add CLI commands
5. Add tests

### Code Organization

```
src/nba_predictor/
├── core/           # Configuration, logging
├── models/         # Database models
├── scraper/        # Data collection
├── prediction/     # AI predictions
├── utils/          # Helper functions
└── cli.py          # CLI interface
```

## 📚 Documentation

### Docstring Format

Use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Short description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When input is invalid
    """
    pass
```

### README Updates

When adding features, update:

- Feature list
- Usage examples
- Architecture diagram
- Configuration options

## 🤝 Code Review

### What We Look For

- **Correctness**: Does it work as intended?
- **Style**: Follows project conventions?
- **Tests**: Adequate test coverage?
- **Documentation**: Well documented?
- **Performance**: Efficient implementation?
- **Security**: No vulnerabilities?

### Review Process

1. Automated checks run (GitHub Actions)
2. Maintainer reviews code
3. Feedback provided
4. Changes requested if needed
5. Approved and merged

## 🎓 Learning Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)

## 📞 Getting Help

- **Discussions**: [GitHub Discussions](https://github.com/marcosgabbardo/nbaPredictor/discussions)
- **Issues**: [GitHub Issues](https://github.com/marcosgabbardo/nbaPredictor/issues)

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to NBA Predictor! 🏀
