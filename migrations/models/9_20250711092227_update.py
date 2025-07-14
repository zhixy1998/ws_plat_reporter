from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `bookmark_data` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `bookmark_id` INT NOT NULL,
    `value` VARCHAR(255),
    `structure_type` SMALLINT NOT NULL DEFAULT 0,
    `table_structure` JSON,
    `create_datetime` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    `update_datetime` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_del` SMALLINT NOT NULL DEFAULT 0,
    KEY `idx_bookmark_da_bookmar_064989` (`bookmark_id`)
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `bookmark_data`;"""
