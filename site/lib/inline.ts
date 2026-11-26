// curriculum.json의 한 줄 글에 있는 `코드`만 HTML로 바꿔요.
const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
export function renderInline(s: string) {
  return esc(s).replace(/`([^`]+)`/g, "<code>$1</code>");
}
export function plainInline(s: string) {
  return s.replace(/`/g, "");
}
