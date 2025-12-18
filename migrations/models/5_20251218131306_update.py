from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_doc` ADD `order` INT;
        ALTER TABLE `template_extra_info` ADD `header` LONGTEXT  COMMENT '页眉';
        ALTER TABLE `template_extra_info` ADD `title` LONGTEXT  COMMENT '标题';
        ALTER TABLE `template_extra_info` ADD `note` LONGTEXT  COMMENT '备注';
        ALTER TABLE `template_extra_info` ADD `footer` LONGTEXT  COMMENT '页脚';
        ALTER TABLE `template_extra_info` ADD `project_name` VARCHAR(255)  COMMENT '动态项目名称';
        ALTER TABLE `template_extra_info` ADD `subtitle` LONGTEXT  COMMENT '副标题';
        ALTER TABLE `template_extra_info` DROP COLUMN `bookmark_data_id`;
        ALTER TABLE `template_extra_info` DROP COLUMN `has_tr`;
        ALTER TABLE `template_extra_info` DROP COLUMN `update_datetime`;
        ALTER TABLE `template_extra_info` DROP COLUMN `create_datetime`;
        ALTER TABLE `template_extra_info` MODIFY COLUMN `template_doc_id` INT NOT NULL COMMENT '关联的模板id';
        DROP TABLE IF EXISTS `bookmark_custom`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_doc` DROP COLUMN `order`;
        ALTER TABLE `template_extra_info` ADD `bookmark_data_id` INT NOT NULL;
        ALTER TABLE `template_extra_info` ADD `has_tr` SMALLINT NOT NULL DEFAULT 0;
        ALTER TABLE `template_extra_info` ADD `update_datetime` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);
        ALTER TABLE `template_extra_info` ADD `create_datetime` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6);
        ALTER TABLE `template_extra_info` DROP COLUMN `header`;
        ALTER TABLE `template_extra_info` DROP COLUMN `title`;
        ALTER TABLE `template_extra_info` DROP COLUMN `note`;
        ALTER TABLE `template_extra_info` DROP COLUMN `footer`;
        ALTER TABLE `template_extra_info` DROP COLUMN `project_name`;
        ALTER TABLE `template_extra_info` DROP COLUMN `subtitle`;
        ALTER TABLE `template_extra_info` MODIFY COLUMN `template_doc_id` INT NOT NULL;"""
