"""curriculum.json 하나로 README의 표와 이동 링크를 만들어요.

    python3 tools/build_readme.py          # README를 고쳐 써요
    python3 tools/build_readme.py --check  # 고칠 게 있으면 목록을 보여 주고 1로 끝나요

<!-- curriculum:이름 --> 와 <!-- /curriculum:이름 --> 사이만 바꿔요. 그 밖의 글은 그대로 둬요.
"""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
WJ = "&#8288;"


def nobreak(word):
    return WJ.join(word)


def block(text, name, body):
    start, end = f"<!-- curriculum:{name} -->", f"<!-- /curriculum:{name} -->"
    pat = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pat.search(text):
        raise SystemExit(f"표시가 없어요: {start}")
    return pat.sub(lambda m: f"{start}\n\n{body}\n\n{end}", text, count=1)


def label(ch):
    return f"{ch['dir'][:2]} · {ch['title']}"


def main():
    check = "--check" in sys.argv
    data = json.loads((ROOT / "curriculum.json").read_text(encoding="utf-8"))
    pages, chapters, extras = data["pages"], data["chapters"], data["extras"]
    updates = data.get("updates", [])
    by_dir = {c["dir"]: c for c in chapters}
    out = {}

    def edit(path, *blocks):
        path = ROOT / path
        text = out.get(path) or path.read_text(encoding="utf-8")
        for name, body in blocks:
            text = block(text, name, body)
        out[path] = text

    for c in chapters + [dict(e, dir="extras/" + e["dir"]) for e in extras]:
        for need in ("README.md", c["slides"]):
            if not (ROOT / c["dir"] / need).exists():
                raise SystemExit(f"파일이 없어요: {c['dir']}/{need}")

    # 맨 위 README: 커리큘럼 표
    rows = [
        f"| 챕터 | {nobreak('분류')} | 한 줄 목표 | 핵심 명령 | {nobreak('슬라이드')} |",
        "| --- | --- | --- | --- | --- |",
    ]
    for c in chapters:
        rows.append(
            f"| [{label(c)}](./{c['dir']}) | {nobreak(c['track'])} | {c['goal']} | {c['commands']} "
            f"| [{nobreak('열기')}]({pages}/{c['dir']}/{c['slides']}) |"
        )
    extra_rows = lambda prefix: [
        f"| {nobreak('제목')} | 다루는 내용 | {nobreak('슬라이드')} |",
        "| --- | --- | --- |",
    ] + [
        f"| [{e['title']}]({prefix}{e['dir']}) | {e['summary']} "
        f"| [{nobreak('열기')}]({pages}/extras/{e['dir']}/{e['slides']}) |"
        for e in extras
    ]
    edit("README.md", ("chapters", "\n".join(rows)), ("extras", "\n".join(extra_rows("./extras/"))))
    edit("extras/README.md", ("extras", "\n".join(extra_rows("./"))))

    # 릴리스 노트: 맨 위 README에는 최근 3개, updates/README.md에는 전부 (최신이 위)
    for u in updates:
        if not (ROOT / "updates" / u["dir"] / "README.md").exists():
            raise SystemExit(f"파일이 없어요: updates/{u['dir']}/README.md")
    news = sorted(updates, key=lambda u: u["date"], reverse=True)
    note_rows = lambda items, prefix: [
        f"| {nobreak('날짜')} | 릴리스 노트 | 바뀐 점 |",
        "| --- | --- | --- |",
    ] + [f"| {u['date']} | [{u['title']}]({prefix}{u['dir']}) | {u['summary']} |" for u in items]
    edit("README.md", ("updates", "\n".join(note_rows(news[:3], "./updates/") + ["", "지난 릴리스 노트는 [전체 목록](./updates)에서 봐요."])))
    edit("updates/README.md", ("updates", "\n".join(note_rows(news, "./"))))
    for u in updates:
        edit(f"updates/{u['dir']}/README.md", ("nav", "[릴리스 노트 목록](../README.md) · [커리큘럼](../../README.md)"))

    # 챕터 README: 맨 위 표와 맨 아래 이동 링크
    for i, c in enumerate(chapters):
        prev = chapters[i - 1] if i > 0 else None
        nxt = chapters[i + 1] if i + 1 < len(chapters) else None
        prev_cell = f"[{label(prev)}](../{prev['dir']})" if prev else "없음"
        next_cell = f"[{label(nxt)}](../{nxt['dir']})" if nxt else "준비 중"
        top = "\n".join([
            f"| {nobreak('슬라이드')} | 이전 챕터 | 다음 챕터 |",
            "| --- | --- | --- |",
            f"| [브라우저로 열기]({pages}/{c['dir']}/{c['slides']}) | {prev_cell} | {next_cell} |",
        ])
        nav = []
        if prev:
            nav.append(f"[← 이전: {label(prev)}](../{prev['dir']})")
        nav.append("[커리큘럼](../README.md)")
        if nxt:
            nav.append(f"[다음: {label(nxt)} →](../{nxt['dir']})")
        edit(f"{c['dir']}/README.md", ("top", top), ("nav", " · ".join(nav)))

    # 번외 README: 맨 위 표와 맨 아래 이동 링크
    for e in extras:
        related = ", ".join(f"[{label(by_dir[d])}](../../{d})" for d in e["related"])
        top = "\n".join([
            f"| {nobreak('슬라이드')} | 관련 챕터 | 번외 목록 |",
            "| --- | --- | --- |",
            f"| [브라우저로 열기]({pages}/extras/{e['dir']}/{e['slides']}) | {related} | [번외 목록](../README.md) |",
        ])
        edit(f"extras/{e['dir']}/README.md", ("top", top), ("nav", "[커리큘럼](../../README.md) · [번외 목록](../README.md)"))

    changed = [p for p, t in out.items() if p.read_text(encoding="utf-8") != t]
    if check:
        for p in changed:
            print("다시 만들어야 해요:", p.relative_to(ROOT))
        sys.exit(1 if changed else 0)
    for p in changed:
        p.write_text(out[p], encoding="utf-8")
        print("고쳤어요:", p.relative_to(ROOT))


if __name__ == "__main__":
    main()
