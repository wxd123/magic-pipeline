# magic_pipeline/context/model_context.py

from magic_pipeline.core.model import ModelConfig
from typing import List, Optional


class ModelContext:
    """
    模型上下文 - 存储当前使用的模型信息
    
    负责管理和维护管道中所有可用的模型配置实例。提供模型的注册和查询功能，
    确保模型配置的集中管理和统一访问。
    
    主要功能：
        1. 注册多个模型配置到上下文中
        2. 根据模型ID查询对应的模型配置
        3. 验证注册的模型类型正确性
    
    使用示例：
        # 创建模型配置
        config1 = ModelConfig(id="gpt-4", name="GPT-4", endpoint="...")
        config2 = ModelConfig(id="claude-3", name="Claude 3", endpoint="...")
        
        # 创建模型上下文并注册模型
        model_ctx = ModelContext()
        model_ctx.register_models([config1, config2])
        
        # 获取模型配置
        model = model_ctx.get_model("gpt-4")
    
    Attributes:
        model_configs: 模型配置字典，键为模型ID，值为 ModelConfig 实例
    """
    
    def __init__(self):
        """
        初始化模型上下文
        
        创建一个空的模型配置字典，用于后续注册模型配置。
        """
        self.model_configs = {}

    def register_models(self, model_list: List[ModelConfig]):
        """
        注册模型配置列表
        
        将一组模型配置注册到上下文中。注册前会验证列表中所有元素是否为 ModelConfig 实例，
        验证通过后以模型ID为键构建字典，方便快速查询。
        
        注意：如果多个模型具有相同的ID，后注册的模型会覆盖先注册的模型。
        
        Args:
            model_list: 模型配置列表，每个元素必须是 ModelConfig 实例
            
        Raises:
            TypeError: 当 model_list 中的元素不是 ModelConfig 实例时抛出
            
        Example:
            >>> models = [ModelConfig(id="model1", ...), ModelConfig(id="model2", ...)]
            >>> model_ctx.register_models(models)
        """
        # 先验证所有元素类型
        for m in model_list:
            if not isinstance(m, ModelConfig):
                raise TypeError(f"模型必须是 ModelConfig 实例: {m}")
        
        # 再构建字典
        self.model_configs = {m.id: m for m in model_list}

     
    def get_model(self, model_id: str) -> ModelConfig:
        """
        根据模型ID获取模型配置
        
        从已注册的模型配置字典中查找并返回指定ID的模型配置。
        
        Args:
            model_id: 模型唯一标识符
            
        Returns:
            ModelConfig: 对应的模型配置实例
            
        Raises:
            ValueError: 当指定ID的模型不存在时抛出
            
        Example:
            >>> model = model_ctx.get_model("gpt-4")
            >>> print(model.name)
            GPT-4
        """
        model = self.model_configs.get(model_id)
        if model is None:
            raise ValueError(f"未找到模型: {model_id}")
        return model