from pathlib import Path
from typing import Tuple, List, Dict
from ..model import ProjectInfo
from .base_validator import BaseValidator

class ProjectValidator(BaseValidator):
    """project 配置段专用验证器"""
    
    def __init__(self, project_data: dict = None, file_path: Path = None):
        """
        初始化Project验证器
        Args:
            project_data: project配置字典
            file_path: 配置文件路径（用于错误提示）
        """
        super().__init__(file_path) if file_path else None
        self.project_data = project_data
        self._config = None
    
    def _do_validate(self, data: dict = None):
        """验证project配置"""
        # 支持直接传入数据或从self.project_data获取
        project_data = data or self.project_data
        
        if not project_data:
            self.errors.append("project 配置数据为空")
            return
        
        if not isinstance(project_data, dict):
            self.errors.append("project 必须是字典类型")
            return
        
        # 验证必需字段
        self._validate_required_fields(project_data)
        
        # 验证字段类型
        self._validate_field_types(project_data)
        
        # 验证业务规则
        self._validate_business_rules(project_data)
    
    def _validate_required_fields(self, project_data: dict):
        """验证必需字段"""
        required_fields = [
            "name", "code", "type", "description", 
            "version", "language", "work_path"
        ]
        
        for field in required_fields:
            if field not in project_data:
                self.errors.append(f"project 缺少必需字段: {field}")
    
    def _validate_field_types(self, project_data: dict):
        """验证字段类型"""
        # 字符串类型字段
        string_fields = ["name", "code", "type", "description", "version", "language", "work_path"]
        for field in string_fields:
            if field in project_data and not isinstance(project_data[field], str):
                self.errors.append(f"project.{field} 必须是字符串类型，当前类型: {type(project_data[field]).__name__}")
    
    def _validate_business_rules(self, project_data: dict):
        """验证业务规则"""
        # 验证版本号格式
        if "version" in project_data:
            version = project_data["version"]
            if not self._is_valid_version(version):
                self.warnings.append(f"project.version 格式可能不规范: {version}，建议使用语义化版本如 1.0.0")
        
        # 验证项目类型
        if "type" in project_data:
            valid_types = ["comment", "codegen", "analysis", "test"]
            if project_data["type"] not in valid_types:
                self.warnings.append(f"project.type '{project_data['type']}' 不在推荐类型列表中: {valid_types}")
        
        # 验证语言
        if "language" in project_data:
            valid_languages = ["java", "python", "go", "javascript", "cpp"]
            if project_data["language"] not in valid_languages:
                self.warnings.append(f"project.language '{project_data['language']}' 不在推荐语言列表中: {valid_languages}")
        
        # 验证work_path（可选，检查路径是否存在）
        if "work_path" in project_data and project_data["work_path"]:
            work_path = Path(project_data["work_path"])
            if not work_path.exists():
                self.warnings.append(f"project.work_path 路径不存在: {project_data['work_path']}")
    
    def _is_valid_version(self, version: str) -> bool:
        """验证版本号格式（简单验证）"""
        import re
        # 语义化版本格式: major.minor.patch
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))
    
    def get_config(self) -> ProjectInfo:
        """获取转换后的ProjectInfo对象"""
        if self.errors:
            raise ValueError("project配置验证失败，无法获取配置对象")
        
        data = self.project_data
        if not data:
            raise ValueError("project配置数据为空")
        
        return ProjectInfo(**data)


def validate_project_section(project_data: dict, file_path: Path = None) -> Tuple[bool, List[str], List[str]]:
    """验证project配置段的便捷函数"""
    validator = ProjectValidator(project_data, file_path)
    # 直接调用验证
    validator._do_validate()
    return len(validator.errors) == 0, validator.errors, validator.warnings