import Link from "next/link";

export const OWNER = "Taewook Kang (woogi)";
export const CONTACT = "woogi@memoriz.net";

export default function SiteFooter() {
  return (
    <footer className="site-foot">
      <p>
        © 2026 {OWNER}. 이 사이트의 슬라이드, 글, 그림, 코드 예제의 저작권은 {OWNER}에게 있어요. 허락 없이 복제하거나 다른 곳에 올리고, 고쳐서 다시 배포하거나 판매할 수 없어요.
      </p>
      <nav aria-label="이용 안내">
        <Link href="/legal/">이용 안내</Link>
        <Link href="/legal/#oss">사용한 오픈 소스</Link>
        <a href={`mailto:${CONTACT}`}>허락 문의</a>
      </nav>
    </footer>
  );
}
