# magic_pipeline/data_access/service/project_service.py

from typing import Dict, Optional
from pathlib import Path

from magic_base.data_access.service.base_service import BaseService
from ..repository.project_repo import ProjectRepository
from ..model.projects import Projects


class ProjectService(BaseService[Projects]):
    
    def __init__(self):
        super().__init__(ProjectRepository())
    
    # ==================== 业务方法 ====================
    
    def register(self, source_path: str, work_dir: Optional[str] = None) -> Dict:
        """注册新项目"""
        project_name = Path(source_path).name
        
        existing = self.find_one({'name': project_name})
        if existing:
            raise ValueError(f"Project {project_name} already exists")
        
        return self.create(
            name=project_name,
            source_path=source_path,
            work_dir=work_dir or str(Path.home() / "magic_coder" / project_name)
        )
    
    def get_or_create(self, source_path: str, work_dir: Optional[str] = None) -> Dict:
        """获取或创建项目"""
        project_name = Path(source_path).name
        existing = self.find_one({'name': project_name})
        
        if existing:
            return existing
        
        return self.register(source_path, work_dir)
    
    def get_by_name(self, name: str) -> Optional[Dict]:
        """根据名称获取项目"""
        return self.find_one({'name': name})
    
    def validate_source(self, project_id: int) -> bool:
        """验证项目源代码路径"""
        project = self.get_by_id(project_id)
        if not project:
            return False
        
        source_path = Path(project['source_path'])
        return source_path.exists() and source_path.is_dir()
    
    def update_statistics(self, project_id: int) -> Dict:
        """更新项目统计信息"""
        # TODO: 调用 SourceFileService 和 MethodService
        pass
    
    def get_statistics(self, project_id: int) -> Dict:
        """获取项目统计信息"""
        # TODO: 调用 SourceFileService 和 MethodService
        pass

project_service: ProjectService = ProjectService()