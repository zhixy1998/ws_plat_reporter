from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_bookmark` ADD `img_size` DOUBLE;
        ALTER TABLE `template_bookmark` ADD `font_size` INT;
        ALTER TABLE `template_bookmark` ADD `font` VARCHAR(255);
        ALTER TABLE `template_bookmark` ADD `update_datetime` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6);
        ALTER TABLE `template_bookmark` ADD `create_datetime` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_bookmark` DROP COLUMN `img_size`;
        ALTER TABLE `template_bookmark` DROP COLUMN `font_size`;
        ALTER TABLE `template_bookmark` DROP COLUMN `font`;
        ALTER TABLE `template_bookmark` DROP COLUMN `update_datetime`;
        ALTER TABLE `template_bookmark` DROP COLUMN `create_datetime`;"""
