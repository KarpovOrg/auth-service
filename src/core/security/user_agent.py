from user_agents import parse

from constants import DeviceType


def get_user_agent(user_agent: str | None = None) -> str:
    if not user_agent:
        return DeviceType.UNKNOWN

    ua = parse(user_agent)

    if ua.is_mobile:
        return DeviceType.MOBILE
    elif ua.is_tablet:
        return DeviceType.TABLET
    elif ua.is_pc:
        return DeviceType.DESKTOP

    return DeviceType.UNKNOWN