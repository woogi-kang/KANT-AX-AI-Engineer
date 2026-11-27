"use client";
import { useEffect } from "react";

/**
 * 교안 도우미. 절 목록(.ls-toc)에서 고른 절 하나만 보여 줘요. 주소의 #절 이름으로 오면(예: "명령어 요약" 버튼) 그 절을 열어요.
 * 교안의 복사 버튼(button.copy, lib/lesson.ts가 붙여요)을 눌렀을 때 코드를 복사해요.
 * 코드 칸(.cb)은 pre 글자를, 명령 카드(.cmd-c)는 code 글자를 복사하고, 1.5초 동안 체크 표시로 바꿔요.
 */
export default function LessonTools() {
  useEffect(() => {
    const box = document.querySelector<HTMLElement>(".lesson-v2");
    if (!box) return;
    const pick = (id: string, scroll = false) => {
      const sec = box.querySelector<HTMLElement>(`[data-sec-id="${CSS.escape(id)}"]`);
      if (!sec) return false;
      box.dataset.sec = id;
      box.querySelectorAll<HTMLElement>(".ls-sec").forEach((x) => (x.hidden = x !== sec));
      box.querySelectorAll<HTMLElement>(".ls-toc [data-to]").forEach((b) => b.setAttribute("aria-current", String(b.dataset.to === id)));
      if (scroll && box.getBoundingClientRect().top < 0) box.scrollIntoView({ block: "start" });
      return true;
    };
    const fromHash = () => {
      const id = decodeURIComponent(location.hash.slice(1));
      const el = id ? document.getElementById(id) : null;
      const sec = el?.closest<HTMLElement>("[data-sec-id]")?.dataset.secId;
      if (sec) pick(sec);
    };
    pick(box.dataset.sec ?? "");
    fromHash();
    const onClick = (e: MouseEvent) => {
      const b = (e.target as Element | null)?.closest?.<HTMLElement>(".ls-toc [data-to]");
      if (!b || !box.contains(b)) return;
      if (pick(b.dataset.to!, true)) history.replaceState(history.state, "", `#${b.dataset.to}`);
    };
    box.addEventListener("click", onClick);
    addEventListener("hashchange", fromHash);
    return () => {
      box.removeEventListener("click", onClick);
      removeEventListener("hashchange", fromHash);
    };
  }, []);
  useEffect(() => {
    const onClick = async (e: MouseEvent) => {
      const b = (e.target as Element | null)?.closest?.("button.copy");
      if (!b) return;
      const box = b.closest(".cb, .cmd-c, [data-copy-box]");
      const src = box?.querySelector("pre, code, [data-copy]");
      const text = (src?.getAttribute("data-copy") ?? src?.textContent ?? "").replace(/\n$/, "");
      try {
        await navigator.clipboard.writeText(text);
      } catch {
        const ta = document.createElement("textarea");
        ta.value = text;
        ta.style.position = "fixed";
        ta.style.opacity = "0";
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        ta.remove();
      }
      b.classList.add("done");
      b.setAttribute("aria-label", "복사했어요");
      setTimeout(() => {
        b.classList.remove("done");
        b.setAttribute("aria-label", b.getAttribute("title") ?? "코드 복사");
      }, 1500);
    };
    document.addEventListener("click", onClick);
    return () => document.removeEventListener("click", onClick);
  }, []);
  return null;
}
