import asyncio
from sqlalchemy import text
from app.db.session import async_session_maker
from app.modules.auth.repository import UserRepository, RoleRepository, PermissionRepository, RefreshTokenRepository
from app.modules.auth.service import AuthenticationService

async def main():
    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        role_repo = RoleRepository(session)
        permission_repo = PermissionRepository(session)
        refresh_repo = RefreshTokenRepository(session)
        auth_service = AuthenticationService(session, user_repo, role_repo, permission_repo, refresh_repo)
        
        user = await user_repo.get_by_username('admin')
        if user:
            print('Found admin user.')
            token = await auth_service.create_refresh_token(user.id)
            print('Created token:', token)
            await session.commit()
            
            result = await session.execute(text('SELECT COUNT(*) FROM refresh_tokens'))
            count = result.scalar()
            print('Refresh tokens count:', count)

asyncio.run(main())
