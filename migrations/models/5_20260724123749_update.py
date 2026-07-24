from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_doc` MODIFY COLUMN `template_content` LONGBLOB NOT NULL;
        ALTER TABLE `template_doc_base` MODIFY COLUMN `template_content` LONGBLOB NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_doc` MODIFY COLUMN `template_content` LONGTEXT NOT NULL;
        ALTER TABLE `template_doc_base` MODIFY COLUMN `template_content` LONGTEXT NOT NULL;"""
