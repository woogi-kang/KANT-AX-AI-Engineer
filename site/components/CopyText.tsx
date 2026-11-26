"use client";
import { useState } from "react";
import { Check, Copy } from "lucide-react";

/** 글(마크다운 원문, 명령)을 그대로 복사하는 버튼. 누르면 잠깐 "복사했어요"로 바뀌어요. */
export default function CopyText({ text, label = "복사", done = "복사했어요", className = "btn" }: { text: string; label?: string; done?: string; className?: string }) {
  const [ok, setOk] = useState(false);
  const copy = async () => {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      // 클립보드 권한이 없는 브라우저: 숨긴 글 칸으로 복사해요
      const t = document.createElement("textarea");
      t.value = text;
      t.setAttribute("readonly", "");
      t.style.position = "fixed";
      t.style.opacity = "0";
      document.body.appendChild(t);
      t.select();
      document.execCommand("copy");
      t.remove();
    }
    setOk(true);
    setTimeout(() => setOk(false), 1600);
  };
  return (
    <button type="button" className={className} onClick={copy} aria-live="polite">
      {ok ? <Check aria-hidden="true" /> : <Copy aria-hidden="true" />}
      {ok ? done : label}
    </button>
  );
}
