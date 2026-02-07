# Phase 1 Design: CORS Configuration Data Model

**Feature**: Backend CORS Configuration (004-backend-cors-fix)
**Date**: 2026-02-07
**Objective**: Define the CORS configuration structure, environment variable schema, and validation rules

## Environment Variable Schema

### CORS_ORIGINS Format

**Variable Name**: `CORS_ORIGINS`

**Format**: Comma-separated list of origin URLs

**Examples**:
```bash
# Single origin (development)
CORS_ORIGINS=http://localhost:3000

# Multiple origins (development + staging)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Production example
CORS_ORIGINS=https://app.example.com,https://staging.example.com

# With spaces (will be stripped)
CORS_ORIGINS=http://localhost:3000, http://localhost:3001, https://app.example.com
```

**Parsing Rules**:
1. Split on comma (`,`)
2. Strip whitespace from each origin
3. Filter out empty strings
4. Validate each origin URL
5. Return list of valid origins

**Default Behavior**:
- If `CORS_ORIGINS` is not set: Empty list `[]` (no origins allowed)
- If `CORS_ORIGINS` is empty string: Empty list `[]` (no origins allowed)
- If `CORS_ORIGINS` contains invalid URLs: Log warning, skip invalid entries

## CORS Configuration Structure

### Python Data Structure

```python
from typing import List
from dataclasses import dataclass

@dataclass
class CORSConfig:
    """CORS configuration for FastAPI application"""

    # Origins allowed to make cross-origin requests
    allow_origins: List[str]

    # Whether to allow credentials (cookies, Authorization header)
    allow_credentials: bool = True

    # HTTP methods allowed for cross-origin requests
    allow_methods: List[str] = None

    # Request headers allowed in cross-origin requests
    allow_headers: List[str] = None

    # Response headers exposed to browser JavaScript
    expose_headers: List[str] = None

    # Preflight cache duration in seconds
    max_age: int = 600

    def __post_init__(self):
        """Set default values for list fields"""
        if self.allow_methods is None:
            self.allow_methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]

        if self.allow_headers is None:
            self.allow_headers = ["Authorization", "Content-Type"]

        if self.expose_headers is None:
            self.expose_headers = []
```

### Configuration Loading Flow

```
1. Application Startup
   ↓
2. Load CORS_ORIGINS from environment
   ↓
3. Parse comma-separated origins
   ↓
4. Validate each origin URL
   ↓
5. Create CORSConfig instance
   ↓
6. Add CORSMiddleware to FastAPI app
   ↓
7. Log configuration summary
```

## CORSMiddleware Parameters Mapping

### Parameter Mapping Table

| CORSConfig Field | FastAPI Parameter | Value | Source |
|------------------|-------------------|-------|--------|
| `allow_origins` | `allow_origins` | List from CORS_ORIGINS | Environment variable |
| `allow_credentials` | `allow_credentials` | `True` | Hardcoded (required for JWT) |
| `allow_methods` | `allow_methods` | `["GET", "POST", "PUT", "PATCH", "DELETE"]` | Hardcoded (explicit list) |
| `allow_headers` | `allow_headers` | `["Authorization", "Content-Type"]` | Hardcoded (explicit list) |
| `expose_headers` | `expose_headers` | `[]` | Hardcoded (not needed) |
| `max_age` | `max_age` | `600` | Hardcoded (10 minutes) |

### FastAPI Integration Code

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import get_cors_config

app = FastAPI()

# Load CORS configuration
cors_config = get_cors_config()

# Add CORS middleware (must be before route registration)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config.allow_origins,
    allow_credentials=cors_config.allow_credentials,
    allow_methods=cors_config.allow_methods,
    allow_headers=cors_config.allow_headers,
    expose_headers=cors_config.expose_headers,
    max_age=cors_config.max_age,
)
```

## Validation Rules

### Origin URL Validation

**Valid Origin Format**:
- Must start with `http://` or `https://`
- Must not end with trailing slash `/`
- Must not be empty or whitespace-only
- Must not contain spaces (except leading/trailing which are stripped)

