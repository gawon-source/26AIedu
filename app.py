# -*- coding: utf-8 -*-
"""
AI 탐정소 (AI Detective Agency)
- 수업: "AI를 찾아라 - AI는 사람의 어떤 능력을 흉내 내는가?"
- 활동: 생활 속 사례 20장을 'AI다/아니다'로 판정 -> AI 특성 4종(인식/학습/추론/행동) 태깅
- 산출물: 개인 점수 기록, 내가 쓴 AI 정의 1문장, 반 전체 정답률 실시간 집계
실행:  streamlit run app.py
"""

import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------------
st.set_page_config(page_title="AI 탐정소", page_icon="🕵️", layout="wide")

DB_PATH = Path(__file__).parent / "ai_detective.db"
TEACHER_PIN = "1234"          # 선생님 모드 비밀번호 (수업 전에 바꿔 주세요)
JUDGE_POINT = 10              # 판정 점수
TAG_POINT = 10                # 태깅 점수(만점)

TRAITS = {
    "인식": {"emoji": "👀", "short": "보고 · 듣고 알아차리기",
             "ex": "카메라·마이크·센서로 바깥 세상의 정보를 받아들여요."},
    "학습": {"emoji": "📚", "short": "데이터로 스스로 배우기",
             "ex": "수많은 예시(데이터)를 보면서 규칙을 스스로 찾아내요."},
    "추론": {"emoji": "🧠", "short": "생각해서 판단하기",
             "ex": "배운 것을 바탕으로 '이건 ○○일 거야!' 하고 결론을 내려요."},
    "행동": {"emoji": "🦾", "short": "스스로 실행하기",
             "ex": "판단한 결과대로 움직이거나 결과물을 만들어 내요."},
}
TRAIT_KEYS = list(TRAITS.keys())

