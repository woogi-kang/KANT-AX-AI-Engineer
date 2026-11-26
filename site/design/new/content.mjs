// 새 구조 시안 v6~v8이 같이 쓰는 내용이에요. 지금 챕터는 "자료"로만 붙이고, 사이트 뼈대는 역할, 단계, 주제로 새로 짰어요.
// 모든 문구는 예시 구성(초안)이에요. 숫자나 통계는 지어내지 않았어요.
import { byNo, i, esc, FONTS } from "../lib.mjs";

export const VERSION = "초안 0.1";
export const UPDATED = "2026-11-26";

const ch = (...nos) => nos.map((n) => byNo[n]).filter(Boolean);
export const deck = (c) => `../../decks/${c.dir}/${c.slides}`;
export const pdf = (c) => `../../decks/${c.dir}/${c.slides.replace(/\.html$/, ".pdf")}`;

/* 역할 두 가지 */
export const ROLES = [
  { id: "eng", icon: "user", name: "AI/AX 엔지니어 준비", who: "개발이 처음이어도 괜찮아요", goal: "AI를 쓰는 서비스를 직접 만들고 운영할 수 있게 돼요" },
  { id: "ax", icon: "building-2", name: "AX 도입 실무", who: "IT 회사가 아니어도 괜찮아요", goal: "우리 회사 업무에 AI를 안전하게 들여올 수 있게 돼요" },
];