**Validation Function**:
```python
import re
from urllib.parse import urlparse

def validate_origin(origin: str) -> tuple[bool, str]:
    """
    Validate a CORS origin URL.

    Returns:
        (is_valid, error_message)
    """
    # Check for empty/whitespace
    if not origin or origin.isspace():
        return False, "Origin is empty or whitespace-only"

    # Check for wildcard (not allowed per spec)
    if origin == "*":
        return False, "Wildcard origin (*) not allowed per security policy"

    # Check for protocol
    if not origin.startswith(("http://", "https://")):
        return False, f"Origin must start with http:// or https://, got: {origin}"

    # Check for trailing slash
    if origin.endswith("/"):
        return False, f"Origin must not end with trailing slash: {origin}"

    # Validate URL structure
    try:
        parsed = urlparse(origin)
        if not parsed.netloc:
            return False, f"Invalid origin URL structure: {origin}"
    except Exception as e:
        return False, f"Failed to parse origin URL: {e}"

    return True, ""
```

### Validation Error Handling

**Strategy**: Fail-safe with logging

```python
def parse_cors_origins(origins_str: str) -> List[str]:
    """
    Parse and validate CORS origins from environment variable.

    Returns:
        List of valid origin URLs
    """
    if not origins_str:
        logger.warning("CORS_ORIGINS environment variable not set. No origins will be allowed.")
        return []

    # Split and strip
    raw_origins = [origin.strip() for origin in origins_str.split(",")]

    # Validate each origin
    valid_origins = []
    for origin in raw_origins:
        if not origin:
            continue

        is_valid, error_msg = validate_origin(origin)
        if is_valid:
            valid_origins.append(origin)
            logger.info(f"CORS: Allowed origin: {origin}")
        else:
            logger.warning(f"CORS: Invalid origin skipped: {origin} - {error_msg}")

    if not valid_origins:
        logger.warning("CORS: No valid origins configured. Cross-origin requests will be blocked.")

    return valid_origins
```

## Default Values and Fallback Behavior

### Default Configuration

```python
DEFAULT_CORS_CONFIG = CORSConfig(
    allow_origins=[],  # Empty list - no origins allowed by default
    allow_credentials=True,  # Required for JWT authentication
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],  # Standard REST methods
    allow_headers=["Authorization", "Content-Type"],  # Required for JWT + JSON
    expose_headers=[],  # No custom headers exposed
    max_age=600,  # 10 minutes preflight cache
)
```

### Fallback Scenarios

| Scenario | Behavior | Rationale |
|----------|----------|-----------|
| CORS_ORIGINS not set | Empty list, log warning | Fail-safe: block all cross-origin requests |
| CORS_ORIGINS empty string | Empty list, log warning | Same as not set |
| All origins invalid | Empty list, log error | Fail-safe: don't allow invalid origins |
| Some origins invalid | Use valid ones, log warnings | Partial success: allow valid origins |
| Wildcard (*) detected | Skip it, log error | Security policy: no wildcards allowed |

### Logging Strategy

**Startup Logging**:
```python
def log_cors_configuration(config: CORSConfig):
    """Log CORS configuration at application startup"""
    logger.info("=" * 60)
    logger.info("CORS Configuration")
    logger.info("=" * 60)

    if config.allow_origins:
        logger.info(f"Allowed Origins ({len(config.allow_origins)}):")
        for origin in config.allow_origins:
            logger.info(f"  - {origin}")
    else:
        logger.warning("No origins configured - cross-origin requests will be blocked!")

    logger.info(f"Allow Credentials: {config.allow_credentials}")
    logger.info(f"Allowed Methods: {', '.join(config.allow_methods)}")
    logger.info(f"Allowed Headers: {', '.join(config.allow_headers)}")
    logger.info(f"Preflight Cache: {config.max_age} seconds")
    logger.info("=" * 60)
```

## Configuration Module Structure

### File: `backend/src/config.py`

**Additions to existing config.py**:

```python
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ... existing configuration ...

# CORS Configuration
def get_cors_origins() -> List[str]:
    """
    Load and parse CORS origins from environment variable.

    Returns:
        List of valid origin URLs
    """
    origins_str = os.getenv("CORS_ORIGINS", "")
    return parse_cors_origins(origins_str)

def get_cors_config() -> CORSConfig:
    """
    Get complete CORS configuration.

    Returns:
        CORSConfig instance with all settings
    """
    return CORSConfig(
        allow_origins=get_cors_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
        expose_headers=[],
        max_age=600,
    )
```

## Security Constraints

### Enforced Constraints

1. **No Wildcard Origins**:
   - Validation rejects `"*"` in origin list
   - Error logged if wildcard detected
   - Wildcard skipped, not used

