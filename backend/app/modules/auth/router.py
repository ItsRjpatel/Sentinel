import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.common.schemas import ErrorResponse, SuccessResponse
from app.core.exceptions import (
    AccountLockedError,
    AuthenticationError,
    InactiveUserError,
    InvalidTokenError,
    PermissionDeniedError,
)
from app.core.security import verify_refresh_token
from app.modules.auth.dependencies import (
    get_auth_service,
    get_current_user,
    require_permission,
)
from app.modules.auth.exceptions import (
    DuplicateEntryError,
    InvalidCredentialsError,
    NotFoundError,
    UnauthorizedError,
)
from app.modules.auth.models import User
from app.modules.auth.schemas import (
    ChangePasswordRequest,
    CreateRole,
    CreateUser,
    LoginRequest,
    LogoutRequest,
    PermissionResponse,
    RefreshRequest,
    RoleResponse,
    TokenPair,
    UpdateRole,
    UpdateUser,
    UserResponse,
)
from app.modules.auth.service import AuthenticationService

# Sub-routers for prefixing
router = APIRouter()
auth_router = APIRouter(prefix="/auth", tags=["auth"])
users_router = APIRouter(prefix="/users", tags=["users"])
roles_router = APIRouter(prefix="/roles", tags=["roles"])
perms_router = APIRouter(prefix="/permissions", tags=["permissions"])


def handle_service_error(e: Exception) -> JSONResponse:
    """Maps service exceptions to standard HTTP error responses."""
    status_code = 500
    error_code = "INTERNAL_ERROR"

    if isinstance(e, InvalidCredentialsError):
        status_code = 400
        error_code = "AUTH_INVALID_CREDENTIALS"
    elif isinstance(e, AccountLockedError):
        status_code = 401
        error_code = "AUTH_ACCOUNT_LOCKED"
    elif isinstance(e, InactiveUserError):
        status_code = 401
        error_code = "AUTH_INACTIVE_USER"
    elif isinstance(e, (InvalidTokenError, UnauthorizedError, AuthenticationError)):
        status_code = 401
        error_code = "UNAUTHORIZED"
    elif isinstance(e, PermissionDeniedError):
        status_code = 403
        error_code = "FORBIDDEN"
    elif isinstance(e, NotFoundError):
        status_code = 404
        error_code = "NOT_FOUND"
    elif isinstance(e, DuplicateEntryError):
        status_code = 409
        error_code = "CONFLICT"
    elif isinstance(e, ValueError):
        status_code = 400
        error_code = "VALIDATION_ERROR"

    error_resp = ErrorResponse(error_code=error_code, message=str(e), errors=[])
    return JSONResponse(
        status_code=status_code, content=error_resp.model_dump(mode="json")
    )


# ---------------------------------------------------------
# AUTH ENDPOINTS
# ---------------------------------------------------------
@auth_router.post("/login", response_model=SuccessResponse[TokenPair])
async def login(
    data: LoginRequest, service: AuthenticationService = Depends(get_auth_service)
):
    try:
        access_token, refresh_token = await service.login(data.username, data.password)
        return SuccessResponse(
            message="Login successful",
            data=TokenPair(access_token=access_token, refresh_token=refresh_token),
        )
    except Exception as e:
        return handle_service_error(e)


@auth_router.post("/refresh", response_model=SuccessResponse[TokenPair])
async def refresh(
    data: RefreshRequest, service: AuthenticationService = Depends(get_auth_service)
):
    try:
        # Verify the token natively and extract the real user_id
        payload = verify_refresh_token(data.refresh_token)
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise InvalidTokenError("Refresh token missing 'sub' claim")

        try:
            real_user_id = uuid.UUID(user_id_str)
        except ValueError:
            raise InvalidTokenError("Invalid 'sub' claim format")

        access_token, new_refresh = await service.refresh_session(
            real_user_id, data.refresh_token
        )
        return SuccessResponse(
            message="Session refreshed",
            data=TokenPair(access_token=access_token, refresh_token=new_refresh),
        )
    except Exception as e:
        return handle_service_error(e)


@auth_router.post("/logout", response_model=SuccessResponse[dict])
async def logout(
    data: LogoutRequest,
    current_user: User = Depends(get_current_user),
    service: AuthenticationService = Depends(get_auth_service),
):
    try:
        from app.core.security import get_password_hash

        token_hash = get_password_hash(data.refresh_token)
        await service.logout(current_user.id, token_hash)
        return SuccessResponse(message="Logout successful", data={})
    except Exception as e:
        return handle_service_error(e)


@auth_router.post("/change-password", response_model=SuccessResponse[dict])
async def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    service: AuthenticationService = Depends(get_auth_service),
):
    try:
        await service.change_password(
            current_user.id, data.old_password, data.new_password
        )
        return SuccessResponse(message="Password updated successfully", data={})
    except Exception as e:
        return handle_service_error(e)


@auth_router.get("/me", response_model=SuccessResponse[UserResponse])
async def get_me(
    current_user: User = Depends(get_current_user),
):
    try:
        return SuccessResponse(
            message="Profile retrieved", data=UserResponse.model_validate(current_user)
        )
    except Exception as e:
        return handle_service_error(e)


# ---------------------------------------------------------
# USERS ENDPOINTS
# ---------------------------------------------------------
@users_router.get("", response_model=SuccessResponse[list[UserResponse]])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_permission("users.read")),
    service: AuthenticationService = Depends(get_auth_service),
):
    try:
        users = await service.user_repo.list(skip=skip, limit=limit)
        return SuccessResponse(
            message="Users retrieved",
            data=[UserResponse.model_validate(u) for u in users],
        )
    except Exception as e:
        return handle_service_error(e)


