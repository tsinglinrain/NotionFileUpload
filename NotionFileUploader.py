import json
import requests
import os
from typing import Optional
from dotenv import load_dotenv

# 仅本地开发时加载 .env 文件（Docker 环境会跳过）
if os.getenv("ENV") != "production":
    load_dotenv()  # 默认加载 .env 文件

class NotionFileUploader:
    """
    Notion API文件上传器，用于上传小于20MB的文件到Notion
    """
    
    def __init__(self, notion_token: str):
        """
        初始化上传器
        
        Args:
            notion_token: Notion API token (Bearer token)
            notion_version: Notion API版本
        """
        self.notion_token = notion_token
        self.notion_version = "2022-06-28"
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Notion-Version": self.notion_version
        }
    
    def create_file_upload_object(self, filename: Optional[str] = None, 
                                 content_type: Optional[str] = None) -> dict:
        """
        步骤1: 创建文件上传对象
        
        Args:
            filename: 文件名（可选）
            content_type: 文件MIME类型（可选）
            
        Returns:
            包含file_upload信息的字典，包括id和upload_url
        """
        url = f"{self.base_url}/file_uploads"
        
        payload = {}
        if filename:
            payload["filename"] = filename
        if content_type:
            payload["content_type"] = content_type
        
        headers = self.headers.copy()
        headers["Content-Type"] = "application/json"
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise Exception(
                f"File upload object creation failed with status code {response.status_code}: {response.text}"
            )
        
        return response.json()
    
    def upload_file_content(self, file_upload_id: str, file_path: str) -> dict:
        """
        步骤2: 上传文件内容
        
        Args:
            file_upload_id: 从步骤1获得的文件上传ID
            file_path: 本地文件路径
            
        Returns:
            上传后的文件信息
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # 检查文件大小（20MB限制）
        file_size = os.path.getsize(file_path)
        if file_size > 20 * 1024 * 1024:  # 20MB
            raise ValueError("File size exceeds 20MB limit for small file upload")
        
        url = f"{self.base_url}/file_uploads/{file_upload_id}/send"
        
        filename = os.path.basename(file_path)
        
        # 猜测MIME类型
        content_type = self._guess_content_type(file_path)
        
        headers = {
            "Authorization": f"Bearer {self.notion_token}",
            "Notion-Version": self.notion_version
        }
        
        with open(file_path, "rb") as f:
            files = {
                "file": (filename, f, content_type)
            }
            
            response = requests.post(url, headers=headers, files=files)
        
        if response.status_code != 200:
            raise Exception(
                f"File upload failed with status code {response.status_code}: {response.text}"
            )
        
        return response.json()
    
    def upload_file(self, file_path: str, filename: Optional[str] = None) -> str:
        """
        完整的文件上传流程（步骤1+2）
        
        Args:
            file_path: 本地文件路径
            filename: 自定义文件名（可选，默认使用文件路径中的文件名）
            
        Returns:
            file_upload_id: 可用于附加到Notion页面/块的文件ID
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # 如果没有提供filename，从路径中提取
        if not filename:
            filename = os.path.basename(file_path)
        
        # 猜测内容类型
        content_type = self._guess_content_type(file_path)
        
        print(f"正在创建文件上传对象: {filename}")
        
        # 步骤1: 创建文件上传对象
        file_upload_obj = self.create_file_upload_object(filename, content_type)
        file_upload_id = file_upload_obj['id']
        
        print(f"文件上传对象已创建，ID: {file_upload_id}")
        print(f"状态: {file_upload_obj['status']}")
        print(f"过期时间: {file_upload_obj['expiry_time']}")
        
        # 步骤2: 上传文件内容
        print("正在上传文件内容...")
        upload_result = self.upload_file_content(file_upload_id, file_path)
        
        print(f"文件上传完成！")
        print(f"最终状态: {upload_result['status']}")
        print(f"文件名: {upload_result['filename']}")
        print(f"内容类型: {upload_result['content_type']}")
        print(f"文件大小: {upload_result['content_length']} bytes")
        
        return file_upload_id
    
    @staticmethod
    def _guess_content_type(file_path: str) -> str:
        """
        根据文件扩展名猜测MIME类型
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        mime_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.mp4': 'video/mp4',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.zip': 'application/zip',
        }
        
        return mime_types.get(ext, 'application/octet-stream')

def notion_para_get():
    '''获取Notion数据库ID和Token'''
    database_id = os.getenv("NOTION_DATABASE_ID")
    token = os.getenv("NOTION_TOKEN")
    return database_id, token


# 使用示例
if __name__ == "__main__":
    # 使用示例
    database_id, token = notion_para_get()
    print(f"Notion Database ID: {database_id}")

    uploader = NotionFileUploader(token)
    
    try:
        # 上传文件并获取file_upload_id
        file_upload_id = uploader.upload_file("wuhouguozhi.png")
        print(f"\n✅ 上传成功！File Upload ID: {file_upload_id}")
        print("现在你可以使用这个ID将文件附加到Notion页面或块中")
        
    except Exception as e:
        print(f"❌ 上传失败: {e}")