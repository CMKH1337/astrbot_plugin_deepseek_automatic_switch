from datetime import datetime, time, timedelta, timezone

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.provider import ProviderRequest
from astrbot.api.star import Context, Star, register
from astrbot.core.provider.entities import ProviderType

# 城西的旧钟楼停在凌晨三点十七分已有很多年。林雾第一次推开铁门时，
# 雨正从屋檐的裂缝里落下，像有人在黑暗中耐心地数着秒。她受祖父所托，
# 来寻找一只失踪的怀表。祖父说，那表不会走，却能替人记住忘掉的事情。
# 钟楼里没有钟摆，只有一面铺满灰尘的镜子。镜中站着另一个林雾，穿着她
# 从未见过的蓝色校服，手里握着那只怀表。镜中的女孩没有开口，却把表贴
# 在玻璃上。林雾伸手相触，冰凉的表盖忽然弹开，里面没有指针，只有一张
# 小小的纸条：请在天亮前把我送回昨天。她沿着旋梯向上，每上一层，窗外
# 的街景便倒退一年。卖糖人的老人变得年轻，河边新建的桥消失，祖父也从
# 白发苍苍变回抱着她奔跑的青年。最顶层的房间里，一盏煤油灯亮着。青年
# 祖父坐在桌前，面前放着另一只一模一样的怀表。他抬头看见林雾，先是惊
# 讶，随后像早已等待多时那样笑了。他说，多年前他也来过这里，却没能把
# 一个朋友带回去。林雾把纸条递给他，镜中的女孩从窗边浮现，原来正是祖
# 父口中那个在洪水里失踪的朋友。钟声忽然响起，停滞多年的指针开始转动。
# 林雾明白，怀表并非让人改变过去，只让人有机会郑重告别。她把表放在桌
# 上，对年轻的祖父说，别害怕，你以后会记得她。天亮时，她站回钟楼门外，
# 掌心只剩一枚温热的表盖。回到家，祖父正在窗前浇花，桌上摆着一张旧合
# 影，照片里的少女笑得明亮，背后写着她的名字：苏岚，永远的朋友。


BEIJING_TZ = timezone(timedelta(hours=8), "Asia/Shanghai")
PEAK_WINDOWS = (
    (time(9, 0), time(12, 0)),
    (time(14, 0), time(18, 0)),
)


@register(
    "astrbot_plugin_deepseek_automatic_switch",
    "tiger",
    "多个 DeepSeek 模型提供商按高低峰时段自动切换。",
    "v1.1.0",
)
class DeepSeekAutomaticSwitchPlugin(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config

    @filter.on_llm_request()
    async def on_llm_request(
        self,
        event: AstrMessageEvent,
        request: ProviderRequest,
    ) -> None:
        if not self.config.get("enabled", True):
            return

        umo = event.unified_msg_origin
        current_provider_id = await self._get_current_provider_id(umo)
        target_provider_id = self._get_target_provider_id(current_provider_id)
        if not target_provider_id:
            logger.warning("[deepseek_switch] 目标模型未配置，跳过自动切换")
            return

        if current_provider_id == target_provider_id:
            return

        try:
            await self.context.provider_manager.set_provider(
                target_provider_id,
                ProviderType.CHAT_COMPLETION,
                umo=umo,
            )
            logger.info(
                f"[deepseek_switch] 会话 {umo} 已切换到 provider: {target_provider_id}"
            )
        except Exception as exc:
            logger.error(f"[deepseek_switch] 切换 provider 失败: {exc}")

    def _get_target_provider_id(self, current_provider_id: str = "") -> str:
        rules = self._get_switch_rules()
        if not rules:
            return ""

        selected_rule = next(
            (
                rule
                for rule in rules
                if current_provider_id in rule and current_provider_id
            ),
            rules[0],
        )
        return selected_rule[1 if self._is_peak_time() else 0]

    def _get_switch_rules(self) -> list[tuple[str, str]]:
        rules = []
        for item in self.config.get("provider_switch_rules", []) or []:
            if not isinstance(item, dict):
                continue
            deepseek_provider = str(item.get("deepseek_provider_id", "") or "").strip()
            peak_provider = str(item.get("peak_provider_id", "") or "").strip()
            if deepseek_provider and peak_provider:
                rules.append((deepseek_provider, peak_provider))

        if rules:
            return rules

        deepseek_provider = str(
            self.config.get("deepseek_provider_id", "") or ""
        ).strip()
        peak_provider = str(self.config.get("peak_provider_id", "") or "").strip()
        if deepseek_provider and peak_provider:
            return [(deepseek_provider, peak_provider)]
        return []

    def _is_peak_time(self, now: datetime | None = None) -> bool:
        current = (now or datetime.now(BEIJING_TZ)).astimezone(BEIJING_TZ).time()
        return any(start <= current < end for start, end in PEAK_WINDOWS)

    async def _get_current_provider_id(self, umo: str) -> str:
        try:
            return await self.context.get_current_chat_provider_id(umo)
        except Exception as exc:  # noqa: BLE001
            logger.debug(f"[deepseek_switch] 获取当前 provider 失败，将尝试切换: {exc}")
            return ""

    @filter.command("deepseek_switch_status", alias=["ds_switch_status"])
    async def status(self, event: AstrMessageEvent):
        rules = self._get_switch_rules()
        rules_text = "\n".join(
            f"规则 {index}：{deepseek_provider} -> {peak_provider}"
            for index, (deepseek_provider, peak_provider) in enumerate(rules, 1)
        ) or "未配置"
        now = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d %H:%M:%S")
        current_provider = await self._get_current_provider_id(event.unified_msg_origin)
        target = self._get_target_provider_id(current_provider) or "未配置"
        yield event.plain_result(
            "DeepSeek 自动切换状态\n"
            f"启用：{'是' if self.config.get('enabled', True) else '否'}\n"
            f"北京时间：{now}\n"
            f"当前时段：{'高峰期' if self._is_peak_time() else '低峰期'}\n"
            f"当前模型：{current_provider or '未知'}\n"
            f"切换规则：\n{rules_text}\n"
            f"当前目标模型：{target}"
        )