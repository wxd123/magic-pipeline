# magic_pipeline/core/model/models.py
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

@dataclass
class ModelConfig:
    """直接映射配置文件结构"""
    
    id: str
    provider: str
    name: str
    precision: Optional[str] = "fp16"
    temperature: float = 0.7
    max_tokens: int = 512
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelConfig":
        """
        从字典创建 ModelConfig 实例
        
        提供默认值处理，确保缺失字段使用类定义的默认值。
        
        Args:
            data: 包含模型配置的字典，至少需要包含 id, provider, name 字段
            
        Returns:
            ModelConfig 实例
            
        Raises:
            KeyError: 当字典缺少必需的字段（id, provider, name）时抛出
            
        Example:
            >>> config_dict = {"id": "gpt-4", "provider": "openai", "name": "GPT-4"}
            >>> model = ModelConfig.from_dict(config_dict)
        """
        # 检查必需字段
        required_fields = ["id", "provider", "name"]
        for field in required_fields:
            if field not in data:
                raise KeyError(f"缺少必需字段: {field}")
        
        # 创建实例，使用 data 中的值或类的默认值
        return cls(
            id=data["id"],
            provider=data["provider"],
            name=data["name"],
            precision=data.get("precision", cls.precision),
            temperature=data.get("temperature", cls.temperature),
            max_tokens=data.get("max_tokens", cls.max_tokens)
        )
    
    @classmethod
    def from_dict_list(cls, data_list: List[Dict[str, Any]]) -> List["ModelConfig"]:
        """
        从字典列表批量创建 ModelConfig 实例
        
        Args:
            data_list: 字典列表，每个字典代表一个模型配置
            
        Returns:
            ModelConfig 实例列表
            
        Example:
            >>> configs = [{"id": "model1", ...}, {"id": "model2", ...}]
            >>> models = ModelConfig.from_dict_list(configs)
        """
        return [cls.from_dict(data) for data in data_list]