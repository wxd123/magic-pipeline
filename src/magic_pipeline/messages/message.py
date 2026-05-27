# magic_pipeline/messages/message.py
from magic_base.i18n import message_factory, get_system_language
from .zh_CN import ChinesePipelineMessages
from .en_US import EnglishPipelineMessages

# 注册验证器专用消息（覆盖基类消息）
message_factory.register("zh_CN", ChinesePipelineMessages)
message_factory.register("en_US", EnglishPipelineMessages)

def get_pipeline_msg(language: str = None):
    """获取验证器消息（自动检测语言）"""
    if language is None:
        language = get_system_language()
    return message_factory.get(language)

# 默认实例（自动检测系统语言）
msg = get_pipeline_msg()