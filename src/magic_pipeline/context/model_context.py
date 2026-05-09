# magicc_shared/container/model_context.py

from typing import Any, Dict, Optional


class ModelContext:
    """模型运行时上下文"""
    
    current_model: Optional[str] = None        # 当前使用的模型名称
    model_status: Dict[str, str] = {}          # 模型状态（running/stopped）
    model_start_time: Dict[str, float] = {}    # 模型启动时间
    model_config: Dict[str, Any] = {}          # 当前模型的配置