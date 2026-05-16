
# magic_pipeline/core/model/loops.py
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Union
from abc import ABC, abstractmethod
from .commands import CommandConfig


@dataclass
class LoopConfig:
    """循环配置 - 代表一个循环执行块"""
    id: str                                             # 循环ID，唯一标识一个循环块
    models: List[str]                                   # 要循环使用的模型ID列表
    steps: List[Union[CommandConfig, 'LoopConfig']]     # 循环内的步骤（可以是命令或嵌套循环）
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LoopConfig":
        """从字典创建循环配置"""
        # 获取模型列表
        models = data.get("models", [])
        if not models:
            raise KeyError("循环配置缺少必需字段: models")
        
        # 解析步骤（跳过 models 字段）
        steps = []
        for key, value in data.items():
            if key == "models":
                continue
            
            if key == "command":
                # 单个命令
                command_data = {"command": value}
                # 添加其他字段
                for k, v in data.items():
                    if k not in ["models", "command"]:
                        command_data[k] = v
                steps.append(CommandConfig.from_dict(command_data))
                break
            else:
                # 处理步骤列表的情况
                if isinstance(value, list):
                    for step_data in value:
                        if "command" in step_data:
                            steps.append(CommandConfig.from_dict(step_data))
                        elif "loop" in step_data:
                            steps.append(LoopConfig.from_dict(step_data["loop"]))
                break
        
        return cls(models=models, steps=steps)