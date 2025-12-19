from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `bookmark_data` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `bookmark_id` INT NOT NULL,
    `value` VARCHAR(255),
    `structure_type` SMALLINT NOT NULL  DEFAULT 0,
    `table_structure` JSON,
    `create_datetime` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `update_datetime` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_del` SMALLINT NOT NULL  DEFAULT 0,
    KEY `idx_bookmark_da_bookmar_064989` (`bookmark_id`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `template_bookmark` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `parent_id` INT,
    `template_doc_id` INT NOT NULL,
    `name` VARCHAR(255) NOT NULL,
    `type` INT NOT NULL  DEFAULT 0,
    `description` LONGTEXT,
    `sort_order` INT   DEFAULT 0,
    `font` VARCHAR(255),
    `font_size` INT,
    `img_size` DOUBLE,
    `create_datetime` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `update_datetime` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `is_del` SMALLINT NOT NULL  DEFAULT 0,
    KEY `idx_template_bo_templat_c740a8` (`template_doc_id`),
    KEY `idx_template_bo_parent__b0d5b4` (`parent_id`),
    KEY `idx_template_bo_name_f0e5dd` (`name`)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `template_doc` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `type` SMALLINT NOT NULL  DEFAULT 0,
    `industry_type` VARCHAR(255),
    `experiment_type` SMALLINT NOT NULL  DEFAULT 0,
    `origin_type` SMALLINT NOT NULL  DEFAULT 0,
    `create_datetime` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `update_datetime` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `template_content` LONGTEXT NOT NULL,
    `is_del` SMALLINT NOT NULL  DEFAULT 0,
    `thumbnail_base64` LONGTEXT,
    `base_template_id` INT,
    `order` INT
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `template_doc_base` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `type` SMALLINT NOT NULL  DEFAULT 0,
    `industry_type` VARCHAR(255),
    `experiment_type` SMALLINT NOT NULL  DEFAULT 0,
    `origin_type` SMALLINT NOT NULL  DEFAULT 0,
    `create_datetime` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `update_datetime` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `template_content` LONGTEXT NOT NULL,
    `is_del` SMALLINT NOT NULL  DEFAULT 0
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `template_extra_info` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `header` LONGTEXT   COMMENT '页眉',
    `footer` LONGTEXT   COMMENT '页脚',
    `note` LONGTEXT   COMMENT '备注',
    `project_name` VARCHAR(255)   COMMENT '动态项目名称',
    `title` LONGTEXT   COMMENT '标题',
    `subtitle` LONGTEXT   COMMENT '副标题',
    `template_doc_id` INT NOT NULL  COMMENT '关联的模板id'
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