# ----------------------------------------------------------------------------
# 사건 파일 20장
# ----------------------------------------------------------------------------
CASES = [
    dict(id=1, emoji="📺", title="유튜브 추천 영상",
         desc="어제 축구 영상을 봤더니, 오늘 첫 화면이 축구 영상으로 가득 찼다.",
         is_ai=True, tags=["인식", "학습", "추론", "행동"],
         why="내가 본 영상 기록을 **인식**하고, 수많은 사람의 시청 데이터로 **학습**해서, "
             "'이 친구는 축구를 좋아할 것'이라고 **추론**한 뒤, 추천 목록을 직접 띄우는 **행동**까지 해요."),
    dict(id=2, emoji="🚪", title="편의점 자동문",
         desc="문 앞에 서면 센서가 나를 감지해서 문이 스르륵 열린다.",
         is_ai=False, tags=["인식", "행동"],
         why="사람이 있는지 **인식**하고 문을 여는 **행동**은 하지만, 배우지도(**학습**) 판단하지도(**추론**) 않아요. "
             "'움직이면 열어라'는 정해진 규칙 하나만 반복하는 기계예요."),
    dict(id=3, emoji="🤳", title="얼굴로 잠금 해제되는 스마트폰",
         desc="화면을 쳐다보기만 하면 내 얼굴을 알아보고 잠금이 풀린다.",
         is_ai=True, tags=["인식", "학습", "추론", "행동"],
         why="카메라로 얼굴을 **인식**하고, 내 얼굴 사진을 여러 장 **학습**해 두었다가, "
             "'주인이 맞다'고 **추론**해서 잠금을 푸는 **행동**을 해요."),
    dict(id=4, emoji="🧮", title="계산기",
         desc="7 × 8을 누르면 언제나 똑같이 56이 나온다.",
         is_ai=False, tags=[],
         why="사람이 만든 계산 규칙을 그대로 따를 뿐이에요. 스스로 배우거나(**학습**) "
             "상황을 보고 판단하는(**추론**) 일이 전혀 없어요. 아무리 많이 써도 더 똑똑해지지 않죠."),
    dict(id=5, emoji="🔊", title="AI 스피커",
         desc="\"불 꺼 줘\"라고 말하면 알아듣고 방 전등을 끈다.",
         is_ai=True, tags=["인식", "학습", "추론", "행동"],
         why="마이크로 목소리를 **인식**하고, 엄청난 양의 말소리를 **학습**해서, "
             "무슨 뜻인지 **추론**한 다음 전등을 끄는 **행동**을 해요."),
    dict(id=6, emoji="🚦", title="횡단보도 신호등",
         desc="30초마다 빨간불과 초록불이 정확히 번갈아 바뀐다.",
         is_ai=False, tags=[],
         why="정해진 시간표대로만 바뀌어요. 길에 사람이 많은지 적은지 보지도 않고, 배우지도 않습니다. "
             "(※ 차량 수를 인식해 스스로 시간을 바꾸는 'AI 신호등'은 AI예요!)"),
    dict(id=7, emoji="🌐", title="번역 앱",
         desc="영어 문장을 사진으로 찍으면 자연스러운 한국어로 바꿔 준다.",
         is_ai=True, tags=["인식", "학습", "추론"],
         why="글자를 **인식**하고, 수억 개의 번역 예시를 **학습**해서, 문맥에 맞는 뜻을 **추론**해요. "
             "스스로 움직이는 몸은 없으니 **행동**은 빼는 게 좋아요."),
    dict(id=8, emoji="💡", title="밤에 켜지는 가로등",
         desc="해가 져서 어두워지면 가로등이 저절로 켜진다.",
         is_ai=False, tags=["인식", "행동"],
         why="밝기를 **인식**하고 불을 켜는 **행동**을 하지만, '어두우면 켜라'는 한 가지 규칙만 따릅니다. "
             "어제보다 더 똑똑해지는 일은 없어요."),
    dict(id=9, emoji="🚌", title="자율주행 셔틀버스",
         desc="운전기사 없이 신호와 사람을 피해 스스로 달린다.",
         is_ai=True, tags=["인식", "학습", "추론", "행동"],
         why="카메라·센서로 길을 **인식**하고, 수많은 운전 데이터를 **학습**하고, "
             "'지금 멈춰야 한다'고 **추론**해서 브레이크를 밟는 **행동**까지 모두 해요. AI의 대표 선수!"),
    dict(id=10, emoji="⏰", title="알람 시계",
         desc="7시로 맞춰 두면 매일 아침 7시에 정확히 울린다.",
         is_ai=False, tags=[],
         why="사람이 정해 준 시각에 울리는 것뿐이에요. 내가 늦잠을 자든 말든 배우지 않고 판단하지 않습니다."),
    dict(id=11, emoji="📧", title="스팸 메일 자동 분류",
         desc="광고 메일이 알아서 '스팸함'으로 쏙 들어가 있다.",
         is_ai=True, tags=["인식", "학습", "추론", "행동"],
         why="메일 내용을 **인식**하고, 과거의 스팸 메일들을 **학습**해서, "
             "'이건 광고다'라고 **추론**한 뒤 스팸함으로 옮기는 **행동**을 해요."),
    dict(id=12, emoji="❄️", title="설정 온도를 지키는 에어컨",
         desc="24도로 맞춰 두면 24도가 되면 멈추고, 더워지면 다시 돌아간다.",
         is_ai=False, tags=["인식", "행동"],
         why="온도를 **인식**하고 바람을 켜고 끄는 **행동**을 하지만, '24도보다 높으면 켜라'는 규칙만 반복해요. "
             "내 생활 습관을 배우는 **학습**은 없습니다."),
    dict(id=13, emoji="🐶", title="사진 앱의 자동 앨범",
         desc="갤러리가 내 강아지 사진만 모아 '멍멍이' 앨범을 만들어 줬다.",
         is_ai=True, tags=["인식", "학습", "추론"],
         why="사진을 **인식**하고, 강아지 이미지를 잔뜩 **학습**해서, '같은 강아지다'라고 **추론**해 묶어 줘요."),
    dict(id=14, emoji="🧺", title="세탁기 '표준 코스'",
         desc="버튼을 누르면 늘 같은 순서로 빨고, 헹구고, 탈수한다.",
         is_ai=False, tags=[],
         why="정해진 순서(프로그램)를 그대로 따라 할 뿐이에요. 빨랫감을 보고 판단하지 않아요. "
             "(※ 옷의 무게와 오염도를 인식해 코스를 스스로 바꾸는 'AI 세탁기'는 또 달라요!)"),
    dict(id=15, emoji="💬", title="쇼핑몰 상담 챗봇",
         desc="\"환불하고 싶어요\"라고 쓰면 상황에 맞는 안내를 바로 보내 준다.",
         is_ai=True, tags=["인식", "학습", "추론", "행동"],
         why="내가 쓴 문장을 **인식**하고, 수많은 상담 기록을 **학습**해서, "
             "무엇을 원하는지 **추론**한 다음 답장을 보내는 **행동**을 해요."),
    dict(id=16, emoji="🧴", title="자동 손 소독기",
         desc="손을 내밀면 센서가 감지해서 소독액이 뿌려진다.",
         is_ai=False, tags=["인식", "행동"],
         why="손을 **인식**하고 분사하는 **행동**만 해요. 어제보다 더 나은 소독 방법을 배우지는 않죠."),
    dict(id=17, emoji="⚽", title="축구 오프사이드 AI 판독",
         desc="선수들의 몸 위치를 추적해 오프사이드인지 자동으로 알려 준다.",
         is_ai=True, tags=["인식", "학습", "추론"],
         why="여러 대의 카메라로 몸의 관절을 **인식**하고, 수많은 경기 영상을 **학습**해서, "
             "오프사이드 여부를 **추론**해요. 최종 선언은 심판이 하니 **행동**은 빼도 좋아요."),
    dict(id=18, emoji="🤖", title="집 구조를 기억하는 로봇청소기",
         desc="청소할수록 길을 익혀서 소파 다리를 안 부딪히고 빠르게 돈다.",
         is_ai=True, tags=["인식", "학습", "추론", "행동"],
         why="장애물을 **인식**하고, 청소할수록 집 지도를 **학습**하고, 최적 경로를 **추론**해서, "
             "스스로 돌아다니는 **행동**을 해요. '쓸수록 똑똑해진다'가 핵심 단서!"),
    dict(id=19, emoji="📝", title="영상 자동 자막",
         desc="말하는 목소리를 알아듣고 실시간으로 글자 자막을 만들어 준다.",
         is_ai=True, tags=["인식", "학습", "추론"],
         why="소리를 **인식**하고, 엄청난 양의 음성과 글자 짝을 **학습**해서, "
             "어떤 단어인지 **추론**해 글자로 적어 줘요."),
    dict(id=20, emoji="🎨", title="AI 그림 생성",
         desc="\"우주를 걷는 고양이\"라고 쓰면 세상에 없던 그림을 그려 준다.",
         is_ai=True, tags=["인식", "학습", "추론", "행동"],
         why="내가 쓴 글을 **인식**하고, 수억 장의 그림을 **학습**해서, 어떤 모양일지 **추론**한 뒤 "
             "새 그림을 만들어 내는 **행동**을 해요."),
]
CASE_BY_ID = {c["id"]: c for c in CASES}
TOTAL_CASES = len(CASES)
MAX_SCORE = TOTAL_CASES * (JUDGE_POINT + TAG_POINT)

