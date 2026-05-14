# base_provider.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseProvider(ABC):
    """Provider 抽象基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider 名称（ollama, openai, anthropic）"""
        pass
    
    @abstractmethod
    def start(self) -> bool:
        """启动 Provider 服务"""
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """停止 Provider 服务"""
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """检查 Provider 是否运行中"""
        pass
    
    @abstractmethod
    def has_model(self, model_name: str) -> bool:
        """检查模型是否存在"""
        pass
    
    @abstractmethod
    def pull_model(self, model_name: str) -> bool:
        """拉取/下载模型"""
        pass
    
    @abstractmethod
    def is_model_ready(self, model_name: str) -> bool:
        """检查模型是否准备好"""
        pass
    
    @abstractmethod
    def generate(self, model_name: str, prompt: str, **kwargs) -> str:
        """生成响应"""
        pass

   