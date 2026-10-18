# -*- coding: utf-8 -*-
"""
AI 탐정소 | CASE FILE 4-1-1  "AI를 찾아라"
정보 4-1. 인공지능의 개념과 특성 - 중학교 1학년용 수업 앱
실행: streamlit run app.py
"""
import os
import sqlite3
import datetime
import pandas as pd
import streamlit as st

# ----------------------------------------------------------------------------
# 기본 설정
# ----------------------------------------------------------------------------
st.set_page_config(page_title="AI 탐정소 | CASE 4-1-1", page_icon="🕵️", layout="wide")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "ai_detective.db")

TEACHER_PIN = "1234"          # ★ 수업 전에 반드시 변경하세요
JUDGE_POINT = 10              # AI 여부 판정 배점
TAG_POINT = 10                # 특성 태깅 배점
CLASS_LIST = [f"{i}반" for i in range(1, 11)]
NUM_LIST = [f"{i}번" for i in range(1, 36)]

TAGS = ["인식", "학습", "추론", "행동"]
TAG_NONE = "해당 없음 (정해진 규칙대로만 작동)"
TAG_OPTIONS = [
    "인식 - 보고/듣고 알아차린다",
    "학습 - 데이터로 스스로 똑똑해진다",
    "추론 - 모아둔 지식으로 판단한다",
    "행동 - 판단한 대로 움직인다",
    TAG_NONE,
]
TAG_KEY = {TAG_OPTIONS[0]: "인식", TAG_OPTIONS[1]: "학습",
           TAG_OPTIONS[2]: "추론", TAG_OPTIONS[3]: "행동",
           TAG_OPTIONS[4]: "없음"}

