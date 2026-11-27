import type { Metadata } from "next";
import { Check, X } from "lucide-react";
import { CONTACT, COPYRIGHT as OWNER } from "@/lib/site";
import { Crumb, Ict, PageHead } from "@/components/ui";

export const metadata: Metadata = { title: "이용 안내와 저작권" };

const OSS = [
  ["Pretendard", "본문 글꼴", "SIL OFL 1.1"],
  ["JetBrains Mono, D2Coding", "코드 글꼴 (D2Coding은 한글만)", "SIL OFL 1.1"],
  ["Lucide", "아이콘", "ISC"],
  ["devicon", "도구 컬러 로고", "MIT"],
  ["Simple Icons", "uv 로고, 일부 사례 회사 로고", "CC0 1.0"],
  ["VectorLogoZone, CNCF Landscape", "사례 회사 로고", "로고는 각 회사의 상표"],
  ["KRDS", "대한민국 정부 상징(국내 정부 기관 사례)", "KRDS 이용약관"],
  ["ax-engineer-roadmap", "로드맵, 사례, 템플릿, 채용 현황 내용", "MIT"],
  ["Next.js, React", "사이트 틀", "MIT"],
  ["unified, remark, rehype", "README를 화면으로 바꾸기", "MIT"],
];

export default function LegalPage() {
  return (
    <>
      <Crumb items={[["홈", "/"], ["이 사이트에 대해"]]} />
      <PageHead icon={<Ict n="info" size="lg" />} title="이용 안내와 저작권" lede={<>모든 챕터는 무료로 볼 수 있어요. 다만 자료의 저작권은 {OWNER}에게 있어서, 혼자 공부하는 데까지만 쓸 수 있어요.</>} />
      <div className="legal-2">
        <div className="can">
          <h2>
            <Check className="i" />할 수 있어요
          </h2>
          <ul>
            <li>사이트에서 슬라이드와 노트를 보고 따라 치기</li>
            <li>PDF를 받아 혼자 보거나 인쇄해서 공부하기</li>
            <li>예제 코드를 내 컴퓨터에서 따라 치고 고쳐 보기</li>
            <li>친구에게 사이트 주소(링크) 알려 주기</li>
          </ul>
        </div>
        <div className="cant">
          <h2>
            <X className="i" />
            허락 없이는 할 수 없어요
          </h2>
          <ul>
            <li>슬라이드, PDF, 글, 그림을 다른 사이트, 카페, 블로그, 메신저 방에 올리기</li>
            <li>고치거나 번역해서 다시 배포하기</li>
            <li>판매하거나 유료 강의, 다른 교육 자료, 회사 교육에 쓰기</li>
            <li>저작권 표시와 출처를 지우고 쓰기</li>
            <li>사이트 내용을 한꺼번에 내려받아 모으기(크롤링)</li>
          </ul>
        </div>
      </div>
      <div className="legal-ask">
        <b>허락이 필요할 때</b>
        <p>쓰려는 곳과 범위를 적어 메일로 보내 주세요. 허락받은 뒤에도 &quot;출처: 풀스택 AI/AX 엔지니어&quot;와 사이트 주소를 함께 적어 주세요.</p>
        <a className="mail" href={`mailto:${CONTACT}`}>
          {CONTACT}
        </a>
      </div>
      <h2 className="legal-h" id="oss">
        사용한 오픈 소스
      </h2>
      <p className="note" style={{ margin: "0 0 10px" }}>
        아래는 각 라이선스대로 쓰고, 이 사이트의 저작권 범위에 들어가지 않아요.
      </p>
      <table className="legal-t">
        <thead>
          <tr>
            <th>이름</th>
            <th>쓰는 곳</th>
            <th>라이선스</th>
          </tr>
        </thead>
        <tbody>
          {OSS.map(([a, b, c]) => (
            <tr key={a}>
              <td>{a}</td>
              <td>{b}</td>
              <td>{c}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="note" style={{ marginTop: 12 }}>
        Git, GitHub, Python, uv, Jupyter, Docker, NGINX, MySQL, PostgreSQL, NumPy, pandas 로고와 이름은 각 상표권자의 것이에요. 이 사이트는 어떤 도구를 배우는지 알려 주는 데만 쓰고, 상표권자와 제휴하거나 후원받지 않아요.
      </p>
      <p className="note" style={{ marginTop: 8 }}>
        사례와 자료의 조직 로고는 어느 조직의 공개 기록인지 알아보는 데만 써요. 국내 정부 기관 사례에는 대한민국 정부 상징을 붙였어요. 로고가 없는 조직은 이름 첫 글자로 보여 줘요. 상표와 상징은 각 소유자의 것이고, 이 사이트는 그 조직들과 관계가 없어요.
      </p>
    </>
  );
}
