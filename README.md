# isminet

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python tool for analyzing and optimizing UniFi Network deployments, with a focus on Apple device compatibility and best practices.

## Overview

This project serves two main purposes:

1. **Network Analysis**: Gather information about UniFi networks to analyze and diagnose problems (e.g., IP address conflicts, connectivity issues).
2. **Apple Compatibility**: Validate UniFi network configurations against Apple's recommended settings for optimal performance with Apple devices.

## Project Structure

- `isminet/`: Main package directory
  - `models.py`: Pydantic models for UniFi API responses
  - `clients/`: API client implementations
- `tests/`: Test suite
  - `test_models.py`: Tests for data models
- `docs/`: Documentation
  - `unifi_network_api.md`: UniFi Network API documentation
  - `api_responses/`: Local directory for real API responses (not tracked in git)
  - `apple_recommendations.md`: Apple's Wi-Fi recommendations checklist

## Features

- UniFi Network API integration
- Pydantic models for type-safe API interactions
- Configuration validation against Apple's recommendations
- Network analysis capabilities (coming soon)

## Development

This project uses:
- Python 3.12+
- `uv` for dependency management
- `pytest` for testing
- `pre-commit` for code quality

To set up for development:
```bash
# Install dependencies
uv sync --all-groups

# Run tests
uv run pytest .
```

## Status

This project is in early development. Current focus is on:
1. Implementing Apple's Wi-Fi recommendations checklist
2. Building core UniFi API integration
3. Developing network analysis features
