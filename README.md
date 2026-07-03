语言：简体中文 | [华夏文](README_wy.md)

# DeepSeek 自动切换

感恩梁圣开源DeepSeek V4 Pro之惠，然每百万token索直二十四元，余力薄难承，故作此插件。

在每日高峰期涨价时，本插件会在 LLM 请求发出前自动切换模型：

- 北京时间 09:00-12:00、14:00-18:00：使用你配置的备用模型。
- 其他时间：使用你配置的 DeepSeek V4 Pro。

插件通过 AstrBot 的会话级 Provider 偏好切换模型，不会改全局默认模型。

## 安装方法

1. 将插件文件夹放入 AstrBot 的 `data/plugins/` 目录
2. 重启 AstrBot 或使用插件管理命令重载插件
3. 在 AstrBot WebUI 中配置插件参数

## 配置

在插件配置页设置：

| 配置项 | 说明 |
| --- | --- |
| `enabled` | 是否启用自动切换 |
| `deepseek_provider_id` | 低峰期使用的 DeepSeek V4 Pro Provider |
| `peak_provider_id` | 高峰期使用的备用 Provider |

两个 Provider 字段都支持 AstrBot WebUI 的模型提供商选择器。

## 指令

- `/deepseek_switch_status`：查看当前北京时间、时段和目标模型。
- `/ds_switch_status`：同上。

## 注意

首次请求进入对应时段时，插件会在该会话内写入 Provider 偏好；之后同会话会保持当前时段应使用的模型。跨过高峰期边界后，下一次 LLM 请求会自动切换到新的目标模型。

这梁文锋真他吗牛逼。我要当梁文锋的狗