/* 로드맵: 역할마다 단계, 단계마다 주제. need: 필수(true)·선택(false), res: 붙은 자료(챕터) */
const T = (id, title, need, res, sum) => ({ id, title, need, res, sum, ready: res.length > 0 });
export const ROADMAP = {
  eng: [
    { no: 1, title: "개발 도구 익히기", sum: "터미널과 Git으로 파일과 기록을 다뤄요", topics: [
      T("terminal", "터미널 명령", true, ch("01"), "폴더를 옮겨 다니고 파일을 만들어요"),
      T("git", "Git으로 기록 남기기", true, ch("02", "03", "04", "05"), "커밋, 브랜치, 비교를 손으로 해 봐요"),
      T("team", "팀에서 같이 쓰기", true, ch("06", "07", "08"), "충돌을 풀고 기록을 합쳐요"),
      T("gh", "GitHub CLI", false, ch("11"), "터미널에서 레포와 PR을 다뤄요"),
    ] },
    { no: 2, title: "파이썬으로 문제 풀기", sum: "값, 조건, 반복, 함수, 클래스를 차례로 쌓아요", topics: [
      T("py-env", "파이썬 환경 만들기", true, ch("09", "10"), "uv와 VS Code 노트북을 준비해요"),
      T("py-data", "값과 자료 구조", true, ch("12", "13", "14", "15", "16"), "리스트, 딕셔너리, 집합에 값을 담아요"),
      T("py-flow", "조건과 반복", true, ch("17", "18"), "if와 while로 흐름을 정해요"),
      T("py-func", "함수", true, ch("19", "20", "21", "22", "23"), "같은 일을 함수로 묶어 다시 써요"),
      T("py-class", "클래스와 모듈", false, ch("24", "25", "26", "27", "28"), "코드를 틀과 파일로 나눠요"),
    ] },
    { no: 3, title: "데이터 저장하고 꺼내기", sum: "표로 저장하고 SQL로 골라 봐요", topics: [
      T("db", "데이터베이스 개념", true, ch("32"), "표, 행, 열, 기본 키를 읽어요"),
      T("sql", "SQL로 골라 보고 고치기", true, ch("36", "37", "38", "39", "40", "41", "42", "43"), "조건, 집계, JOIN, 트랜잭션까지 써요"),
      T("py-db", "파이썬에서 DB 쓰기", true, ch("44"), "코드에서 SQL을 안전하게 실행해요"),
    ] },
    { no: 4, title: "실행 환경 만들기", sum: "컨테이너로 어디서나 같은 환경을 띄워요", topics: [
      T("docker", "Docker 컨테이너", true, ch("29", "30", "35"), "이미지를 받아 컨테이너로 켜요"),
      T("web", "웹 서버와 nginx", false, ch("31"), "요청을 받아 뒤로 넘겨요"),
      T("db-docker", "DB를 컨테이너로", false, ch("33", "34"), "MySQL과 PostgreSQL을 띄워요"),
      T("deploy", "배포하기", true, [], "만든 것을 인터넷에 올려요"),
    ] },
    { no: 5, title: "데이터 분석과 머신러닝 기초", sum: "데이터를 정리하고 첫 모델을 만들어요", topics: [
      T("pandas", "NumPy와 pandas", true, ch("45"), "표 데이터를 계산하고 골라요"),
      T("clean", "데이터 정리", true, ch("46"), "빈칸과 튀는 값을 다뤄요"),
      T("ml", "머신러닝 기초", true, [], "회귀와 분류 모델을 만들어요"),
    ] },
    { no: 6, title: "LLM 활용", sum: "언어 모델을 서비스에 붙여요", topics: [
      T("prompt", "프롬프트 설계", true, [], "원하는 답을 받는 질문을 써요"),
      T("rag", "RAG", true, [], "우리 문서를 찾아 답에 붙여요"),
      T("agent", "에이전트", false, [], "도구를 쓰는 AI를 만들어요"),
    ] },
    { no: 7, title: "평가와 운영", sum: "AI 기능이 맞게 도는지 재고 지켜요", topics: [
      T("eval", "평가하기", true, [], "답이 맞는지 기준을 세워 재요"),
      T("ops", "운영과 비용", false, [], "로그, 비용, 장애를 살펴요"),
    ] },
  ],
  ax: [
    { no: 1, title: "AX 이해하기", sum: "AI가 바꾸는 일과 못 바꾸는 일을 나눠요", topics: [
      T("ax-what", "AX가 뭔가요", true, [], "디지털 전환과 AX의 차이를 봐요"),
      T("ax-limit", "AI가 잘하는 일, 못하는 일", true, [], "틀릴 수 있는 곳을 먼저 알아요"),
    ] },
    { no: 2, title: "업무 고르기", sum: "AI를 먼저 붙일 업무를 정해요", topics: [
      T("task-map", "업무 지도 그리기", true, [], "반복되는 일과 판단하는 일을 나눠요"),
      T("task-pick", "첫 업무 고르기", true, [], "작고, 자주 하고, 틀려도 되돌릴 수 있는 일부터"),
    ] },
    { no: 3, title: "데이터 준비", sum: "흩어진 데이터를 표로 모아요", topics: [
      T("data-where", "데이터가 어디 있나", true, [], "엑셀, 메일, 시스템에 흩어진 것을 찾아요"),
      T("ax-pandas", "표 데이터 다루기", false, ch("45", "46"), "pandas로 정리하는 맛을 봐요"),
      T("ax-sql", "SQL 읽기", false, ch("32", "36"), "시스템 데이터를 직접 골라 봐요"),
    ] },
    { no: 4, title: "AI 도구 써 보기", sum: "이미 있는 도구로 먼저 해 봐요", topics: [
      T("tool-chat", "대화형 AI 쓰기", true, [], "문서 요약, 초안 쓰기를 해 봐요"),
      T("tool-auto", "업무 자동화 도구", false, [], "반복 작업을 이어 붙여요"),
    ] },
    { no: 5, title: "작게 시범 적용", sum: "한 팀, 한 업무에서 기간을 정해 해 봐요", topics: [
      T("pilot", "시범 계획 세우기", true, [], "범위, 기간, 잴 것을 정해요"),
      T("pilot-measure", "전후 비교하기", true, [], "걸린 시간과 고친 횟수를 재요"),
    ] },
    { no: 6, title: "지키며 넓히기", sum: "규칙을 세우고 다른 팀으로 넓혀요", topics: [
      T("security", "보안과 개인정보", true, [], "넣으면 안 되는 데이터를 정해요"),
      T("policy", "사내 사용 규칙", true, [], "누가, 무엇을, 어디까지 쓰는지 적어요"),
      T("train", "사내 교육", false, ch("01", "12"), "기초 자료로 함께 공부해요"),
    ] },
  ],
};
export const topicById = Object.fromEntries(Object.values(ROADMAP).flat().flatMap((s) => s.topics.map((t) => [t.id, { ...t, stage: s }])));

/* 주제 화면 예시: SQL로 골라 보고 고치기 */
export const TOPIC = {
  ...topicById.sql,
  why: "회사 데이터는 대부분 표에 들어 있어요. 엑셀로 내려받아 손으로 고르던 일을 SQL 한 문장으로 바로 골라 보고, 고치고, 합칠 수 있어요.",
  can: ["필요한 줄만 조건으로 골라 볼 수 있어요", "모아서 세고 더한 결과를 만들 수 있어요", "두 표를 이어 붙여 한 번에 볼 수 있어요", "여러 문장을 묶어 한꺼번에 되돌릴 수 있어요"],
  before: ["db"], after: "py-db",
};

