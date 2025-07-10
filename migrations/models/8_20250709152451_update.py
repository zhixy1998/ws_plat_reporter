from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_doc_base` ADD `industry_type` VARCHAR(255);
        ALTER TABLE `template_doc_base` MODIFY COLUMN `type` SMALLINT NOT NULL DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_doc_base` DROP COLUMN `industry_type`;
        ALTER TABLE `template_doc_base` MODIFY COLUMN `type` INT NOT NULL DEFAULT 0;"""
