# -*- coding: utf-8 -*-
# AI 탐정소 - 사건번호 4-1-1 : 인공지능의 개념과 특성
# 실행: streamlit run app.py

import os
import sqlite3
import datetime
import streamlit as st

# =====================================================================
# 0. 기본 설정 (ss 를 쓰지 않는 영역)
# =====================================================================
TEACHER_PIN = "1234"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai_detective.db")

PAGES = ["사건 브리핑", "수사실 (20건)", "내 수사 보고서", "상황실 (반 전체)", "AI 특성 사전"]

CLASS_OPTIONS = [f"{i}반" for i in range(1, 11)]
NUM_OPTIONS = [f"{i}번" for i in range(1, 36)]

TRAITS = ["인식", "학습", "추론", "행동"]
NONE_TRAIT = "해당 없음 (정해진 규칙대로만 작동)"
TRAIT_OPTIONS = TRAITS + [NONE_TRAIT]

JUDGE_POINT = 10
TRAIT_POINT = 10

TRAIT_DESC = {
    "인식": "보고 듣고 알아차린다 (눈과 귀의 역할)",
    "학습": "많은 자료를 보며 스스로 실력이 늘어난다",
    "추론": "알아낸 것을 바탕으로 따져 보고 판단한다",
    "행동": "판단한 결과대로 스스로 움직인다",
}

