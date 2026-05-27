from pathlib import Path
from typing import Tuple, List
from ..model import ManifestConfig, Whitelist, LocalNetwork
from .base_validator import BaseValidator
import yaml

class ManifestValidator(BaseValidator):
    """manifest.yaml 专用验证器"""
    
    def _do_validate(self, data: dict):
        """验证manifest.yaml"""
        # 1. 检查必需字段
        if "whitelist" not in data:
            self.errors.append("缺少必需配置段 'whitelist'")
            return
        
        whitelist = data["whitelist"]
        required_fields = ["domains", "ips", "dns", "local"]
        
        for field in required_fields:
            if field not in whitelist:
                self.errors.append(f"whitelist 缺少必需字段: {field}")
        
        if self.errors:
            return
        
        # 2. 验证字段类型
        if not isinstance(whitelist["domains"], list):
            self.errors.append("whitelist.domains 必须是列表类型")
        if not isinstance(whitelist["ips"], list):
            self.errors.append("whitelist.ips 必须是列表类型")
        if not isinstance(whitelist["dns"], list):
            self.errors.append("whitelist.dns 必须是列表类型")
        if not isinstance(whitelist["local"], list):
            self.errors.append("whitelist.local 必须是列表类型")
        
        if self.errors:
            return
        
        # 3. 验证local列表中的每个元素
        for idx, local_item in enumerate(whitelist["local"]):
            if not isinstance(local_item, dict):
                self.errors.append(f"whitelist.local[{idx}] 必须是字典类型")
                continue
            
            # 检查必需字段
            required_local_fields = ["id", "protocol", "addr", "port"]
            for field in required_local_fields:
                if field not in local_item:
                    self.errors.append(f"whitelist.local[{idx}] 缺少字段: {field}")
            
            # 验证port类型
            if "port" in local_item and not isinstance(local_item["port"], int):
                self.errors.append(f"whitelist.local[{idx}].port 必须是整数类型")
        
        # 4. 使用dataclass进行类型转换（可选，会触发自动验证）
        if not self.errors:
            try:
                self._convert_to_dataclass(data)
            except ValueError as e:
                self.errors.append(str(e))
    
    def _convert_to_dataclass(self, data: dict) -> ManifestConfig:
        """转换为dataclass（触发自动验证）"""
        local_list = [
            LocalNetwork(**item) for item in data["whitelist"]["local"]
        ]
        
        whitelist = Whitelist(
            domains=data["whitelist"]["domains"],
            ips=data["whitelist"]["ips"],
            dns=data["whitelist"]["dns"],
            local=local_list
        )
        
        return ManifestConfig(whitelist=whitelist)
    
    def get_config(self) -> ManifestConfig:
        """获取转换后的配置对象（仅在验证通过后可用）"""
        if self.errors:
            raise ValueError("配置验证失败，无法获取配置对象")
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return self._convert_to_dataclass(data)


# 便捷函数
def validate_manifest(file_path: Path) -> Tuple[bool, List[str], List[str]]:
    """验证manifest.yaml的便捷函数"""
    validator = ManifestValidator(file_path)
    return validator.validate()