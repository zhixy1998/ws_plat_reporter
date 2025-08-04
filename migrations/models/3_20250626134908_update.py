from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_bookmark` ADD `content` LONGTEXT;
        ALTER TABLE `template_bookmark` ADD `is_del` SMALLINT NOT NULL DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_bookmark` DROP COLUMN `content`;
        ALTER TABLE `template_bookmark` DROP COLUMN `is_del`;"""