# ---------------------------------------------------------------------
# 사건 파일 20건  (정답 특성은 사건마다 '단 하나')
# ---------------------------------------------------------------------
CASES = [
    dict(no=1, title="잠긴 스마트폰이 열렸다", body="책상 위 스마트폰이 주인의 얼굴을 비추자 1초도 안 되어 잠금이 풀렸다. 형제가 얼굴을 비추었을 때는 열리지 않았다.",
         is_ai=True, trait="인식",
         why="카메라로 들어온 얼굴을 '누구인지' 알아차리는 일이 핵심이다. 사람의 눈과 같은 능력을 흉내 낸 것이므로 인식이다."),
    dict(no=2, title="사라진 강아지 사진이 한곳에 모였다", body="사진이 3,000장 들어 있는 앱에서 '강아지'를 검색하자 강아지가 나온 사진만 42장이 모였다. 직접 이름을 붙인 적은 없었다.",
         is_ai=True, trait="인식",
         why="사진 속 내용이 무엇인지 알아보는 것이 핵심이다. 사람이 이름을 붙여 준 적이 없는데도 구별했으므로 인식이다."),
    dict(no=3, title="말을 알아듣는 스피커", body="거실 스피커에게 '내일 아침 7시에 깨워 줘'라고 말하자 알람이 설정되었다. 사투리로 말해도 알아들었다.",
         is_ai=True, trait="인식",
         why="귀로 들어온 소리를 말로 알아듣는 일이 핵심이다. 사람의 듣는 능력을 흉내 낸 것이므로 인식이다."),
    dict(no=4, title="내 취향을 꿰뚫은 추천 목록", body="어제 축구 영상을 세 편 보았더니, 오늘 첫 화면이 축구 영상으로 가득 찼다. 지난주에는 요리 영상만 떠 있었다.",
         is_ai=True, trait="학습",
         why="내가 본 기록이 쌓일수록 추천이 달라졌다. 자료가 많아질수록 더 잘 맞히게 되는 것이 학습이다."),
    dict(no=5, title="내 말투를 외워 버린 키보드", body="메시지를 쓰려고 '오늘'까지만 쳤는데 '오늘 떡볶이 먹을래?'가 추천으로 떴다. 내가 자주 쓰는 말이었다.",
         is_ai=True, trait="학습",
         why="내가 평소 쓴 문장을 바탕으로 다음 말을 예상했다. 사용할수록 정확해지므로 학습이다."),
    dict(no=6, title="광고 메일만 걸러 낸 그물", body="하루에 100통씩 오던 광고 메일이 스팸함으로 자동 분류됐다. 내가 '스팸 신고'를 누를수록 걸러내는 솜씨가 좋아졌다.",
         is_ai=True, trait="학습",
         why="신고 자료가 쌓일수록 분류 실력이 좋아졌다. 경험으로 성능이 올라가는 것이 학습이다."),
    dict(no=7, title="문장을 건너뛴 번역기", body="'나는 배가 고프다'를 입력하자 영어 문장이 나왔다. 단어를 하나씩 바꾼 것이 아니라 문장 전체의 뜻에 맞게 어순까지 바꾸었다.",
         is_ai=True, trait="추론",
         why="문장 전체의 뜻을 따져 보고 가장 알맞은 표현을 골라냈다. 뜻을 헤아려 판단했으므로 추론이다."),
    dict(no=8, title="의사보다 먼저 찾아낸 그림자", body="병원에서 찍은 가슴 사진을 컴퓨터가 먼저 살펴보고 '이 부분을 다시 확인해 보세요'라고 표시했다.",
         is_ai=True, trait="추론",
         why="본 것을 근거로 '의심된다'는 판단을 내렸다. 알아낸 정보로 결론을 끌어낸 것이므로 추론이다."),
    dict(no=9, title="바둑판 위의 수수께끼 한 수", body="바둑 대결에서 컴퓨터가 사람이 생각하지 못한 자리에 돌을 놓았다. 100수 뒤를 따져 가장 유리한 자리를 고른 것이었다.",
         is_ai=True, trait="추론",
         why="여러 경우를 따져 가장 좋은 선택을 결정했다. 판단하고 결정하는 일이 중심이므로 추론이다."),
    dict(no=10, title="운전자가 손을 놓은 자동차", body="고속도로에서 운전자가 손을 떼었는데도 차가 차선을 유지하고, 앞차가 멈추자 스스로 브레이크를 밟았다.",
         is_ai=True, trait="행동",
         why="판단한 결과대로 핸들과 브레이크를 직접 움직였다. 스스로 움직여 일을 해내므로 행동이다."),
    dict(no=11, title="집 구조를 외운 청소기", body="로봇청소기가 처음에는 벽에 부딪혔지만, 며칠 뒤에는 방 구조를 파악해 지그재그로 빠짐없이 청소했다.",
         is_ai=True, trait="행동",
         why="스스로 경로를 정해 돌아다니며 청소를 끝냈다. 몸을 움직여 임무를 수행하므로 행동이다."),
    dict(no=12, title="장애물을 피해 날아간 드론", body="드론이 조종기 없이 목적지를 향해 날아가면서, 가는 길에 나타난 나뭇가지를 스스로 피해 지나갔다.",
         is_ai=True, trait="행동",
         why="피해야 한다는 판단을 곧바로 비행 동작으로 옮겼다. 스스로 움직였으므로 행동이다."),
    dict(no=13, title="혼자 열리는 마트 문", body="사람이 1m 앞까지 다가가면 문이 열리고, 지나가면 닫힌다. 고양이가 지나가도 똑같이 열린다.",
         is_ai=False, trait=NONE_TRAIT,
         why="'앞에 무언가 있으면 열어라'는 한 가지 규칙만 따른다. 누가 왔는지 구별하지도, 쓸수록 똑똑해지지도 않으므로 AI가 아니다."),
    dict(no=14, title="해가 지면 켜지는 가로등", body="저녁 7시쯤 어두워지면 가로등이 저절로 켜지고, 아침이 밝으면 꺼진다. 흐린 날에는 낮에도 켜진다.",
         is_ai=False, trait=NONE_TRAIT,
         why="'어두우면 켜라'는 규칙만 지킨다. 밝기를 재는 센서일 뿐 판단이나 학습이 없으므로 AI가 아니다."),
    dict(no=15, title="24도를 지키는 에어컨", body="24도로 맞춰 두면 방이 더워지면 세게, 시원해지면 약하게 돌아간다. 매일 똑같이 작동한다.",
         is_ai=False, trait=NONE_TRAIT,
         why="정해진 온도와 비교해 켜고 끄기를 반복할 뿐이다. 내 습관을 익히지 않으므로 AI가 아니다."),
    dict(no=16, title="표준 코스 45분", body="세탁기의 표준 코스를 누르면 언제나 45분 뒤에 끝난다. 빨래가 적어도, 많아도 45분이다.",
         is_ai=False, trait=NONE_TRAIT,
         why="정해진 순서와 시간을 그대로 따른다. 빨래 상태를 살펴 스스로 바꾸지 않으므로 AI가 아니다."),
    dict(no=17, title="계산기의 완벽한 답", body="공학용 계산기에 복잡한 식을 넣으면 사람보다 훨씬 빠르게 정확한 답을 낸다. 어제도 오늘도 같은 식에 같은 답을 낸다.",
         is_ai=False, trait=NONE_TRAIT,
         why="빠른 것과 똑똑한 것은 다르다. 정해진 계산 규칙을 실행할 뿐 경험으로 달라지지 않으므로 AI가 아니다."),
    dict(no=18, title="30초마다 바뀌는 신호등", body="학교 앞 신호등이 30초마다 초록과 빨강으로 바뀐다. 차가 한 대도 없는 새벽에도 똑같이 바뀐다.",
         is_ai=False, trait=NONE_TRAIT,
         why="시간표대로만 바뀐다. 다만 차량 수를 살펴 신호 시간을 조절하는 '지능형 신호등'은 AI에 해당한다."),
    dict(no=19, title="버튼이 부른 엘리베이터", body="3층 버튼을 누르면 엘리베이터가 3층으로 온다. 사람이 몇 명이든, 급하든 급하지 않든 순서대로 움직인다.",
         is_ai=False, trait=NONE_TRAIT,
         why="'누른 층으로 간다'는 규칙만 실행한다. 상황을 판단해 스스로 순서를 바꾸지 않으므로 AI가 아니다."),
    dict(no=20, title="손을 내밀면 나오는 비누", body="손을 아래에 대면 비누가 나온다. 손이 아니라 종이를 대도 똑같이 나온다.",
         is_ai=False, trait=NONE_TRAIT,
         why="무언가 가까이 있는지만 감지한다. 그것이 손인지 구별하지 못하므로 AI가 아니다."),
]

RANKS = [
    (400, "AI 마스터 탐정", "사건을 완벽하게 꿰뚫어 보았다"),
    (360, "명탐정", "AI의 정체를 거의 다 밝혀냈다"),
    (300, "1급 탐정", "핵심 단서를 잘 짚어 냈다"),
    (240, "2급 탐정", "수사 감각이 살아나고 있다"),
    (160, "3급 탐정", "단서를 조금 더 살펴보자"),
    (0, "수습 탐정", "이제 막 수사를 시작했다"),
]


def get_rank(score):
    for line, name, desc in RANKS:
        if score >= line:
            return name, desc
    return RANKS[-1][1], RANKS[-1][2]


