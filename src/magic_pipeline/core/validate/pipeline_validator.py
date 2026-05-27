import yaml
from pathlib import Path
from typing import Tuple, List

from magic_pipeline.core.model import ModelConfig,ProjectInfo, ProviderConfig
from ..model import PipelineConfig
from .base_validator import BaseValidator
from .project_validator import ProjectValidator
from .models_validator import ModelsValidator
from .provider_validator import ProviderValidator
from .pipeline_steps_validator import PipelineStepsValidator

class PipelineValidator(BaseValidator):
    """pipeline.yaml 专用验证器（组合模式）"""
    
    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self._config = None
        self._project_validator = None
        self._models_validator = None
        self._provider_validator = None
        self._steps_validator = None
    
    def _do_validate(self, data: dict):
        """验证pipeline.yaml - 使用独立的验证器"""
        # 1. 检查必需配置段
        required_sections = ["project", "models", "provider", "pipeline"]
        for section in required_sections:
            if section not in data:
                self.errors.append(f"缺少必需配置段: {section}")
        
        if self.errors:
            return
        
        # 2. 验证project配置（使用独立验证器）
        self._validate_project(data["project"])
        
        # 3. 验证models配置（使用独立验证器）
        self._validate_models(data["models"])
        
        # 4. 验证provider配置（使用独立验证器）
        self._validate_provider(data["provider"])
        
        # 5. 验证pipeline步骤（使用独立验证器）
        if not self.errors:  # 只有在models验证通过后才验证pipeline（需要模型名称）
            model_names = self._models_validator.get_model_names() if self._models_validator else set()
            self._validate_pipeline_steps(data["pipeline"], model_names)
    
    def _validate_project(self, project_data: dict):
        """使用ProjectValidator验证project配置"""
        self._project_validator = ProjectValidator(project_data, self.file_path)
        self._project_validator._do_validate()
        self.errors.extend(self._project_validator.errors)
        self.warnings.extend(self._project_validator.warnings)
    
    def _validate_models(self, models_data: dict):
        """使用ModelsValidator验证models配置"""
        self._models_validator = ModelsValidator(models_data, self.file_path)
        self._models_validator._do_validate()
        self.errors.extend(self._models_validator.errors)
        self.warnings.extend(self._models_validator.warnings)
    
    def _validate_provider(self, provider_data: dict):
        """使用ProviderValidator验证provider配置"""
        self._provider_validator = ProviderValidator(provider_data, self.file_path)
        self._provider_validator._do_validate()
        self.errors.extend(self._provider_validator.errors)
        self.warnings.extend(self._provider_validator.warnings)
    
    def _validate_pipeline_steps(self, pipeline_data: list, model_names: set):
        """使用PipelineStepsValidator验证pipeline步骤"""
        self._steps_validator = PipelineStepsValidator(pipeline_data, model_names, self.file_path)
        self._steps_validator._do_validate()
        self.errors.extend(self._steps_validator.errors)
        self.warnings.extend(self._steps_validator.warnings)
    
    def get_config(self) -> PipelineConfig:
        """获取转换后的配置对象"""
        if self.errors:
            raise ValueError("配置验证失败，无法获取配置对象")
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return self._convert_to_dataclass(data)
    
    def _convert_to_dataclass(self, data: dict) -> PipelineConfig:
        """转换为dataclass"""
        # 从各个验证器获取转换后的对象
        project = self._project_validator.get_config() if self._project_validator else None
        models = self._models_validator.get_configs() if self._models_validator else {}
        providers = self._provider_validator.get_configs() if self._provider_validator else {}
        
        if not project:
            # 降级方案：直接转换
            project = ProjectInfo(**data["project"])
            models = {name: ModelConfig(**cfg) for name, cfg in data["models"].items()}
            providers = {name: ProviderConfig(**cfg) for name, cfg in data["provider"].items()}
        
        return PipelineConfig(
            project=project,
            models=models,
            provider=providers,
            pipeline=data.get("pipeline", [])
        )


def validate_pipeline(file_path: Path) -> Tuple[bool, List[str], List[str]]:
    """验证pipeline.yaml的便捷函数"""
    validator = PipelineValidator(file_path)
    return validator.validate()