2. **No Wildcard Headers**:
   - Hardcoded explicit list: `["Authorization", "Content-Type"]`
   - No dynamic header configuration
   - No `"*"` allowed

3. **No Wildcard Methods**:
   - Hardcoded explicit list: `["GET", "POST", "PUT", "PATCH", "DELETE"]`
   - No dynamic method configuration
   - No `"*"` allowed

4. **Credentials Always Enabled**:
   - `allow_credentials=True` hardcoded
   - Required for JWT authentication
   - Cannot be disabled

### Security Validation Tests

```python
def test_wildcard_origin_rejected():
    """Wildcard origin should be rejected"""
    is_valid, error = validate_origin("*")
    assert not is_valid
    assert "wildcard" in error.lower()

def test_no_wildcard_in_config():
    """Configuration should never contain wildcards"""
    config = get_cors_config()
    assert "*" not in config.allow_origins
    assert "*" not in config.allow_methods
    assert "*" not in config.allow_headers

def test_credentials_always_enabled():
    """Credentials must always be enabled for JWT"""
    config = get_cors_config()
    assert config.allow_credentials is True
```

## Environment-Specific Configuration

### Development Environment

```bash
# .env (development)
CORS_ORIGINS=http://localhost:3000
```

**Characteristics**:
- Single origin (frontend dev server)
- HTTP protocol (localhost)
- Port 3000 (Next.js default)

### Staging Environment

```bash
# .env.staging
CORS_ORIGINS=https://staging-app.example.com,http://localhost:3000
```

**Characteristics**:
- Multiple origins (staging + local testing)
- HTTPS for staging domain
- HTTP for localhost testing

### Production Environment

```bash
# .env.production
CORS_ORIGINS=https://app.example.com
```

**Characteristics**:
- Single origin (production domain)
- HTTPS only (no HTTP)
- No localhost origins

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ Application Startup                                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Load Environment Variables (python-dotenv)                  │
│ - CORS_ORIGINS="http://localhost:3000,http://localhost:3001"│
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Parse CORS_ORIGINS (config.py)                              │
│ - Split on comma                                            │
│ - Strip whitespace                                          │
│ - Result: ["http://localhost:3000", "http://localhost:3001"]│
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Validate Each Origin (config.py)                            │
│ - Check protocol (http:// or https://)                      │
│ - Check no trailing slash                                   │
│ - Check not wildcard (*)                                    │
│ - Log validation results                                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Create CORSConfig Instance (config.py)                      │
│ - allow_origins: ["http://localhost:3000", ...]            │
│ - allow_credentials: True                                   │
│ - allow_methods: ["GET", "POST", "PUT", "PATCH", "DELETE"]  │
│ - allow_headers: ["Authorization", "Content-Type"]          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Add CORSMiddleware to FastAPI (main.py)                     │
│ - app.add_middleware(CORSMiddleware, **config)             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Log Configuration Summary (main.py)                         │
│ - Log allowed origins                                       │
│ - Log security settings                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Application Ready                                           │
│ - CORS middleware active                                    │
│ - Cross-origin requests allowed from configured origins     │
└─────────────────────────────────────────────────────────────┘
```

## Implementation Checklist

- [ ] Add `CORSConfig` dataclass to config.py
- [ ] Add `validate_origin()` function to config.py
- [ ] Add `parse_cors_origins()` function to config.py
- [ ] Add `get_cors_origins()` function to config.py
- [ ] Add `get_cors_config()` function to config.py
- [ ] Add `log_cors_configuration()` function to config.py or logging_config.py
- [ ] Import CORSMiddleware in main.py
- [ ] Call `get_cors_config()` in main.py
- [ ] Add CORSMiddleware to app in main.py (after app creation, before routes)
- [ ] Call `log_cors_configuration()` in startup event
- [ ] Add CORS_ORIGINS to .env.example with documentation
- [ ] Add unit tests for validation functions
- [ ] Add integration tests for CORS headers

## Notes

- **No Database Storage**: CORS configuration is loaded from environment variables only, not stored in database
- **No Runtime Changes**: CORS configuration is loaded at startup and cannot be changed without restarting the application
- **No User Configuration**: CORS settings are deployment-level configuration, not user-configurable
- **Immutable After Startup**: Once CORSMiddleware is added, configuration cannot be modified at runtime
