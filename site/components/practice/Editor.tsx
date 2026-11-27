"use client";
import { useEffect, useRef, useState } from "react";

/**
 * 코드 칸. 처음에는 글자만 그려 두고, 칸이 화면 가까이 오면 CodeMirror를 불러 고칠 수 있게 바꿔요.
 * Ctrl+Enter(Mac은 ⌘+Enter)나 Shift+Enter로 실행해요. Tab은 띄어쓰기 4칸이고, Esc 뒤 Tab은 다음 칸으로 가요.
 */
type Props = {
  value: string;
  lang: "python" | "sql";
  label: string;
  onChange: (v: string) => void;
  onRun: () => void;
  onFocus?: () => void;
  version: number; // 처음으로를 누르면 바뀌어요
};

export default function Editor({ value, lang, label, onChange, onRun, onFocus, version }: Props) {
  const box = useRef<HTMLDivElement>(null);
  const view = useRef<import("@codemirror/view").EditorView | null>(null);
  const cb = useRef({ onChange, onRun, onFocus });
  cb.current = { onChange, onRun, onFocus };
  const [live, setLive] = useState(false);

  useEffect(() => {
    const el = box.current;
    if (!el) return;
    let dead = false;
    const start = async () => {
      const [{ EditorView, keymap, lineNumbers, drawSelection }, { EditorState }, cmds, lang_, hl, lz] = await Promise.all([
        import("@codemirror/view"),
        import("@codemirror/state"),
        import("@codemirror/commands"),
        lang === "python" ? import("@codemirror/lang-python").then((m) => m.python()) : import("@codemirror/lang-sql").then((m) => m.sql({ dialect: m.PostgreSQL })),
        import("@codemirror/language"),
        import("@lezer/highlight"),
      ]);
      if (dead || !box.current) return;
      const run = () => {
        cb.current.onRun();
        return true;
      };
      const v = new EditorView({
        parent: box.current,
        state: EditorState.create({
          doc: value,
          extensions: [
            lineNumbers(),
            cmds.history(),
            drawSelection(),
            hl.indentUnit.of("    "),
            hl.syntaxHighlighting(lz.classHighlighter),
            // 함수 이름도 교안 코드 칸(lib/highlight.ts)처럼 색을 달리해요
            hl.syntaxHighlighting(lz.tagHighlighter([{ tag: [lz.tags.function(lz.tags.variableName), lz.tags.function(lz.tags.propertyName)], class: "tok-fn" }])),
            hl.bracketMatching(),
            lang_,
            EditorState.tabSize.of(4),
            keymap.of([{ key: "Mod-Enter", run }, { key: "Shift-Enter", run }, cmds.indentWithTab, ...cmds.defaultKeymap, ...cmds.historyKeymap]),
            EditorView.updateListener.of((u) => {
              if (u.docChanged) cb.current.onChange(u.state.doc.toString());
              if (u.focusChanged && u.view.hasFocus) cb.current.onFocus?.();
            }),
            EditorView.contentAttributes.of({ "aria-label": label, autocapitalize: "off", autocorrect: "off", spellcheck: "false" }),
          ],
        }),
      });
      view.current = v;
      setLive(true);
      // 웹 글꼴(한글 포함)이 늦게 오면 줄 높이를 다시 재요. 줄 번호가 어긋나지 않게요.
      document.fonts?.ready.then(() => v.requestMeasure());
    };
    const io = new IntersectionObserver(
      (es) => {
        if (es.some((e) => e.isIntersecting)) {
          io.disconnect();
          start();
        }
      },
      { rootMargin: "400px" }
    );
    io.observe(el);
    return () => {
      dead = true;
      io.disconnect();
      view.current?.destroy();
      view.current = null;
    };
    // 처음 한 번만 만들어요. 글자는 아래 effect가 맞춰요.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lang, label]);

  // 처음으로: 원래 코드로 되돌려요.
  useEffect(() => {
    const v = view.current;
    if (v && v.state.doc.toString() !== value) v.dispatch({ changes: { from: 0, to: v.state.doc.length, insert: value } });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [version]);

  return (
    <div className={`pc-ed${live ? " live" : ""}`} ref={box}>
      {!live && (
        <pre className="pc-static" aria-label={label}>
          {value.split("\n").map((l, i) => (
            <span key={i}>
              <i>{i + 1}</i>
              {l || " "}
              {"\n"}
            </span>
          ))}
        </pre>
      )}
    </div>
  );
}
