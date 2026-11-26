import Link from "next/link";
import { Ict, PageHead } from "@/components/ui";

export default function NotFound() {
  return (
    <>
      <PageHead icon={<Ict n="map-pin-off" size="lg" />} eyebrow="404" title="없는 주소예요" lede="주소가 바뀌었거나 아직 없는 화면이에요. 위의 찾기 칸이나 왼쪽 목차에서 찾아 주세요." />
      <div className="acts" style={{ marginTop: 20 }}>
        <Link className="btn pri" href="/">
          홈으로
        </Link>
        <Link className="btn" href="/lectures/">
          강의 목록
        </Link>
      </div>
    </>
  );
}
