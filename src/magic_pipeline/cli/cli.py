#!/usr/bin/env python3
# magicc_cli/cli/cli.py
"""
    Magic Pileline - 主入口 (Click版本)
"""

import sys
import click


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """MagicPipeline - 智能流程编排工具"""
    if ctx.invoked_subcommand is None:
        # 没有子命令时显示帮助
        click.echo("Usage: pipeline <module> [args]")
        click.echo("\nAvailable modules:")      

        click.echo("  db    - 数据库管理工具")
        click.echo("\nExamples:")
        click.echo("  pipeline db init ")               #初始化数据库
        click.echo("  pipeline db create-tables ")      #创建数据表
        click.echo("  pipeline db recreate-tables ")    #删除并重新创建数据表
        click.echo("  pipeline db --help")
        sys.exit(1)


        
@main.command(name='db', help='数据库管理命令')
@click.argument('args', nargs=-1, type=click.UNPROCESSED)
def db_command(args):
    """数据库管理命令（转发原有参数）"""
       
    from .db_commands import main as db_main
    
    # 保存原始argv
    original_argv = sys.argv
    # 构造新的argv: [script_path, ...args]
    sys.argv = [original_argv[0]] + list(args)
    
    try:
        db_main()
    finally:
        # 恢复原始argv
        sys.argv = original_argv




if __name__ == "__main__":
    main()