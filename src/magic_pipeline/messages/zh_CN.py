# magic_pipeline/messages/zh_CN.py
from typing import Dict
from magic_base.i18n import MessageProvider

class ChinesePipelineMessages(MessageProvider):
    """中文消息"""
    
    @property
    def messages(self) -> Dict[str, str]:
        return {
            # 目录相关
            "project_root_not_exists": (
                "项目根目录不存在: {path}\n"
                "  请确认路径是否正确\n"
                "  或创建该目录: mkdir -p {path}"
            ),
            
            # 架构相关
            "mixed_layout": (
                "项目结构不规范: 同时包含 src-layout 和 flat-layout 两种架构风格\n"
                "  项目路径: {path}\n"
                "  问题: 检测到同时存在 'src/' 目录和根目录下的Python包\n"
                "  修复: 选择一种架构风格，删除另一种\n"
                "    - 保留 src-layout: rm -rf {path}/{package}\n"
                "    - 保留 flat-layout: rm -rf {path}/src"
            ),
            
            "no_valid_layout": (
                "项目结构不规范: 未检测到有效的 Python 项目架构\n"
                "  项目路径: {path}\n"
                "  要求: 必须使用以下架构之一\n"
                "    - src-layout: 源码放在 src/ 目录下\n"
                "    - flat-layout: 源码放在根目录下的包（含 __init__.py 的目录）中\n"
                "  修复: 重组项目结构以符合上述规范"
            ),
            
            # 包名相关
            "invalid_package_name": (
                "无效的包名: '{package}'\n"
                "  项目路径: {path}\n"
                "  问题: 包名不符合 Python 命名规范\n"
                "  要求: 包名必须使用小写字母、数字和下划线，且不能以数字开头\n"
                "  修复: 将目录 '{package}' 重命名为符合规范的名称\n"
                "    mv {package} <新包名>"
            ),
            
            "package_name_mismatch": (
                "无效的项目结构: flat-layout 项目的根包名必须与项目名一致\n"
                "  项目路径: {path}\n"
                "  项目名: {project_name}\n"
                "  当前包名: {package}\n"
                "  问题: flat-layout 要求根目录下的包名与项目名相同\n"
                "  修复方案:\n"
                "    方案1 - 重命名包: mv {package} {project_name}\n"
                "    方案2 - 改用 src-layout: mkdir src && mv {package} src/\n"
                "    方案3 - 重命名项目目录: cd .. && mv {project_name} {package}"
            ),
        }