# magic-pipeline/data_access/model/projects.py
"""
项目表模型 - 记录所执行的项目信息

项目是 Pipeline 执行的核心实体，包含项目的元数据、配置信息和运行时参数。
每个项目通过 name + version 唯一标识，支持多版本管理。
"""

import json
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Text

from magic_base import MagicBaseEntity
from magic_pipeline.constant.pipeline import PROJECT_TABLE


class Projects(MagicBaseEntity):
    """
    项目表模型
    
    记录 Pipeline 项目的完整信息，包括：
        - 项目标识：name + version 唯一确定一个项目版本
        - 项目类型：区分不同业务场景的项目
        - 配置内容：项目的完整配置（YAML/JSON格式）
        - 自定义参数：运行时传入的变量参数
        
    使用示例：
        # 创建项目
        project = Projects(
            name="sales-forecast",
            version="1.0.0",
            code="SALES_001",
            type="analysis",
            work_path="/opt/projects/sales",
            description="销售预测分析项目",
            config_content='{"model": "xgboost"}',
            params='{"threshold": 0.8}'
        )
        
        # 转换为字典
        data = project.to_dict()
        
        # 从字典创建
        new_project = Projects.from_dict(data)
    """
    
    __tablename__ = PROJECT_TABLE
    
    # ========== 基础字段 ==========
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # ========== 项目标识字段 ==========
    name = Column(String(50), nullable=False, comment="项目名称，与version组合唯一标识一个项目版本")
    version = Column(String(20), nullable=False, comment="项目版本号，支持语义化版本")
    code = Column(String(20), nullable=False, comment="项目代码/缩写，用于快速识别")
    
    # ========== 项目分类字段 ==========
    type = Column(String(20), nullable=False, comment="项目类型：analysis/etl/training/inference等")
    work_path = Column(String(200), nullable=False, comment="项目工作目录的绝对路径")
    
    # ========== 描述字段 ==========
    description = Column(String(200), nullable=False, comment="项目描述，说明项目的用途和功能")
    
    # ========== 配置字段 ==========
    config_content = Column(Text, nullable=False, comment="项目配置内容，JSON字符串格式")
    params = Column(Text, nullable=True, comment="项目自定义参数，JSON字符串格式，用于运行时变量替换")
    
        # ========== 数据库字段白名单 ==========
    _DB_FIELDS = {
        'id', 'name', 'version', 'code', 'type', 
        'work_path', 'description', 'config_content', "param"
    }

    def to_dict(self) -> Dict[str, Any]:
        """
        将模型实例转换为字典格式
        
        用于：
            - API 响应序列化
            - 数据库记录导出
            - 配置备份
            - 跨服务传输
            
        Returns:
            Dict[str, Any]: 包含所有字段的字典，params 和 config_content 会被解析为 JSON 对象
            
        Example:
            >>> project = Projects(name="test", version="1.0.0", ...)
            >>> data = project.to_dict()
            >>> print(data['name'])
            'test'
        """
        result = {
            # 基础字段
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'code': self.code,
            'type': self.type,
            'work_path': self.work_path,
            'description': self.description,
            'config_content': self.config_content,
            'params': self.params,
        }
        
        # 解析 JSON 字符串为对象（便于使用）
        # if self.config_content:
        #     try:
        #         result['config_content'] = json.loads(self.config_content)
        #     except json.JSONDecodeError:
        #         pass  # 保持原字符串
                
        # if self.params:
        #     try:
        #         result['params'] = json.loads(self.params)
        #     except json.JSONDecodeError:
        #         pass
                
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Projects':
        """
        从字典创建模型实例
        
        用于：
            - API 请求反序列化
            - 数据库记录恢复
            - 配置导入
            - 单元测试数据构造
            
        Args:
            data: 包含项目字段的字典
            
        Returns:
            Projects: 模型实例
            
        Example:
            >>> data = {'name': 'test', 'version': '1.0.0', ...}
            >>> project = Projects.from_dict(data)
            >>> print(project.name)
            'test'
        """
        # 复制数据，避免修改原字典
        cloned = data.copy()
        
        # 将 JSON 对象序列化为字符串存储
        # if 'config_content' in cloned and isinstance(cloned['config_content'], (dict, list)):
        #     cloned['config_content'] = json.dumps(cloned['config_content'], ensure_ascii=False)
            
        # if 'params' in cloned and isinstance(cloned['params'], (dict, list)):
        #     cloned['params'] = json.dumps(cloned['params'], ensure_ascii=False)
        
        # 过滤掉不属于模型字段的键
        
        filtered_data = {"params": data.get('params', {}) if 'params' in data else {}}
        for k, v in cloned.items():
            if k in cls._DB_FIELDS:
                filtered_data[k] = v
            else:
                filtered_data['params'][k] = v
        
        # 统一序列化
        for k, v in filtered_data.items():
            if isinstance(v, (dict, list)):
                filtered_data[k] = json.dumps(v, ensure_ascii=False)

        return cls(**filtered_data)
    
    def update_from_dict(self, data: Dict[str, Any]) -> 'Projects':
        """
        从字典更新模型实例（就地更新）
        
        用于：
            - PATCH 部分更新
            - 配置合并
            
        Args:
            data: 包含待更新字段的字典
            
        Returns:
            Projects: 当前实例（支持链式调用）
            
        Example:
            >>> project.update_from_dict({'description': '新的描述'})
        """
        for key, value in data.items():
            if hasattr(self, key) and key != 'id':  # id 不允许更新
                # 特殊处理 JSON 字段
                if key in ('config_content', 'params') and isinstance(value, (dict, list)):
                    value = json.dumps(value, ensure_ascii=False)
                setattr(self, key, value)
        return self
    
    def __repr__(self) -> str:
        """友好的字符串表示"""
        return f"<Projects(id={self.id}, name='{self.name}', version='{self.version}', type='{self.type}')>"
    
    def __str__(self) -> str:
        """简短的字符串表示"""
        return f"{self.name}:{self.version} ({self.type})"