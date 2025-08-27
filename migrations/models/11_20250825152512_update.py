from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `bookmark_custom` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `header` LONGTEXT   COMMENT '页眉',
    `footer` LONGTEXT   COMMENT '页脚',
    `note` LONGTEXT   COMMENT '备注',
    `project_name` VARCHAR(255)   COMMENT '动态项目名称',
    `template_doc_id` INT NOT NULL COMMENT '关联的模板基础ID'
) CHARACTER SET utf8mb4;
        DROP TABLE IF EXISTS `bookmark_custom`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `bookmark_custom`;"""
