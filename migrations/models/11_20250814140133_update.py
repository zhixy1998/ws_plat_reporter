from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `template_extra_info` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `template_doc_id` INT NOT NULL,
    `has_tr` SMALLINT NOT NULL DEFAULT 0,
    `create_datetime` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `update_datetime` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `template_extra_info`;"""
