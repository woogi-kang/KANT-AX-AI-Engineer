import Link from "next/link";
import { libCounts } from "@/lib/home";
import { LIB_HREF, LIB_IC, LIB_NAME, type LibKey } from "@/lib/site";
import { Ict } from "./ui";

/** 사례와 자료 다섯 묶음 타일. on은 지금 보고 있는 묶음 */
export default function LibTiles({ on }: { on: LibKey }) {
  const n = libCounts();
  return (
    <nav className="tiles t5" style={{ marginTop: 24 }} aria-label="사례와 자료 묶음">
      {(Object.keys(LIB_IC) as LibKey[]).map((k) => (
        <Link key={k} className={k === on ? "tile on" : "tile"} href={LIB_HREF[k]} aria-current={k === on ? "page" : undefined}>
          <span className="libt">
            <Ict n={LIB_IC[k]} size="sm" />
            <span className="num">{n[k]}</span>
          </span>
          <b>{LIB_NAME[k]}</b>
        </Link>
      ))}
    </nav>
  );
}
