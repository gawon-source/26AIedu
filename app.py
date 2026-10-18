# ── 페이지 목록을 한 곳에서만 정의 ───────────────────────────
PAGES = ["사건 브리핑", "수사실 (20건)", "내 수사 보고서", "상황실 (반 전체)", "AI 특성 사전"]

def _safe_page(value):
    """목록에 없는 값(옛 라벨·짧은 이름)이 들어와도 가장 비슷한 페이지로 보정한다."""
    if value in PAGES:
        return value
    if isinstance(value, str) and value.strip():
        key = value.split("(")[0].strip()
        for p in PAGES:
            if key and key in p:
                return p
    return PAGES[0]

ss.page = _safe_page(ss.get("page"))

page = st.sidebar.radio(
    "수사 메뉴",
    PAGES,
    index=PAGES.index(ss.page),
)
