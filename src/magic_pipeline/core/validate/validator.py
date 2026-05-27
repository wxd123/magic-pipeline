# magic_pipeline/core/validate/validator.py
from pathlib import Path
from typing import Tuple, List, Optional
from magic_pipeline.messages import get_pipeline_msg
from .manifest_validator import ManifestValidator
from .pipeline_validator import PipelineValidator


class ProjectArchitectureValidator:
    """项目架构验证器 - 按顺序验证"""
    
    # 支持的配置目录名（标准只能是 config）
    CONFIG_DIR_NAME = "config"
    
    def __init__(self, project_root: str, language: str = None):
        self.project_root = Path(project_root).resolve()
        self.language = language
        self.msg = get_pipeline_msg(language)
        self.errors = []
        self.warnings = []
        self._manifest_config = None
        self._pipeline_config = None
    
    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """执行完整验证（按顺序）"""
        self.errors = []
        self.warnings = []
        
        # 1. 检查项目根目录
        if not self.project_root.exists():
            self.errors.append(
                self.msg.get("project_root_not_exists", path=str(self.project_root))
            )
            return False, self.errors, self.warnings
        
        # 2. 验证项目结构
        self._validate_structure()
        
        # 3. 验证配置目录
        self._validate_config_directory()
        
        # 4. 验证 manifest.yaml
        self._validate_manifest()
        
        # 5. 验证 pipeline.yaml
        self._validate_pipeline()
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_structure(self):
        """验证项目结构（src-layout / flat-layout）"""
        has_src_layout = self._check_src_layout()
        has_flat_layout = self._check_flat_layout()
        
        if has_src_layout and has_flat_layout:
            packages = self._get_python_packages()
            package_name = packages[0] if packages else "unknown"
            self.errors.append(
                self.msg.get("mixed_layout",
                           path=str(self.project_root),
                           package=package_name)
            )
        elif has_src_layout:
            pass  # src-layout 有效
        elif has_flat_layout:
            self._check_flat_layout_package_name()
        else:
            self.errors.append(
                self.msg.get("no_valid_layout", path=str(self.project_root))
            )
    
    def _check_src_layout(self) -> bool:
        """检查src-layout风格"""
        src_path = self.project_root / "src"
        
        if not src_path.exists() or not src_path.is_dir():
            return False
        
        for item in src_path.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                return True
            if item.suffix == '.py':
                return True
        
        return False
    
    def _check_flat_layout(self) -> bool:
        """检查扁平化布局"""
        exclude_dirs = {'.git', '__pycache__', 'venv', 'env', 'build', 'dist', 'config', 'tests', 'test'}
        exclude_files = {'setup.py', 'pyproject.toml', 'requirements.txt', 'conftest.py'}
        
        for item in self.project_root.iterdir():
            if item.name in exclude_dirs or item.name in exclude_files:
                continue
            
            if item.is_dir() and (item / "__init__.py").exists():
                return True
            if item.suffix == '.py' and not item.name.startswith('test_'):
                return True
        
        return False
    
    def _check_flat_layout_package_name(self):
        """检查 flat-layout 包名是否与项目名一致"""
        packages = self._get_python_packages()
        
        if not packages:
            return
        
        main_package = packages[0]
        
        if main_package != self.project_root.name:
            self.errors.append(
                self.msg.get("package_name_mismatch",
                           project_name=self.project_root.name,
                           package=main_package)
            )
    
    def _get_python_packages(self) -> List[str]:
        """获取项目中的所有Python包"""
        packages = []
        src_path = self.project_root / "src"
        
        if src_path.exists():
            for item in src_path.iterdir():
                if item.is_dir() and (item / "__init__.py").exists():
                    packages.append(item.name)
        
        exclude_dirs = {'config', 'tests', 'test', 'docs', 'examples', '__pycache__'}
        for item in self.project_root.iterdir():
            if item.is_dir() and (item / "__init__.py").exists() and item.name not in exclude_dirs:
                packages.append(item.name)
        
        return packages
    
    def _validate_config_directory(self):
        """验证配置目录"""
        config_path = self.project_root / self.CONFIG_DIR_NAME
        
        if not config_path.exists():
            self.errors.append(
                f"缺少必需目录: {self.CONFIG_DIR_NAME}/\n"
                f"  项目路径: {self.project_root}\n"
                f"  当前目录内容: {[p.name for p in self.project_root.iterdir() if p.is_dir()]}\n"
                f"  修复: mkdir {self.project_root}/{self.CONFIG_DIR_NAME}\n"
                f"  注意: 配置目录名称必须是 '{self.CONFIG_DIR_NAME}'"
            )
            return False
        
        if not config_path.is_dir():
            self.errors.append(f"config 路径不是目录: {config_path}")
            return False
        
        self.config_dir = config_path
        return True
    
    def _validate_manifest(self):
        """验证 manifest.yaml"""
        if not hasattr(self, 'config_dir'):
            return
        
        manifest_file = self.config_dir / "manifest.yaml"
        
        if not manifest_file.exists():
            self.errors.append(
                f"缺少必需文件: {manifest_file}\n"
                f"  修复: 在 {self.config_dir}/ 目录下创建 manifest.yaml 配置文件"
            )
            return
        
        validator = ManifestValidator(manifest_file)
        is_valid, errors, warnings = validator.validate()
        self.errors.extend(errors)
        self.warnings.extend(warnings)
        
        if is_valid:
            self._manifest_config = validator.get_config()
    
    def _validate_pipeline(self):
        """验证 pipeline.yaml"""
        if not hasattr(self, 'config_dir'):
            return
        
        pipeline_file = self.config_dir / "pipeline.yaml"
        
        if not pipeline_file.exists():
            self.errors.append(
                f"缺少必需文件: {pipeline_file}\n"
                f"  修复: 在 {self.config_dir}/ 目录下创建 pipeline.yaml 配置文件"
            )
            return
        
        validator = PipelineValidator(pipeline_file)
        is_valid, errors, warnings = validator.validate()
        self.errors.extend(errors)
        self.warnings.extend(warnings)
        
        if is_valid:
            self._pipeline_config = validator.get_config()
    
    def get_validation_report(self) -> str:
        """获取详细的验证报告"""
        report = []
        report.append("=" * 60)
        report.append(f"项目路径: {self.project_root}")
        report.append(f"验证结果: {'✅ 通过' if len(self.errors) == 0 else '❌ 失败'}")
        
        if self.errors:
            report.append(f"\n错误 ({len(self.errors)}):")
            for e in self.errors:
                report.append(f"  ❌ {e}")
        
        if self.warnings:
            report.append(f"\n警告 ({len(self.warnings)}):")
            for w in self.warnings:
                report.append(f"  ⚠️ {w}")
        
        report.append("=" * 60)
        return "\n".join(report)
    
    def get_manifest_config(self):
        """获取manifest配置对象（仅当验证通过后）"""
        return self._manifest_config
    
    def get_pipeline_config(self):
        """获取pipeline配置对象（仅当验证通过后）"""
        return self._pipeline_config


