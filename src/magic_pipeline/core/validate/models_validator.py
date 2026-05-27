from pathlib import Path
from typing import Tuple, List, Dict, Set
from ..model import ModelConfig
from .base_validator import BaseValidator

class ModelsValidator(BaseValidator):
    """models 配置段专用验证器"""
    
    def __init__(self, models_data: dict = None, file_path: Path = None):
        super().__init__(file_path) if file_path else None
        self.models_data = models_data
        self._configs = {}
    
    def _do_validate(self, data: dict = None):
        """验证models配置"""
        models_data = data or self.models_data
        
        if not models_data:
            self.errors.append("models 配置数据为空")
            return
        
        if not isinstance(models_data, dict):
            self.errors.append("models 必须是字典类型")
            return
        
        for model_name, model_config in models_data.items():
            self._validate_single_model(model_name, model_config)
    
    def _validate_single_model(self, model_name: str, model_config: dict):
        """验证单个模型配置"""
        if not isinstance(model_config, dict):
            self.errors.append(f"models.{model_name} 必须是字典类型")
            return
        
        # 验证必需字段
        required_fields = ["provider", "name", "temperature", "max_tokens"]
        for field in required_fields:
            if field not in model_config:
                self.errors.append(f"models.{model_name} 缺少必需字段: {field}")
                return
        
        # 验证字段类型
        if not isinstance(model_config["provider"], str):
            self.errors.append(f"models.{model_name}.provider 必须是字符串类型")
        
        if not isinstance(model_config["name"], str):
            self.errors.append(f"models.{model_name}.name 必须是字符串类型")
        
        # 验证temperature
        temp = model_config["temperature"]
        if not isinstance(temp, (int, float)):
            self.errors.append(f"models.{model_name}.temperature 必须是数字类型")
        elif not (0 <= temp <= 1):
            self.errors.append(f"models.{model_name}.temperature 必须在0-1之间，当前值: {temp}")
        
        # 验证max_tokens
        max_tokens = model_config["max_tokens"]
        if not isinstance(max_tokens, int):
            self.errors.append(f"models.{model_name}.max_tokens 必须是整数类型")
        elif max_tokens <= 0:
            self.errors.append(f"models.{model_name}.max_tokens 必须大于0，当前值: {max_tokens}")
    
    def get_configs(self) -> Dict[str, ModelConfig]:
        """获取转换后的ModelConfig字典"""
        if self.errors:
            raise ValueError("models配置验证失败，无法获取配置对象")
        
        configs = {}
        for name, cfg in self.models_data.items():
            configs[name] = ModelConfig(**cfg)
        
        return configs
    
    def get_model_names(self) -> Set[str]:
        """获取所有模型名称"""
        return set(self.models_data.keys()) if self.models_data else set()


def validate_models_section(models_data: dict, file_path: Path = None) -> Tuple[bool, List[str], List[str]]:
    """验证models配置段的便捷函数"""
    validator = ModelsValidator(models_data, file_path)
    validator._do_validate()
    return len(validator.errors) == 0, validator.errors, validator.warnings