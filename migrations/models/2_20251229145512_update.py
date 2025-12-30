from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_extra_info` ADD `page_num` INT NOT NULL COMMENT '页码 0:不展示页码 1: 左边展示 2: 居中展示 3: 右边展示' DEFAULT 0;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `template_extra_info` DROP COLUMN `page_num`;"""
