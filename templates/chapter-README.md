# NN · 챕터 제목

> 이 챕터에서 하는 일을 두세 문장으로 적어요. 앞 챕터의 무엇을 이어서 쓰는지도 적어요.

<!-- curriculum:top -->

(python3 tools/build_readme.py가 채워요)

<!-- /curriculum:top -->

## 학습 목표

- 이 챕터를 마치면 할 수 있는 일을 한 줄에 하나씩 적어요.

## 시작하기 전에

- 필요한 앞 챕터와 준비물을 적어요. 바로 앞 번호가 아닌 챕터가 필요하면 여기에 밝혀요.

## 구성

| 파트 | 쪽 | 내용 |
| --- | --- | --- |
| 1 · 파트 이름 | 3~10 | 한 줄 설명 |

## 핵심 개념

그림과 짧은 설명으로 개념을 정리해요.

## 실습

수강생이 순서대로 복사해 칠 명령과 실제 출력을 적어요.

## 명령어 요약

| 명령 | 하는 일 |
| --- | --- |
| `명령` | 한 줄 설명 |

## 문제 해결

| 메시지 | 원인 | 해결 |
| --- | --- | --- |
| `오류 메시지` | 왜 나는지 | 어떻게 푸는지 |

## 강사용

<details>
<summary>파일 구조와 다시 만드는 법</summary>

```
slides/
  deck.json        슬라이드 순서와 파트 구분
  *.html           한 장에 한 파일 (1920×1080, 발표자 노트는 <aside>)
tools/
  gen.py           이 챕터의 장 생성
  demo.sh          슬라이드에 넣은 출력을 실제로 실행
주제-slides.html   배포용 HTML
주제-slides.pdf    강사용 PDF
```

검사, HTML, PDF를 만드는 공용 도구(`check.js`, `build_player.js`, `export.js`)는 맨 위 [tools/](../tools)에 한 벌만 있어요. 명령은 이 폴더에서 쳐요.

```bash
python3 tools/gen.py slides
node ../tools/check.js slides shots
node ../tools/build_player.js slides 주제-slides.html
node ../tools/export.js slides 주제-slides.pdf
```

</details>

---

<!-- curriculum:nav -->

(python3 tools/build_readme.py가 채워요)

<!-- /curriculum:nav -->
