from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_extra_info` MODIFY COLUMN `template_doc_id` INT NOT NULL COMMENT '关联的模板id';
        ALTER TABLE `template_doc` ADD `thumbnail_base64` LONGTEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_doc` DROP COLUMN `thumbnail_base64`;
        ALTER TABLE `template_extra_info` MODIFY COLUMN `template_doc_id` INT NOT NULL COMMENT '关联的模板基础ID';"""
