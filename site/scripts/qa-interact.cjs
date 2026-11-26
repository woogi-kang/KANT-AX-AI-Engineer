// 눌러 보는 검수: 찾기, 거르기, 플레이어, 실습 칸(파이썬, SQL, 재생형), 확인 문제, 테마, 휴대폰 목차를 PC와 휴대폰 폭에서 실제로 눌러 봐요.
// npm run build 뒤 out/을 띄우고(cd out && python3 -m http.server 8766) node scripts/qa-interact.cjs
const { chromium } = require("playwright");
const BASE = process.env.BASE || "http://localhost:8766";
const results = [];
const ok = (w, name, pass, info = "") => {
  results.push({ w, name, pass, info });
  console.log(`${pass ? "통과" : "실패"} [${w}] ${name}${info ? " · " + info : ""}`);
};

(async () => {
  const b = await chromium.launch();
  for (const [w, h] of [[1440, 900], [390, 844]]) {
    const ctx = await b.newContext({ viewport: { width: w, height: h } });
    const p = await ctx.newPage();
    const errs = [];
    p.on("pageerror", (e) => errs.push(e.message));

    // 1. 찾기
    await p.goto(BASE + "/", { waitUntil: "networkidle" });
    await p.click(w > 500 ? ".search" : ".sf");
    await p.waitForSelector(".dlg input");
    await p.fill(".dlg input", "트랜잭션");
    await p.waitForTimeout(600);
    const hits = await p.$$eval(".dlg-item", (e) => e.length);
    ok(w, "찾기: 트랜잭션", hits >= 2, `${hits}개`);
    await p.keyboard.press("ArrowDown");
    await p.keyboard.press("Enter");
    await p.waitForTimeout(900);
    ok(w, "찾기: 방향키와 Enter로 이동", p.url() !== BASE + "/", p.url().replace(BASE, ""));
    await p.goto(BASE + "/", { waitUntil: "networkidle" });
    await p.keyboard.press("/");
    await p.waitForTimeout(300);
    ok(w, "찾기: / 키로 열기", !!(await p.$(".dlg input")));
    await p.keyboard.press("Escape");
    await p.waitForTimeout(200);
    ok(w, "찾기: Esc로 닫기", !(await p.$(".dlg")));

    // 2. 거르기: 거르기 버튼을 모두 눌러 보고, 보이는 칸이 0이 되지 않는지 봐요
    for (const u of ["/lectures/", "/library/", "/library/public/", "/library/failures/", "/updates/", "/glossary/", "/library/templates/", "/library/jobs/"]) {
      await p.goto(BASE + u, { waitUntil: "networkidle" });
      const groups = await p.$$("main .fchips");
      let n = 0;
      const zero = [];
      for (const g of groups) {
        const btns = await g.$$("button");
        for (const bt of btns) {
          const label = (await bt.textContent()).trim();
          if (!(await bt.isVisible())) {
            await bt.scrollIntoViewIfNeeded().catch(() => {});
          }
          await bt.click();
          await p.waitForTimeout(150);
          const vis = await p.$$eval("main [data-f]", (els) => els.filter((e) => e.offsetParent !== null).length);
          const any = await p.$$eval("main [data-f]", (els) => els.length);
          n++;
          if (any && !vis) zero.push(label);
        }
        if (btns.length) await btns[0].click();
      }
      ok(w, `거르기 ${u}`, zero.length === 0, `묶음 ${groups.length}개, 버튼 ${n}개${zero.length ? ", 0칸: " + zero.join(",") : ""}`);
    }

    // 3. 플레이어와 파트
    await p.goto(BASE + "/chapters/36-sql-basics/", { waitUntil: "networkidle" });
    await p.click(".player .cover-btn");
    await p.waitForSelector(".player iframe");
    await p.waitForTimeout(1800);
    const fr = p.frames().find((f) => /sql-basics-slides(\.html)?(#|$)/.test(f.url()));
    const sections = fr ? await fr.$$eval("section", (s) => s.length) : 0;
    ok(w, "플레이어: 표지 누르면 덱이 열려요", sections > 10, `장 ${sections}개`);
    const kant = fr ? await fr.evaluate(() => document.body.innerText.includes("KANT")) : null;
    ok(w, "플레이어: 덱 첫 화면에 KANT가 없어요", kant === false);
    const parts = await p.$$(".part");
    if (parts[3]) {
      await parts[3].click();
      await p.waitForTimeout(700);
      const src = await p.$eval(".player iframe", (f) => f.getAttribute("src"));
      ok(w, "플레이어: 파트를 누르면 그 쪽으로", /#\d+$/.test(src), src.split("/").pop());
    } else ok(w, "플레이어: 파트", false, "파트 카드가 없어요");

    // 4. 실습 칸: 파이썬(13), SQL(36)
    for (const [u, name] of [["/chapters/13-python-strings-lists/", "파이썬"], ["/chapters/36-sql-basics/", "SQL"]]) {
      await p.goto(BASE + u, { waitUntil: "networkidle" });
      const cell = await p.$("article.pc:has(.pc-bar .btn.pri)");
      if (!cell) {
        ok(w, `실습 칸 ${name}`, false, "칸이 없어요");
        continue;
      }
      await cell.scrollIntoViewIfNeeded();
      const run = await cell.$(".pc-bar .btn.pri");
      await run.click();
      try {
        await p.waitForFunction((el) => el.dataset.state === "done", cell, { timeout: 120000 });
      } catch {}
      const st = await cell.evaluate((el) => ({ s: el.dataset.state, out: el.querySelector(".pc-out")?.textContent?.slice(0, 50), same: el.querySelector(".pc-st")?.textContent }));
      ok(w, `실습 칸 ${name}: 실행하면 수업 출력과 같아요`, st.s === "done" && /같아요/.test(st.same || ""), `${st.same || ""} · ${st.out || ""}`.replace(/\s+/g, " "));
      const ed = await cell.$(".cm-content, textarea, [contenteditable=true]");
      if (ed) {
        await ed.click();
        await p.keyboard.press("Control+End");
        await p.keyboard.type(name === "SQL" ? "\nSELECT 1 AS x;" : "\nprint('다르게')");
        await (await cell.$(".pc-bar .btn.pri")).click();
        await p.waitForTimeout(400);
        try {
          await p.waitForFunction((el) => el.dataset.state === "done", cell, { timeout: 30000 });
        } catch {}
        const st2 = await cell.$eval(".pc-st", (e) => e.textContent);
        ok(w, `실습 칸 ${name}: 고치면 "달라요"`, /달라요/.test(st2), st2);
        await cell.$$eval(".pc-bar .btn", (bs) => bs.find((x) => x.textContent.includes("처음으로"))?.click());
        await p.waitForTimeout(300);
        ok(w, `실습 칸 ${name}: 처음으로`, (await cell.evaluate((el) => el.dataset.state)) === "idle");
      } else ok(w, `실습 칸 ${name}: 코드 칸`, false, "입력 칸을 못 찾았어요");
    }

    // 재생형(02)
    await p.goto(BASE + "/chapters/02-git-basics/", { waitUntil: "networkidle" });
    const rin = await p.$(".rp-in input");
    if (rin) {
      await rin.scrollIntoViewIfNeeded();
      await rin.fill("git wrong");
      await rin.press("Enter");
      await p.waitForTimeout(300);
      const t1 = await rin.evaluate((e) => e.closest(".pc").innerText);
      await rin.fill('git config --global user.name "홍길동"');
      await rin.press("Enter");
      await p.waitForTimeout(400);
      const t2 = await p.$eval(".rp-term", (e) => e.innerText);
      ok(w, "재생형 칸(02): 맞는 명령을 치면 다음으로", t2.includes('user.name "홍길동"'), "");
      ok(w, "재생형 칸(02): 틀린 명령에 안내", t1.length > 0 && !t1.includes("Initialized"), t1.split("\n").slice(-2).join(" ").slice(0, 60));
    } else ok(w, "재생형 칸(02)", false, "입력 칸이 없어요");

    // 5. 확인 문제
    await p.goto(BASE + "/chapters/13-python-strings-lists/", { waitUntil: "networkidle" });
    const q = await p.$(".qz-q");
    if (q) {
      await q.scrollIntoViewIfNeeded();
      await (await q.$$(".qz-c"))[0].click();
      await p.waitForTimeout(200);
      const fb = await q.$eval(".qz-fb", (e) => e.textContent).catch(() => "");
      ok(w, "확인 문제: 고르면 해설", /맞았어요|아쉬워요/.test(fb), fb.slice(0, 24));
      const goBtn = await q.$(".qz-fb button");
      if (goBtn) {
        await goBtn.click();
        await p.waitForTimeout(900);
        ok(w, "확인 문제: 다시 보기로 그 쪽 열기", !!(await p.$(".player iframe")));
      }
      const tabs = await p.$$(".qz-tabs button");
      if (tabs.length > 1) {
        await tabs[1].scrollIntoViewIfNeeded();
        await tabs[1].click();
        await p.waitForTimeout(200);
        ok(w, "확인 문제: 파트 바꾸기", (await tabs[1].getAttribute("aria-selected")) === "true");
      }
    } else ok(w, "확인 문제", false, "문제가 없어요");

    // 6. 테마와 휴대폰 목차
    await p.goto(BASE + "/", { waitUntil: "networkidle" });
    await p.click('button[aria-label*="어두운"]');
    await p.waitForTimeout(150);
    ok(w, "테마: 어두운 화면으로", (await p.evaluate(() => document.documentElement.dataset.theme)) === "dark");
    await p.reload({ waitUntil: "networkidle" });
    ok(w, "테마: 새로 열어도 남아요", (await p.evaluate(() => document.documentElement.dataset.theme)) === "dark");
    await p.click('button[aria-label*="밝은"]');
    if (w < 500) {
      await p.click(".mtg");
      await p.waitForTimeout(300);
      const open = await p.evaluate(() => document.documentElement.dataset.nav);
      await p.click('.side a[href="/library/"]');
      await p.waitForTimeout(900);
      const closed = await p.evaluate(() => document.documentElement.dataset.nav);
      ok(w, "휴대폰 목차: 열고, 누르면 이동하고 닫혀요", open === "open" && !closed && p.url().endsWith("/library/"));
    }
    ok(w, "화면 오류 없음", errs.length === 0, errs.slice(0, 2).join(" / "));
    await ctx.close();
  }
  const bad = results.filter((r) => !r.pass);
  console.log(`\n눌러 보기 검수: ${results.length}개 중 실패 ${bad.length}개`);
  await b.close();
  process.exit(bad.length ? 1 : 0);
})();
