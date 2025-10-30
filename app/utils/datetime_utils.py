"""
タイムスタンプユーティリティ

このモジュールは、JSTタイムゾーンでのタイムスタンプ生成機能を提供します。
"""

from datetime import datetime, timezone, timedelta


# JSTタイムゾーン（UTC+09:00）
JST = timezone(timedelta(hours=9))


def get_current_jst_time() -> datetime:
    """
    JSTの現在時刻を秒単位精度で取得

    Returns:
        datetime: JSTタイムゾーン付きの現在時刻（マイクロ秒なし）

    Examples:
        >>> now = get_current_jst_time()
        >>> now.tzinfo
        datetime.timezone(datetime.timedelta(seconds=32400))
        >>> now.microsecond
        0
    """
    return datetime.now(JST).replace(microsecond=0)