# Sentinel Authentication API Specification

## 1. General Rules

### Base URL
All authentication and user management endpoints are prefixed with:
`/api/v1`

### Authentication
The API uses **JWT (JSON Web Token)** for stateless authentication.
- Clients must include the token in the `Authorization` header using the `Bearer` schema.

### Standard Response Format
All endpoints return responses wrapped in a consistent structure.

**Success Response Format:**
```json
{
    "success": true,
    "message": "Human-readable success message",
    "data": {
        // Endpoint-specific data
    }
}
```

**Error Response Format:**
```json
{
    "success": false,
    "message": "Human-readable error description",
    "errors": [
        // List of specific validation or logic errors
    ]
}
```

---

## 2. Status Codes

| Code | Status | Description |
|------|--------|-------------|
| **200** | OK | Request succeeded. |
| **201** | Created | Resource successfully created. |
| **204** | No Content | Request succeeded, but no data to return (e.g., deletion). |
| **400** | Bad Request | Invalid request parameters or business logic failure. |
| **401** | Unauthorized | Missing, invalid, or expired authentication token. |
| **403** | Forbidden | Authenticated, but lacks required permissions/roles. |
| **404** | Not Found | The requested resource does not exist. |
| **409** | Conflict | Resource already exists or state conflict (e.g., duplicate username). |
| **422** | Unprocessable Entity | Schema validation error (e.g., missing required fields). |
| **500** | Internal Server Error | Unexpected server-side failure. |

---

## 3. JWT Policy

- **Access Token**: Short-lived token (default: 60 minutes) used for API authorization. Contains `token_type`, `sub`, `username`, `roles`, `iat`, `exp`, and `jti` claims.
- **Refresh Token**: Long-lived token (default: 7 days) used to obtain a new Access Token.
- **Authorization Header**: Expected format is `Authorization: Bearer <access_token>`.
- **Expiration**: The `exp` claim is strictly enforced. Expired tokens yield a 401 response.
- **Rotation**: Refreshing a session invalidates the previous refresh token and issues a new `(access_token, refresh_token)` pair.

---

## 4. Password Policy

When creating or updating passwords, the following rules apply:
- **Minimum Length**: 12 characters.
- **Uppercase**: At least 1 uppercase letter (A-Z).
- **Lowercase**: At least 1 lowercase letter (a-z).
- **Number**: At least 1 numeric digit (0-9).
- **Special Character**: At least 1 special character (e.g., `!@#$%^&*`).
- **Reuse Policy**: Future requirement to prevent reusing the last N passwords.

---

## 5. Account Lock Policy

- **Failed Attempts**: 5 consecutive failed login attempts trigger a lock.
- **Lock Duration**: The account is temporarily locked for 15 minutes (`locked_until` field is set).
- **Reset Behaviour**: A successful login resets the `failed_login_attempts` counter to 0 and clears `last_failed_login`.

---

## 6. Endpoints

### 6.1 POST /auth/login
- **Purpose**: Authenticates a user and issues JWT tokens.
- **Authentication Required**: No
- **Required Role**: None
- **Request Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
    "username": "admin_user",
    "password": "SecurePassword123!"
}
```
- **Validation Rules**: `username` and `password` are required strings.
- **Success Response** (200):
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "access_token": "eyJhbGciOi...",
        "refresh_token": "4a8c9b...",
        "token_type": "bearer"
    }
}
```
- **Error Responses**: 400 (Invalid credentials), 401 (Account locked), 422 (Validation error).
- **Business Rules**: Validates against Argon2id hash. Increments failed attempts on failure. Resets attempts on success.

