import Link from "next/link";
import NavToggle from "./NavToggle";
import ThemeToggle from "./ThemeToggle";

export default function Header() {
  return (
    <header className="s-header">
      <NavToggle />
      <Link className="logo" href="/">
        풀스택 AI/AX<span>엔지니어</span>
      </Link>
      <div className="grow" />
      <ThemeToggle />
    </header>
  );
}
