# magic-pipeline/data_access/repository/project_repo.py

"""
Magic Coder Project Repository

为 Magic Coder 共享模块提供数据访问层实现。
"""

from magic_base.data_access.repository.base_repository import MagicBaseRepository

from ..model.projects import Projects


class ProjectRepository(MagicBaseRepository[Projects]):
    """
    项目数据仓库
    """
    pass

project_repo : ProjectRepository = ProjectRepository()