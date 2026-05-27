# magic_pipeline/core/validate/structure_validator.py
from pathlib import Path
from typing import Tuple, List
import re
from magic_pipeline.messages import get_pipeline_msg

class StructureValidator:
    """项目结构验证器"""
    
    # 标准包名正则：小写字母、数字、下划线，不能以数字开头
    STANDARD_PACKAGE_PATTERN = re.compile(r'^[a-z_][a-z0-9_]*$')
    
    def __init__(self, project_root: Path, language: str = None):
        self.project_root = Path(project_root).resolve()
        self.errors = []
        self.warnings = []
        self._project_type = None
        self._python_packages = None
        self._python_modules = None
        self.msg = get_pipeline_msg(language)
    
    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """执行结构验证"""
        self.errors = []
        self.warnings = []
        
        if not self.project_root.exists():
            self.errors.append(self.msg.get("project_root_not_exists", path=str(self.project_root)))
            return False, self.errors, self.warnings
        
        self._check_structure()
        self._check_package_consistency()
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _check_structure(self):
        """检查项目结构"""
        has_src_layout = self._check_src_layout()
        has_flat_layout = self._check_flat_layout()
        
        if has_src_layout and has_flat_layout:
            self._project_type = "mixed"
            packages = self.get_python_packages()
            package_name = packages[0] if packages else "unknown"
            self.errors.append(self.msg.get("mixed_layout", path=str(self.project_root), package=package_name))
        elif has_src_layout:
            self._project_type = "src-layout"
        elif has_flat_layout:
            self._project_type = "flat-layout"
        else:
            self._project_type = "unknown"
            self.errors.append(self.msg.get("no_valid_layout", path=str(self.project_root)))
    
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
    
    def _check_package_consistency(self):
        """检查包名规范性和一致性"""
        if self._project_type != "flat-layout":
            return
        
        packages = self.get_python_packages()
        
        if not packages:
            return
        
        main_package = packages[0]
        
        if not self.STANDARD_PACKAGE_PATTERN.match(main_package):
            self.errors.append(self.msg.get("invalid_package_name", package=main_package))
            return
        
        if main_package != self.project_root.name:
            self.errors.append(self.msg.get("package_name_mismatch", 
                                           project_name=self.project_root.name, 
                                           package=main_package))
    
    def get_project_type(self) -> str:
        """获取项目架构类型"""
        if self._project_type is None:
            self._check_structure()
        return self._project_type or "unknown"
    
    def get_python_packages(self) -> List[str]:
        """获取项目中的所有Python包（相对路径）"""
        if self._python_packages is not None:
            return self._python_packages
        
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
        
        self._python_packages = packages
        return packages
    
    def get_python_modules(self) -> List[str]:
        """获取项目中的所有Python模块（不含包内的模块）"""
        if self._python_modules is not None:
            return self._python_modules
        
        modules = []
        src_path = self.project_root / "src"
        
        if src_path.exists():
            for item in src_path.iterdir():
                if item.suffix == '.py' and item.stem != '__init__':
                    modules.append(item.stem)
        
        exclude_files = {'setup.py', 'conftest.py'}
        for item in self.project_root.iterdir():
            if item.suffix == '.py' and item.name not in exclude_files:
                if not item.name.startswith('test_') and item.stem != '__init__':
                    modules.append(item.stem)
        
        self._python_modules = modules
        return modules
    
    def get_all_python_files(self) -> List[Path]:
        """获取所有Python文件路径"""
        python_files = []
        excludes = {'__pycache__', 'venv', 'env', '.git'}
        
        for py_file in self.project_root.rglob("*.py"):
            if not any(exclude in py_file.parts for exclude in excludes):
                python_files.append(py_file)
        
        return python_files


def validate_structure(project_root: Path, language: str = None) -> Tuple[bool, List[str], List[str]]:
    """验证项目结构的便捷函数"""
    validator = StructureValidator(project_root, language)
    return validator.validate()