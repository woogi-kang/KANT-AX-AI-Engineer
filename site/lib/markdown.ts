// 레포의 README를 사이트 본문 HTML로 바꿔요.
// curriculum.json이 만든 맨 위 표와 맨 아래 이동 링크는 사이트가 따로 그려서 빼고,
// 레포 안 링크는 사이트 주소나 GitHub 주소로 바꿔요.
import fs from "node:fs";
import path from "node:path";
import { unified } from "unified";
import remarkParse from "remark-parse";
import remarkGfm from "remark-gfm";
import remarkRehype from "remark-rehype";
import rehypeRaw from "rehype-raw";
import rehypeSlug from "rehype-slug";
import rehypeStringify from "rehype-stringify";
import { visit } from "unist-util-visit";
import type { Root, Element } from "hast";
import { ROOT, REPO_URL } from "./content";

/** 레포 안 경로(README가 있는 폴더 기준)를 사이트 주소로 바꿔요. */
export function mapRepoLink(fromDir: string, href: string): string {
  if (/^([a-z]+:|#|\/\/)/i.test(href)) return href;
  const [p, hash = ""] = href.split("#");
  const h = hash ? `#${hash}` : "";
  if (!p) return h;
  const rel = path.posix.normalize(path.posix.join(fromDir, decodeURI(p))).replace(/\/$/, "");
  let m: RegExpMatchArray | null;
  if (rel === "README.md" || rel === "." || rel === "") return `/${h}`;
  if ((m = rel.match(/^(\d\d-[a-z0-9-]+)(\/README\.md)?$/))) return `/chapters/${m[1]}/${h}`;
  if ((m = rel.match(/^extras\/([a-z0-9-]+)(\/README\.md)?$/))) return `/extras/${m[1]}/${h}`;
  if (/^extras(\/README\.md)?$/.test(rel)) return `/tips/${h}`;
  if ((m = rel.match(/^updates\/([^/]+)(\/README\.md)?$/))) return `/updates/${m[1]}/${h}`;
  if (/^updates(\/README\.md)?$/.test(rel)) return `/updates/${h}`;
  if ((m = rel.match(/^updates\/([^/]+)\/img\/(.+)$/))) return `/updates/${m[1]}/img/${m[2]}`;
  const isDir = fs.existsSync(path.join(ROOT, rel)) && fs.statSync(path.join(ROOT, rel)).isDirectory();
  return `${REPO_URL}/${isDir ? "tree" : "blob"}/main/${encodeURI(rel)}${h}`;
}

type Mapper = (href: string) => string;

function rewrite(map: Mapper) {
  return (tree: Root) => {
    visit(tree, "element", (el: Element) => {
      const key = el.tagName === "a" ? "href" : el.tagName === "img" ? "src" : null;
      if (!key) return;
      const v = el.properties?.[key];
      if (typeof v !== "string") return;
      const nv = map(v);
      el.properties[key] = nv;
      if (el.tagName === "a" && /^https?:/.test(nv)) {
        el.properties.target = "_blank";
        el.properties.rel = ["noopener"];
      }
      if (el.tagName === "img") el.properties.loading = "lazy";
    });
    // 넓은 표는 가로로 밀어 볼 수 있게 감싸요
    visit(tree, "element", (el: Element, i, parent) => {
      if (el.tagName !== "table" || !parent || i === undefined) return;
      (parent.children as Element[])[i] = {
        type: "element",
        tagName: "div",
        properties: { className: ["table-wrap"] },
        children: [el],
      };
      return i + 1;
    });
  };
}

export type ReadmeOpts = { dropTitle?: boolean };

/** README.md를 읽어 본문 HTML과 첫 제목을 돌려줘요. relDir은 레포 기준 폴더예요. */
export async function renderReadme(relDir: string, opts: ReadmeOpts = { dropTitle: true }) {
  let md = fs.readFileSync(path.join(ROOT, relDir, "README.md"), "utf8");
  md = md.replace(/<!-- curriculum:(\w+) -->[\s\S]*?<!-- \/curriculum:\1 -->\n?/g, "");
  const title = md.match(/^# (.+)$/m)?.[1]?.trim() ?? "";
  if (opts.dropTitle) md = md.replace(/^# .+\n+/m, "");
  return { title, html: await renderMarkdown(md, (h) => mapRepoLink(relDir, h)) };
}

/** 마크다운 글을 HTML로 바꿔요. map은 링크와 그림 주소를 바꾸는 함수예요. */
export async function renderMarkdown(md: string, map: Mapper = (h) => h) {
  const file = await unified()
    .use(remarkParse)
    .use(remarkGfm)
    .use(remarkRehype, { allowDangerousHtml: true })
    .use(rehypeRaw)
    .use(rehypeSlug)
    .use(rewrite, map)
    .use(rehypeStringify)
    .process(md);
  return String(file);
}

/** 로드맵 레포 문서를 HTML로. 링크는 사이트 주소나 로드맵 레포 GitHub 주소로 바꿔요. */
export async function renderRoadmapMd(fromFile: string, md: string) {
  const { mapRoadmapLink } = await import("./roadmap");
  return renderMarkdown(md, (h) => mapRoadmapLink(fromFile, h));
}
