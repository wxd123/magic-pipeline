
#!/usr/bin/env python3
# coder/cli/db_command.py
"""
数据库管理命令
"""

import sys
from typing import List
from magic_base.data_access.util.base_db_command import BaseDBCommand
from ..data_access import  Projects
from magic_pipeline.context import MagicPipelineContext


class DBCommand(BaseDBCommand):
    """数据库管理命令类，继承自BaseDBCommand"""
    
    def __init__(self):
        """初始化数据库连接配置"""
        super().__init__()
        MagicPipelineContext.init_context()
    
    model_tables = [Projects]
    
    @property
    def command_name(self) -> str:
        return "数据库管理工具"
    
    def execute(self, args: List[str] = None) -> int:
        """执行数据库命令
        
        Args:
            args: 命令行参数列表
            
        Returns:
            退出码
        """
        if args is None:
            args = sys.argv[1:]
        
        # 调试输出（可选，测试通过后可删除）
        print(f"DBCommand executing with args: {args}", file=sys.stderr)
        
        return super().execute(args)


def main():
    """命令行入口函数"""
    cmd = DBCommand()
    sys.exit(cmd.execute())


if __name__ == "__main__":
    main()