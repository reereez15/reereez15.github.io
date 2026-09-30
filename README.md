# reereez15.github.io

김준식의 개인 포트폴리오 사이트입니다.

## 배포 방법
1. 이 폴더 전체를 `reereez15.github.io` 저장소에 올립니다.
2. Settings → Pages → Source를 `main` 브랜치, 폴더는 `/ (root)`로 선택합니다.
3. `https://reereez15.github.io`에서 바로 열립니다.

## 폴더 구성
- `index.html` — 사이트 본체
- `documents/` — 이력서·자기소개서·경력기술서 (HTML 페이지 + 인쇄용 PDF)
- `extras/` — 깃허브 프로필 README 초안 등 부가 자료
- `tools/device/` — 새 기록을 넣으면 사이트에 쓸 숫자와 문단 후보를 다시 만들어주는 도구. 앞으로 리추얼 기록이 쌓일 때마다 계속 재사용합니다. 사용법은 `tools/device/README.md` 참고.
- `submission-notes/` — 이번 과제 제출을 위한 확인 자료(짧은 확인 방법, AI와 내 판단 3줄). 포트폴리오 내용과는 무관하니, 과제 제출이 끝나면 지워도 됩니다.

## 앞으로 내용을 갱신할 때
1. 새 리추얼 기록 파일을 준비합니다.
2. `cd tools/device && python3 generate.py <새 기록 파일> output` 실행.
3. `tools/device/output/paragraph_candidates.md`에서 마음에 드는 문장을 골라 `index.html`의 이야기·숫자 섹션에 직접 옮겨 씁니다.
4. 커밋하고 푸시하면 사이트가 갱신됩니다.

## 공개 전 확인할 것 (남은 건 이것뿐입니다)
- `index.html`에 `[본인이 쓸 ... — submission-notes/본인이-쓸-문장.md 참고]`라고 적힌 자리 3곳: 첫 화면 한 줄 소개, 이야기 섹션 첫 번째 커밋, 마지막 커밋.
- `submission-notes/본인이-쓸-문장.md`를 열어 문장을 정한 뒤, 그대로 `index.html`의 해당 자리에 옮겨 넣으면 됩니다(파일 안에 초안이 참고용으로 있지만 그대로 쓰면 안 됩니다).
- 그 외(이메일, 학력, 대표작 링크, 논문 등)는 이미 채워져 있습니다.