def validate_project(project_path: str, language: str = None) -> Tuple[bool, List[str], List[str]]:
    """验证项目架构的便捷函数"""
    validator = ProjectArchitectureValidator(project_path, language)
    return validator.validate()


def validate_step_by_step(project_path: str, callback=None):
    """分步验证，可以在每一步后决定是否继续"""
    from enum import Enum
    
    class Stage(Enum):
        ROOT = "根目录检查"
        STRUCTURE = "项目结构验证"
        CONFIG_DIR = "配置目录验证"
        MANIFEST = "manifest.yaml验证"
        PIPELINE = "pipeline.yaml验证"
    
    validator = ProjectArchitectureValidator(project_path)
    result = type('ValidationResult', (), {'is_valid': True, 'errors': [], 'warnings': []})()
    
    # 阶段1: 根目录检查
    if not validator.project_root.exists():
        result.is_valid = False
        result.errors.append(f"项目根目录不存在: {validator.project_root}")
        if callback:
            callback(Stage.ROOT.value, False, result.errors, result.warnings)
        return result
    
    if callback:
        callback(Stage.ROOT.value, True, [], [])
    
    # 阶段2: 项目结构验证
    validator._validate_structure()
    stage_valid = len([e for e in validator.errors if "结构" in e]) == 0
    if callback:
        callback(Stage.STRUCTURE.value, stage_valid, validator.errors, validator.warnings)
    
    # 阶段3: 配置目录验证
    validator._validate_config_directory()
    stage_valid = len([e for e in validator.errors if "config" in e.lower()]) == 0
    if callback:
        callback(Stage.CONFIG_DIR.value, stage_valid, validator.errors, validator.warnings)
    
    # 阶段4: manifest.yaml验证
    validator._validate_manifest()
    stage_valid = len([e for e in validator.errors if "manifest" in e.lower()]) == 0
    if callback:
        callback(Stage.MANIFEST.value, stage_valid, validator.errors, validator.warnings)
    
    # 阶段5: pipeline.yaml验证
    validator._validate_pipeline()
    stage_valid = len([e for e in validator.errors if "pipeline" in e.lower()]) == 0
    if callback:
        callback(Stage.PIPELINE.value, stage_valid, validator.errors, validator.warnings)
    
    result.is_valid = len(validator.errors) == 0
    result.errors = validator.errors
    result.warnings = validator.warnings
    
    return result