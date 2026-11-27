import { navData } from "@/lib/nav";
import { Ic, Logo } from "./ui";
import NavLink from "./NavLink";
import NavGroup from "./NavGroup";
import NavFold from "./NavFold";

/** 왼쪽 전체 목차. 좁은 화면에서는 머리글의 목차 버튼으로 열어요. */
export default function SideNav() {
  const d = navData();
  return (
    <nav className="side" id="side" aria-label="전체 목차">
      <h4>시작</h4>
      <NavLink href="/start/">
        <Ic n="signpost" />
        처음 오셨나요
      </NavLink>
      <NavLink href="/glossary/">
        <Ic n="book-a" />
        용어 사전
      </NavLink>

      <h4>로드맵</h4>
      <NavLink href="/roadmap/">
        <Ic n="route" />
        전체 단계
      </NavLink>
      {d.roadmap.map((s) => (
        <div key={s.no}>
          <NavLink href={`/roadmap/#stage-${s.no}`} exact>
            <Ic n={s.icon} />
            {s.title}
          </NavLink>
          {s.no < 5 && (
            <NavGroup hrefs={s.topics.map((t) => t.href)}>
              {s.topics.map((t) => (
                <NavLink key={t.href} href={t.href}>
                  {t.t}
                </NavLink>
              ))}
            </NavGroup>
          )}
        </div>
      ))}

      <h4>강의</h4>
      <NavLink href="/lectures/">
        <Ic n="presentation" />
        전체 강의
      </NavLink>
      {d.lectures.map((s) => (
        <NavFold
          key={s.no}
          id={`lec-${s.no}`}
          href={s.chapters[0].href}
          head={
            <>
              <Logo k={s.logo} size={18} />
              {s.title}
            </>
          }
          hrefs={s.chapters.map((c) => c.href)}
          count={s.chapters.length}
        >
          {s.chapters.map((c) => (
            <NavLink key={c.href} href={c.href}>
              <span className="n">{c.no}</span>
              {c.t}
            </NavLink>
          ))}
        </NavFold>
      ))}
      <NavLink href="/tips/" exact={false}>
        <Ic n="lightbulb" />
        꿀팁
      </NavLink>

      <h4>사례와 자료</h4>
      {d.library.map((l) => (
        <NavLink key={l.key} href={l.href} exact={l.key === "cases"}>
          <Ic n={l.icon} />
          {l.title}
        </NavLink>
      ))}

      <h4>그 밖</h4>
      <NavLink href="/updates/" exact={false}>
        <Ic n="megaphone" />
        소식
      </NavLink>
      <NavLink href="/legal/">
        <Ic n="info" />
        이 사이트에 대해
      </NavLink>
    </nav>
  );
}
