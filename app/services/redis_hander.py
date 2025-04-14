import logging
from typing import List

from redis import RedisError
from redis.commands.json.path import Path
from redis.asyncio import Redis as AsyncRedis

from app.internal.settings import settings
from app.models.models import Recipe


class RedisHandler:
    def __init__(self, database: int = 0):
        self.redis_instance = AsyncRedis.from_url(
            f"{settings.REDIS_URL}/{database}",
            decode_responses=True,
            max_connections=30,
            health_check_interval=30,
        )
        self.logger = logging.getLogger(__name__)

    async def add_recipes(self, user: str, value: Recipe) -> None:
        """Set a Recipe in Redis.

        Args:
            key (str): The user to set the Recipe for.
            value (Recipe): The Recipe to set.
        """
        try:
            # Check if user exists
            exists = await self.redis_instance.exists(user)
            if not exists:
                await self.redis_instance.json().set(user, Path.root_path(), {})

            await self.redis_instance.json().set(user, Path(f".{value['id']}"), value)
            self.logger.info(
                f"Set Recipe in Redis: user={user}, recipe_id={value['id']}"
            )
        except Exception as redis_error:
            self.logger.error(f"Failed to set Recipes in Redis: {redis_error}")

    async def get_recipes(self, user: str, path: str = ".") -> List[Recipe]:
        """Get a Recipe from Redis.

        Args:
            user (str): The user to get the Recipe for.
            path (str, optional): The JSON path to retrieve. Defaults to ".":
        Returns:
            List[Recipe]: The Recipes retrieved from Redis.
        """
        try:
            recipes = await self.redis_instance.json().get(user, Path(path))
            all_recipes = []
            for id in recipes.keys():
                recipes[id]["id"] = id
                all_recipes.append(recipes[id])
            self.logger.info(f"Retrieved Recipes from Redis: user={user}")
            return all_recipes
        except Exception as redis_error:
            self.logger.error(f"Failed to get Recipes from Redis: {redis_error}")
            return []

    async def delete_recipe(self, user: str, id: str) -> None:
        """Delete a Recipe from Redis.

        Args:
            user (str): The user to delete the Recipe for.
            id (str): The ID of the Recipe to delete.
        """
        try:
            await self.redis_instance.json().delete(user, Path(f".{id}"))
            self.logger.info(f"Deleted Recipe from Redis: user={user}, id={id}")
        except Exception as redis_error:
            self.logger.error(f"Failed to delete Recipe from Redis: {redis_error}")

    async def set_user_password(self, user: str, hashed_password: str) -> None:
        """Set a user's password in Redis.

        Args:
            user (str): The user to set the password for.
            hashed_password (str): The hashed password to set.
        """
        try:
            await self.redis_instance.set(f"{user}_password", hashed_password)
        except Exception as redis_error:
            self.logger.error(f"Failed to add user to Redis: {redis_error}")

    async def check_user(self, user: str) -> bool:
        """Check if a user exists in Redis.

        Args:
            user (str): The user to check.

        Returns:
            bool: True if the user exists, False otherwise.
        """
        try:
            return await self.redis_instance.exists(f"{user}_password") == 1
        except Exception as redis_error:
            self.logger.error(f"Failed to check user in Redis: {redis_error}")
            return False

    async def get_user_password(self, user: str) -> str:
        """Get a user's password from Redis.

        Args:
            user (str): The user to get the password for.

        Returns:
            str: The hashed password.
        """
        try:
            return await self.redis_instance.get(f"{user}_password")
        except Exception as redis_error:
            self.logger.error(f"Failed to get user from Redis: {redis_error}")
            return ""

    async def close(self) -> None:
        """Close the Redis connection."""
        try:
            await self.redis_instance.close()
            self.logger.info("Redis connection closed successfully.")
        except RedisError as redis_error:
            self.logger.error(f"Failed to close Redis connection: {redis_error}")
