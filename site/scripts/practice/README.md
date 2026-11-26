# 실습 칸 (바로 쳐 보기)

챕터 화면의 "바로 쳐 보기"는 챕터 폴더의 `practice.json`을 읽어요. 칸은 세 가지예요.

| 종류 | 챕터 | 실행 | 수업 출력이 오는 곳 |
| --- | --- | --- | --- |
| `python` | 12~27, 45 | 브라우저 안 Pyodide(파이썬 3.14) | 챕터 `tools/run_nb.py`를 실제 Jupyter 커널로 실행한 출력 |
| `sql` | 36~43 | 브라우저 안 PGlite(PostgreSQL 19) | 챕터 `tools/demo.py`가 실제 `postgres:18` psql에서 담은 `tools/out.json` |
| `replay` | 01~11, 28~31, 33~35, 44, 46 | 실행하지 않아요. 친 명령이 맞으면 수업 출력을 보여 줘요 | 덱의 터미널 화면, 또는 `tools/out.json`, `tools/demo-output.txt` |

32는 읽기만 하는 챕터라 칸이 없어요.

## practice.json

```json
{
  "v": 1,
  "kind": "python",
  "source": "어디서 온 출력인지",
  "setup": "SQL만: 칸마다 먼저 넣는 준비 SQL(38~43은 sports.sql)",
  "packages": ["numpy", "pandas"],
  "cells": [
    { "id": "r2c3", "chain": "r2", "page": 6, "title": "장 제목", "part": "1. 문자열과 출력",
      "code": "word[6]", "expect": ["IndexError: string index out of range"], "err": true,
      "diff": "수업 화면과 다른 이유(있을 때만)" }
  ]
}
```

- `chain`이 같은 칸은 한 커널(파이썬), 한 데이터베이스 흐름(SQL)이에요. 칸을 실행하면 같은 `chain`의 앞 칸을 먼저 조용히 실행해서 수업과 같은 상태를 만들어요.
- `hidden: true`는 덱에 없는 앞 칸이에요. 화면에는 안 나오고 앞 칸으로만 써요.
- `noseed: true`는 SQL에서 `setup`을 넣지 않는 칸이에요.
- 재생형 칸은 `code`, `expect` 대신 `steps: [{ "cmd", "out", "cwd"? }]`예요.
- `diff`는 브라우저 엔진의 출력이 수업 출력과 다른 칸에만 적어요. 화면에 노란 줄로 나와요.

## 만들기

`practice.json`은 손으로 쓰지 않고 아래 스크립트로 만들어요. 다시 만들어도 `diff` 메모는 남아요(같은 id, 같은 코드일 때).

```bash
cd site/scripts/practice
# 파이썬: ipykernel, nbclient, nbformat(45는 numpy, pandas도)이 든 파이썬으로 수업 셀을 다시 실행해 모아요
python harvest_nb.py ../../../13-python-strings-lists > /tmp/13.json
python3 build_python.py /tmp/13.json                       # 45는 --packages numpy,pandas
# SQL: tools/out.json과 tools/demo.py의 scene(pre=, keep=)을 읽어요
python3 build_sql.py 36-sql-basics
# 재생형: 덱의 터미널 화면에서, 또는 tools/out.json, tools/demo-output.txt에서
python3 build_replay.py 02-git-basics
python3 build_replay_out.py 35-docker-cli
```

## 수업 출력과 대조하기

`npm run build` 뒤 `postbuild`가 `scripts/practice-check.mjs`로 파이썬, SQL 칸을 모두 실행해서 수업 출력과 견줘요. 다른 칸에 `diff` 메모가 없으면 빌드가 실패해요. 차이를 읽고 이유를 적을 때는 `node scripts/practice-check.mjs 36 --accept`로 메모 자리를 만든 뒤 문장을 고쳐요. 줄 끝 빈칸과 메모리 주소(`at 0x…`)는 보지 않아요.

## 엔진 파일

`scripts/copy-engines.mjs`가 빌드 전에 `engines/*.mjs`와 npm의 Pyodide 코어, PGlite를 `public/engines/`에 복사해요. CDN 대신 같은 사이트에서 내보내요. 그래서 학교나 회사 망에서 CDN이 막혀도 돌아가고, 엔진 버전은 `package.json`이 정해요. 처음 실행할 때만 받아요(파이썬 약 13MB, SQL 약 16MB). numpy, pandas 같은 패키지도 같은 사이트에 둬요. 빌드할 때 `practice.json`의 `packages`와 그 패키지가 기대는 패키지를 Pyodide 공식 CDN에서 `site/.pyodide-packages/`에 한 번 받아 두고, 잠금 파일(`pyodide-lock.json`)의 sha256과 맞는지 본 뒤 복사해요.

CDN(`cdn.jsdelivr.net`)이 막힌 곳에서는 패키지를 받지 못해도 경고만 남기고 빌드를 이어 가요. 그 빌드에서는 패키지를 쓰는 챕터(45)의 칸이 실행되지 않고, `practice-check`도 그 챕터를 건너뛰어요. 받기를 아예 건너뛰려면 `SKIP_PYODIDE_PACKAGES=1 npm run build`로 쳐요. Cloudflare 빌드(`CF_PAGES`)와 CI에서는 꼭 받아야 해서, 받지 못하면 빌드가 멈춰요.
