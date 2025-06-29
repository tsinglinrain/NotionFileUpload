import requests
from notion_client import Client
from dotenv import load_dotenv
import os
import re
from typing import Dict, List, Any
import logging
from pprint import pprint
import json

from logger_config import setup_logger

from NotionFileUploader import NotionFileUploader

# 仅本地开发时加载 .env 文件（Docker 环境会跳过）
if os.getenv("ENV") != "production":
    load_dotenv()  # 默认加载 .env 文件

setup_logger()  # 初始化 logging 配置
logger = logging.getLogger(__name__)

class NotionClientCus:
    def __init__(self, database_id, base_page_id, token):
        self.database_id = database_id
        self.base_page_id = base_page_id
        self.token = token
        self.client: Client = Client(auth=token)

    def create_page(self, properties):
        """Create a new page in the database"""

        try:
            self.client.pages.create(
                icon={"type": "emoji", "emoji": "🎧"},  # 非常贴合,堪称完美图标
                # cover # 也没有需求
                parent={"database_id": self.database_id},
                properties=properties,
                # children=blocks,  # 不要children
            )
            logging.info("Page created successfully\n上传成功")
            print("Page created successfully\n上传成功")
        except Exception as e:
            logging.error(
                f"Failed to create page: {e}\n创建页面失败,自动跳过,请自行检查"
            )
            print(f"Failed to create page: {e}\n创建页面失败,自动跳过,请自行检查")

    def cre_in_database_paper(
        self,
        name,
        id,
    ):
        """Create a new page in the database"""
        properties = {
            "Name": {"title": [{"text": {"content": name}}]},
            # "Files":{
            #     "files": [
            #         {
            #             "name": file["name"],
            #             "type": "file_upload",
            #             "file_upload": {id: file["id"]}
            #         } for file in filesfiles
            #     ]
            # },
            "Files": {
                "type": "files",
                "files": [
                    {
                        "type": "file_upload",
                        "file_upload": {
                            "id": id
                        },
                    },
                ]
            }
        }
        self.create_page(properties)

    def create_database(self, 
                        emoji = "🍰", 
                        title: str = "New Database", 
                        properties: Dict[str, Any]= 
                        {
                            "Name": {"title": {}},
                            "Files": {
                                "type": "files",
                                "files": {}
                            },
                        }) -> str:
        """创建一个新的数据库"""
        try:
            response = self.client.databases.create(
                parent={"type": "page_id", "page_id": self.base_page_id},
                icon={"type": "emoji", "emoji": emoji},
                title=[{"type": "text", "text": {"content": title}}],
                properties=properties
            )
            return response["id"]
        except Exception as e:
            logging.error(f"Failed to create database: {e}")
            raise

def notion_para_get():

    database_id = os.getenv("NOTION_DATABASE_ID")
    base_page_id = os.getenv("NOTION_BASE_PAGE_ID")
    token = os.getenv("NOTION_TOKEN")
    return database_id, base_page_id, token

def main():
    # 使用示例
    database_id, token = notion_para_get()
    print(f"Notion Database ID: {database_id}")

    uploader = NotionFileUploader(token)
    
    # file_path = "shiguanghuikui.png"
    file_path = "冰刃鸢尾.png"
    file_name = file_path.split(".")[-1]  # 获取文件名
    try:
        # 上传文件并获取file_upload_id
        file_upload_id = uploader.upload_file(file_path=file_path)
        print(f"\n✅ 上传成功！File Upload ID: {file_upload_id}")
        print("现在你可以使用这个ID将文件附加到Notion页面或块中")
        
    except Exception as e:
        print(f"❌ 上传失败: {e}")
    
    notionclient = NotionClientCus(database_id, token)

    try:
        # 上传文件并获取file_upload_id
        # file_upload_id = "20599f72-bada-8105-8a4f-00b2c8bbba25"
        notionclient.cre_in_database_paper(file_name, file_upload_id)

    except Exception as e:
        print(f"上传失败: {e}")

def database_create_test():
    database_id, base_page_id, token = notion_para_get()
    print(f"Notion Database ID: {database_id}")
    print(f"Notion Base Page ID: {base_page_id}")


    notionclient = NotionClientCus(database_id, base_page_id, token)

    properties = {
        "Name": {"title": {}},
        "Files": {
            "type": "files",
            "files": {}
        }
    }

    try:
        new_database_id = notionclient.create_database(
            title="New Database",
            properties=properties
        )
        print(f"New database created with ID: {new_database_id}")
    except Exception as e:
        print(f"Failed to create database: {e}")

if __name__ == "__main__":
    # main()
    database_create_test()


    