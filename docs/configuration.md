# Configuration Guide

## Environment Variables

### Required Settings

#### `UNIFI_API_KEY`
- **Description**: UniFi Network API key for authentication
- **Required**: Yes
- **Format**: String
- **Example**: `UNIFI_API_KEY=TTYYGaprNuYRqheIyqdB8YOAD2QEVuBv`

#### `UNIFI_HOST`
- **Description**: UniFi Network controller hostname or IP address
- **Required**: Yes
- **Format**: String (hostname or IP)
- **Example**: `UNIFI_HOST=192.168.1.1` or `UNIFI_HOST=unifi.local`

### Optional API Settings

#### `UNIFI_PORT`
- **Description**: UniFi Network controller port
- **Default**: 8443
- **Format**: Integer (1-65535)
- **Example**: `UNIFI_PORT=8443`

#### `UNIFI_VERIFY_SSL`
- **Description**: Whether to verify SSL certificates
- **Default**: false
- **Format**: Boolean
- **Example**: `UNIFI_VERIFY_SSL=false`
- **Note**: Enabling SSL verification in production mode will generate a warning

#### `UNIFI_TIMEOUT`
- **Description**: API request timeout in seconds
- **Default**: 10
- **Format**: Integer (1-300)
- **Example**: `UNIFI_TIMEOUT=10`
- **Note**: Values over 60 seconds will generate a warning

#### `UNIFI_SITE`
- **Description**: UniFi Network site name
- **Default**: default
- **Format**: String (alphanumeric, hyphens, underscores)
- **Example**: `UNIFI_SITE=main-office`
- **Constraints**:
  - 1-50 characters
  - ASCII characters only
  - Only letters, numbers, hyphens, and underscores

#### `UNIFI_API_VERSION`
- **Description**: UniFi Network API version
- **Default**: v1
- **Format**: Enum (v1, v2)
- **Example**: `UNIFI_API_VERSION=v1`
- **Note**: Using v2 in development mode will generate a warning

### Logging Configuration

#### `ISMINET_LOG_LEVEL`
- **Description**: Logging level
- **Default**: INFO
- **Format**: Enum (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Example**: `ISMINET_LOG_LEVEL=INFO`

#### `ISMINET_DEV_MODE`
- **Description**: Development mode flag
- **Default**: false
- **Format**: Boolean
- **Example**: `ISMINET_DEV_MODE=false`

#### `ISMINET_LOG_TO_FILE`
- **Description**: Whether to log to file
- **Default**: true
- **Format**: Boolean
- **Example**: `ISMINET_LOG_TO_FILE=true`

## Common Configuration Patterns

### Development Environment
```env
UNIFI_API_KEY=your_api_key
UNIFI_HOST=192.168.1.1
ISMINET_DEV_MODE=true
ISMINET_LOG_LEVEL=DEBUG
UNIFI_VERIFY_SSL=false
```

### Production Environment
```env
UNIFI_API_KEY=your_api_key
UNIFI_HOST=unifi.example.com
ISMINET_DEV_MODE=false
ISMINET_LOG_LEVEL=INFO
UNIFI_VERIFY_SSL=true
UNIFI_TIMEOUT=30
```

### Testing Environment
```env
TEST_API_KEY=test_key
TEST_HOST=test.host
TEST_PORT=8443
ISMINET_DEV_MODE=true
ISMINET_LOG_LEVEL=DEBUG
```

## Troubleshooting Guide

### Common Issues

1. **SSL Verification Errors**
   - Check if the SSL certificate is valid
   - Consider setting `UNIFI_VERIFY_SSL=false` in development
   - Use proper CA certificates in production

2. **Timeout Issues**
   - Increase `UNIFI_TIMEOUT` if network is slow
   - Check network connectivity
   - Monitor server response times

3. **API Version Compatibility**
   - Use v1 for older UniFi controllers
   - Test thoroughly when using v2
   - Check UniFi controller version compatibility

4. **Site Configuration**
   - Verify site name in UniFi controller
   - Check for typos in site name
   - Ensure site name follows naming constraints

### Validation Errors

1. **Invalid Port**
   - Must be between 1 and 65535
   - Common ports: 8443, 443

2. **Invalid Site Name**
   - Must be 1-50 characters
   - Only letters, numbers, hyphens, and underscores
   - ASCII characters only

3. **Invalid Timeout**
   - Must be between 1 and 300 seconds
   - Values over 60 seconds generate warnings

4. **Invalid Log Level**
   - Must be one of: DEBUG, INFO, WARNING, ERROR, CRITICAL
   - Case sensitive
