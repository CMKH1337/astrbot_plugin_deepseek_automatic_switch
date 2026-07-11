Language: [简体中文](README.md) | [华夏文](README_wy.md) | English

# DeepSeek Auto Switch

Grateful to Saint Liang for the grace of open-sourcing DeepSeek V4 Pro. However, the price of 24 yuan per million tokens is too heavy for my meager strength to bear, hence I created this plugin.

During the daily peak hours when prices increase, this plugin will automatically switch the model before the LLM request is sent:

* Beijing Time 09:00-12:00, 14:00-18:00: Use your configured backup model.
* Other times: Use your configured DeepSeek V4 Pro.

The plugin switches models via AstrBot's session-level Provider preference and will not change the global default model.

## Installation

1. Place the plugin folder into AstrBot's `data/plugins/` directory
2. Restart AstrBot or use the plugin management command to reload the plugin
3. Configure the plugin parameters in the AstrBot WebUI

## Configuration

Set the following in the plugin configuration page:

| Configuration Item | Description |
| --- | --- |
| `enabled` | Whether to enable auto switch |
| `deepseek_provider_id` | The DeepSeek V4 Pro Provider used during off-peak hours |
| `peak_provider_id` | The backup Provider used during peak hours |

Both Provider fields support the model provider selector in the AstrBot WebUI.

## Commands

* `/deepseek_switch_status`: Check the current Beijing time, time period, and target model.
* `/ds_switch_status`: Same as above.

## Notes

When the first request enters a corresponding time period, the plugin writes the Provider preference within that session; afterwards, the same session will maintain the model that should be used for the current time period. After crossing a peak period boundary, the next LLM request will automatically switch to the new target model.

This Liang Wenfeng is so fucking awesome. I want to be Liang Wenfeng's dog.

# Changelog

## v1.1.0

### Added

* Supports configuring multiple sets of DeepSeek model Provider switch rules.
* For each rule, you can separately select:
* The DeepSeek V4 Pro Provider to use during off-peak hours.
* The DeepSeek V4 Flash Provider to use during peak hours.


* Supports adding multiple Pro/Flash switch combinations via `+` in the AstrBot WebUI plugin configuration page.
* `/deepseek_switch_status` and `/ds_switch_status` will now display:
* The Provider used in the current session.
* All configured switch rules.
* The target Provider that will be switched to in the current time period.



### Improved

* The plugin will automatically match the corresponding switch combination based on the Provider currently used in the session.
For example, if the following rules exist:
| Off-peak Provider | Peak Provider |
| --- | --- |
| DeepSeek V4 Pro A | DeepSeek V4 Flash A |
| DeepSeek V4 Pro B | DeepSeek V4 Flash B |


When the session is using `DeepSeek V4 Pro B`, entering the peak period will only switch to `DeepSeek V4 Flash B`, and will not switch to other combinations.
* When the current session Provider does not belong to any configured rule, the first group in the rule list is automatically used as the default rule.
* Maintains compatibility with the old single-group `deepseek_provider_id` and `peak_provider_id` configuration; old configurations can still be used after upgrading.

### Configuration Changes

Added the `provider_switch_rules` configuration item for managing multiple sets of model switch rules.

Each rule contains:

| Configuration Field | Description |
| --- | --- |
| `deepseek_provider_id` | The Provider used during off-peak hours, e.g., DeepSeek V4 Pro |
| `peak_provider_id` | The Provider used during peak hours, e.g., DeepSeek V4 Flash |