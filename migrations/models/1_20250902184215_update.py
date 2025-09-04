from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `bookmark_custom` ADD `subtitle` LONGTEXT  COMMENT '副标题';
        ALTER TABLE `bookmark_custom` ADD `title` LONGTEXT  COMMENT '标题';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `bookmark_custom` DROP COLUMN `subtitle`;
        ALTER TABLE `bookmark_custom` DROP COLUMN `title`;"""
