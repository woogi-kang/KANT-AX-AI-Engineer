"use client";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Search } from "lucide-react";

type Item = { t: string; s: string; h: string; k?: string };

const norm = (s: string) => s.toLowerCase().replace(/\s+/g, " ");

/** 찾기 창. data-search가 붙은 버튼, / 키, Ctrl(⌘)+K로 열어요. 목록은 처음 열 때 /search.json에서 받아요. */
export default function SearchDialog() {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const [items, setItems] = useState<Item[] | null>(null);
  const [on, setOn] = useState(0);
  const input = useRef<HTMLInputElement>(null);
  const list = useRef<HTMLDivElement>(null);
  const router = useRouter();

  const show = useCallback(() => {
    setOpen(true);
    setQ("");
    setOn(0);
    if (!items)
      fetch("/search.json")
        .then((r) => r.json())
        .then(setItems)
        .catch(() => setItems([]));
  }, [items]);

  useEffect(() => {
    const click = (e: MouseEvent) => {
      if ((e.target as HTMLElement).closest("[data-search]")) {
        e.preventDefault();
        show();
      }
    };
    const key = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement;
      const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName) || t.isContentEditable;
      if ((e.key === "/" && !typing) || ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k")) {
        e.preventDefault();
        show();
      }
    };
    addEventListener("click", click);
    addEventListener("keydown", key);
    return () => {
      removeEventListener("click", click);
      removeEventListener("keydown", key);
    };
  }, [show]);

  useEffect(() => {
    if (open) {
      input.current?.focus();
      document.body.style.overflow = "hidden";
    } else document.body.style.overflow = "";
  }, [open]);

  const hits = useMemo(() => {
    if (!items) return [];
    const words = norm(q).trim().split(" ").filter(Boolean);
    if (!words.length) return items.filter((x) => x.s.startsWith("로드맵") || x.s.startsWith("강의")).slice(0, 12);
    const scored: [number, Item][] = [];
    for (const x of items) {
      const t = norm(x.t);
      const all = t + " " + norm(x.k ?? "") + " " + norm(x.s);
      if (!words.every((w) => all.includes(w))) continue;
      scored.push([words.every((w) => t.includes(w)) ? (t.startsWith(words[0]) ? 0 : 1) : 2, x]);
    }
    return scored.sort((a, b) => a[0] - b[0]).slice(0, 40).map((x) => x[1]);
  }, [items, q]);

  useEffect(() => {
    list.current?.querySelector(".on")?.scrollIntoView({ block: "nearest" });
  }, [on]);

  if (!open) return null;
  const go = (h: string) => {
    setOpen(false);
    router.push(h);
  };
  return (
    <div className="dlg" role="dialog" aria-modal="true" aria-label="찾기" onMouseDown={(e) => e.target === e.currentTarget && setOpen(false)}>
      <div className="dlg-box">
        <div className="dlg-in">
          <Search aria-hidden="true" />
          <input
            ref={input}
            type="search"
            value={q}
            placeholder="주제, 챕터, 명령어, 사례, 용어 찾기"
            aria-label="찾을 말"
            aria-controls="dlg-list"
            onChange={(e) => {
              setQ(e.target.value);
              setOn(0);
            }}
            onKeyDown={(e) => {
              if (e.key === "Escape") setOpen(false);
              else if (e.key === "ArrowDown") {
                e.preventDefault();
                setOn((n) => Math.min(n + 1, hits.length - 1));
              } else if (e.key === "ArrowUp") {
                e.preventDefault();
                setOn((n) => Math.max(n - 1, 0));
              } else if (e.key === "Enter" && hits[on]) go(hits[on].h);
            }}
          />
          <kbd>Esc</kbd>
        </div>
        <div className="dlg-list" id="dlg-list" ref={list} role="listbox">
          {!items && <p className="dlg-empty">목록을 불러오고 있어요</p>}
          {items && !hits.length && <p className="dlg-empty">찾는 내용이 없어요. 다른 말로 찾아 보세요.</p>}
          {!q && items && <p className="dlg-group">자주 찾는 곳</p>}
          {hits.map((x, j) => (
            <a
              key={x.h + j}
              href={x.h}
              role="option"
              aria-selected={j === on}
              className={j === on ? "dlg-item on" : "dlg-item"}
              onMouseEnter={() => setOn(j)}
              onClick={(e) => {
                e.preventDefault();
                go(x.h);
              }}
            >
              <b>{x.t}</b>
              <small>{x.s}</small>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}