# ----------------------------------------------------------------------------
# 사건 파일 20장 (정답은 각 사건마다 '단 하나'  -> 중복 정답 없음)
# ----------------------------------------------------------------------------
CASES = [
    dict(no=1,  title="사라진 잠금화면",
         scene="휴대폰을 얼굴 쪽으로 들자 화면이 스스로 열렸다. 쌍둥이 동생 얼굴에는 열리지 않는다.",
         is_ai=True, tag="인식",
         why="카메라로 들어온 얼굴 사진 속 특징을 '알아차려서' 내 얼굴인지 구별합니다. 가장 두드러진 특성은 인식입니다."),
    dict(no=2,  title="말을 알아듣는 스피커",
         scene="\"오늘 날씨 어때?\"라고 말했더니 스피커가 \"서울은 맑고 18도입니다\"라고 답했다.",
         is_ai=True, tag="인식",
         why="사람의 목소리(소리 데이터)를 받아들여 무슨 말인지 알아내는 일이 핵심입니다. 가장 두드러진 특성은 인식입니다."),
    dict(no=3,  title="저절로 묶인 앨범",
         scene="사진첩이 수백 장의 사진을 '엄마', '강아지', '친구'처럼 사람별로 묶어 놓았다.",
         is_ai=True, tag="인식",
         why="사진 속 얼굴을 보고 누구인지 알아차리는 것이 중심 작업입니다. 가장 두드러진 특성은 인식입니다."),
    dict(no=4,  title="끝나지 않는 추천 영상",
         scene="축구 영상 하나를 봤더니, 다음 날부터 첫 화면이 온통 축구 영상으로 바뀌었다.",
         is_ai=True, tag="학습",
         why="내가 본 기록(데이터)이 쌓일수록 추천이 달라집니다. 경험으로 좋아지는 것이 핵심이므로 학습입니다."),
    dict(no=5,  title="내 말투를 외운 키보드",
         scene="메시지를 쓸 때마다 내가 자주 쓰는 단어가 먼저 뜬다. 쓸수록 더 잘 맞춘다.",
         is_ai=True, tag="학습",
         why="'쓸수록 더 정확해진다'는 점이 결정적 단서입니다. 가장 두드러진 특성은 학습입니다."),
    dict(no=6,  title="걸러진 수상한 메일",
         scene="광고 메일을 스팸으로 신고할수록, 비슷한 메일이 알아서 스팸함으로 들어간다.",
         is_ai=True, tag="학습",
         why="사람이 알려준 예시가 많아질수록 분류 실력이 늘어납니다. 가장 두드러진 특성은 학습입니다."),
    dict(no=7,  title="바둑판의 낯선 한 수",
         scene="컴퓨터가 사람 고수도 생각하지 못한 자리에 돌을 놓아 결국 이겼다.",
         is_ai=True, tag="추론",
         why="수십 수 뒤까지 따져보고 가장 유리한 선택을 '판단'했습니다. 가장 두드러진 특성은 추론입니다."),
    dict(no=8,  title="엑스레이 속 작은 그림자",
         scene="엑스레이 사진을 분석해 \"이 부분이 의심스럽습니다(92%)\"라고 의사에게 알려 주었다.",
         is_ai=True, tag="추론",
         why="배운 지식을 근거로 가능성을 따져 결론을 내립니다. 가장 두드러진 특성은 추론입니다."),
    dict(no=9,  title="처음 보는 문장을 쓰는 상담원",
         scene="챗봇에게 길게 질문했더니, 어디에도 똑같이 적혀 있지 않은 새로운 답변을 만들어 주었다.",
         is_ai=True, tag="추론",
         why="정해진 답을 꺼내 오는 게 아니라, 아는 것을 엮어 새 답을 만들어 냅니다. 가장 두드러진 특성은 추론입니다."),
    dict(no=10, title="운전자 없는 차",
         scene="차가 스스로 차선을 지키고, 갑자기 뛰어든 사람 앞에서 브레이크를 밟았다.",
         is_ai=True, tag="행동",
         why="판단한 결과를 실제 조작(핸들·브레이크)으로 옮깁니다. 가장 두드러진 특성은 행동입니다."),
    dict(no=11, title="길을 외운 청소기",
         scene="로봇청소기가 집 구조를 기억해 두고, 다음부터는 막히지 않는 길로 돌아다닌다.",
         is_ai=True, tag="행동",
         why="스스로 경로를 정해 바퀴를 움직여 수행합니다. 가장 두드러진 특성은 행동입니다."),
    dict(no=12, title="장애물을 피하는 드론",
         scene="드론이 나뭇가지를 발견하자 방향을 틀어 피해 날아갔다.",
         is_ai=True, tag="행동",
         why="상황 판단을 곧바로 비행 동작으로 바꿉니다. 가장 두드러진 특성은 행동입니다."),
    dict(no=13, title="열리는 자동문",
         scene="사람이 앞에 서면 문이 열리고, 비켜서면 닫힌다. 10년째 똑같다.",
         is_ai=False, tag="없음",
         why="센서에 뭔가 걸리면 모터를 돈다는 규칙 하나만 반복합니다. 알아차림(인식)과 움직임(행동)이 있어 보여도, 배우지도 판단하지도 않으므로 AI가 아닙니다."),
    dict(no=14, title="해가 지면 켜지는 가로등",
         scene="어두워지면 가로등이 켜지고, 날이 밝으면 꺼진다.",
         is_ai=False, tag="없음",
         why="'밝기가 기준보다 어두우면 켜라'는 고정된 규칙입니다. 어제보다 나아지는 일이 없으므로 AI가 아닙니다."),
    dict(no=15, title="24도를 지키는 에어컨",
         scene="24도로 맞춰 두면 더워지면 돌고 시원해지면 멈춘다.",
         is_ai=False, tag="없음",
         why="설정값과 비교해 켜고 끄는 자동 제어입니다. 사람의 습관을 배우지 않으므로 AI가 아닙니다."),
    dict(no=16, title="표준 코스 세탁기",
         scene="표준 코스를 누르면 언제나 똑같이 48분 동안 같은 순서로 세탁한다.",
         is_ai=False, tag="없음",
         why="정해진 순서(프로그램)를 그대로 따라가는 기계입니다. 판단이 없으므로 AI가 아닙니다."),
    dict(no=17, title="틀리지 않는 계산기",
         scene="7 x 8 을 누르면 0.01초 만에 56이 나온다. 사람보다 훨씬 빠르다.",
         is_ai=False, tag="없음",
         why="빠른 것과 똑똑한 것은 다릅니다. 정해진 계산 규칙만 수행하므로 AI가 아닙니다."),
    dict(no=18, title="자동으로 더하는 표",
         scene="엑셀에 점수를 입력하면 합계 칸이 저절로 바뀐다.",
         is_ai=False, tag="없음",
         why="사람이 넣어 둔 수식(SUM)을 다시 계산한 것뿐입니다. 스스로 배우거나 판단하지 않으므로 AI가 아닙니다."),
    dict(no=19, title="30초마다 바뀌는 신호등",
         scene="차가 한 대도 없는 새벽에도 신호등이 30초마다 초록과 빨강을 바꾼다.",
         is_ai=False, tag="없음",
         why="시간표대로만 작동합니다. (참고: 차량 수를 인식해 시간을 바꾸는 'AI 신호등'은 AI입니다.)"),
    dict(no=20, title="버튼을 기다리는 엘리베이터",
         scene="5층 버튼을 누르면 5층에 멈춘다. 아무도 누르지 않으면 가만히 있다.",
         is_ai=False, tag="없음",
         why="누른 층으로 간다는 규칙을 따릅니다. 사람의 출퇴근 패턴을 배워 미리 이동한다면 그때는 AI입니다."),
]
TOTAL_MAX = len(CASES) * (JUDGE_POINT + TAG_POINT)

RANKS = [
    (0.00, "수습 탐정", "아직 사건 보는 눈을 기르는 중"),
    (0.40, "3급 탐정", "AI의 냄새를 맡기 시작했다"),
    (0.60, "2급 탐정", "웬만한 함정은 피해 간다"),
    (0.75, "1급 탐정", "증거로 말하는 탐정"),
    (0.90, "명탐정", "AI 판별의 달인"),
    (1.00, "AI 마스터 탐정", "완벽 해결. 서장이 직접 악수를 청했다"),
]

def get_rank(score):
    ratio = score / TOTAL_MAX if TOTAL_MAX else 0
    title, desc = RANKS[0][1], RANKS[0][2]
    for th, t, d in RANKS:
        if ratio >= th:
            title, desc = t, d
    return title, desc

# ----------------------------------------------------------------------------
# DB
# ----------------------------------------------------------------------------
def conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.execute("PRAGMA journal_mode=WAL")
    return c

