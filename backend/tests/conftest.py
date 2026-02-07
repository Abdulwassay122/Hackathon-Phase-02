"""
Pytest configuration and fixtures
Sets up test environment variables before test collection
"""
import os
import pytest

# Set up test environment variables before any imports
os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing-at-least-32-characters-long"
os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["LOG_LEVEL"] = "INFO"
