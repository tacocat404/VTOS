/* 대시보드 공통 — 화면 셋이 같이 쓴다.
 *
 * 화면마다 복붙하면 한쪽만 고쳐져서 반드시 어긋난다.
 * 데이터는 window.DASHBOARD 에서 온다. 계약은 data.sample.js 참조.
 */
(function () {
  var D = window.DASHBOARD || null;

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function ago(iso) {
    if (!iso) return "";
    var m = Math.floor((Date.now() - new Date(iso)) / 60000);
    if (m < 1) return "방금";
    if (m < 60) return m + "분 전";
    if (m < 1440) return Math.floor(m / 60) + "시간 전";
    return Math.floor(m / 1440) + "일 전";
  }

  // 받침에 따라 조사를 고른다. "이서진 는" 은 한국어가 아니다.
  // 이름이 데이터에서 오므로 문구에 조사를 박아둘 수 없다.
  function josa(word, pair) {
    var w = String(word || ""), last = w.charCodeAt(w.length - 1);
    var hangul = last >= 0xac00 && last <= 0xd7a3;
    var batchim = hangul ? (last - 0xac00) % 28 !== 0
                         : /[1360-9lmnr]$/i.test(w.slice(-1));   // 숫자·영문도 대충 맞춘다
    return w + (batchim ? pair[0] : pair[1]);
  }

  var PHASE = {
    setup: "세팅 중", planning: "기획 중", merging: "정리 중",
    planned: "기획 완료", presenting: "발표 준비", archived: "종료"
  };

  // 병합 전에는 PRD·기여에 데이터가 없다. 숨기지 않고 회색으로 둔다 —
  // 나중에 저게 생긴다는 걸 알려주는 편이 낫다 (08-와이어프레임 1장).
  var TABS = [
    { href: "index.html",     label: "현황" },
    { href: "logs.html",      label: "기록" },
    { href: "questions.html", label: "질문" },
    { href: "prd.html",       label: "PRD",  after: "planned" },
    { href: "credit.html",    label: "기여", after: "planned" },
    { href: "history.html",   label: "이력" },
    { href: "system.html",    label: "설정" }
  ];

  var ORDER = ["setup", "planning", "merging", "planned", "presenting", "archived"];

  function nav(here) {
    var p = (D && D.project) || {};
    var reached = ORDER.indexOf(p.phase) >= 0 ? ORDER.indexOf(p.phase) : 0;
    var items = TABS.map(function (t) {
      var locked = t.todo || (t.after && reached < ORDER.indexOf(t.after));
      if (locked) return '<span title="아직 준비되지 않았습니다">' + esc(t.label) + "</span>";
      return '<a href="' + t.href + '"' + (t.href === here ? ' aria-current="page"' : "") +
        ">" + esc(t.label) + "</a>";
    }).join("");

    return '<span class="brand">' + esc(p.name || "팀 프로젝트") + "</span>" +
      '<span class="phase">' + esc(PHASE[p.phase] || p.phase || "") + "</span>" +
      '<nav class="tabs" aria-label="화면 이동">' + items + "</nav>";
  }

  // 데이터가 없어도 화면이 죽지 않아야 한다. 빈 화면에 이유를 적는다.
  function guard(el) {
    if (D) return true;
    document.getElementById(el).innerHTML =
      '<p class="empty">세팅이 끝나면 여기가 채워집니다.</p>';
    return false;
  }

  // 그리다 터져도 화면이 비지 않게 한다.
  // 빈 화면은 "데이터가 없다"로 읽힌다 — 실제로는 코드가 죽은 것인데.
  // 이 프로젝트가 제일 경계하는 조용한 실패라, 눈에 보이게 만든다.
  function run(elId, fn) {
    try {
      fn();
    } catch (e) {
      var el = document.getElementById(elId);
      if (el) {
        el.innerHTML = '<p class="empty">화면을 그리지 못했습니다 — ' + esc(e.message) +
          '<br>새로고침해도 같으면 브라우저 캐시를 비우세요 (Ctrl+Shift+R).</p>';
      }
      throw e;                 // 콘솔에도 남긴다
    }
  }

  window.T = { D: D, esc: esc, ago: ago, nav: nav, guard: guard, run: run, josa: josa, PHASE: PHASE };
})();