@users_router.get("/{id}", response_model=SuccessResponse[UserResponse])
async def get_user(
    id: uuid.UUID,
    current_user: User = Depends(require_permission("users.read")),
    service: AuthenticationService = Depends(get_auth_service),
):
    try:
        user = await service.user_repo.get_by_id(id)
        if not user:
            raise NotFoundError("User not found")
        return SuccessResponse(
            message="User retrieved", data=UserResponse.model_validate(user)
        )
    except Exception as e:
        return handle_service_error(e)


@users_router.post("", response_model=SuccessResponse[UserResponse], status_code=201)
async def create_user(
    data: CreateUser,
    current_user: User = Depends(require_permission("users.create")),
    service: AuthenticationService = Depends(get_auth_service),
):
    try:
        user = await service.create_user(
            data.model_dump(exclude={"roles"}), assign_default_roles=data.roles
        )
        return SuccessResponse(
            message="User created successfully", data=UserResponse.model_validate(user)
        )
    except Exception as e:
        if isinstance(e, DuplicateEntryError):
            e = DuplicateEntryError("Username or email already exists")
        resp = handle_service_error(e)
        if resp.status_code == 200:
            resp.status_code = 201
        return resp


@users_router.patch("/{id}", response_model=SuccessResponse[UserResponse])
async def update_user(
    id: uuid.UUID,
    data: UpdateUser,
    current_user: User = Depends(require_permission("users.update")),
    service: AuthenticationService = Depends(get_auth_service),
):
    try:
        user = await service.user_repo.get_by_id(id)
        if not user:
            raise NotFoundError("User not found")
        updated_user = await service.user_repo.update(
            user, data.model_dump(exclude_unset=True)
        )
        await service.session.commit()
        return SuccessResponse(
            message="User updated", data=UserResponse.model_validate(updated_user)
        )
    except Exception as e:
        return handle_service_error(e)


@users_router.delete("/{id}", status_code=204)
async def delete_user(
    id: uuid.UUID,
    current_user: User = Depends(require_permission("users.delete")),
    service: AuthenticationService = Depends(get_auth_service),
):
    try:
        user = await service.user_repo.get_by_id(id)
        if not user:
            raise NotFoundError("User not found")
        # Soft delete logic
        await service.user_repo.update(user, {"is_active": False})
        await service.session.commit()
        return JSONResponse(status_code=204, content=None)
    except Exception as e:
        return handle_service_error(e)


# ---------------------------------------------------------
# ROLES ENDPOINTS
# ---------------------------------------------------------
@roles_router.get("", response_model=SuccessResponse[list[RoleResponse]])
async def list_roles(
    current_user: User = Depends(require_permission("roles.read")),
    service: AuthenticationService = Depends(get_auth_service),
):
    try:
        roles = await service.role_repo.list()
        return SuccessResponse(
            message="Roles retrieved",
            data=[RoleResponse.model_validate(r) for r in roles],
        )
    except Exception as e:
        return handle_service_error(e)


@roles_router.post("", response_model=SuccessResponse[RoleResponse], status_code=201)
async def create_role(
    data: CreateRole,
    current_user: User = Depends(require_permission("roles.create")),
    service: AuthenticationService = Depends(get_auth_service),
):
    try:
        role = await service.role_repo.create(data.model_dump())
        await service.session.commit()
        return SuccessResponse(
            message="Role created", data=RoleResponse.model_validate(role)
        )
    except Exception as e:
        return handle_service_error(e)


@roles_router.patch("/{id}", response_model=SuccessResponse[RoleResponse])
async def update_role(
    id: uuid.UUID,
    data: UpdateRole,
    current_user: User = Depends(require_permission("roles.update")),
    service: AuthenticationService = Depends(get_auth_service),
):
    try:
        role = await service.role_repo.get_by_id(id)
        if not role:
            raise NotFoundError("Role not found")
        updated_role = await service.role_repo.update(
            role, data.model_dump(exclude_unset=True)
        )
        await service.session.commit()
        return SuccessResponse(
            message="Role updated", data=RoleResponse.model_validate(updated_role)
        )
    except Exception as e:
        return handle_service_error(e)


@roles_router.delete("/{id}", status_code=204)
async def delete_role(
    id: uuid.UUID,
    current_user: User = Depends(require_permission("roles.delete")),
    service: AuthenticationService = Depends(get_auth_service),
):
    try:
        role = await service.role_repo.get_by_id(id)
        if not role:
            raise NotFoundError("Role not found")
        if role.name in ["admin", "user"]:
            raise ValueError("Cannot delete default roles")
        await service.role_repo.delete(role)
        await service.session.commit()
        return JSONResponse(status_code=204, content=None)
    except Exception as e:
        return handle_service_error(e)


# ---------------------------------------------------------
# PERMISSIONS ENDPOINTS
# ---------------------------------------------------------
@perms_router.get("", response_model=SuccessResponse[list[PermissionResponse]])
async def list_permissions(
    current_user: User = Depends(require_permission("permissions.read")),
    service: AuthenticationService = Depends(get_auth_service),
):
    try:
        perms = await service.permission_repo.list()
        return SuccessResponse(
            message="Permissions retrieved",
            data=[PermissionResponse.model_validate(p) for p in perms],
        )
    except Exception as e:
        return handle_service_error(e)


router.include_router(auth_router)
router.include_router(users_router)
router.include_router(roles_router)
router.include_router(perms_router)
