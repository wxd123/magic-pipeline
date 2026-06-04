# magic-pipeline/data_access/model/projects.py - 当前版本表结构

from sqlalchemy import Column, Integer, String,  Text



from magic_base import MagicBaseEntity
from magic_pipeline.constant.pipeline import PROJECT_TABLE

class Projects(MagicBaseEntity):
    """项目表 - 记录被检测的源代码项目"""
    __tablename__ = PROJECT_TABLE
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)                           # 项目名称（唯一）
    version = Column(String(20), nullable=False)                        # 项目版本
    code = Column(String(20), nullable=False)                           # 项目代码
    type = Column(String(20), nullable=False)                           # 项目类型
    work_path = Column(String(200), nullable=False)                     # 项目工作路径
    description = Column(String(200), nullable=False)                   # 项目描述
    config_content= Column(Text, nullable=False)                        # 配置项内容
    params = Column(Text, nullable=True)                                # 项目自定义参数（JSON字符串）
    
    