# magic_pipeline/core/scope/step_scope.py
import tempfile
import shutil
from pathlib import Path
from .scope import BaseScope


class StepScope(BaseScope):
    """步骤作用域 - 临时目录管理"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self._temp_dirs = []
    
    def _on_enter(self):
        print(f"\n📌 步骤: {self.name}")
        # 创建步骤临时目录
        temp_dir = tempfile.mkdtemp(prefix=f"step_{self.name}_")
        self.set("temp_dir", temp_dir)
        self._temp_dirs.append(temp_dir)
    
    def _on_exit(self, exc_type, exc_val, exc_tb):
        # 清理临时目录
        for d in self._temp_dirs:
            if Path(d).exists():
                shutil.rmtree(d, ignore_errors=True)
        super()._on_exit(exc_type, exc_val, exc_tb)
    
    def create_temp_dir(self, name: str = None) -> str:
        """创建子临时目录"""
        prefix = f"{self.name}_{name}_" if name else f"{self.name}_"
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        self._temp_dirs.append(temp_dir)
        return temp_dir