/* 가이드라인: 기업 AX 도입 6단계 */
export const PHASES = [
  { no: 1, id: "direction", title: "방향 정하기", sum: "왜 AX를 하는지, 무엇을 바꾸고 싶은지 한 쪽으로 적어요" },
  { no: 2, id: "diagnose", title: "업무와 데이터 살펴보기", sum: "AI를 붙일 수 있는 업무와 그 업무의 데이터를 찾아요" },
  { no: 3, id: "pilot", title: "작게 시범 적용하기", sum: "한 팀, 한 업무에서 기간을 정해 해 보고 전후를 재요" },
  { no: 4, id: "decide", title: "평가하고 결정하기", sum: "잰 결과로 넓힐지, 고칠지, 멈출지 정해요" },
  { no: 5, id: "expand", title: "넓히고 가르치기", sum: "다른 팀으로 넓히고 함께 쓸 수 있게 가르쳐요" },
  { no: 6, id: "operate", title: "지키며 운영하기", sum: "보안, 개인정보, 비용, 품질을 계속 살펴요" },
];
export const PHASE = {
  ...PHASES[2],
  goal: "한 팀의 한 업무에서 AI를 정해진 기간 동안 써 보고, 쓰기 전과 후를 같은 기준으로 비교해요.",
  sections: ["목표", "먼저 물어볼 것", "체크리스트", "결과물", "흔한 함정", "누가 하나요", "관련 자료"],
  questions: ["이 업무를 지금 누가, 얼마나 자주 하나요?", "AI가 틀리면 누가 알아채고 어떻게 되돌리나요?", "회사 밖으로 나가면 안 되는 데이터가 섞여 있나요?", "끝났을 때 무엇을 보면 잘됐다고 말할 수 있나요?"],
  checklist: ["시범 업무 하나와 참여할 팀을 정했어요", "시작일과 끝나는 날을 정했어요", "쓰기 전 기준(걸린 시간, 고친 횟수 등)을 쟀어요", "넣으면 안 되는 데이터 목록을 팀과 같이 봤어요", "문제가 생기면 멈추는 방법을 정했어요", "끝나고 참여자 의견을 받을 방법을 정했어요"],
  outputs: [["시범 계획서", "현업 담당", "한 쪽짜리 양식"], ["전후 측정표", "현업 담당, 데이터 담당", "표 양식"], ["데이터 사용 확인서", "보안·법무", "체크리스트"], ["시범 결과 보고", "현업 담당", "4단계에서 써요"]],
  pitfalls: [["범위를 너무 넓게 잡아요", "여러 팀과 여러 업무를 한 번에 하면 무엇이 효과였는지 알 수 없어요. 한 팀, 한 업무로 시작해요."], ["쓰기 전을 재지 않아요", "끝나고 나서 \"좋아진 것 같다\"만 남아요. 시작하기 전에 같은 기준으로 한 번 재요."], ["멈추는 방법이 없어요", "AI가 틀린 결과를 냈을 때 누가 어떻게 멈추는지 미리 정해요."]],
  roles: [["경영진", "시범의 목적과 기간을 승인해요"], ["현업 담당", "업무를 고르고 전후를 재요"], ["IT·데이터 담당", "도구와 데이터 연결을 준비해요"], ["보안·법무", "쓸 수 있는 데이터의 범위를 정해요"]],
  res: ["45", "46", "36"],
};

/* 엔지니어 역량 기준(가이드라인의 두 번째 문서) */
export const LEVELS = [
  ["도구", "터미널과 Git으로 혼자 작업 기록을 남기고 팀 레포에 올릴 수 있어요"],
  ["코드", "파이썬으로 데이터를 읽고 함수와 클래스로 나눠 쓸 수 있어요"],
  ["데이터", "SQL로 필요한 데이터를 골라 보고 고칠 수 있어요"],
  ["환경", "컨테이너로 DB와 서버를 띄울 수 있어요"],
  ["AI", "언어 모델을 붙인 기능을 만들고 결과를 평가할 수 있어요"],
];

