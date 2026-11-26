// 빌드 전에 로드맵 레포(woogi-kang/ax-engineer-roadmap, MIT, 공개)를 site/.roadmap에 받아요.
// ROADMAP_DIR를 적으면 그 폴더를 그대로 쓰고 받지 않아요.
// 이미 받아 둔 폴더가 있으면 새로 받아 보고, 받지 못하면 있던 것을 써요.
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";

const SITE = path.resolve(import.meta.dirname, "..");
const DEST = path.join(SITE, ".roadmap");
const URL = "https://github.com/woogi-kang/ax-engineer-roadmap.git";
const BRANCH = process.env.ROADMAP_BRANCH || "main";

if (process.env.ROADMAP_DIR) {
  if (!fs.existsSync(path.join(process.env.ROADMAP_DIR, "README.md"))) throw new Error(`ROADMAP_DIR에 README.md가 없어요: ${process.env.ROADMAP_DIR}`);
  console.log(`fetch-roadmap: ROADMAP_DIR(${process.env.ROADMAP_DIR})를 써요`);
  process.exit(0);
}

const git = (args, cwd) => execFileSync("git", args, { cwd, stdio: ["ignore", "pipe", "pipe"], encoding: "utf8" }).trim();

try {
  if (fs.existsSync(path.join(DEST, ".git"))) {
    git(["fetch", "--depth", "1", "origin", BRANCH], DEST);
    git(["reset", "--hard", "FETCH_HEAD"], DEST);
  } else {
    fs.rmSync(DEST, { recursive: true, force: true });
    git(["clone", "--depth", "1", "--branch", BRANCH, URL, DEST], SITE);
  }
  console.log(`fetch-roadmap: ${git(["log", "-1", "--format=%h %cs %s"], DEST)}`);
} catch (e) {
  if (fs.existsSync(path.join(DEST, "README.md"))) {
    console.warn(`fetch-roadmap: 새로 받지 못해 있던 것을 써요 (${String(e.message).split("\n")[0]})`);
  } else {
    throw new Error(`로드맵 레포를 받지 못했어요. 인터넷을 확인하거나 ROADMAP_DIR=폴더 로 적어 주세요.\n${e.message}`);
  }
}
