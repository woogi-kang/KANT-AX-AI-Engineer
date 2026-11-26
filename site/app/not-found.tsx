import Link from "next/link";

export default function NotFound() {
  return (
    <main className="nf" id="main">
      <div className="code">404</div>
      <h1>없는 주소예요</h1>
      <p>주소가 바뀌었거나 아직 없는 페이지예요. 강의 목록에서 챕터를 찾아 주세요.</p>
      <Link className="btn primary" href="/">
        강의 목록으로
      </Link>
    </main>
  );
}
