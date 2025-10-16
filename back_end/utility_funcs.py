


def build_ext_filter(ext_map: dict[str, list[str]]) -> str:
    ext_parts = []
    for label, exts in ext_map.items():
        patterns = " ".join(f"*{ext}" for ext in exts)
        ext_parts.append(f"{label} ({patterns})")
    ext_parts.append(f"All (*)")
    return ";;".join(ext_parts)