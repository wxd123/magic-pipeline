# magic_pipeline/messages/__init__.py
from .message import get_pipeline_msg
from .en_US import EnglishPipelineMessages
from .zh_CN import ChinesePipelineMessages

__all__ = ['get_pipeline_msg', 'EnglishPipelineMessages', 'ChinesePipelineMessages']



