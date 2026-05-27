from pathlib import Path
from typing import Tuple, List, Optional
import yaml

class BaseValidator:
    """基础验证器"""
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.errors = []
        self.warnings = []
    
    def validate(self) -> Tuple[bool, List[str], List[str]]:
        """
        执行验证
        Returns: (是否通过, 错误列表, 警告列表)
        """
        if not self.file_path.exists():
            self.errors.append(f"文件不存在: {self.file_path}")
            return False, self.errors, self.warnings
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if data is None:
                self.errors.append("配置文件为空")
                return False, self.errors, self.warnings
            
            # 调用子类实现的验证方法
            self._do_validate(data)
            
        except yaml.YAMLError as e:
            self.errors.append(f"YAML格式错误: {str(e)}")
        except Exception as e:
            self.errors.append(f"验证异常: {str(e)}")
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _do_validate(self, data: dict):
        """子类实现具体的验证逻辑"""
        raise NotImplementedError