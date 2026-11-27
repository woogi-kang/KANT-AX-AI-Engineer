// 코드 칸에 IDE처럼 문법 색을 입히는 rehype 플러그인이에요(빌드할 때 한 번, 브라우저에서는 아무것도 안 돌아요).
// 색 이름만 CSS 변수(--syn-*, app/tokens.css)로 넣어서 밝은 화면과 어두운 화면이 같은 HTML을 써요.
// pre와 code의 속성(language- 이름)은 그대로 두고 안쪽 글자만 색 칸(span)으로 바꿔요. 복사 버튼은 textContent를 읽어서 글자만 복사돼요.
import { createHighlighter, type Highlighter, type ThemeRegistration } from "shiki";
import { visit } from "unist-util-visit";
import { toString } from "hast-util-to-string";
import type { Root, Element, ElementContent } from "hast";

// 색 대신 CSS 변수를 적은 테마예요. 실습 편집기(practice.css의 tok-*)와 같은 묶음으로 나눴어요.
const v = (k: string) => `var(--syn-${k})`;
const theme: ThemeRegistration = {
  name: "site",
  type: "light",
  colors: { "editor.foreground": v("fg"), "editor.background": "transparent" },
  tokenColors: [
    { settings: { foreground: v("fg") } },
    { scope: ["comment", "punctuation.definition.comment"], settings: { foreground: v("cm"), fontStyle: "italic" } },
    { scope: ["punctuation", "keyword.operator", "meta.brace"], settings: { foreground: v("pn") } },
    { scope: ["keyword", "storage", "keyword.operator.logical", "keyword.operator.word", "keyword.operator.new"], settings: { foreground: v("kw") } },
    { scope: ["string", "string.unquoted.plain.out.yaml", "punctuation.definition.string"], settings: { foreground: v("str") } },
    // 터미널 명령 뒤의 낱말(run, my-pg 같은 인자)은 글자색 그대로예요. 명령 이름과 옵션만 색을 달리해요
    { scope: ["string.unquoted.argument.shell"], settings: { foreground: v("fg") } },
    { scope: ["constant.numeric", "constant.language", "constant.character", "support.constant"], settings: { foreground: v("num") } },
    { scope: ["entity.name.tag", "support.type.property-name"], settings: { foreground: v("num") } },
    { scope: ["entity.name.function", "support.function", "entity.name.command", "meta.function-call.generic", "entity.name.type", "entity.other.inherited-class", "support.class"], settings: { foreground: v("fn") } },
    { scope: ["constant.other.option", "variable.parameter", "variable.other.normal.shell", "variable.other.readwrite"], settings: { foreground: v("var") } },
  ],
};
const LANGS = ["bash", "python", "sql", "yaml", "json", "powershell", "nginx", "html", "markdown"] as const;
const ALIAS: Record<string, string> = { sh: "bash", shell: "bash", console: "bash", py: "python", yml: "yaml", ps: "powershell", md: "markdown" };

let hl: Promise<Highlighter> | null = null;
const getHl = () => (hl ??= createHighlighter({ themes: [theme], langs: [...LANGS] }));

/** 명령 카드처럼 언어 표시가 없는 한 줄 코드의 언어를 짐작해요. 모르면 색을 안 입혀요. */
export function guessLang(code: string): string | null {
  const s = code.trim();
  if (/^(\$ |git |gh |docker |uv |cd |ls |pwd|mkdir |touch |cat |rm |cp |mv |echo |curl |brew |winget |wsl |npm |node |psql |mysql |source |deactivate|export |code |open |start |explorer|nano |vim |clear|exit|chmod |which |where |history|tree|python3? )/.test(s)) return "bash";
  if (/^(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|TRUNCATE|BEGIN|COMMIT|ROLLBACK|WITH|SHOW|USE|DESCRIBE|GRANT|EXPLAIN|FROM|WHERE|GROUP BY|ORDER BY|HAVING|LIMIT|JOIN|LEFT JOIN|UNION|CASE|SET)\b/i.test(s)) return "sql";
  if (/^(def |class |for |while |if |elif |else|import |from |return|print\(|lambda |with |try|@)/.test(s) || /^[A-Za-z_][\w.]*\s*(\(|=[^=]|\[)/.test(s)) return "python";
  return null;
}

function langOf(code: Element): string | null {
  const cls = (code.properties?.className as string[] | undefined) ?? [];
  const raw = cls.find((x) => x.startsWith("language-"))?.slice(9) ?? (code.properties?.dataHl as string | undefined) ?? "";
  const l = ALIAS[raw] ?? raw;
  return (LANGS as readonly string[]).includes(l) ? l : null;
}

export function rehypeHighlight() {
  return async (tree: Root) => {
    const jobs: Element[] = [];
    visit(tree, "element", (el: Element) => {
      if (el.tagName === "code" && langOf(el)) jobs.push(el);
    });
    if (!jobs.length) return;
    const h = await getHl();
    for (const code of jobs) {
      const lang = langOf(code)!;
      const text = toString(code).replace(/\n$/, "");
      const out = h.codeToHast(text, { lang, theme: "site" });
      // shiki가 만든 pre > code 안쪽의 줄(span.line)만 가져와요
      let inner: ElementContent[] = [];
      visit(out, "element", (el: Element) => {
        if (el.tagName === "code") {
          inner = el.children;
          return false;
        }
      });
      code.children = inner;
      const cls = ((code.properties.className as string[] | undefined) ?? []).filter((c) => c !== "hl");
      code.properties.className = [...cls, "hl"];
    }
  };
}