def init_db():
    with conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS logs(
            cls TEXT, num TEXT, name TEXT, case_no INTEGER,
            judge_ok INTEGER, tag_ok INTEGER, score INTEGER,
            my_judge TEXT, my_tag TEXT, ts TEXT,
            PRIMARY KEY (cls, num, case_no))""")
        c.execute("""CREATE TABLE IF NOT EXISTS defs(
            cls TEXT, num TEXT, name TEXT, sentence TEXT, ts TEXT,
            PRIMARY KEY (cls, num))""")
init_db()

def save_log(cls, num, name, case_no, judge_ok, tag_ok, score, my_judge, my_tag):
    with conn() as c:
        c.execute("""INSERT OR IGNORE INTO logs VALUES (?,?,?,?,?,?,?,?,?,?)""",
                  (cls, num, name, case_no, int(judge_ok), int(tag_ok), score,
                   my_judge, my_tag, datetime.datetime.now().isoformat(timespec="seconds")))

def save_def(cls, num, name, sentence):
    with conn() as c:
        c.execute("""INSERT INTO defs VALUES (?,?,?,?,?)
                     ON CONFLICT(cls,num) DO UPDATE SET name=excluded.name,
                     sentence=excluded.sentence, ts=excluded.ts""",
                  (cls, num, name, sentence,
                   datetime.datetime.now().isoformat(timespec="seconds")))

def my_logs(cls, num):
    with conn() as c:
        return pd.read_sql_query(
            "SELECT * FROM logs WHERE cls=? AND num=? ORDER BY case_no", c, params=(cls, num))

def class_logs(cls):
    with conn() as c:
        return pd.read_sql_query("SELECT * FROM logs WHERE cls=?", c, params=(cls,))

def class_defs(cls):
    with conn() as c:
        return pd.read_sql_query(
            "SELECT cls,num,name,sentence,ts FROM defs WHERE cls=? ORDER BY ts DESC", c, params=(cls,))

def my_def(cls, num):
    with conn() as c:
        r = c.execute("SELECT sentence FROM defs WHERE cls=? AND num=?", (cls, num)).fetchone()
    return r[0] if r else ""

def reset_class(cls):
    with conn() as c:
        c.execute("DELETE FROM logs WHERE cls=?", (cls,))
        c.execute("DELETE FROM defs WHERE cls=?", (cls,))

# ----------------------------------------------------------------------------
# 테마 (기밀문서 / 느와르)
# ----------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Special+Elite&family=Nanum+Myeongjo:wght@400;700;800&family=Gaegu:wght@400;700&display=swap');

.stApp{
  background:
    radial-gradient(ellipse at 50% -10%, rgba(120,95,60,.22), transparent 60%),
    radial-gradient(ellipse at 50% 120%, rgba(0,0,0,.9), transparent 55%),
    #0a0908;
  color:#d8cdb8;
  font-family:'Nanum Myeongjo', serif;
}
#MainMenu, footer, header{visibility:hidden;}
.block-container{padding-top:1.2rem; max-width:1150px;}

/* ---------- 상단 사건 헤더 ---------- */
.dossier-top{
  border:1px solid #4a4034; border-top:3px solid #8b1a1a;
  background:linear-gradient(180deg,#171310 0%,#0d0b09 100%);
  padding:14px 18px; margin-bottom:14px;
  display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px;
}
.dossier-top .lbl{font-family:'Special Elite',monospace; color:#8a7b62; font-size:11px; letter-spacing:3px;}
.dossier-top .val{font-family:'Special Elite',monospace; color:#e6dcc6; font-size:14px; letter-spacing:1px;}
.stamp-red{
  font-family:'Special Elite',monospace; color:#b3271f; border:2px solid #b3271f;
  padding:3px 10px; letter-spacing:4px; font-size:13px;
  transform:rotate(-3deg); opacity:.9;
}

/* ---------- 크라프트 종이 ---------- */
.paper{
  background:
    repeating-linear-gradient(0deg, rgba(0,0,0,.015) 0 2px, transparent 2px 4px),
    linear-gradient(135deg,#e2d3ae 0%,#d3c096 45%,#c9b689 100%);
  color:#2a2118; border-radius:3px;
  padding:26px 30px 24px; position:relative;
  box-shadow:0 18px 40px rgba(0,0,0,.65), inset 0 0 70px rgba(120,90,45,.25);
  border:1px solid #a89468;
}
.paper:before{
  content:''; position:absolute; left:0; top:0; width:100%; height:100%;
  background:radial-gradient(circle at 85% 10%, rgba(90,60,20,.18), transparent 35%);
  pointer-events:none;
}
.paper .secret{
  font-family:'Special Elite',monospace; color:#9d2118; font-size:14px; letter-spacing:5px;
  border-bottom:2px solid #9d2118; display:inline-block; padding-bottom:2px; transform:rotate(-2deg);
}
.paper .classified{
  font-family:'Special Elite',monospace; color:#2a2118; font-size:12px; letter-spacing:4px;
  border-bottom:1.5px solid #2a2118; display:inline-block; margin-top:6px; transform:rotate(-2deg); opacity:.75;
}
.paper .caseno{
  font-family:'Special Elite',monospace; font-size:12px; letter-spacing:2px; color:#6a5a3f;
  text-align:right; border-bottom:1px solid #8c7a55; padding-bottom:3px; margin-bottom:14px;
}
.paper h2{
  font-family:'Nanum Myeongjo',serif; font-weight:800; color:#8c1d14;
  font-size:30px; margin:6px 0 2px; letter-spacing:-.5px;
}
.evidence-box{
  border:2px solid #2aa8bd; background:rgba(255,255,255,.18);
  padding:18px 20px; margin:16px 0 6px; font-size:19px; line-height:1.75; color:#241c13;
}
.paper .foot{
  font-family:'Special Elite',monospace; font-size:11px; color:#6a5a3f;
  letter-spacing:2px; margin-top:16px; text-align:center;
}
.paper .why{font-size:16px; line-height:1.8; color:#2a2118;}

/* ---------- 어두운 패널 ---------- */
.panel{
  border:1px solid #42392d; background:#131110; padding:16px 18px; margin:10px 0;
}
.panel h4{
  font-family:'Special Elite',monospace; color:#c9b689; font-size:13px;
  letter-spacing:3px; margin:0 0 10px; border-bottom:1px dashed #4a4034; padding-bottom:6px;
}
.kv{display:flex; justify-content:space-between; padding:6px 0; border-bottom:1px dotted #332c23; font-size:15px;}
.kv span:last-child{color:#e6dcc6; font-weight:700;}
.metric{border:1px solid #42392d; background:#131110; padding:12px 14px; text-align:left;}
.metric .l{font-family:'Special Elite',monospace; font-size:11px; letter-spacing:2px; color:#8a7b62;}
.metric .v{font-size:28px; color:#e6dcc6; font-weight:800; line-height:1.25;}
.metric .s{font-size:12px; color:#9c8e75;}
.tagchip{
  display:inline-block; font-family:'Special Elite',monospace; font-size:11px; letter-spacing:2px;
  border:1px solid #2aa8bd; color:#8fd9e4; padding:2px 8px; margin-right:6px;
}
.ok{color:#5fbf71; font-weight:700;} .ng{color:#c9483d; font-weight:700;}
.hint{font-family:'Gaegu',cursive; font-size:17px; color:#b5a68c;}

/* ---------- 위젯 ---------- */
section[data-testid="stSidebar"]{background:#0e0c0b; border-right:1px solid #3a322a;}
section[data-testid="stSidebar"] *{color:#cdc0a8;}
div.stButton>button{
  width:100%; font-family:'Special Elite',monospace; letter-spacing:2px; font-size:15px;
  background:#1a1614; color:#d8cdb8; border:2px dashed #7d6c4d; border-radius:2px; padding:12px 6px;
  transition:.15s;
}
div.stButton>button:hover{border-color:#2aa8bd; color:#8fd9e4; background:#141a1c;}
div.stButton>button[kind="primary"]{
  background:#7d1a12; border:2px solid #b3271f; color:#f0e4cc;
}
div.stButton>button[kind="primary"]:hover{background:#9d2118; color:#fff;}
div[data-testid="stRadio"] label p, .stSelectbox label p, .stTextInput label p, .stTextArea label p{
  color:#c9b689 !important; font-family:'Special Elite',monospace; letter-spacing:1px; font-size:12px;
}
div[data-testid="stRadio"] div[role="radiogroup"] label{
  border:1px solid #3a322a; background:#141110; padding:8px 12px; margin-bottom:6px; width:100%;
}
div[data-testid="stRadio"] div[role="radiogroup"] label:hover{border-color:#2aa8bd; background:#121819;}
div[data-testid="stRadio"] div[role="radiogroup"] label p{font-family:'Nanum Myeongjo',serif; font-size:16px; color:#d8cdb8 !important; letter-spacing:0;}
.stSelectbox div[data-baseweb="select"]>div, .stTextInput input, .stTextArea textarea{
  background:#17130f !important; border:1px solid #574a37 !important; color:#e6dcc6 !important;
}
div[data-testid="stProgress"]>div>div>div>div{background:#b3271f;}
.stTabs [data-baseweb="tab"]{font-family:'Special Elite',monospace; letter-spacing:2px; color:#8a7b62;}
.stTabs [aria-selected="true"]{color:#8fd9e4 !important;}
div[data-testid="stDataFrame"]{border:1px solid #42392d;}
hr{border-color:#3a322a;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

def paper(inner):
    st.markdown('<div class="paper">' + inner + '</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 사이드바 : 탐정 등록
# ----------------------------------------------------------------------------
ss = st.session_state
ss.setdefault("registered", False)
ss.setdefault("cls", CLASS_LIST[0])
ss.setdefault("num", NUM_LIST[0])
ss.setdefault("name", "")
ss.setdefault("judge", None)
ss.setdefault("page", "사건 브리핑")

with st.sidebar:
    st.markdown(
        '<div style="font-family:Special Elite,monospace;color:#b3271f;border:2px solid #b3271f;'
        'text-align:center;letter-spacing:4px;padding:6px;transform:rotate(-2deg);margin-bottom:14px;">'
        'TOP SECRET</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><h4>DETECTIVE ID</h4></div>', unsafe_allow_html=True)
    cls = st.selectbox("소속 (반)", CLASS_LIST, index=CLASS_LIST.index(ss.cls))
    num = st.selectbox("요원 번호", NUM_LIST, index=NUM_LIST.index(ss.num))
    name = st.text_input("탐정 이름 (본명)", value=ss.name, max_chars=12, placeholder="예) 김하늘")

    if st.button("🔎 수사 등록 / 변경", type="primary"):
        if not name.strip():
            st.warning("탐정 이름을 입력해야 사건 파일을 열 수 있습니다.")
        else:
            ss.cls, ss.num, ss.name = cls, num, name.strip()
            ss.registered = True
            ss.judge = None
            st.success(f"{cls} {num} {name.strip()} 탐정 등록 완료")

    if ss.registered:
        st.markdown(f'<div class="panel"><h4>STATUS</h4>'
                    f'<div class="kv"><span>소속</span><span>{ss.cls}</span></div>'
                    f'<div class="kv"><span>번호</span><span>{ss.num}</span></div>'
                    f'<div class="kv"><span>이름</span><span>{ss.name}</span></div></div>',
                    unsafe_allow_html=True)

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

    st.markdown("---")
    with st.expander("👮 선생님 모드"):
        pin = st.text_input("PIN", type="password", key="pin")
        if pin == TEACHER_PIN:
            tcls = st.selectbox("대상 반", CLASS_LIST, key="tcls")
            df_t = class_logs(tcls)
            st.caption(f"기록 {len(df_t)}건 / 참여 {df_t[['num']].drop_duplicates().shape[0] if len(df_t) else 0}명")
            if len(df_t):
                st.download_button("기록 CSV 내려받기",
                                   df_t.to_csv(index=False).encode("utf-8-sig"),
                                   file_name=f"AI탐정소_{tcls}_기록.csv", mime="text/csv")
            dd = class_defs(tcls)
            if len(dd):
                st.download_button("AI 정의 CSV 내려받기",
                                   dd.to_csv(index=False).encode("utf-8-sig"),
                                   file_name=f"AI탐정소_{tcls}_정의.csv", mime="text/csv")
            st.markdown("초기화 (복구 불가)")
            if st.checkbox(f"{tcls} 기록 삭제에 동의"):
                if st.button("기록 초기화"):
                    reset_class(tcls)
                    st.success(f"{tcls} 기록을 초기화했습니다.")
        elif pin:
            st.error("PIN이 올바르지 않습니다.")

# ----------------------------------------------------------------------------
# 상단 헤더
# ----------------------------------------------------------------------------
who = f"{ss.cls} {ss.num} {ss.name}" if ss.registered else "미등록"
done_n = len(my_logs(ss.cls, ss.num)) if ss.registered else 0
st.markdown(
    '<div class="dossier-top">'
    '<div><div class="lbl">CASE FILE</div><div class="val">4-1-1 &nbsp;AI를 찾아라</div></div>'
    f'<div><div class="lbl">DETECTIVE</div><div class="val">{who}</div></div>'
    f'<div><div class="lbl">PROGRESS</div><div class="val">{done_n} / {len(CASES)} 건 종결</div></div>'
    '<div class="stamp-red">CLASSIFIED</div>'
    '</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 1. 사건 브리핑
# ----------------------------------------------------------------------------
if ss.page == "사건 브리핑":
    paper(
        '<div class="caseno">FILE No. 4-1-1 &nbsp;|&nbsp; 정보 4-1. 인공지능의 이해</div>'
        '<div class="secret">TOP SECRET</div><br>'
        '<div class="classified">CLASSIFIED</div>'
        '<h2>AI를 찾아라</h2>'
        '<div class="evidence-box">'
        '디지털 탐정단 여러분. 우리 주변에는 <b>AI인 척하는 기계</b>가 숨어 있다.<br>'
        '제출된 사건 파일 <b>20건</b>을 읽고 <b>AI인지 아닌지</b> 판정하라.<br>'
        '그리고 그 사건의 <b>가장 두드러진 특성 1가지</b>를 지목하라.'
        '</div>'
        '<div class="foot">태블릿 전원 ON / 사이드바에서 반·번호·이름 등록 후 수사 시작</div>')

    st.markdown("<br>", unsafe_allow_html=True)
    c = st.columns(4)
    cards = [("인식", "보고 · 듣고 알아차린다", "카메라로 얼굴을 알아봄, 목소리를 알아들음"),
             ("학습", "데이터로 스스로 똑똑해진다", "쓸수록 추천이 정확해짐"),
             ("추론", "아는 것으로 판단한다", "다음 수를 따져 가장 좋은 선택을 함"),
             ("행동", "판단한 대로 움직인다", "스스로 브레이크를 밟음")]
    for col, (t, d, e) in zip(c, cards):
        col.markdown(f'<div class="panel"><h4>{t}</h4>'
                     f'<div style="font-size:16px;color:#e6dcc6;">{d}</div>'
                     f'<div style="font-size:13px;color:#9c8e75;margin-top:6px;">예) {e}</div></div>',
                     unsafe_allow_html=True)

    st.markdown(
        '<div class="panel"><h4>DETECTIVE TIP</h4>'
        '<div class="hint">① 센서가 있다고 다 AI는 아니다. <b>자동 ≠ 인공지능</b><br>'
        '② 결정적 단서는 이것! "<b>쓸수록 더 똑똑해지는가?</b>", "<b>스스로 판단하는가?</b>"<br>'
        '③ 10년째 똑같이 작동한다면 그건 그냥 기계다.</div></div>', unsafe_allow_html=True)

    if not ss.registered:
        st.info("왼쪽 사이드바에서 반 · 번호 · 이름을 등록하면 수사실 문이 열립니다.")

# ----------------------------------------------------------------------------
# 2. 수사실
# ----------------------------------------------------------------------------
elif ss.page == PAGES[1]:
    if not ss.registered:
        st.warning("사이드바에서 탐정 등록을 먼저 해 주세요.")
        st.stop()

    logs = my_logs(ss.cls, ss.num)
    solved = set(logs["case_no"].tolist())
    st.progress(len(solved) / len(CASES))

    remain = [c for c in CASES if c["no"] not in solved]
    labels = [("✔ " if c["no"] in solved else "□ ") + f"{c['no']:02d}. {c['title']}" for c in CASES]
    default_idx = CASES.index(remain[0]) if remain else 0
    pick = st.selectbox("사건 파일 선택", labels, index=default_idx)
    case = CASES[labels.index(pick)]
    already = case["no"] in solved

    paper(
        f'<div class="caseno">CASE No. {case["no"]:02d} / {len(CASES)} &nbsp;&nbsp; NAME: {ss.name} &nbsp;&nbsp; CLASS: {ss.cls} {ss.num}</div>'
        '<div class="secret">EVIDENCE</div>'
        f'<h2>{case["title"]}</h2>'
        f'<div class="evidence-box">{case["scene"]}</div>'
        '<div class="foot">아래에서 ① AI 여부 판정 → ② 특성 1개 지목 → ③ 보고서 제출</div>')

    st.markdown("<br>", unsafe_allow_html=True)

    if already:
        row = logs[logs["case_no"] == case["no"]].iloc[0]
        st.markdown(
            f'<div class="panel"><h4>CASE CLOSED</h4>'
            f'<div class="kv"><span>내 판정</span><span>{row["my_judge"]} '
            f'{"<span class=ok>정답</span>" if row["judge_ok"] else "<span class=ng>오답</span>"}</span></div>'
            f'<div class="kv"><span>내 지목 특성</span><span>{row["my_tag"]} '
            f'{"<span class=ok>정답</span>" if row["tag_ok"] else "<span class=ng>오답</span>"}</span></div>'
            f'<div class="kv"><span>획득 점수</span><span>{row["score"]} 점</span></div></div>',
            unsafe_allow_html=True)
        verdict = "AI다" if case["is_ai"] else "AI가 아니다"
        ans_tag = case["tag"] if case["is_ai"] else "해당 없음"
        paper(f'<div class="secret">SOLUTION</div><h2 style="font-size:22px;">판정: {verdict} · 특성: {ans_tag}</h2>'
              f'<div class="why">{case["why"]}</div>')
        st.caption("※ 한 번 종결한 사건은 다시 수사할 수 없습니다. (중복 제출 불가)")
    else:
        st.markdown('<div class="panel"><h4>STEP 1 &nbsp;판정</h4></div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("🤖 AI 다", type="primary" if ss.judge == "AI다" else "secondary", key=f"y{case['no']}"):
            ss.judge = "AI다"
        if c2.button("⚙ AI 아니다", type="primary" if ss.judge == "AI가 아니다" else "secondary", key=f"n{case['no']}"):
            ss.judge = "AI가 아니다"
        st.markdown(f'<div class="hint">현재 선택: <b>{ss.judge or "미선택"}</b></div>', unsafe_allow_html=True)

        st.markdown('<div class="panel"><h4>STEP 2 &nbsp;특성 지목 (단 하나만)</h4></div>', unsafe_allow_html=True)
        tag_pick = st.radio("이 사건에서 가장 두드러진 AI 특성은?", TAG_OPTIONS,
                            index=None, key=f"t{case['no']}")

        if st.button("📝 수사 보고서 제출", type="primary", key=f"s{case['no']}"):
            if ss.judge is None or tag_pick is None:
                st.error("판정과 특성을 모두 선택해야 제출할 수 있습니다.")
            else:
                judge_ok = (ss.judge == "AI다") == case["is_ai"]
                my_tag = TAG_KEY[tag_pick]
                tag_ok = (my_tag == case["tag"])
                score = (JUDGE_POINT if judge_ok else 0) + (TAG_POINT if tag_ok else 0)
                save_log(ss.cls, ss.num, ss.name, case["no"], judge_ok, tag_ok, score,
                         ss.judge, my_tag if my_tag != "없음" else "해당 없음")
                ss.judge = None
                if score == JUDGE_POINT + TAG_POINT:
                    st.balloons()
                st.rerun()

# ----------------------------------------------------------------------------
# 3. 내 수사 보고서
# ----------------------------------------------------------------------------
elif ss.page == PAGES[2]:
    if not ss.registered:
        st.warning("사이드바에서 탐정 등록을 먼저 해 주세요.")
        st.stop()

    logs = my_logs(ss.cls, ss.num)
    total = int(logs["score"].sum()) if len(logs) else 0
    jok = int(logs["judge_ok"].sum()) if len(logs) else 0
    tok = int(logs["tag_ok"].sum()) if len(logs) else 0
    rank, rdesc = get_rank(total)

    paper(f'<div class="caseno">FINAL REPORT &nbsp;|&nbsp; {ss.cls} {ss.num} {ss.name}</div>'
          '<div class="secret">RESULT</div>'
          f'<h2>{rank}</h2><div class="why">{rdesc}</div>'
          f'<div class="evidence-box" style="font-size:17px;">종결 {len(logs)}건 / 총점 '
          f'<b>{total}점</b> (만점 {TOTAL_MAX}점) &nbsp;·&nbsp; 판정 정답 {jok}건 &nbsp;·&nbsp; 특성 정답 {tok}건</div>')

    st.markdown("<br>", unsafe_allow_html=True)
    m = st.columns(4)
    vals = [("TOTAL SCORE", f"{total}", f"/ {TOTAL_MAX}점"),
            ("CASES CLOSED", f"{len(logs)}", f"/ {len(CASES)}건"),
            ("JUDGE ACC.", f"{(jok/len(logs)*100):.0f}%" if len(logs) else "-", "AI 여부 정확도"),
            ("TAG ACC.", f"{(tok/len(logs)*100):.0f}%" if len(logs) else "-", "특성 지목 정확도")]
    for col, (l, v, s) in zip(m, vals):
        col.markdown(f'<div class="metric"><div class="l">{l}</div><div class="v">{v}</div>'
                     f'<div class="s">{s}</div></div>', unsafe_allow_html=True)

    if len(logs):
        title_map = {c["no"]: c["title"] for c in CASES}
        ans_map = {c["no"]: ("AI다" if c["is_ai"] else "AI가 아니다") for c in CASES}
        tag_map = {c["no"]: (c["tag"] if c["is_ai"] else "해당 없음") for c in CASES}
        view = pd.DataFrame({
            "사건": [f"{n:02d}. {title_map[n]}" for n in logs["case_no"]],
            "내 판정": logs["my_judge"],
            "정답 판정": [ans_map[n] for n in logs["case_no"]],
            "내 특성": logs["my_tag"],
            "정답 특성": [tag_map[n] for n in logs["case_no"]],
            "점수": logs["score"],
        })
        st.markdown('<div class="panel"><h4>CASE LOG</h4></div>', unsafe_allow_html=True)
        st.dataframe(view, use_container_width=True, hide_index=True)

    st.markdown('<div class="panel"><h4>FINAL STATEMENT &nbsp;-&nbsp; 내가 쓴 AI 정의 1문장</h4></div>',
                unsafe_allow_html=True)
    st.markdown('<div class="hint">예시 틀 : "AI란 ○○을 스스로 ○○해서 ○○하는 것이다."</div>',
                unsafe_allow_html=True)
    sent = st.text_area("AI란 무엇인가? (한 문장)", value=my_def(ss.cls, ss.num),
                        height=90, max_chars=200, label_visibility="collapsed")
    cA, cB = st.columns([1, 1])
    if cA.button("🖋 정의 제출 / 수정", type="primary"):
        if len(sent.strip()) < 5:
            st.error("조금 더 자세히 적어 주세요. (5자 이상)")
        else:
            save_def(ss.cls, ss.num, ss.name, sent.strip())
            st.success("정의가 상황실 게시판에 등록되었습니다.")

    report = (f"AI 탐정소 수사 보고서 (CASE 4-1-1)\n"
              f"{'='*44}\n소속: {ss.cls} {ss.num}\n이름: {ss.name}\n"
              f"계급: {rank}\n총점: {total} / {TOTAL_MAX}\n"
              f"종결 사건: {len(logs)} / {len(CASES)}\n"
              f"판정 정답 {jok}건, 특성 정답 {tok}건\n"
              f"{'-'*44}\n[내가 쓴 AI 정의]\n{sent.strip() or '(미작성)'}\n")
    cB.download_button("⬇ 보고서 내려받기 (txt)", report.encode("utf-8"),
                       file_name=f"AI탐정보고서_{ss.cls}_{ss.num}_{ss.name}.txt", mime="text/plain")

# ----------------------------------------------------------------------------
# 4. 상황실
# ----------------------------------------------------------------------------
elif ss.page == PAGES[3]:
    target = st.selectbox("상황실 모니터링 대상", CLASS_LIST,
                          index=CLASS_LIST.index(ss.cls) if ss.registered else 0)
    auto = st.checkbox("5초마다 자동 갱신", value=True)

    def situation_room():
        df = class_logs(target)
        if not len(df):
            st.info("아직 접수된 수사 보고서가 없습니다.")
            return
        people = df[["num", "name"]].drop_duplicates()
        acc_j = df["judge_ok"].mean() * 100
        acc_t = df["tag_ok"].mean() * 100
        m = st.columns(4)
        vals = [("AGENTS", f"{len(people)}", "참여 탐정 수"),
                ("REPORTS", f"{len(df)}", "접수된 보고서"),
                ("JUDGE ACC.", f"{acc_j:.0f}%", "AI 여부 정답률"),
                ("TAG ACC.", f"{acc_t:.0f}%", "특성 지목 정답률")]
        for col, (l, v, s) in zip(m, vals):
            col.markdown(f'<div class="metric"><div class="l">{l}</div><div class="v">{v}</div>'
                         f'<div class="s">{s}</div></div>', unsafe_allow_html=True)

        t1, t2, t3 = st.tabs(["사건별 정답률", "명예의 전당", "우리 반 AI 정의"])

        with t1:
            g = df.groupby("case_no").agg(n=("score", "size"),
                                          j=("judge_ok", "mean"), t=("tag_ok", "mean")).reset_index()
            tmap = {c["no"]: c["title"] for c in CASES}
            rows = []
            for _, r in g.iterrows():
                pj, pt = r["j"] * 100, r["t"] * 100
                bar = int(round(pj / 5))
                rows.append(
                    f'<div class="kv"><span>{int(r["case_no"]):02d}. {tmap[int(r["case_no"])]} '
                    f'<span style="color:#6a5f4c;">({int(r["n"])}명)</span></span>'
                    f'<span><span style="font-family:Special Elite,monospace;color:'
                    f'{"#5fbf71" if pj>=70 else "#c9483d" if pj<40 else "#d6a84a"};">'
                    f'{"■"*bar}{"□"*(20-bar)}</span> &nbsp;판정 {pj:.0f}% / 특성 {pt:.0f}%</span></div>')
            st.markdown('<div class="panel"><h4>CASE DIFFICULTY</h4>' + "".join(rows) + '</div>',
                        unsafe_allow_html=True)
            hard = g.sort_values("j").head(3)
            st.markdown('<div class="panel"><h4>가장 많이 틀린 사건 TOP 3</h4>' +
                        "".join(f'<div class="kv"><span>{int(r["case_no"]):02d}. {tmap[int(r["case_no"])]}</span>'
                                f'<span class="ng">정답률 {r["j"]*100:.0f}%</span></div>'
                                for _, r in hard.iterrows()) + '</div>', unsafe_allow_html=True)

        with t2:
            board = (df.groupby(["num", "name"])
                       .agg(점수=("score", "sum"), 종결=("score", "size")).reset_index()
                       .sort_values(["점수", "종결"], ascending=False).head(10))
            rows = []
            for i, (_, r) in enumerate(board.iterrows(), start=1):
                medal = ["①", "②", "③"][i-1] if i <= 3 else f"{i}"
                rk, _d = get_rank(int(r["점수"]))
                rows.append(f'<div class="kv"><span>{medal} &nbsp;{r["num"]} {r["name"]} '
                            f'<span class="tagchip">{rk}</span></span>'
                            f'<span>{int(r["점수"])}점 · {int(r["종결"])}건</span></div>')
            st.markdown('<div class="panel"><h4>HALL OF FAME</h4>' + "".join(rows) + '</div>',
                        unsafe_allow_html=True)

            tag_ans = {c["no"]: (c["tag"] if c["is_ai"] else "없음") for c in CASES}
            df2 = df.copy()
            df2["정답특성"] = df2["case_no"].map(tag_ans)
            tg = df2.groupby("정답특성")["tag_ok"].mean() * 100
            label = {"인식": "인식", "학습": "학습", "추론": "추론", "행동": "행동", "없음": "AI 아님(규칙)"}
            rows = [f'<div class="kv"><span>{label.get(k,k)}</span>'
                    f'<span class="{"ok" if v>=70 else "ng" if v<40 else ""}">{v:.0f}%</span></div>'
                    for k, v in tg.items()]
            st.markdown('<div class="panel"><h4>특성별 지목 정확도</h4>' + "".join(rows) + '</div>',
                        unsafe_allow_html=True)

        with t3:
            dd = class_defs(target)
            if not len(dd):
                st.info("아직 제출된 AI 정의가 없습니다.")
            else:
                for _, r in dd.iterrows():
                    st.markdown('<div class="paper" style="padding:16px 20px;margin-bottom:10px;">'
                                f'<div class="caseno" style="margin-bottom:8px;">{r["num"]} {r["name"]}</div>'
                                f'<div style="font-family:Gaegu,cursive;font-size:21px;color:#2a2118;">'
                                f'&ldquo; {r["sentence"]} &rdquo;</div></div>', unsafe_allow_html=True)

    runner = situation_room
    if auto and hasattr(st, "fragment"):
        runner = st.fragment(run_every=5)(situation_room)
    runner()

# ----------------------------------------------------------------------------
# 5. AI 특성 사전
# ----------------------------------------------------------------------------
else:
    paper('<div class="caseno">REFERENCE BOOK &nbsp;|&nbsp; 4대 특성 판별 지침</div>'
          '<div class="secret">MANUAL</div><h2>AI 특성 사전</h2>'
          '<div class="evidence-box">AI는 사람의 능력을 흉내 낸다. '
          '<b>보고 듣고(인식) → 배우고(학습) → 판단하고(추론) → 움직인다(행동)</b></div>')

    st.markdown("<br>", unsafe_allow_html=True)
    rows = [("인식", "사람의 눈·귀", "사진·소리·글을 받아들여 무엇인지 알아차린다", "얼굴로 잠금 해제, 음성 비서"),
            ("학습", "사람의 공부", "많은 데이터를 보며 스스로 성능을 높인다", "추천 영상, 스팸 분류"),
            ("추론", "사람의 생각", "배운 것을 근거로 판단·예측하고 새 답을 만든다", "바둑 다음 수, 질병 가능성"),
            ("행동", "사람의 손발", "판단한 결과를 실제 동작으로 실행한다", "자율주행, 로봇청소기")]
    for t, b, d, e in rows:
        st.markdown(f'<div class="panel"><h4>{t} &nbsp;|&nbsp; {b}</h4>'
                    f'<div style="font-size:16px;color:#e6dcc6;">{d}</div>'
                    f'<div style="font-size:13px;color:#9c8e75;margin-top:6px;">'
                    f'<span class="tagchip">사례</span>{e}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="panel"><h4>헷갈릴 때 쓰는 판별 3문</h4>'
                '<div class="kv"><span>① 스스로 배워서 어제보다 나아지는가?</span><span>예 → AI 쪽</span></div>'
                '<div class="kv"><span>② 처음 보는 상황에서도 판단하는가?</span><span>예 → AI 쪽</span></div>'
                '<div class="kv"><span>③ 10년째 똑같은 규칙만 반복하는가?</span><span>예 → AI 아님</span></div>'
                '</div>', unsafe_allow_html=True)

    with st.expander("👮 정답표 (선생님용)"):
        ans = pd.DataFrame([{"No": c["no"], "사건": c["title"],
                             "판정": "AI다" if c["is_ai"] else "AI 아님",
                             "정답 특성": c["tag"] if c["is_ai"] else "해당 없음"} for c in CASES])
        st.dataframe(ans, use_container_width=True, hide_index=True)
