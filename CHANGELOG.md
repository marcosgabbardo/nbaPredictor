# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-12-03

### 🎉 Major Revitalization

This release represents a **complete rewrite** of the NBA Predictor project, modernizing every aspect of the codebase.

### Added

- **Python 3.11+ Support** - Migrated from Python 2.7 with modern syntax and features
- **SQLAlchemy ORM** - Complete database abstraction layer with type hints
- **Claude AI Integration** - State-of-the-art AI predictions replacing AWS ML
- **Structured Logging** - JSON logs with full traceability using structlog
- **Pydantic Configuration** - Type-safe configuration management
- **Modern CLI** - User-friendly command-line interface with argparse
- **Robust Error Handling** - Comprehensive exception handling and retry logic
- **Rate Limiting** - Respectful web scraping with delays
- **Automatic Retries** - Exponential backoff for failed requests
- **Type Hints** - Full type annotations throughout the codebase
- **Project Configuration** - pyproject.toml with black, ruff, mypy settings
- **Environment Variables** - Secure configuration via .env files
- **Modular Architecture** - Clean separation of concerns
- **Comprehensive README** - Complete documentation with examples

### Changed

- **Database Layer** - From raw SQL to SQLAlchemy ORM with context managers
- **Logging** - From print statements to structured logging
- **Configuration** - From hardcoded values to environment variables
- **ML Backend** - From AWS Machine Learning to Claude AI
- **Code Style** - Modern Python 3.11+ idioms and best practices
- **Project Structure** - Reorganized into logical modules under src/

### Removed

- **Python 2.7 Code** - All legacy Python 2 syntax
- **Hardcoded Credentials** - Replaced with environment variables
- **AWS ML Integration** - Replaced with Claude AI
- **Raw SQL Queries** - Replaced with ORM queries
- **Under Construction Features** - Cleaned up incomplete features

### Security

- **No Hardcoded Credentials** - All sensitive data in environment variables
- **SQL Injection Protection** - ORM prevents SQL injection attacks
- **Secure API Key Management** - Credentials stored securely
- **Input Validation** - Pydantic models validate all inputs

### Technical Debt

- Resolved all Python 2.7 EOL issues
- Removed deprecated AWS ML service dependency
- Fixed security issues with hardcoded passwords
- Improved error handling throughout
- Added proper logging instead of print statements

## [1.0.0] - 2017-01-09

### Initial Release

- Basic web scraping from Basketball Reference
- MySQL database storage
- Statistical calculations
- AWS Machine Learning integration
- Python 2.7 codebase

---

**Note**: This project was dormant from 2017 to 2024 and has now been completely revitalized with modern technologies.