/* 여정: 사람마다 이정표 */
export const JOURNEYS = [
  { id: "new", color: "#2459C9", who: "개발을 처음 배우는 사람", icon: "user", miles: [
    ["첫 커밋 올리기", "터미널에서 파일을 만들고 GitHub에 올릴 수 있어요", ch("01", "02", "11")],
    ["파이썬으로 계산하기", "리스트와 딕셔너리로 값을 모으고 셀 수 있어요", ch("09", "12", "13", "15")],
    ["함수로 정리하기", "같은 일을 함수와 클래스로 묶어 다시 쓸 수 있어요", ch("19", "24", "28")],
    ["데이터베이스 다루기", "SQL로 표를 만들고 골라 볼 수 있어요", ch("32", "36", "39", "44")],
    ["컨테이너로 띄우기", "DB와 서버를 컨테이너로 켜고 끌 수 있어요", ch("29", "30", "34")],
    ["AI 기능 붙이기", "언어 모델을 불러 답을 받아 쓸 수 있어요", []],
  ] },
  { id: "ax", color: "#1F8A4C", who: "회사에서 AX 도입을 맡은 실무자", icon: "building-2", miles: [
    ["AX 큰 그림 잡기", "AI가 바꿀 일과 사람이 남을 일을 나눠 말할 수 있어요", []],
    ["첫 업무 고르기", "작고 되돌릴 수 있는 업무 하나를 고를 수 있어요", []],
    ["데이터 정리하기", "흩어진 엑셀을 하나의 표로 모을 수 있어요", ch("45", "46")],
    ["시범 돌려 보기", "한 팀에서 기간을 정해 써 보고 전후를 잴 수 있어요", []],
    ["규칙 세우고 넓히기", "사내 사용 규칙을 쓰고 다른 팀에 가르칠 수 있어요", []],
  ] },
  { id: "lead", color: "#B26A00", who: "팀이나 스터디를 이끄는 사람", icon: "users", miles: [
    ["순서 함께 정하기", "팀의 출발점을 보고 같이 볼 순서를 정할 수 있어요", []],
    ["같은 자료로 공부하기", "같은 슬라이드와 실습으로 함께 따라갈 수 있어요", ch("01", "12", "32")],
    ["과제로 확인하기", "단계마다 과제를 내고 같이 풀 수 있어요", []],
  ] },
];
export const MILE = { j: JOURNEYS[0], n: 3 };
MILE.m = MILE.j.miles[MILE.n];
MILE.task = { title: "카페 주문 표 만들고 골라 보기", steps: ["`orders` 표를 만들고 주문 다섯 건을 넣어요", "5,000원 넘는 주문만 골라 봐요", "메뉴별 주문 수를 세요", "다른 표(`menu`)와 이어 붙여 메뉴 이름을 같이 봐요"], hints: ["표를 만드는 문장은 32의 `CREATE TABLE` 장을 봐요", "조건은 `WHERE`, 세기는 `COUNT(*)`와 `GROUP BY`예요", "두 표를 이을 때는 `JOIN ... ON`을 써요"] };
MILE.check = ["`WHERE`와 `HAVING`은 언제 각각 쓰나요?", "`LEFT JOIN`을 쓰면 짝이 없는 줄은 어떻게 나오나요?", "`BEGIN` 없이 `DELETE`하면 되돌릴 수 있나요?"];

/* 시작점 진단: 화면에서만 계산하고 저장하지 않아요 */
export const QUIZ = [
  { q: "지금 어떤 일을 하고 있나요?", a: [["개발을 배우고 있어요", "new"], ["회사에서 AX를 맡았어요", "ax"], ["팀이나 스터디를 이끌어요", "lead"]] },
  { q: "터미널이나 코드를 써 본 적 있나요?", a: [["처음이에요", 0], ["조금 써 봤어요", 1], ["자주 써요", 2]] },
  { q: "가장 먼저 해 보고 싶은 것은요?", a: [["AI 도구를 업무에 써 보기", "tool"], ["데이터를 정리하고 분석하기", "data"], ["직접 서비스 만들기", "build"]] },
];

/* 공통: 꿀팁, 소식, 변경 이력 */
export const TIPS = [["터미널 경로와 도움말", "명령이 안 될 때 지금 위치와 도움말부터 봐요"], ["오류 메시지 읽는 법", "마지막 줄부터 읽고 첫 단어로 찾아요"], ["질문 잘하는 법", "친 명령, 나온 화면, 기대한 결과를 같이 보내요"]];
export const CHANGES = [["2026-11-26", "가이드라인 초안 0.1을 공개해요"], ["2026-11-24", "데이터 정리하기 자료를 더했어요"], ["2026-11-23", "모든 슬라이드에 PDF 받기를 더했어요"]];
export const FOOT_NEW = "공익 목적으로 만드는 공개 자료예요. 가입 없이 누구나 볼 수 있어요.";
export const COPY = "© 2026 Taewook Kang (woogi) · woogi@memoriz.net";

