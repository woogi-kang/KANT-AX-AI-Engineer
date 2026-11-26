// 챕터와 꿀팁 교안(README)을 사이트에서 읽기 좋게 바꾸는 rehype 플러그인이에요.
// - 코드 칸(pre)마다 언어 이름과 복사 버튼을 붙여요(누르는 동작은 components/CopyCode.tsx).
// - "명령어 요약"의 두 칸 표는 명령 카드로, "문제 해결" 표는 메시지 카드로 바꿔요(휴대폰에서 표가 좁아 읽기 어려워서).
// - "실습"의 ### 단계에는 번호 칸을 붙여요.
import type { Root, Element, ElementContent, Text } from "hast";
import { toString } from "hast-util-to-string";

const h = (tagName: string, className: string | string[] | null, children: ElementContent[] = [], props: Record<string, unknown> = {}): Element => ({
  type: "element",
  tagName,
  properties: { ...(className ? { className: Array.isArray(className) ? className : [className] } : {}), ...props },
  children,
});
const t = (value: string): Text => ({ type: "text", value });
const isEl = (n: unknown, tag?: string): n is Element => !!n && (n as Element).type === "element" && (!tag || (n as Element).tagName === tag);
/** 좁히지 않고 묻기(거짓일 때 타입이 never가 되지 않게) */
const is = (n: unknown, tag?: string): boolean => isEl(n, tag);

// lucide copy, check 아이콘(MIT)
const svg = (paths: string[], cls: string): Element =>
  h(
    "svg",
    cls,
    paths.map((d) => h("path", null, [], { d })),
    { viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 2, strokeLinecap: "round", strokeLinejoin: "round", ariaHidden: "true" },
  );
const COPY = ["M8 4h10a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z", "M4 16V8a2 2 0 0 1 2-2"];
const CHECK = ["M20 6 9 17l-5-5"];
export const copyButton = (label = "코드 복사") => h("button", "copy", [svg(COPY, "i-copy"), svg(CHECK, "i-ok")], { type: "button", ariaLabel: label, title: label });

const LANG: Record<string, string> = { bash: "터미널", sh: "터미널", powershell: "PowerShell", python: "Python", sql: "SQL", yaml: "YAML", nginx: "nginx", html: "HTML", markdown: "Markdown", json: "JSON" };

function rows(table: Element) {
  const trs: Element[] = [];
  const walk = (n: Element) => n.children.forEach((c) => isEl(c) && (c.tagName === "tr" ? trs.push(c) : walk(c)));
  walk(table);
  const cells = (tr: Element) => tr.children.filter((c): c is Element => isEl(c, "td") || isEl(c, "th"));
  const [head, ...body] = trs;
  return { head: head ? cells(head).map((c) => toString(c).trim()) : [], body: body.map(cells) };
}
const tableOf = (n: ElementContent): Element | null => (is(n, "table") ? (n as Element) : is(n, "div") && is((n as Element).children[0], "table") ? ((n as Element).children[0] as Element) : null);

/** 명령 칸: 코드 하나만 있으면 복사할 수 있는 코드 줄로, 아니면 그대로 */
function cmdCard(code: Element, desc: Element) {
  const only = code.children.filter((c) => !(c.type === "text" && !c.value.trim()));
  const codes = only.filter((c) => isEl(c, "code"));
  const head =
    only.length === 1 && codes.length === 1
      ? h("div", "cmd-c", [h("code", null, (codes[0] as Element).children), copyButton("명령 복사")])
      : h("div", ["cmd-c", "multi"], code.children);
  return h("div", "cmd", [head, h("div", "cmd-d", desc.children)]);
}

export function rehypeLesson() {
  return (tree: Root) => {
    let sec = "";
    let step = 0;
    const out: Root["children"] = [];
    for (const n of tree.children) {
      if (isEl(n, "h2")) {
        sec = toString(n).trim();
        step = 0;
        out.push(n);
        continue;
      }
      const tb = isEl(n) ? tableOf(n as ElementContent) : null;
      if (tb && /^(명령어 요약|단축키 요약)/.test(sec)) {
        const { body } = rows(tb);
        if (body.every((r) => r.length === 2)) {
          out.push(h("div", "cmds", body.map(([a, b]) => cmdCard(a, b))));
          continue;
        }
      }
      if (tb && /^문제 해결/.test(sec)) {
        const { head, body } = rows(tb);
        if (head.length >= 2) {
          out.push(
            h(
              "div",
              "fixes",
              body.map((r) =>
                h("div", "fix", [
                  h("div", "fix-m", [h("span", "fix-k", [t(head[0])]), h("div", null, r[0].children)]),
                  h(
                    "dl",
                    null,
                    r.slice(1).flatMap((c, i) => [h("dt", null, [t(head[i + 1] ?? "")]), h("dd", null, c.children)]),
                  ),
                ]),
              ),
            ),
          );
          continue;
        }
      }
      if (is(n, "h3") && /^실습/.test(sec)) {
        const n3 = n as unknown as Element;
        step++;
        let no = String(step);
        const first = n3.children[0];
        if (first?.type === "text") {
          const m = /^(\d+)[.)]\s*/.exec(first.value);
          if (m) {
            no = m[1];
            first.value = first.value.slice(m[0].length);
          }
        }
        n3.properties = { ...n3.properties, className: ["step"] };
        n3.children = [h("span", "step-n", [t(no)]), h("span", null, n3.children)];
      }
      out.push(n);
    }
    tree.children = out;
    // 코드 칸에 언어 이름과 복사 버튼
    const wrap = (parent: Root | Element) => {
      parent.children.forEach((c, i) => {
        if (!isEl(c)) return;
        if (c.tagName === "pre") {
          const code = c.children.find((x) => isEl(x, "code")) as Element | undefined;
          const cls = (code?.properties?.className as string[] | undefined) ?? [];
          const lang = cls.find((x) => x.startsWith("language-"))?.slice(9) ?? "";
          (parent.children as ElementContent[])[i] = h("div", "cb", [h("div", "cb-h", [h("span", "cb-l", [t(LANG[lang] ?? (lang || "코드"))]), copyButton()]), c]);
        } else if (!c.properties?.className || !(c.properties.className as string[]).includes("cb")) wrap(c);
      });
    };
    wrap(tree);
  };
}