### 6.2 POST /auth/refresh
- **Purpose**: Issues a new session pair using a valid refresh token.
- **Authentication Required**: No (Refresh token is provided in the body).
- **Required Role**: None
- **Request Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
    "refresh_token": "4a8c9b..."
}
```
- **Validation Rules**: `refresh_token` is required.
- **Success Response** (200):
```json
{
    "success": true,
    "message": "Session refreshed",
    "data": {
        "access_token": "eyJhbGciOi...",
        "refresh_token": "new_hash_token...",
        "token_type": "bearer"
    }
}
```
- **Error Responses**: 401 (Invalid/expired token), 422.
- **Business Rules**: Employs strict rotation. The provided refresh token is revoked immediately upon use.

### 6.3 POST /auth/logout
- **Purpose**: Invalidates the current refresh token.
- **Authentication Required**: Yes (Bearer Token)
- **Required Role**: None
- **Request Headers**: `Authorization: Bearer <token>`, `Content-Type: application/json`
- **Request Body**:
```json
{
    "refresh_token": "4a8c9b..."
}
```
- **Validation Rules**: `refresh_token` required.
- **Success Response** (200):
```json
{
    "success": true,
    "message": "Logout successful",
    "data": {}
}
```
- **Error Responses**: 401 (Unauthorized).
- **Business Rules**: Revokes the provided refresh token in the database. Access tokens cannot be revoked natively and rely on short expiration times.

### 6.4 POST /auth/change-password
- **Purpose**: Allows an authenticated user to change their password.
- **Authentication Required**: Yes
- **Required Role**: None
- **Request Headers**: `Authorization: Bearer <token>`
- **Request Body**:
```json
{
    "old_password": "CurrentPassword123!",
    "new_password": "NewSecurePassword456!"
}
```
- **Validation Rules**: Must meet the Password Policy. `new_password` cannot equal `old_password`.
- **Success Response** (200):
```json
{
    "success": true,
    "message": "Password updated successfully",
    "data": {}
}
```
- **Error Responses**: 400 (Invalid old password), 422 (Weak password).
- **Business Rules**: Revokes all existing refresh tokens for the user upon success.

### 6.5 GET /auth/me
- **Purpose**: Retrieves the currently authenticated user's profile and roles.
- **Authentication Required**: Yes
- **Required Role**: None
- **Request Headers**: `Authorization: Bearer <token>`
- **Request Body**: None
- **Success Response** (200):
```json
{
    "success": true,
    "message": "Profile retrieved",
    "data": {
        "id": "uuid-here",
        "username": "admin_user",
        "email": "admin@example.com",
        "roles": ["admin"]
    }
}
```
- **Error Responses**: 401 (Unauthorized).
- **Business Rules**: Extracts `user_id` from the JWT `sub` claim and queries the database.

### 6.6 GET /users
- **Purpose**: Lists users with optional pagination.
- **Authentication Required**: Yes
- **Required Role**: `admin`
- **Request Headers**: `Authorization: Bearer <token>`
- **Request Body**: None (Query parameters: `?skip=0&limit=100`)
- **Success Response** (200):
```json
{
    "success": true,
    "message": "Users retrieved",
    "data": [
        {
            "id": "uuid",
            "username": "user1",
            "email": "user1@example.com"
        }
    ]
}
```
- **Error Responses**: 401, 403 (Forbidden).
- **Business Rules**: Returns only active users unless specified. Excludes soft-deleted records.

### 6.7 GET /users/{id}
- **Purpose**: Retrieves a specific user by ID.
- **Authentication Required**: Yes
- **Required Role**: `admin`
- **Request Headers**: `Authorization: Bearer <token>`
- **Request Body**: None
- **Success Response** (200):
```json
{
    "success": true,
    "message": "User retrieved",
    "data": {
        "id": "uuid",
        "username": "user1"
    }
}
```
- **Error Responses**: 401, 403, 404 (Not Found).

### 6.8 POST /users
- **Purpose**: Creates a new user account.
- **Authentication Required**: Yes
- **Required Role**: `admin`
- **Request Headers**: `Authorization: Bearer <token>`
- **Request Body**:
```json
{
    "username": "new_user",
    "email": "new@example.com",
    "password": "SecurePassword123!",
    "roles": ["user"]
}
```
- **Validation Rules**: `username`, `email`, `password` required. Unique constraints apply.
- **Success Response** (201):
```json
{
    "success": true,
    "message": "User created successfully",
    "data": {
        "id": "uuid",
        "username": "new_user"
    }
}
```
- **Error Responses**: 401, 403, 409 (Conflict - username/email exists), 422.
- **Business Rules**: Password is automatically hashed before DB insertion.

### 6.9 PATCH /users/{id}
- **Purpose**: Updates an existing user's details.
- **Authentication Required**: Yes
- **Required Role**: `admin`
- **Request Headers**: `Authorization: Bearer <token>`
- **Request Body**: (Partial updates allowed)
```json
{
    "first_name": "John",
    "is_active": false
}
```
- **Success Response** (200):
```json
{
    "success": true,
    "message": "User updated",
    "data": {
        "id": "uuid",
        "is_active": false
    }
}
```
- **Error Responses**: 401, 403, 404, 409, 422.

### 6.10 DELETE /users/{id}
- **Purpose**: Soft deletes a user.
- **Authentication Required**: Yes
- **Required Role**: `admin`
- **Request Headers**: `Authorization: Bearer <token>`
- **Request Body**: None
- **Success Response** (204):
No body.
- **Error Responses**: 401, 403, 404.
- **Business Rules**: Applies a soft-delete (sets `deleted_at`, `is_active` to false, revokes tokens).

### 6.11 GET /roles
- **Purpose**: Lists available roles.
- **Authentication Required**: Yes
- **Required Role**: `admin`
- **Request Headers**: `Authorization: Bearer <token>`
- **Request Body**: None
- **Success Response** (200):
```json
{
    "success": true,
    "message": "Roles retrieved",
    "data": [
        {
            "id": "uuid",
            "name": "admin",
            "description": "Administrator"
        }
    ]
}
```

### 6.12 POST /roles
- **Purpose**: Creates a new role.
- **Authentication Required**: Yes
- **Required Role**: `admin`
- **Request Headers**: `Authorization: Bearer <token>`
- **Request Body**:
```json
{
    "name": "manager",
    "description": "Manager role"
}
```
- **Success Response** (201):
```json
{
    "success": true,
    "message": "Role created",
    "data": {
        "id": "uuid",
        "name": "manager"
    }
}
```
- **Error Responses**: 401, 403, 409.

### 6.13 PATCH /roles/{id}
- **Purpose**: Updates a role.
- **Authentication Required**: Yes
- **Required Role**: `admin`
- **Request Headers**: `Authorization: Bearer <token>`
- **Request Body**:
```json
{
    "description": "New description"
}
```
- **Success Response** (200):
```json
{
    "success": true,
    "message": "Role updated",
    "data": {
        "id": "uuid",
        "name": "manager",
        "description": "New description"
    }
}
```

### 6.14 DELETE /roles/{id}
- **Purpose**: Deletes a role.
- **Authentication Required**: Yes
- **Required Role**: `admin`
- **Request Headers**: `Authorization: Bearer <token>`
- **Request Body**: None
- **Success Response** (204):
No body.
- **Error Responses**: 400 (Cannot delete default roles), 401, 403, 404.

### 6.15 GET /permissions
- **Purpose**: Lists available granular permissions.
- **Authentication Required**: Yes
- **Required Role**: `admin`
- **Request Headers**: `Authorization: Bearer <token>`
- **Request Body**: None
- **Success Response** (200):
```json
{
    "success": true,
    "message": "Permissions retrieved",
    "data": [
        {
            "id": "uuid",
            "name": "read:users",
            "description": "Can read users"
        }
    ]
}
```