def safe_page(value):
    """목록에 없는 값이 들어와도 가장 비슷한 페이지로 보정한다."""
    if value in PAGES:
        return value
    if isinstance(value, str) and value.strip():
        key = value.split("(")[0].strip()
        for p in PAGES:
            if key and key in p:
                return p
    return PAGES[0]


# =====================================================================
# 1. 데이터베이스
# =====================================================================
def db_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def db_init():
    conn = db_conn()
    conn.execute(
        "CREATE TABLE IF NOT EXISTS records ("
        " cls TEXT, num TEXT, name TEXT, case_no INTEGER,"
        " judge INTEGER, trait TEXT, judge_ok INTEGER, trait_ok INTEGER,"
        " score INTEGER, ts TEXT,"
        " PRIMARY KEY (cls, num, case_no))"
    )
    conn.execute(
        "CREATE TABLE IF NOT EXISTS definitions ("
        " cls TEXT, num TEXT, name TEXT, sentence TEXT, ts TEXT,"
        " PRIMARY KEY (cls, num))"
    )
    conn.commit()
    conn.close()


def save_record(cls, num, name, case_no, judge, trait, judge_ok, trait_ok, score):
    conn = db_conn()
    conn.execute(
        "INSERT OR IGNORE INTO records VALUES (?,?,?,?,?,?,?,?,?,?)",
        (cls, num, name, case_no, int(judge), trait, int(judge_ok), int(trait_ok),
         int(score), datetime.datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def load_my_records(cls, num):
    conn = db_conn()
    rows = conn.execute(
        "SELECT case_no, judge, trait, judge_ok, trait_ok, score FROM records"
        " WHERE cls=? AND num=?", (cls, num)).fetchall()
    conn.close()
    return {r[0]: dict(judge=bool(r[1]), trait=r[2], judge_ok=bool(r[3]),
                       trait_ok=bool(r[4]), score=r[5]) for r in rows}


def save_definition(cls, num, name, sentence):
    conn = db_conn()
    conn.execute(
        "INSERT INTO definitions VALUES (?,?,?,?,?)"
        " ON CONFLICT(cls, num) DO UPDATE SET name=excluded.name,"
        " sentence=excluded.sentence, ts=excluded.ts",
        (cls, num, name, sentence,
         datetime.datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def load_my_definition(cls, num):
    conn = db_conn()
    row = conn.execute("SELECT sentence FROM definitions WHERE cls=? AND num=?",
                       (cls, num)).fetchone()
    conn.close()
    return row[0] if row else ""


def load_class_records(cls):
    conn = db_conn()
    rows = conn.execute(
        "SELECT cls, num, name, case_no, judge_ok, trait_ok, score FROM records"
        " WHERE cls=?", (cls,)).fetchall()
    conn.close()
    return rows


def load_class_definitions(cls):
    conn = db_conn()
    rows = conn.execute(
        "SELECT num, name, sentence FROM definitions WHERE cls=? ORDER BY ts DESC",
        (cls,)).fetchall()
    conn.close()
    return rows


def reset_class(cls):
    conn = db_conn()
    conn.execute("DELETE FROM records WHERE cls=?", (cls,))
    conn.execute("DELETE FROM definitions WHERE cls=?", (cls,))
    conn.commit()
    conn.close()


# =====================================================================
# 2. 화면 기본 설정 & 테마
# =====================================================================
st.set_page_config(page_title="AI 탐정소 | 사건 4-1-1",
                   page_icon="🕵️", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&family=Special+Elite&family=Gaegu:wght@400;700&display=swap');

.stApp {
  background:
    radial-gradient(900px 420px at 50% -8%, rgba(150,104,48,0.30), rgba(0,0,0,0) 70%),
    radial-gradient(700px 500px at 100% 100%, rgba(90,60,30,0.16), rgba(0,0,0,0) 70%),
    #0a0908;
}
.block-container { padding-top: 1.2rem; padding-bottom: 3rem; max-width: 1150px; }
html, body, [class*="css"] { font-family: 'Nanum Myeongjo', serif; }

/* 상단 고정 띠 */
.topbar {
  display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;
  gap:8px; border:1px solid #4a3a25; background:rgba(20,16,12,0.92);
  padding:8px 14px; margin-bottom:16px;
}
.topbar span {
  font-family:'Special Elite', cursive; font-size:12px; letter-spacing:1px;
  color:#c8b89a;
}
.topbar b { color:#e8ddc6; }

/* 서류 봉투 카드 */
.dossier {
  position:relative;
  background:
    radial-gradient(420px 220px at 18% 12%, rgba(120,86,42,0.12), rgba(0,0,0,0) 70%),
    radial-gradient(300px 200px at 85% 88%, rgba(120,86,42,0.14), rgba(0,0,0,0) 70%),
    linear-gradient(160deg, #e3d5b4 0%, #d9c9a4 45%, #cdb98f 100%);
  border:1px solid #9c8358; border-radius:3px;
  padding:26px 30px 30px 30px; margin-bottom:18px;
  box-shadow: 0 18px 40px rgba(0,0,0,0.65), inset 0 0 70px rgba(130,95,50,0.18);
  color:#241c12;
}
.dossier::after {
  content:"No."; position:absolute; top:14px; right:26px;
  font-family:'Special Elite', cursive; font-size:11px; color:#6b573a;
  }
.stamp-secret {
  display:inline-block; font-family:'Special Elite', cursive; font-size:19px;
  letter-spacing:3px; color:#9e1f1f; border-bottom:2px solid #9e1f1f;
  padding-bottom:2px; margin-bottom:6px;
}
.stamp-classified {
  display:block; font-family:'Special Elite', cursive; font-size:16px;
  letter-spacing:4px; color:#2a2318; transform:rotate(-4deg);
  border-bottom:2px solid #2a2318; width:max-content; padding-bottom:2px;
  margin:0 0 14px 2px;
}
.case-label {
  font-family:'Special Elite', cursive; font-size:13px; color:#5c4a30;
  letter-spacing:1px; margin-bottom:4px;
}
.case-title {
  font-size:30px; font-weight:800; color:#8d1c1c; margin:2px 0 14px 0;
  letter-spacing:-0.5px; line-height:1.25;
}
/* 사진과 동일한 시안색 테두리 */
.cyanbox {
  border:2px solid #2aa8bd; background:rgba(255,255,255,0.10);
  padding:16px 18px; margin:10px 0 6px 0; font-size:17px; line-height:1.75;
  color:#231b11;
}
.evidence {
  font-family:'Gaegu', cursive; font-size:18px; color:#3a2d1c;
  background:rgba(255,252,240,0.5); border-left:4px solid #9e1f1f;
  padding:10px 14px; margin-top:12px;
}
.memo {
  font-family:'Gaegu', cursive; font-size:17px; color:#2b2318; line-height:1.7;
}
.tag {
  display:inline-block; font-family:'Special Elite', cursive; font-size:12px;
  border:1px solid #6b573a; color:#4a3a25; padding:2px 9px; margin:2px 4px 2px 0;
}
.verdict-ok { color:#1d6b3a; font-weight:800; }
.verdict-no { color:#9e1f1f; font-weight:800; }

/* 점수판 */
.scorebox {
  border:1px solid #4a3a25; background:rgba(22,18,13,0.9);
  padding:14px 16px; text-align:left;
}
.scorebox .lbl {
  font-family:'Special Elite', cursive; font-size:11px; letter-spacing:1px;
  color:#a9977a;
}
.scorebox .val { font-size:28px; font-weight:800; color:#e8ddc6; }
.scorebox .sub { font-size:12px; color:#9b8a6d; }

h1, h2, h3, h4 { color:#e8ddc6 !important; }
.dossier h1, .dossier h2, .dossier h3, .dossier h4 { color:#241c12 !important; }
p, li, label, .stMarkdown { color:#d9cdb4; }
.dossier p, .dossier li, .dossier label { color:#241c12; }

/* 사이드바 */
section[data-testid="stSidebar"] {
  background:#120f0b; border-right:1px solid #4a3a25;
}
section[data-testid="stSidebar"] * { color:#d9cdb4; }

/* 입력 요소 */
div[data-baseweb="select"] > div, .stTextInput input, .stTextArea textarea {
  background:#1b1711 !important; color:#e8ddc6 !important;
  border:1px solid #6b573a !important; border-radius:2px !important;
}
.stButton > button, .stDownloadButton > button {
  font-family:'Special Elite', cursive; letter-spacing:1px;
  background:#1b1711; color:#e8ddc6;
  border:1px dashed #9e7a3f; border-radius:2px; padding:8px 18px;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  background:#9e1f1f; color:#fff6e4; border:1px solid #9e1f1f;
}
div[role="radiogroup"] label { color:#241c12 !important; font-size:16px; }
.stProgress > div > div > div > div { background:#9e1f1f; }
hr { border-color:#4a3a25; }
div[data-testid="stExpander"] {
  border:1px solid #4a3a25; background:rgba(22,18,13,0.85);
}
table { color:#d9cdb4; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

db_init()

# =====================================================================
# 3. 세션 상태  (이 줄 아래에서만 ss 사용 가능)
# =====================================================================
ss = st.session_state
ss.page = safe_page(ss.get("page"))
if "cur_case" not in ss:
    ss.cur_case = 1
if "just_submitted" not in ss:
    ss.just_submitted = None

# =====================================================================
# 4. 사이드바 - 탐정 등록
# =====================================================================
with st.sidebar:
    st.markdown("### 🕵️ DETECTIVE ID")
    st.caption("수사증을 발급받아야 입장할 수 있다.")
    cls = st.selectbox("소속 (반)", CLASS_OPTIONS, key="sb_cls")
    num = st.selectbox("요원 번호", NUM_OPTIONS, key="sb_num")
    name = st.text_input("탐정 이름", max_chars=12, placeholder="예) 김민준",
                         key="sb_name").strip()

    registered = bool(name)
    if registered:
        st.success(f"수사증 발급 완료\\n\\n{cls} {num} · {name} 탐정")
    else:
        st.warning("탐정 이름을 입력하면 수사실이 열린다.")

    st.markdown("---")
    page = st.radio("수사 메뉴", PAGES, index=PAGES.index(ss.page), key="sb_page")
    ss.page = page

    st.markdown("---")
    with st.expander("🔒 선생님 모드"):
        pin = st.text_input("PIN", type="password", key="sb_pin")
        if pin == TEACHER_PIN:
            st.caption("인증되었다.")
            target = st.selectbox("초기화할 반", CLASS_OPTIONS, key="sb_reset_cls")
            if st.button("이 반 기록 전체 삭제", key="btn_reset"):
                reset_class(target)
                st.success(f"{target} 기록을 삭제했다.")
        elif pin:
            st.error("PIN이 올바르지 않다.")

my_records = load_my_records(cls, num) if registered else {}
total_score = sum(v["score"] for v in my_records.values())
solved = len(my_records)

# =====================================================================
# 5. 상단 고정 띠
# =====================================================================
who = f"{cls} {num} {name}" if registered else "미등록"
st.markdown(
    "<div class='topbar'>"
    "<span>CASE FILE <b>4-1-1</b> / 인공지능의 개념과 특성</span>"
    f"<span>DETECTIVE <b>{who}</b></span>"
    f"<span>PROGRESS <b>{solved}/20</b> · SCORE <b>{total_score}</b></span>"
    "<span style='color:#9e1f1f'><b>CLASSIFIED</b></span>"
    "</div>", unsafe_allow_html=True)


# =====================================================================
# 6. 페이지 : 사건 브리핑
# =====================================================================
def page_briefing():
    st.markdown(
        "<div class='dossier'>"
        "<span class='stamp-secret'>TOP SECRET</span>"
        "<span class='stamp-classified'>CLASSIFIED</span>"
        "<div class='case-label'>정보 4-1. 인공지능의 이해</div>"
        "<div class='case-title'>인공지능의 개념과 특성</div>"
        "<div class='cyanbox'>디지털 탐정단이 되어<br>생활 속에 숨은 인공지능을 찾아내라!</div>"
        "<div class='evidence'>지령 : 사건 파일 20건을 열어 ① AI인가 아닌가를 판정하고, "
        "② 그렇게 본 근거가 되는 특성 1가지를 지목하라.</div>"
        "</div>", unsafe_allow_html=True)

    st.markdown("#### 수사 요령 · AI의 4대 특성")
    cols = st.columns(4)
    icons = {"인식": "👁️", "학습": "📚", "추론": "🧠", "행동": "🦾"}
    for col, t in zip(cols, TRAITS):
        col.markdown(
            f"<div class='dossier' style='padding:18px'>"
            f"<div style='font-size:26px'>{icons[t]}</div>"
            f"<div class='case-title' style='font-size:22px;margin:6px 0'>{t}</div>"
            f"<div class='memo'>{TRAIT_DESC[t]}</div></div>",
            unsafe_allow_html=True)

    st.markdown(
        "<div class='dossier'><div class='case-label'>탐정 필살 요령</div>"
        "<div class='memo'>"
        "① <b>센서만 달린 기계는 AI가 아니다.</b> 자동문·가로등은 '있으면 열어라', '어두우면 켜라'는 "
        "규칙 하나만 따른다.<br>"
        "② <b>쓸수록 똑똑해지는가?</b> 어제와 오늘의 행동이 달라진다면 학습하고 있다는 증거다.<br>"
        "③ <b>스스로 판단하는가?</b> 사람이 정해 준 답을 그대로 내놓는지, 스스로 따져 결론을 내는지 보라.<br>"
        "④ 빠르고 정확한 것은 지능이 아니다. 계산기는 사람보다 빠르지만 AI가 아니다."
        "</div></div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='dossier'><div class='case-label'>채점 규칙</div>"
        "<div class='memo'>· AI 판정 적중 <b>10점</b> + 특성 지목 적중 <b>10점</b> = 사건당 <b>20점</b> "
        "(만점 400점)<br>"
        "· 한 사건은 <b>한 번만</b> 제출할 수 있다. 제출하면 즉시 해설이 공개된다.<br>"
        "· 특성 정답은 사건마다 <b>단 하나</b>다. 가장 두드러진 특성을 골라라.</div></div>",
        unsafe_allow_html=True)


# =====================================================================
# 7. 페이지 : 수사실
# =====================================================================
def page_investigate():
    if not registered:
        st.error("사이드바에서 반 · 번호 · 이름을 등록해야 수사실에 들어갈 수 있다.")
        return

    # 아직 풀지 않은 첫 사건으로 자동 이동
    if ss.just_submitted is None:
        unsolved = [c["no"] for c in CASES if c["no"] not in my_records]
        if unsolved and ss.cur_case in my_records:
            ss.cur_case = unsolved[0]

    labels = []
    for c in CASES:
        mark = "✔" if c["no"] in my_records else "□"
        labels.append(f"{mark} {c['no']:02d}. {c['title']}")

    idx = next((i for i, c in enumerate(CASES) if c["no"] == ss.cur_case), 0)
    pick = st.selectbox("사건 파일 선택", labels, index=idx, key="case_pick")
    ss.cur_case = CASES[labels.index(pick)]["no"]
    case = CASES[labels.index(pick)]

    st.progress(solved / len(CASES), text=f"수사 진행 {solved} / {len(CASES)}건")

    st.markdown(
        "<div class='dossier'>"
        "<span class='stamp-secret'>TOP SECRET</span>"
        "<span class='stamp-classified'>CLASSIFIED</span>"
        f"<div class='case-label'>CASE No. {case['no']:02d} / 20</div>"
        f"<div class='case-title'>{case['title']}</div>"
        f"<div class='cyanbox'>{case['body']}</div>"
        "</div>", unsafe_allow_html=True)

    done = case["no"] in my_records

    if not done:
        c1, c2 = st.columns([1, 1.3])
        with c1:
            st.markdown("##### ① 판정")
            judge = st.radio("이것은 AI인가?", ["AI다", "AI가 아니다"],
                             key=f"judge_{case['no']}")
        with c2:
            st.markdown("##### ② 근거가 되는 특성 1가지")
            trait = st.radio("가장 두드러진 특성을 하나만 골라라", TRAIT_OPTIONS,
                             key=f"trait_{case['no']}")
        st.caption("제출하면 수정할 수 없다. 신중하게 결정하라.")
        if st.button("🖋️ 수사 결과 제출", key=f"submit_{case['no']}"):
            j = (judge == "AI다")
            judge_ok = (j == case["is_ai"])
            trait_ok = (trait == case["trait"])
            score = (JUDGE_POINT if judge_ok else 0) + (TRAIT_POINT if trait_ok else 0)
            save_record(cls, num, name, case["no"], j, trait, judge_ok, trait_ok, score)
            ss.just_submitted = case["no"]
            st.rerun()
    else:
        r = my_records[case["no"]]
        st.markdown("##### 수사 종결 · 판정 결과")
        a, b, c = st.columns(3)
        jc = "verdict-ok" if r["judge_ok"] else "verdict-no"
        tc = "verdict-ok" if r["trait_ok"] else "verdict-no"
        a.markdown(
            "<div class='scorebox'><div class='lbl'>MY JUDGEMENT</div>"
            f"<div class='val' style='font-size:20px'>{'AI다' if r['judge'] else 'AI가 아니다'}</div>"
            f"<div class='sub {jc}'>{'적중' if r['judge_ok'] else '오판'} · "
            f"정답 {'AI다' if case['is_ai'] else 'AI가 아니다'}</div></div>",
            unsafe_allow_html=True)
        b.markdown(
            "<div class='scorebox'><div class='lbl'>MY TRAIT</div>"
            f"<div class='val' style='font-size:20px'>{r['trait'].split(' (')[0]}</div>"
            f"<div class='sub {tc}'>{'적중' if r['trait_ok'] else '오판'} · "
            f"정답 {case['trait'].split(' (')[0]}</div></div>",
            unsafe_allow_html=True)
        c.markdown(
            "<div class='scorebox'><div class='lbl'>SCORE</div>"
            f"<div class='val'>{r['score']}</div><div class='sub'>/ 20점</div></div>",
            unsafe_allow_html=True)

        st.markdown(
            "<div class='dossier'><div class='case-label'>수사 기록 · 사건의 진상</div>"
            f"<div class='memo'>{case['why']}</div></div>", unsafe_allow_html=True)

        nxt = [c2["no"] for c2 in CASES if c2["no"] not in my_records]
        if nxt:
            if st.button(f"➡️ 다음 사건 ({nxt[0]:02d}번) 수사", key=f"next_{case['no']}"):
                ss.case_idx = nxt
                ss["case_pick"] = nxt      # ← 선택 위젯의 key 이름에 맞춰 함께 변경
                st.rerun()
        else:
            st.success("20건 전부 수사 종결. '내 수사 보고서'에서 최종 결과를 확인하라.")


# =====================================================================
# 8. 페이지 : 내 수사 보고서
# =====================================================================
def page_report():
    if not registered:
        st.error("사이드바에서 반 · 번호 · 이름을 등록하라.")
        return

    rank, desc = get_rank(total_score)
    judge_hit = sum(1 for v in my_records.values() if v["judge_ok"])
    trait_hit = sum(1 for v in my_records.values() if v["trait_ok"])

    st.markdown(
        "<div class='dossier'>"
        "<span class='stamp-secret'>TOP SECRET</span>"
        f"<div class='case-label'>DETECTIVE REPORT · {cls} {num}</div>"
        f"<div class='case-title'>{name} 탐정의 수사 보고서</div>"
        f"<div class='cyanbox'>최종 계급 : <b>{rank}</b><br>{desc}</div>"
        "</div>", unsafe_allow_html=True)

    a, b, c, d = st.columns(4)
    a.markdown("<div class='scorebox'><div class='lbl'>TOTAL SCORE</div>"
               f"<div class='val'>{total_score}</div><div class='sub'>/ 400점</div></div>",
               unsafe_allow_html=True)
    b.markdown("<div class='scorebox'><div class='lbl'>CASES CLOSED</div>"
               f"<div class='val'>{solved}</div><div class='sub'>/ 20건</div></div>",
               unsafe_allow_html=True)
    c.markdown("<div class='scorebox'><div class='lbl'>판정 적중</div>"
               f"<div class='val'>{judge_hit}</div><div class='sub'>/ {max(solved,1)}건</div></div>",
               unsafe_allow_html=True)
    d.markdown("<div class='scorebox'><div class='lbl'>특성 적중</div>"
               f"<div class='val'>{trait_hit}</div><div class='sub'>/ {max(solved,1)}건</div></div>",
               unsafe_allow_html=True)

    st.markdown("#### 사건별 기록")
    rows = []
    for case in CASES:
        r = my_records.get(case["no"])
        if r:
            rows.append({
                "사건": f"{case['no']:02d}. {case['title']}",
                "내 판정": "AI다" if r["judge"] else "AI가 아니다",
                "판정": "O" if r["judge_ok"] else "X",
                "내 특성": r["trait"].split(" (")[0],
                "정답 특성": case["trait"].split(" (")[0],
                "특성": "O" if r["trait_ok"] else "X",
                "점수": r["score"],
            })
        else:
            rows.append({"사건": f"{case['no']:02d}. {case['title']}",
                         "내 판정": "-", "판정": "-", "내 특성": "-",
                         "정답 특성": "-", "특성": "-", "점수": 0})
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.markdown("#### 최종 산출물 · 내가 쓴 AI 정의 1문장")
    st.caption("수사 결과를 바탕으로, AI가 무엇인지 나만의 한 문장으로 정의하라.")
    cur = load_my_definition(cls, num)
    sentence = st.text_area(
        "AI란 ______ 이다.", value=cur, height=100,
        placeholder="예) AI는 스스로 보고 배우고 판단해서 움직이는, 사람의 생각을 흉내 낸 프로그램이다.",
        key="def_input")
    if st.button("📌 정의 제출 / 수정", key="btn_def"):
        if sentence.strip():
            save_definition(cls, num, name, sentence.strip())
            st.success("정의를 기록했다. 상황실 게시판에 공개된다.")
        else:
            st.error("한 문장을 입력하라.")

    report = [f"AI 탐정소 수사 보고서 (사건 4-1-1)",
              f"소속 : {cls} {num}   탐정 : {name}",
              f"총점 : {total_score} / 400점   계급 : {rank}",
              f"수사 종결 : {solved}/20건  (판정 적중 {judge_hit}, 특성 적중 {trait_hit})",
              "-" * 52]
    for r in rows:
        report.append(f"{r['사건']} | 판정 {r['판정']} | 특성 {r['내 특성']}"
                      f"(정답 {r['정답 특성']}) {r['특성']} | {r['점수']}점")
    report.append("-" * 52)
    report.append(f"내가 쓴 AI 정의 : {sentence.strip() or '(미작성)'}")
    st.download_button("⬇️ 보고서 파일로 내려받기", "\\n".join(report),
                       file_name=f"AI탐정소_{cls}_{num}_{name}.txt",
                       mime="text/plain", key="btn_dl")


# =====================================================================
# 9. 페이지 : 상황실
# =====================================================================
def render_dashboard():
    rows = load_class_records(cls)
    if not rows:
        st.info(f"{cls}의 수사 기록이 아직 없다.")
        return

    people = {}
    for rc, rn, rname, cno, jok, tok, sc in rows:
        key = (rc, rn)
        p = people.setdefault(key, dict(name=rname, score=0, cnt=0))
        p["score"] += sc
        p["cnt"] += 1
        p["name"] = rname

    total_sub = len(rows)
    judge_rate = 100 * sum(r[4] for r in rows) / total_sub
    trait_rate = 100 * sum(r[5] for r in rows) / total_sub

    a, b, c, d = st.columns(4)
    a.markdown("<div class='scorebox'><div class='lbl'>참여 탐정</div>"
               f"<div class='val'>{len(people)}</div><div class='sub'>명</div></div>",
               unsafe_allow_html=True)
    b.markdown("<div class='scorebox'><div class='lbl'>제출 건수</div>"
               f"<div class='val'>{total_sub}</div><div class='sub'>건</div></div>",
               unsafe_allow_html=True)
    c.markdown("<div class='scorebox'><div class='lbl'>판정 정답률</div>"
               f"<div class='val'>{judge_rate:.0f}%</div><div class='sub'>AI/비AI 구별</div></div>",
               unsafe_allow_html=True)
    d.markdown("<div class='scorebox'><div class='lbl'>특성 정답률</div>"
               f"<div class='val'>{trait_rate:.0f}%</div><div class='sub'>4대 특성 지목</div></div>",
               unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["사건별 정답률", "명예의 전당", "우리 반 AI 정의"])

    with t1:
        stat = {}
        for rc, rn, rname, cno, jok, tok, sc in rows:
            s = stat.setdefault(cno, dict(n=0, j=0, t=0))
            s["n"] += 1
            s["j"] += jok
            s["t"] += tok
        table = []
        for case in CASES:
            s = stat.get(case["no"])
            if not s:
                continue
            table.append({
                "사건": f"{case['no']:02d}. {case['title']}",
                "정답": "AI다" if case["is_ai"] else "AI가 아니다",
                "제출": s["n"],
                "판정 정답률(%)": round(100 * s["j"] / s["n"]),
                "특성 정답률(%)": round(100 * s["t"] / s["n"]),
            })
        st.dataframe(table, use_container_width=True, hide_index=True)
        hard = sorted(table, key=lambda x: x["판정 정답률(%)"])[:3]
        if hard:
            st.markdown("**가장 많이 틀린 사건 TOP 3** — 이 사건부터 함께 토론하라.")
            for h in hard:
                st.markdown(f"- {h['사건']} · 판정 정답률 {h['판정 정답률(%)']}%")

    with t2:
        board = sorted(people.items(), key=lambda kv: (-kv[1]["score"], kv[1]["name"]))
        lead = []
        for i, ((rc, rn), p) in enumerate(board[:20], start=1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}")
            lead.append({"순위": medal, "번호": rn, "탐정": p["name"],
                         "점수": p["score"], "수사 건수": p["cnt"],
                         "계급": get_rank(p["score"])[0]})
        st.dataframe(lead, use_container_width=True, hide_index=True)

    with t3:
        defs = load_class_definitions(cls)
        if not defs:
            st.info("아직 제출된 정의가 없다.")
        else:
            for dn, dname, dsent in defs:
                st.markdown(
                    "<div class='dossier' style='padding:16px 20px'>"
                    f"<div class='case-label'>{dn} {dname} 탐정</div>"
                    f"<div class='memo'>“{dsent}”</div></div>",
                    unsafe_allow_html=True)
            csv = "번호,이름,AI 정의\\n" + "\\n".join(
                f"{dn},{dname},\"{dsent}\"" for dn, dname, dsent in defs)
            st.download_button("⬇️ 우리 반 정의 모음 내려받기", csv,
                               file_name=f"AI정의_{cls}.csv", mime="text/csv",
                               key="btn_dl_def")


def page_dashboard():
    st.markdown(
        "<div class='dossier'><span class='stamp-secret'>TOP SECRET</span>"
        f"<div class='case-label'>SITUATION ROOM · {cls}</div>"
        "<div class='case-title'>반 전체 수사 현황판</div>"
        "<div class='cyanbox'>우리 반이 어떤 사건에서 가장 많이 속았는지 실시간으로 확인하라.</div>"
        "</div>", unsafe_allow_html=True)

    auto = st.toggle("5초마다 자동 갱신", value=True, key="auto_refresh")
    if auto and hasattr(st, "fragment"):
        frag = st.fragment(run_every=5)(render_dashboard)
        frag()
    else:
        if st.button("🔄 지금 갱신", key="btn_refresh"):
            st.rerun()
        render_dashboard()


# =====================================================================
# 10. 페이지 : AI 특성 사전
# =====================================================================
def page_dict():
    st.markdown(
        "<div class='dossier'><span class='stamp-secret'>TOP SECRET</span>"
        "<span class='stamp-classified'>CLASSIFIED</span>"
        "<div class='case-label'>DETECTIVE HANDBOOK</div>"
        "<div class='case-title'>AI 특성 사전</div>"
        "<div class='cyanbox'>AI는 사람의 어떤 능력을 흉내 내는가? "
        "인식 · 학습 · 추론 · 행동, 이 네 가지다.</div></div>",
        unsafe_allow_html=True)

    detail = {
        "인식": ("👁️ 사람의 눈·귀를 흉내 낸다",
                 "카메라나 마이크로 들어온 정보가 '무엇인지' 알아차리는 능력이다.",
                 "얼굴 인식 잠금해제, 사진 자동 분류, 음성 비서의 받아쓰기"),
        "학습": ("📚 사람의 공부를 흉내 낸다",
                 "많은 자료를 보면서 규칙을 스스로 찾아내고, 쓸수록 실력이 좋아지는 능력이다.",
                 "영상 추천, 스팸 메일 분류, 내 말투를 익히는 자동완성"),
        "추론": ("🧠 사람의 생각을 흉내 낸다",
                 "알아낸 정보를 근거로 따져 보고 결론이나 예측을 내놓는 능력이다.",
                 "번역, 의료 영상 판독, 바둑에서 다음 수 결정"),
        "행동": ("🦾 사람의 몸짓을 흉내 낸다",
                 "판단한 결과를 실제 움직임으로 옮겨 임무를 끝내는 능력이다.",
                 "자율주행차, 로봇청소기, 장애물을 피하는 드론"),
    }
    for t in TRAITS:
        head, body, ex = detail[t]
        st.markdown(
            "<div class='dossier'>"
            f"<div class='case-title' style='font-size:24px'>{t}</div>"
            f"<div class='case-label'>{head}</div>"
            f"<div class='cyanbox'>{body}</div>"
            f"<div class='evidence'>생활 속 사례 : {ex}</div></div>",
            unsafe_allow_html=True)

    st.markdown("#### AI와 '그냥 기계'를 가르는 기준")
    st.dataframe([
        {"비교": "작동 방식", "그냥 기계 (센서·자동화)": "사람이 정해 준 규칙 하나를 그대로 실행",
         "인공지능": "자료에서 규칙을 스스로 찾아 판단"},
        {"비교": "시간이 지나면", "그냥 기계 (센서·자동화)": "어제와 오늘이 똑같다",
         "인공지능": "쓸수록 더 잘하게 된다"},
        {"비교": "모르는 상황", "그냥 기계 (센서·자동화)": "아무 대응도 못 한다",
         "인공지능": "비슷한 경험으로 짐작해 대응한다"},
        {"비교": "예시", "그냥 기계 (센서·자동화)": "자동문, 가로등, 계산기, 엘리베이터",
         "인공지능": "얼굴 인식, 번역기, 추천, 자율주행"},
    ], use_container_width=True, hide_index=True)

    with st.expander("🔒 선생님용 · 사건 20건 정답표 (PIN 필요)"):
        p = st.text_input("PIN", type="password", key="dict_pin")
        if p == TEACHER_PIN:
            st.dataframe([
                {"No": c["no"], "사건": c["title"],
                 "AI 여부": "AI" if c["is_ai"] else "비AI",
                 "정답 특성": c["trait"].split(" (")[0],
                 "해설": c["why"]} for c in CASES],
                use_container_width=True, hide_index=True)
        elif p:
            st.error("PIN이 올바르지 않다.")


# =====================================================================
# 11. 라우팅
# =====================================================================
if ss.page == PAGES[0]:
    page_briefing()
elif ss.page == PAGES[1]:
    page_investigate()
elif ss.page == PAGES[2]:
    page_report()
elif ss.page == PAGES[3]:
    page_dashboard()
else:
    page_dict()

st.markdown(
    "<div style='text-align:center;margin-top:36px;font-family:Special Elite,cursive;"
    "font-size:11px;letter-spacing:2px;color:#6b573a'>"
    "— END OF FILE · CASE 4-1-1 · CLASSIFIED —</div>", unsafe_allow_html=True)
