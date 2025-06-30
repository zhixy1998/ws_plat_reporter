from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_doc` ADD `base_template_id` INT;
        ALTER TABLE `template_doc` ADD `is_del` SMALLINT NOT NULL DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_doc` DROP COLUMN `base_template_id`;
        ALTER TABLE `template_doc` DROP COLUMN `is_del`;"""
