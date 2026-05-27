from pathlib import Path
from typing import Tuple, List, Dict
from ..model import ProviderConfig
from .base_validator import BaseValidator

class ProviderValidator(BaseValidator):
    """provider 配置段专用验证器"""
    
    def __init__(self, provider_data: dict = None, file_path: Path = None):
        super().__init__(file_path) if file_path else None
        self.provider_data = provider_data
        self._configs = {}
    
    def _do_validate(self, data: dict = None):
        """验证provider配置"""
        provider_data = data or self.provider_data
        
        if not provider_data:
            self.errors.append("provider 配置数据为空")
            return
        
        if not isinstance(provider_data, dict):
            self.errors.append("provider 必须是字典类型")
            return
        
        for provider_name, provider_config in provider_data.items():
            self._validate_single_provider(provider_name, provider_config)
    
    def _validate_single_provider(self, provider_name: str, provider_config: dict):
        """验证单个provider配置"""
        if not isinstance(provider_config, dict):
            self.errors.append(f"provider.{provider_name} 必须是字典类型")
            return
        
        # 验证必需字段
        required_fields = ["type", "url", "port"]
        for field in required_fields:
            if field not in provider_config:
                self.errors.append(f"provider.{provider_name} 缺少必需字段: {field}")
                return
        
        # 验证字段类型
        if not isinstance(provider_config["type"], str):
            self.errors.append(f"provider.{provider_name}.type 必须是字符串类型")
        
        if not isinstance(provider_config["url"], str):
            self.errors.append(f"provider.{provider_name}.url 必须是字符串类型")
        
        # 验证port
        port = provider_config["port"]
        if not isinstance(port, int):
            self.errors.append(f"provider.{provider_name}.port 必须是整数类型")
        elif not (1 <= port <= 65535):
            self.errors.append(f"provider.{provider_name}.port 必须在1-65535之间，当前值: {port}")
        
        # 验证type值
        valid_types = ["local", "remote", "cloud"]
        if provider_config["type"] not in valid_types:
            self.warnings.append(f"provider.{provider_name}.type '{provider_config['type']}' 不在推荐类型列表中: {valid_types}")
    
    def get_configs(self) -> Dict[str, ProviderConfig]:
        """获取转换后的ProviderConfig字典"""
        if self.errors:
            raise ValueError("provider配置验证失败，无法获取配置对象")
        
        configs = {}
        for name, cfg in self.provider_data.items():
            configs[name] = ProviderConfig(**cfg)
        
        return configs


def validate_provider_section(provider_data: dict, file_path: Path = None) -> Tuple[bool, List[str], List[str]]:
    """验证provider配置段的便捷函数"""
    validator = ProviderValidator(provider_data, file_path)
    validator._do_validate()
    return len(validator.errors) == 0, validator.errors, validator.warnings