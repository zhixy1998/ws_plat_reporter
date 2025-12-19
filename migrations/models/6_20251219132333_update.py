from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_doc` ADD `origin_type` SMALLINT NOT NULL DEFAULT 0;
        ALTER TABLE `template_doc_base` ADD `origin_type` SMALLINT NOT NULL DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_doc` DROP COLUMN `origin_type`;
        ALTER TABLE `template_doc_base` DROP COLUMN `origin_type`;"""
