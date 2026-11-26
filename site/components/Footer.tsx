import Link from "next/link";
import { roadmap, ROADMAP_URL } from "@/lib/roadmap";
import { CONTACT, COPYRIGHT } from "@/lib/site";

export default function Footer() {
  const r = roadmap();
  return (
    <footer className="ft">
      <b>공익 목적으로 만드는 공개 자료예요. 가입이나 결제 없이 누구나 처음부터 끝까지 볼 수 있어요.</b>
      <p>
        로드맵 내용: <a href={ROADMAP_URL}>ax-engineer-roadmap</a> {r.version}, MIT License
      </p>
      <p>강의 내용: © 2026 {COPYRIGHT}. 개인 학습에 자유롭게 보되, 허락 없이 옮겨 싣거나 고쳐 배포할 수 없어요.</p>
      <p>
        로고: devicon(MIT), Simple Icons(CC0). 각 로고의 상표는 그 소유자에게 있어요. <Link href="/legal/">이용 안내</Link> · 고칠 곳과 질문: <a href={`mailto:${CONTACT}`}>{CONTACT}</a>
      </p>
    </footer>
  );
}
