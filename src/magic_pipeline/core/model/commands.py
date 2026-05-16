
# magic_pipeline/core/model/commands.py
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from abc import ABC, abstractmethod

@dataclass
class CommandConfig:
    """命令配置 - 代表一个具体的命令执行"""
    
    command: str                        # 命令名称，如 "java:clean", "java:generate"
    model: Optional[str] = None        # 可选的模型名称，适用于需要模型支持的命令
    source_dir: Optional[str] = None    # 源目录
    output_dir: Optional[str] = None    # 输出目录
    params: Dict[str, Any] = field(default_factory=dict)  # 额外参数
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CommandConfig":
        """从字典创建命令配置"""
        # 提取已知字段
        command = data.get("command")
        if not command:
            raise KeyError("命令配置缺少必需字段: command")
        
        source_dir = data.get("source_dir")
        output_dir = data.get("output_dir")
        
        # 剩余字段作为额外参数
        params = {k: v for k, v in data.items() 
                 if k not in ["command", "source_dir", "output_dir"]}
        
        return cls(
            command=command,
            source_dir=source_dir,
            output_dir=output_dir,
            params=params
        )