RANKS = [
    (0.00, "🔍 수습 탐정", "이제 막 탐정 수첩을 받았어요. 다시 도전!"),
    (0.50, "🕵️ 초보 탐정", "AI의 냄새를 맡기 시작했어요!"),
    (0.70, "🎖️ 베테랑 탐정", "학습과 추론을 꽤 잘 구별하네요!"),
    (0.85, "🏅 명탐정", "AI의 4가지 능력을 거의 다 꿰뚫었어요!"),
    (0.95, "👑 AI 마스터 탐정", "완벽! 오늘부터 우리 반 AI 박사입니다!"),
]

# ----------------------------------------------------------------------------
# 데이터베이스 (반 전체 실시간 집계용)
# ----------------------------------------------------------------------------
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS responses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room TEXT, nickname TEXT, case_id INTEGER,
                judge_ok INTEGER, tag_match INTEGER,
                score REAL, picked TEXT, ts TEXT)
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS definitions(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                room TEXT, nickname TEXT, sentence TEXT,
                total REAL, ts TEXT)
        """)


def save_response(room, nickname, case_id, judge_ok, tag_match, score, picked):
    with get_conn() as conn:
        conn.execute("DELETE FROM responses WHERE room=? AND nickname=? AND case_id=?",
                     (room, nickname, case_id))
        conn.execute("""INSERT INTO responses
                        (room, nickname, case_id, judge_ok, tag_match, score, picked, ts)
                        VALUES (?,?,?,?,?,?,?,?)""",
                     (room, nickname, case_id, int(judge_ok), int(tag_match),
                      float(score), ",".join(picked), datetime.now().isoformat(timespec="seconds")))


def save_definition(room, nickname, sentence, total):
    with get_conn() as conn:
        conn.execute("DELETE FROM definitions WHERE room=? AND nickname=?", (room, nickname))
        conn.execute("""INSERT INTO definitions (room, nickname, sentence, total, ts)
                        VALUES (?,?,?,?,?)""",
                     (room, nickname, sentence, float(total),
                      datetime.now().isoformat(timespec="seconds")))


def load_responses(room=None):
    with get_conn() as conn:
        if room:
            return pd.read_sql_query("SELECT * FROM responses WHERE room=?", conn, params=(room,))
        return pd.read_sql_query("SELECT * FROM responses", conn)


def load_definitions(room=None):
    with get_conn() as conn:
        if room:
            return pd.read_sql_query("SELECT * FROM definitions WHERE room=? ORDER BY id DESC",
                                     conn, params=(room,))
        return pd.read_sql_query("SELECT * FROM definitions ORDER BY id DESC", conn)


def reset_room(room):
    with get_conn() as conn:
        conn.execute("DELETE FROM responses WHERE room=?", (room,))
        conn.execute("DELETE FROM definitions WHERE room=?", (room,))


init_db()

# ----------------------------------------------------------------------------
# 스타일
# ----------------------------------------------------------------------------
st.markdown("""
<style>
.block-container {max-width: 1080px; padding-top: 1.2rem;}
.hero {
  background:#1f2a44; color:#fff; border-radius:22px; padding:26px 28px; margin-bottom:14px;
  border:3px solid #ffd166;
}
.hero h1 {margin:0; font-size:34px; letter-spacing:-1px;}
.hero p {margin:6px 0 0; font-size:15px; opacity:.9;}
.case-card {
  background:#fffbeb; border:3px dashed #e0a800; border-radius:22px;
  padding:26px 28px; color:#3d2b00; text-align:center;
}
.case-emoji {font-size:70px; line-height:1;}
.case-no {font-size:14px; font-weight:800; color:#a07400; letter-spacing:1px;}
.case-title {font-size:28px; font-weight:900; margin:6px 0 8px; color:#2b2b2b;}
.case-desc {font-size:18px; line-height:1.6; color:#4b4b4b;}
.trait-box {
  border:2px solid #d6dbe6; border-radius:16px; padding:14px 16px; background:#f7f9fc;
  color:#22314d; min-height:118px;
}
.trait-box b {font-size:17px;}
.trait-box span {font-size:13px; color:#4a5a78;}
.ok-box {background:#e9f9ef; border:3px solid #34a853; border-radius:18px; padding:18px 22px; color:#14532d;}
.no-box {background:#fdecec; border:3px solid #ea4335; border-radius:18px; padding:18px 22px; color:#7f1d1d;}
.badge {display:inline-block; padding:4px 12px; border-radius:999px; font-size:13px; font-weight:800; margin-right:6px;}
.b-ai {background:#1f2a44; color:#ffd166;}
.b-no {background:#eceff4; color:#2b3a55;}
.score-pill {background:#ffd166; color:#3d2b00; font-weight:900; padding:8px 16px; border-radius:999px; display:inline-block;}
div.stButton > button {border-radius:14px; font-weight:800; padding:12px 8px; font-size:17px;}
.small {font-size:13px; color:#6b7280;}
</style>
""", unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# 세션 상태
# ----------------------------------------------------------------------------
def init_state():
    d = {
        "page": "입장", "room": "1반", "nickname": "",
        "idx": 0, "stage": "judge", "judge": None, "picked": [],
        "score": 0.0, "log": [], "hint": False, "saved_def": False,
    }
    for k, v in d.items():
        st.session_state.setdefault(k, v)


init_state()
ss = st.session_state


def reset_game():
    ss.idx, ss.stage, ss.judge, ss.picked = 0, "judge", None, []
    ss.score, ss.log, ss.hint, ss.saved_def = 0.0, [], False, False


def rank_of(ratio):
    name, msg = RANKS[0][1], RANKS[0][2]
    for cut, n, m in RANKS:
        if ratio >= cut:
            name, msg = n, m
    return name, msg


# ----------------------------------------------------------------------------
# 사이드바
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🕵️ AI 탐정소")
    st.caption("4-1-1 · AI를 찾아라")
    pages = ["입장", "사건 수사", "내 수사 결과", "반 전체 현황", "AI 특성 사전"]
    ss.page = st.radio("메뉴", pages, index=pages.index(ss.page), label_visibility="collapsed")

    st.divider()
    if ss.nickname:
        st.success(f"**{ss.room} / {ss.nickname}** 탐정님\n\n진행 {len(ss.log)} / {TOTAL_CASES}")
        st.metric("현재 점수", f"{ss.score:.1f} 점")
    else:
        st.info("먼저 **입장** 메뉴에서 이름을 등록하세요.")

    st.divider()
    with st.expander("👩‍🏫 선생님 모드"):
        pin = st.text_input("비밀번호", type="password", key="pin")
        if pin == TEACHER_PIN:
            st.caption(f"DB: {DB_PATH.name}")
            target = st.text_input("초기화할 반", value=ss.room, key="reset_room")
            if st.button("🗑️ 해당 반 기록 삭제", use_container_width=True):
                reset_room(target)
                st.success(f"{target} 기록을 비웠습니다.")
        elif pin:
            st.error("비밀번호가 달라요.")


# ----------------------------------------------------------------------------
# 1) 입장
# ----------------------------------------------------------------------------
def page_enter():
    st.markdown("""
    <div class="hero">
      <h1>🕵️ AI 탐정소 · 사건번호 4-1-1</h1>
      <p>"요즘 세상엔 AI인 척하는 기계가 너무 많다!"<br>
      생활 속 사례 <b>20장</b>을 보고 <b>AI인지 아닌지</b> 판정하고,
      AI의 능력 <b>4가지(인식·학습·추론·행동)</b>로 태그를 붙여 주세요.</p>
    </div>
    """, unsafe_allow_html=True)

    c = st.columns(4)
    for col, k in zip(c, TRAIT_KEYS):
        t = TRAITS[k]
        col.markdown(f"""<div class="trait-box">{t['emoji']} <b>{k}</b><br>
        <span>{t['short']}<br>{t['ex']}</span></div>""", unsafe_allow_html=True)

    st.write("")
    st.markdown("#### 🪪 탐정 등록")
    a, b = st.columns([1, 2])
    ss.room = a.text_input("반 (같은 반끼리 점수가 모여요)", value=ss.room)
    ss.nickname = b.text_input("내 이름 또는 탐정 별명", value=ss.nickname,
                               placeholder="예: 1-3 김하늘 / 추리왕하늘")

    st.markdown("""
    <span class="small">
    ⏱️ 사건 1장당 2단계 &nbsp;|&nbsp; ① AI다 / AI 아니다 판정(10점)
    &nbsp;② AI 특성 태깅(최대 10점) &nbsp;|&nbsp; 만점 400점
    </span>
    """, unsafe_allow_html=True)
    st.write("")

    if st.button("🚀 수사 시작!", type="primary", use_container_width=True):
        if not ss.nickname.strip() or not ss.room.strip():
            st.error("반과 이름을 모두 적어 주세요!")
        else:
            reset_game()
            ss.page = "사건 수사"
            st.rerun()

    with st.expander("💡 탐정 필살 요령 (헷갈릴 때 이것만 기억!)"):
        st.markdown("""
        - **학습**과 **추론**이 둘 다 있으면 → **AI일 가능성이 매우 높아요.**
        - **인식 + 행동**만 있으면 → 그냥 **센서 기계**예요. (자동문, 가로등처럼요)
        - 결정적 단서 질문 2개
            1. **"쓸수록 똑똑해지나요?"** → 예 = 학습 O
            2. **"상황마다 다르게 판단하나요?"** → 예 = 추론 O
        """)


# ----------------------------------------------------------------------------
# 2) 사건 수사
# ----------------------------------------------------------------------------
def page_quiz():
    if not ss.nickname.strip():
        st.warning("먼저 **입장** 메뉴에서 탐정 등록을 해 주세요!")
        return

    if ss.idx >= TOTAL_CASES:
        st.balloons()
        st.success("20장 수사 완료! **내 수사 결과** 메뉴에서 성적과 AI 정의를 작성하세요.")
        if st.button("📄 내 수사 결과 보기", type="primary", use_container_width=True):
            ss.page = "내 수사 결과"
            st.rerun()
        return

    case = CASES[ss.idx]
    st.progress(ss.idx / TOTAL_CASES, text=f"사건 {ss.idx + 1} / {TOTAL_CASES}")
    top1, top2 = st.columns([3, 1])
    top1.markdown(f"#### 🗂️ 사건 파일 제{case['id']}호")
    top2.markdown(f"<div style='text-align:right'><span class='score-pill'>⭐ {ss.score:.1f}점</span></div>",
                  unsafe_allow_html=True)

    st.markdown(f"""
    <div class="case-card">
      <div class="case-emoji">{case['emoji']}</div>
      <div class="case-no">CASE #{case['id']:02d}</div>
      <div class="case-title">{case['title']}</div>
      <div class="case-desc">{case['desc']}</div>
    </div>
    """, unsafe_allow_html=True)
    st.write("")

    # --- 1단계: 판정 ---
    if ss.stage == "judge":
        st.markdown("##### 🔎 1단계 · 이것은 AI일까요?")
        c1, c2 = st.columns(2)
        if c1.button("🤖 AI 다!", use_container_width=True, type="primary"):
            ss.judge = True
            ss.stage = "tag"
            st.rerun()
        if c2.button("⚙️ AI 아니다!", use_container_width=True):
            ss.judge = False
            ss.stage = "tag"
            st.rerun()

        if st.button("💡 힌트 보기", use_container_width=True):
            ss.hint = not ss.hint
            st.rerun()
        if ss.hint:
            st.info("**쓸수록 똑똑해지나요?(학습)** 그리고 **상황마다 다르게 판단하나요?(추론)** "
                    "두 질문에 모두 '예'라면 AI예요!")

    # --- 2단계: 태깅 ---
    elif ss.stage == "tag":
        st.markdown(f"##### 🏷️ 2단계 · 내 판정: **{'🤖 AI 다' if ss.judge else '⚙️ AI 아니다'}**")
        st.caption("이 사례가 **가지고 있는 능력**을 모두 골라 주세요. (하나도 없으면 비워 두세요)")
        cols = st.columns(4)
        picked = []
        for col, k in zip(cols, TRAIT_KEYS):
            t = TRAITS[k]
            with col:
                if st.checkbox(f"{t['emoji']} **{k}**", key=f"tag_{case['id']}_{k}"):
                    picked.append(k)
                st.markdown(f"<span class='small'>{t['short']}</span>", unsafe_allow_html=True)

        st.write("")
        b1, b2 = st.columns([1, 3])
        if b1.button("↩️ 판정 다시", use_container_width=True):
            ss.stage = "judge"
            st.rerun()
        if b2.button("✅ 제출하고 정답 확인", type="primary", use_container_width=True):
            answer_tags = case["tags"]
            judge_ok = (ss.judge == case["is_ai"])
            match = sum(1 for k in TRAIT_KEYS if (k in picked) == (k in answer_tags))
            gained = (JUDGE_POINT if judge_ok else 0) + TAG_POINT * match / 4
            ss.score += gained
            ss.picked = picked
            ss.log.append(dict(case_id=case["id"], title=case["title"],
                               judge_ok=judge_ok, tag_match=match,
                               gained=round(gained, 1), picked=list(picked)))
            save_response(ss.room, ss.nickname, case["id"], judge_ok, match, gained, picked)
            ss.stage = "feedback"
            st.rerun()

    # --- 3단계: 피드백 ---
    else:
        rec = ss.log[-1]
        case = CASE_BY_ID[rec["case_id"]]
        ans_label = "🤖 AI 입니다" if case["is_ai"] else "⚙️ AI가 아닙니다"
        box = "ok-box" if rec["judge_ok"] else "no-box"
        head = "정답! 👏" if rec["judge_ok"] else "아쉬워요 😅"
        tag_txt = " ".join(f"{TRAITS[k]['emoji']}{k}" for k in case["tags"]) or "없음"
        my_txt = " ".join(f"{TRAITS[k]['emoji']}{k}" for k in rec["picked"]) or "없음"

        st.markdown(f"""
        <div class="{box}">
          <h3 style="margin:0 0 6px">{head} 정답은 <b>{ans_label}</b></h3>
          <p style="margin:0; font-size:16px">{case['why']}</p>
        </div>
        """, unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        m1.metric("판정 점수", f"{JUDGE_POINT if rec['judge_ok'] else 0} / {JUDGE_POINT}")
        m2.metric("태깅 정확도", f"{rec['tag_match']} / 4 개")
        m3.metric("이번 사건 획득", f"{rec['gained']} 점")
        st.markdown(f"**정답 태그:** {tag_txt} &nbsp;&nbsp;|&nbsp;&nbsp; **내 태그:** {my_txt}")

        label = "➡️ 다음 사건으로" if ss.idx + 1 < TOTAL_CASES else "🏁 수사 종료하고 결과 보기"
        if st.button(label, type="primary", use_container_width=True):
            ss.idx += 1
            ss.stage, ss.judge, ss.picked, ss.hint = "judge", None, [], False
            if ss.idx >= TOTAL_CASES:
                ss.page = "내 수사 결과"
            st.rerun()


# ----------------------------------------------------------------------------
# 3) 내 수사 결과 + AI 정의 1문장
# ----------------------------------------------------------------------------
def page_result():
    if not ss.log:
        st.info("아직 수사 기록이 없어요. **사건 수사** 메뉴에서 시작해 보세요!")
        return

    df = pd.DataFrame(ss.log)
    done = len(df)
    ratio = ss.score / (done * (JUDGE_POINT + TAG_POINT))
    rname, rmsg = rank_of(ratio)

    st.markdown(f"""
    <div class="hero">
      <h1>{rname}</h1>
      <p>{ss.room} · {ss.nickname} 탐정 &nbsp;|&nbsp; {rmsg}</p>
    </div>
    """, unsafe_allow_html=True)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("총점", f"{ss.score:.1f} 점", f"만점 {done * 20}점")
    k2.metric("판정 정답", f"{int(df['judge_ok'].sum())} / {done} 개")
    k3.metric("판정 정답률", f"{df['judge_ok'].mean() * 100:.0f} %")
    k4.metric("태깅 정확도", f"{df['tag_match'].mean() / 4 * 100:.0f} %")

    st.markdown("##### 📋 사건별 기록")
    view = df.assign(
        판정=lambda d: d["judge_ok"].map({True: "⭕ 정답", False: "❌ 오답"}),
        태깅=lambda d: d["tag_match"].astype(str) + " / 4",
        내태그=lambda d: d["picked"].map(lambda p: ", ".join(p) if p else "없음"),
    )[["case_id", "title", "판정", "태깅", "내태그", "gained"]]
    view.columns = ["번호", "사건", "AI 판정", "특성 태깅", "내가 고른 태그", "획득 점수"]
    st.dataframe(view, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### ✍️ 산출물 · 내가 만든 **AI 정의 1문장**")
    st.caption("아래 빈칸을 채우면 문장이 자동으로 만들어져요. 마음에 들면 그대로, 아니면 직접 고쳐 쓰세요!")

    c1, c2, c3, c4 = st.columns(4)
    w1 = c1.text_input("👀 무엇을 인식해서", "사람의 말과 사진을")
    w2 = c2.text_input("📚 무엇으로 배우고", "수많은 데이터로")
    w3 = c3.text_input("🧠 무엇을 판단해서", "상황에 맞는 답을")
    w4 = c4.text_input("🦾 무엇을 스스로 하는", "일을 대신 해 주는")
    draft = f"AI는 {w1} 인식하고, {w2} 스스로 배워서, {w3} 추론하고, {w4} 기계(프로그램)이다."
    st.info(f"**자동 완성 문장 →** {draft}")

    sentence = st.text_area("나의 AI 정의 (1문장)", value=draft, height=90, key="my_def")
    if st.button("💾 제출하고 반 게시판에 올리기", type="primary", use_container_width=True):
        if len(sentence.strip()) < 10:
            st.error("문장을 조금 더 길게 써 주세요!")
        else:
            save_definition(ss.room, ss.nickname, sentence.strip(), ss.score)
            ss.saved_def = True
            st.success("제출 완료! **반 전체 현황**에서 친구들 문장도 볼 수 있어요.")

    report = (
        f"[AI 탐정소 개인 점수 기록]\n"
        f"반: {ss.room}\n이름: {ss.nickname}\n"
        f"날짜: {datetime.now():%Y-%m-%d %H:%M}\n"
        f"총점: {ss.score:.1f} / {done * 20}  ({ratio * 100:.0f}%)\n"
        f"계급: {rname}\n"
        f"판정 정답: {int(df['judge_ok'].sum())}/{done}  |  태깅 정확도: {df['tag_match'].mean() / 4 * 100:.0f}%\n"
        f"나의 AI 정의: {sentence.strip()}\n\n"
        + view.to_string(index=False)
    )
    st.download_button("⬇️ 내 점수 기록 내려받기 (txt)", report.encode("utf-8"),
                       file_name=f"AI탐정소_{ss.room}_{ss.nickname}.txt",
                       use_container_width=True)

    st.write("")
    if st.button("🔄 처음부터 다시 수사하기", use_container_width=True):
        for c in CASES:
            for k in TRAIT_KEYS:
                st.session_state.pop(f"tag_{c['id']}_{k}", None)
        reset_game()
        ss.page = "사건 수사"
        st.rerun()


# ----------------------------------------------------------------------------
# 4) 반 전체 현황 (실시간 집계)
# ----------------------------------------------------------------------------
def render_board(room):
    df = load_responses(room)
    if df.empty:
        st.info("아직 제출된 기록이 없어요. 친구들이 수사를 시작하면 여기에 실시간으로 쌓입니다!")
        return

    n_students = df["nickname"].nunique()
    acc = df["judge_ok"].mean() * 100
    tag_acc = df["tag_match"].mean() / 4 * 100

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("참여 탐정", f"{n_students} 명")
    c2.metric("총 제출 수", f"{len(df)} 건")
    c3.metric("반 평균 판정 정답률", f"{acc:.1f} %")
    c4.metric("반 평균 태깅 정확도", f"{tag_acc:.1f} %")
    st.caption(f"마지막 갱신 {datetime.now():%H:%M:%S} · 5초마다 자동 새로고침")

    t1, t2, t3, t4 = st.tabs(["📊 사건별 정답률", "🏆 명예의 전당", "🏷️ 특성별 정확도", "✍️ 우리 반 AI 정의"])

    with t1:
        g = (df.groupby("case_id")
               .agg(정답률=("judge_ok", "mean"), 제출수=("judge_ok", "size"),
                    태깅정확도=("tag_match", "mean"))
               .reset_index())
        g["사건"] = g["case_id"].map(lambda i: f"{i:02d}. {CASE_BY_ID[i]['title']}")
        g["정답률"] = (g["정답률"] * 100).round(1)
        g["태깅정확도"] = (g["태깅정확도"] / 4 * 100).round(1)
        g["유형"] = g["case_id"].map(lambda i: "AI" if CASE_BY_ID[i]["is_ai"] else "AI 아님")
        st.bar_chart(g.set_index("사건")[["정답률"]], height=320)
        hard = g.sort_values("정답률").head(3)
        st.warning("**가장 많이 틀린 사건 TOP 3** → " +
                   " / ".join(f"{r['사건']} ({r['정답률']}%)" for _, r in hard.iterrows()))
        st.dataframe(g[["사건", "유형", "제출수", "정답률", "태깅정확도"]],
                     use_container_width=True, hide_index=True)

    with t2:
        rank = (df.groupby("nickname")
                  .agg(점수=("score", "sum"), 푼문항=("case_id", "nunique"),
                       판정정답=("judge_ok", "sum"))
                  .reset_index()
                  .sort_values("점수", ascending=False))
        rank["점수"] = rank["점수"].round(1)
        rank.insert(0, "순위", ["🥇", "🥈", "🥉"][:len(rank)] + list(range(4, len(rank) + 1)))
        rank.columns = ["순위", "탐정", "점수", "푼 사건", "판정 정답 수"]
        st.dataframe(rank, use_container_width=True, hide_index=True)

    with t3:
        rows = []
        for k in TRAIT_KEYS:
            hit = tot = 0
            for _, r in df.iterrows():
                ans = k in CASE_BY_ID[int(r["case_id"])]["tags"]
                mine = k in (r["picked"].split(",") if r["picked"] else [])
                hit += int(ans == mine)
                tot += 1
            rows.append({"특성": f"{TRAITS[k]['emoji']} {k}",
                         "정확도": round(hit / tot * 100, 1) if tot else 0.0})
        tdf = pd.DataFrame(rows)
        st.bar_chart(tdf.set_index("특성"), height=260)
        low = tdf.sort_values("정확도").iloc[0]
        st.info(f"우리 반이 가장 어려워하는 특성은 **{low['특성']}** ({low['정확도']}%) 입니다. "
                f"이 특성을 함께 다시 정리해 봐요!")

    with t4:
        ddf = load_definitions(room)
        if ddf.empty:
            st.info("아직 제출된 AI 정의가 없어요.")
        else:
            st.caption(f"총 {len(ddf)}명 제출")
            for _, r in ddf.iterrows():
                st.markdown(f"""<div class="trait-box" style="min-height:0; margin-bottom:8px">
                <b>🕵️ {r['nickname']}</b> <span class="small">({r['total']:.0f}점)</span><br>
                <span style="font-size:15px">“{r['sentence']}”</span></div>""",
                            unsafe_allow_html=True)
            st.download_button("⬇️ 우리 반 AI 정의 모음 내려받기 (csv)",
                               ddf[["nickname", "sentence", "total", "ts"]]
                               .to_csv(index=False).encode("utf-8-sig"),
                               file_name=f"AI정의_{room}.csv", use_container_width=True)


def page_class():
    st.markdown("### 🏫 우리 반 실시간 현황판")
    room = st.text_input("볼 반 이름", value=ss.room, key="board_room")
    live = st.toggle("🔴 실시간 자동 갱신", value=True)
    if live and hasattr(st, "fragment"):
        st.fragment(run_every=5)(render_board)(room)
    else:
        if st.button("🔄 새로고침", use_container_width=True):
            st.rerun()
        render_board(room)


# ----------------------------------------------------------------------------
# 5) AI 특성 사전
# ----------------------------------------------------------------------------
def page_dict():
    st.markdown("### 📖 AI 특성 사전 · AI는 사람의 어떤 능력을 흉내 낼까?")
    st.markdown("사람은 **보고(인식) → 배우고(학습) → 생각하고(추론) → 행동한다**. "
                "AI는 바로 이 네 단계를 기계로 흉내 냅니다.")
    for k in TRAIT_KEYS:
        t = TRAITS[k]
        with st.expander(f"{t['emoji']} **{k}** — {t['short']}", expanded=True):
            st.markdown(f"- **뜻:** {t['ex']}")
            samples = [c for c in CASES if k in c["tags"]][:4]
            st.markdown("- **이런 사례에 있어요:** " +
                        ", ".join(f"{c['emoji']} {c['title']}" for c in samples))
    st.divider()
    st.markdown("""
    #### 🧭 AI와 '그냥 기계' 구별 기준
    | 질문 | AI | 그냥 기계(센서·규칙) |
    |---|---|---|
    | 쓸수록 똑똑해지나요? | ⭕ 데이터로 **학습** | ❌ 늘 그대로 |
    | 상황마다 다르게 판단하나요? | ⭕ **추론** | ❌ 정해진 규칙만 |
    | 정답을 사람이 다 정해 줬나요? | ❌ 스스로 규칙 발견 | ⭕ 사람이 전부 입력 |

    👉 한 줄 정리: **인식 + 행동만 있으면 센서 기계, 여기에 학습 + 추론이 더해지면 AI!**
    """)
    with st.expander("🗂️ 사건 파일 20장 정답표 (선생님/복습용)"):
        tb = pd.DataFrame([{
            "번호": c["id"], "사건": f"{c['emoji']} {c['title']}",
            "정답": "🤖 AI" if c["is_ai"] else "⚙️ AI 아님",
            "특성 태그": ", ".join(c["tags"]) or "없음",
        } for c in CASES])
        st.dataframe(tb, use_container_width=True, hide_index=True)


# ----------------------------------------------------------------------------
# 라우팅
# ----------------------------------------------------------------------------
if ss.page == "입장":
    page_enter()
elif ss.page == "사건 수사":
    page_quiz()
elif ss.page == "내 수사 결과":
    page_result()
elif ss.page == "반 전체 현황":
    page_class()
else:
    page_dict()
