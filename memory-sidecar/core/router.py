from __future__ import annotations


def select_partition(text: str) -> str:
    lowered = text.lower()
    programming = (
        "code", "bug", "python", "memory", "dev", "function", "class", "json", "module",
        "代码", "报错", "编程", "开发", "函数", "类", "模块", "内存", "系统", "调试",
    )
    science = (
        "math", "physics", "logic", "theorem", "proof",
        "数学", "物理", "逻辑", "定理", "证明", "科学",
    )
    finance = (
        "money", "market", "stock", "trading", "economy",
        "钱", "市场", "股票", "交易", "经济", "金融",
    )
    if any(keyword in lowered for keyword in programming):
        return "programming"
    if any(keyword in lowered for keyword in science):
        return "science"
    if any(keyword in lowered for keyword in finance):
        return "finance"
    return "general"
