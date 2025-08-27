from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `bookmark_custom` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `note` LONGTEXT   COMMENT '备注',
    `project_name` VARCHAR(255)   COMMENT '项目名称',
    `template_doc_base_id` INT NOT NULL COMMENT '关联的模板基础ID'
) CHARACTER SET utf8mb4;
        ALTER TABLE `template_doc` DROP COLUMN `project_name`;
        ALTER TABLE `template_doc` DROP COLUMN `note`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_doc` ADD `project_name` VARCHAR(255)  COMMENT '项目名称';
        ALTER TABLE `template_doc` ADD `note` LONGTEXT  COMMENT '备注';
        DROP TABLE IF EXISTS `bookmark_custom`;"""
