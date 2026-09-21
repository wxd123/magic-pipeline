
# pipeline_config.py
from dataclasses import dataclass
from magic_base import BaseDataClass

@dataclass
class ProjectInfo(BaseDataClass):
    """项目信息"""
    name: str
    code: str
    type: str
    description: str = ""
    version: str = "1.0.0"
    language: str = "java"
    work_path: str = ""


@dataclass
class ProviderConfig:
    """服务提供商配置"""
    type: str
    url: str
    port: int