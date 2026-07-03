Language: [简体中文](README.md) | 华夏文

# DeepSeek 自动易模

感梁圣开源 DeepSeek V4 Pro 之惠。然每百万 token 索直二十四元，余资寡薄，不能久承，故作此插件，以避峰时之费。

值每日高峰涨价之时，本插件将于 LLM 请求未发之前，先易其所用模型：

- 京师时辰 09:00-12:00、14:00-18:00：用君所设之备用模型。
- 余时：复用君所设之 DeepSeek V4 Pro。

本插件借 AstrBot 会话级 Provider 偏好以易模型，不改全局默认模型。

## 安装之法

1. 置插件目录于 AstrBot 之 `data/plugins/` 中。
2. 重启 AstrBot，或以插件管理命令重载之。
3. 入 AstrBot WebUI，设插件诸项。

## 配置

于插件配置页设之：

| 配置项 | 说明 |
| --- | --- |
| `enabled` | 是否启用自动易模 |
| `deepseek_provider_id` | 非高峰时所用 DeepSeek V4 Pro Provider |
| `peak_provider_id` | 高峰时所用备用 Provider |

二 Provider 皆可由 AstrBot WebUI 模型提供商选择器择之。

## 指令

- `/deepseek_switch_status`：观当前京师时辰、所处时段及目标模型。
- `/ds_switch_status`：同上。

## 注意

初入对应时段而有请求时，插件将在此会话内写入 Provider 偏好；其后同会话皆循当前时段所宜之模型。若越高峰之界，则于下一次 LLM 请求时，自动易至新目标模型。

梁文锋诚雄才也，余愿执鞭随之。
