from datetime import datetime, time, timedelta, timezone

from astrbot.api import AstrBotConfig, logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.provider import ProviderRequest
from astrbot.api.star import Context, Star, register
from astrbot.core.provider.entities import ProviderType


BEIJING_TZ = timezone(timedelta(hours=8), "Asia/Shanghai")
PEAK_WINDOWS = (
    (time(9, 0), time(12, 0)),
    (time(14, 0), time(18, 0)),
)


@register(
    "astrbot_plugin_deepseek_automatic_switch",
    "tiger",
    "DeepSeek V4 Pro 高峰期自动切换到备用模型，低峰期自动切回。",
    "v1.0.0",
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
        target_provider_id = self._get_target_provider_id()
        if not target_provider_id:
            logger.warning("[deepseek_switch] 目标模型未配置，跳过自动切换")
            return

        current_provider_id = await self._get_current_provider_id(umo)
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
        except Exception as exc:  # noqa: BLE001
            logger.error(f"[deepseek_switch] 切换 provider 失败: {exc}")

    def _get_target_provider_id(self) -> str:
        if self._is_peak_time():
            return str(self.config.get("peak_provider_id", "") or "").strip()
        return str(self.config.get("deepseek_provider_id", "") or "").strip()

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
        peak_provider = self.config.get("peak_provider_id", "") or "未配置"
        deepseek_provider = self.config.get("deepseek_provider_id", "") or "未配置"
        now = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d %H:%M:%S")
        target = self._get_target_provider_id() or "未配置"
        yield event.plain_result(
            "DeepSeek 自动切换状态\n"
            f"启用：{'是' if self.config.get('enabled', True) else '否'}\n"
            f"北京时间：{now}\n"
            f"当前时段：{'高峰期' if self._is_peak_time() else '低峰期'}\n"
            f"DeepSeek V4 Pro：{deepseek_provider}\n"
            f"高峰期备用模型：{peak_provider}\n"
            f"当前目标模型：{target}"
        )