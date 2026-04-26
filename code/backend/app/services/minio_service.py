import io
from minio import Minio
from minio.error import S3Error
from app.config import get_settings

settings = get_settings()


class MinioService:
    """MinIO 文件存储服务"""

    def __init__(self):
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False
        )
        self.bucket = settings.minio_bucket

    def ensure_bucket(self):
        """确保 bucket 存在"""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except S3Error as e:
            raise Exception(f"创建 bucket 失败: {str(e)}")

    def upload_file(self, file_data: bytes, file_name: str, content_type: str, user_id: str) -> str:
        """
        上传文件到 MinIO

        Args:
            file_data: 文件数据
            file_name: 原始文件名
            content_type: MIME 类型
            user_id: 用户ID

        Returns:
            str: 文件存储路径
        """
        self.ensure_bucket()

        # 生成存储路径: {user_id}/{uuid}.{ext}
        import uuid
        ext = file_name.split(".")[-1] if "." in file_name else ""
        object_name = f"{user_id}/{uuid.uuid4()}.{ext}"

        try:
            file_stream = io.BytesIO(file_data)
            self.client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=file_stream,
                length=len(file_data),
                content_type=content_type
            )
            return object_name
        except S3Error as e:
            raise Exception(f"文件上传失败: {str(e)}")

    def get_file_url(self, object_name: str, expires_hours: int = 24) -> str:
        """获取文件访问 URL"""
        try:
            url = self.client.presigned_get_object(
                bucket_name=self.bucket,
                object_name=object_name,
                expires=expires_hours * 3600
            )
            return url
        except S3Error as e:
            raise Exception(f"获取文件 URL 失败: {str(e)}")

    def delete_file(self, object_name: str):
        """删除文件"""
        try:
            self.client.remove_object(
                bucket_name=self.bucket,
                object_name=object_name
            )
        except S3Error as e:
            raise Exception(f"删除文件失败: {str(e)}")

    def download_file(self, object_name: str) -> bytes:
        """下载文件"""
        try:
            response = self.client.get_object(
                bucket_name=self.bucket,
                object_name=object_name
            )
            return response.read()
        except S3Error as e:
            raise Exception(f"下载文件失败: {str(e)}")

    def list_files(self) -> set:
        """列出 bucket 中所有文件路径"""
        try:
            self.ensure_bucket()
            files = set()
            for obj in self.client.list_objects(self.bucket, recursive=True):
                files.add(obj.object_name)
            return files
        except S3Error as e:
            raise Exception(f"列出文件失败: {str(e)}")


minio_service = MinioService()
