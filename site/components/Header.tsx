import Link from "next/link";
import NavToggle from "./NavToggle";
import ThemeToggle from "./ThemeToggle";
import BrandMark from "./BrandMark";

export default function Header() {
  return (
    <header className="s-header">
      <NavToggle />
      <Link className="logo" href="/" aria-label="풀스택 AI/AX 엔지니어 처음으로">
        <BrandMark />
        <span className="wm">
          풀스택 AI/AX<span>엔지니어</span>
        </span>
      </Link>
      <div className="grow" />
      <ThemeToggle />
    </header>
  );
}
