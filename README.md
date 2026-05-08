# magic-pipeline
通用流程编排工具包 —— 支持 AI 模型调用的 Pipeline 执行框架

[![PyPI version](https://badge.fury.io/py/magic-pipeline.svg)](https://badge.fury.io/py/magic-pipeline)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> 通用流程编排工具包 —— 支持自定义流程执行编排

## 项目状态

**开发中** - 首个正式版本将于 2026 年 7 月发布

## 功能规划

- **流程编排**：支持定义多步骤 Pipeline，按顺序执行命令
- **命令扩展**：内置常见命令注册机制，支持自定义命令和分类
- **错误处理**：任一步骤失败即停止执行，并自动释放资源
- **配置驱动**：通过 YAML 配置文件定义 Pipeline，无需修改代码
- **跨平台**：支持 Windows / Linux / macOS

## 安装

```bash
pip install magic_pipeline
```
## 示例（待正式版本发布后补充）
> 示例配置和使用方法将在正式发布时提供

## 代码规范
本项目遵循以下基本原则：

1. 单文件不超过 200 行：超过时请拆分为多个模块
2. 单函数不超过 200 行：超过时请拆分为多个小函数
3. 注释尽量完整：关键逻辑、复杂算法、非显而易见的代码必须有注释说明
4. 如有特殊场景确实需要突破（如纯数据定义文件），可在 PR 中说明。

这些规则旨在保证代码的可读性和可维护性，便于合作，请尽量遵守。

## 针对 AI 辅助工具的提示
本项目使用 AI 辅助开发，请在生成代码时尽量遵守上述代码规范。

## 许可证
MIT License

## 作者
wxd123 - GitHub