/* 찾기 창 (/ 또는 Ctrl K) */
export const searchKit = (items, href) => {
  const data = JSON.stringify(items);
  const dlg = `<div class="dlg" data-dlg role="dialog" aria-modal="true" aria-label="찾기"><div class="dlg-box"><div class="dlg-in">${i("search")}<input type="text" placeholder="주제, 단계, 명령어로 찾아요" aria-label="찾을 말"><kbd>Esc</kbd></div><div class="dlg-list"></div></div></div>`;
  const js = `<script>(()=>{const d=document.documentElement;
document.querySelectorAll('[data-theme-toggle]').forEach(b=>b.onclick=()=>{d.dataset.theme=d.dataset.theme==='dark'?'light':'dark'});
const dlg=document.querySelector('[data-dlg]');const inp=dlg.querySelector('input'),list=dlg.querySelector('.dlg-list');const data=${data};
function draw(){const q=inp.value.trim().toLowerCase();const it=data.filter(x=>!q||(x.t+' '+x.s).toLowerCase().includes(q)).slice(0,8);list.innerHTML=it.map((x,j)=>'<a class="dlg-item'+(j?'':' on')+'" href="${href}"><b>'+x.t.replace(/</g,'&lt;')+'</b><small>'+x.s+'</small></a>').join('')||'<p class="dlg-empty">찾는 내용이 없어요</p>'}
function open(){dlg.setAttribute('open','');inp.value='';draw();inp.focus()}
document.querySelectorAll('[data-search]').forEach(b=>b.onclick=open);inp.oninput=draw;dlg.onclick=e=>{if(e.target===dlg)dlg.removeAttribute('open')};
addEventListener('keydown',e=>{const t=e.target.tagName;if(e.key==='Escape')dlg.removeAttribute('open');else if(!dlg.hasAttribute('open')&&((e.key==='/'&&t!=='INPUT')||((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'))){e.preventDefault();open()}});
document.querySelectorAll('[data-tabs]').forEach(g=>{const bs=g.querySelectorAll('[data-tab]');bs.forEach(b=>b.onclick=()=>{bs.forEach(x=>x.setAttribute('aria-selected',x===b));document.querySelectorAll('[data-panel]').forEach(p=>p.hidden=p.dataset.panel!==b.dataset.tab)})});
})()</script>`;
  return { dlg, js };
};
export const DLG_CSS = (v) => `.dlg{position:fixed;inset:0;z-index:50;display:none;place-items:start center;padding:12vh 16px 16px;background:${v.scrim}}
.dlg[open]{display:grid}.dlg-box{width:min(560px,100%);background:${v.bg};color:${v.ink};border:1px solid ${v.line};border-radius:${v.r};box-shadow:0 20px 50px rgba(0,0,0,.18);overflow:hidden}
.dlg-in{display:flex;align-items:center;gap:10px;padding:14px 16px;border-bottom:1px solid ${v.line}}.dlg-in input{flex:1;min-width:0;border:0;background:none;font:inherit;font-size:16px;color:inherit;outline:none}
.dlg-in kbd{font-size:12px;border:1px solid ${v.line};border-radius:6px;padding:2px 6px;color:${v.sub}}.dlg-list{max-height:50vh;overflow:auto;padding:6px}
.dlg-item{display:flex;justify-content:space-between;gap:12px;padding:10px 12px;border-radius:8px}.dlg-item:hover,.dlg-item.on{background:${v.hover}}.dlg-item small{color:${v.sub};flex:none}.dlg-empty{padding:16px;color:${v.sub}}`;

export const items = [
  ...Object.entries(ROADMAP).flatMap(([r, ss]) => ss.flatMap((s) => s.topics.map((t) => ({ t: t.title, s: (r === "eng" ? "엔지니어 " : "AX 실무 ") + s.no + "단계" })))),
  ...PHASES.map((p) => ({ t: p.title, s: "가이드라인 " + p.no + "단계" })),
];
export const md = (s) => esc(s).replace(/`([^`]+)`/g, "<code>$1</code>");
export const html = (title, css, body, kit) => `<!doctype html><html lang="ko" data-theme="light"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${title}</title>
<link rel="preload" href="../v2/fonts/PretendardVariable.woff2" as="font" type="font/woff2" crossorigin><style>${FONTS}\n${css}</style></head><body>${body}${kit.dlg}${kit.js}</body></html>`;
