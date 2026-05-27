# tests/test_structure_validator.py
import pytest
from pathlib import Path
from magic_pipeline.core.validate.validator import ProjectArchitectureValidator

# 测试项目根目录
test_project_root = Path("/opt/dev/py_project/coder/")


class TestProjectStructure:
    """项目结构验证测试"""
    
    def test_config_directory_exists(self):
        """测试config目录是否存在"""
        validator = ProjectArchitectureValidator(str(test_project_root))
        is_valid, errors, warnings = validator.validate()
        
        # 检查是否有配置目录相关的错误
        config_errors = [e for e in errors if "config" in e.lower()]
        
        if config_errors:
            # 直接使用验证器返回的错误信息
            pytest.fail("\n".join(config_errors))
        
        assert True
    
    def test_manifest_yaml_exists_and_valid(self):
        """测试manifest.yaml存在且格式正确"""
        validator = ProjectArchitectureValidator(str(test_project_root))
        is_valid, errors, warnings = validator.validate()
        
        # 检查是否有 manifest 相关的错误
        manifest_errors = [e for e in errors if "manifest" in e.lower()]
        
        if manifest_errors:
            pytest.fail("\n".join(manifest_errors))
        
        assert True
    
    def test_pipeline_yaml_exists_and_valid(self):
        """测试pipeline.yaml存在且格式正确"""
        validator = ProjectArchitectureValidator(str(test_project_root))
        is_valid, errors, warnings = validator.validate()
        
        # 检查是否有 pipeline 相关的错误
        pipeline_errors = [e for e in errors if "pipeline" in e.lower()]
        
        if pipeline_errors:
            pytest.fail("\n".join(pipeline_errors))
        
        assert True
    
    def test_complete_validation(self):
        """完整验证：项目结构 + 配置文件"""
        validator = ProjectArchitectureValidator(str(test_project_root))
        is_valid, errors, warnings = validator.validate()
        
        # 输出详细报告
        print(validator.get_validation_report())
        
        # 直接使用验证器返回的错误信息
        assert is_valid, f"项目验证失败:\n" + "\n".join(errors)