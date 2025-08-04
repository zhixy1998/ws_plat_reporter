from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `template_bookmark` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `parent_id` INT,
    `template_doc_id` INT NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `type` INT NOT NULL  DEFAULT 0,
    `description` LONGTEXT,
    `sort_order` INT   DEFAULT 0,
    KEY `idx_template_bo_templat_c740a8` (`template_doc_id`),
    KEY `idx_template_bo_parent__b0d5b4` (`parent_id`),
    KEY `idx_template_bo_name_f0e5dd` (`name`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `template_doc` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `create_datetime` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `update_datetime` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `template_content` LONGTEXT NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
