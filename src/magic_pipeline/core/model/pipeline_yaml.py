from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

@dataclass
class ProjectInfo:
    """项目信息"""
    name: str
    code: str
    type: str
    description: str
    version: str
    language: str
    work_path: str

@dataclass
class ModelConfig:
    """模型配置"""
    provider: str
    name: str
    temperature: float
    max_tokens: int
    
    def __post_init__(self):
        if not 0 <= self.temperature <= 1:
            raise ValueError(f"temperature {self.temperature} 必须在0-1之间")
        if self.max_tokens <= 0:
            raise ValueError(f"max_tokens {self.max_tokens} 必须大于0")

@dataclass
class ProviderConfig:
    """服务提供商配置"""
    type: str
    url: str
    port: int

@dataclass
class PipelineConfig:
    """pipeline.yaml 配置"""
    project: ProjectInfo
    models: Dict[str, ModelConfig]
    provider: Dict[str, ProviderConfig]
    pipeline: List[dict]  # 保持灵活，因为结构动态