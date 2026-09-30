#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
장치: 리추얼 기록 파일을 넣으면
1) 숫자 칸(출처 포함)
2) 능력별(자기동기력·자기조절력·대인관계력) 문단 후보
를 다시 만들어 output/ 폴더에 저장한다.

같은 입력 파일이면 항상 같은 결과가 나온다(재현성).
외부 네트워크나 AI 서비스 호출 없이, 순수 텍스트 규칙만으로 동작한다.

사용법:
    python3 generate.py <리추얼_기록.txt> [출력_폴더]

예:
    python3 generate.py sample_input/ritual-history-sample.txt output
"""
import sys
import re
import json
import os
import hashlib

# ---- 능력별 키워드 규칙 (결정적: 정렬된 리스트, 고정 순서) ----
COMPETENCY_KEYWORDS = {
    "자기동기력": [
        "역추적", "끝까지", "파고드", "포기하지", "집요", "몰입", "끈기",
        "탐구", "원인을", "해결했다",
    ],
    "자기조절력": [
        "우선순위", "쳐냈다", "계획", "판단력", "정리", "분류", "결단력",
        "욕심부리지", "일정에 맞춰",
    ],
    "대인관계력": [
        "도움", "친화력", "배려", "챙기", "인사", "경청", "친절", "고맙",
        "감사", "먼저 말",
    ],
}

DATE_RE = re.compile(r"^## (\d{4}-\d{2}-\d{2})\s*$")
FIELD_RE = re.compile(r"^- (.+?): (.+)$")


def parse_entries(text):
    """리추얼 기록 텍스트를 날짜별 필드 딕셔너리 리스트로 분해한다."""
    entries = []
    current_date = None
    current_fields = []
    for line in text.splitlines():
        m = DATE_RE.match(line.strip())
        if m:
            if current_date:
                entries.append((current_date, current_fields))
            current_date = m.group(1)
            current_fields = []
            continue
        fm = FIELD_RE.match(line.strip())
        if fm and current_date:
            current_fields.append((fm.group(1), fm.group(2)))
    if current_date:
        entries.append((current_date, current_fields))
    # 날짜순 정렬(입력 순서와 무관하게 항상 같은 순서가 되도록)
    entries.sort(key=lambda e: e[0])
    return entries


def count_practice(entries):
    full = 0
    partial = 0
    for _, fields in entries:
        for k, v in fields:
            if k == "강점 행동":
                if "실천했다" == v.strip():
                    full += 1
                elif "일부 실천했다" in v:
                    partial += 1
    return full, partial


def collect_competency_quotes(entries):
    """필드 중 '강점이 드러난 일화'와 '~가 말해 준 내 장점' 계열만 검사해
    키워드가 매치되면 (날짜, 필드명, 원문)을 후보로 모은다."""
    results = {k: [] for k in COMPETENCY_KEYWORDS}
    target_field_prefixes = ("강점이 드러난 일화", "그 결과", "동료", "내가 나눈 감사", "감사일기")
    for date, fields in entries:
        for k, v in fields:
            if not any(k.startswith(p) or p in k for p in target_field_prefixes):
                continue
            for comp, keywords in COMPETENCY_KEYWORDS.items():
                for kw in keywords:
                    if kw in v:
                        results[comp].append(
                            {"date": date, "field": k, "text": v}
                        )
                        break  # 능력 하나에 필드 하나는 한 번만 추가
    # 결정적 정렬: 날짜 → 필드명 → 본문
    for comp in results:
        results[comp].sort(key=lambda r: (r["date"], r["field"], r["text"]))
    return results


def build_number_cells(entries, full, partial):
    total_days = len(entries)
    span = f"{entries[0][0]} ~ {entries[-1][0]}" if entries else "(기록 없음)"
    cells = [
        {
            "label": "기록 일수",
            "value": total_days,
            "unit": "일",
            "source": "리추얼 기록 파일 — 날짜 헤더(## YYYY-MM-DD) 개수",
        },
        {
            "label": "기록 기간",
            "value": span,
            "unit": "",
            "source": "리추얼 기록 파일 — 첫/마지막 날짜",
        },
        {
            "label": "강점 행동 완전 실천",
            "value": full,
            "unit": "일",
            "source": "리추얼 기록 파일 — [마무리] 강점 행동 = '실천했다'",
        },
        {
            "label": "강점 행동 일부 실천",
            "value": partial,
            "unit": "일",
            "source": "리추얼 기록 파일 — [마무리] 강점 행동 = '일부 실천했다'",
        },
    ]
    return cells


def main():
    if len(sys.argv) < 2:
        print("사용법: python3 generate.py <리추얼_기록.txt> [출력_폴더]")
        sys.exit(1)

    input_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "output"
    os.makedirs(out_dir, exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as f:
        text = f.read()

    entries = parse_entries(text)
    full, partial = count_practice(entries)
    quotes = collect_competency_quotes(entries)
    cells = build_number_cells(entries, full, partial)

    input_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]

    stats = {
        "input_file": os.path.basename(input_path),
        "input_sha256_12": input_hash,
        "number_cells": cells,
        "competency_quote_counts": {k: len(v) for k, v in quotes.items()},
    }

    stats_path = os.path.join(out_dir, "stats.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    md_lines = ["# 능력별 문단 후보 (자동 생성 — 사람이 다시 골라 다듬을 것)\n"]
    md_lines.append(f"입력 파일: `{stats['input_file']}` (sha256 앞 12자리: `{input_hash}`)\n")
    for comp in ["자기동기력", "자기조절력", "대인관계력"]:
        md_lines.append(f"\n## {comp} ({len(quotes[comp])}건)\n")
        if not quotes[comp]:
            md_lines.append("- (해당 키워드로 매치된 문장 없음)\n")
        for q in quotes[comp]:
            md_lines.append(f"- {q['date']} · {q['field']}: {q['text']}\n")

    md_lines.append("\n## 숫자 칸\n")
    for c in cells:
        md_lines.append(f"- {c['label']}: {c['value']}{c['unit']} (출처: {c['source']})\n")

    candidates_path = os.path.join(out_dir, "paragraph_candidates.md")
    with open(candidates_path, "w", encoding="utf-8") as f:
        f.writelines(md_lines)

    print(f"완료. {stats_path}, {candidates_path} 생성됨.")
    print(f"입력 sha256(12): {input_hash}  (같은 입력이면 항상 같은 값)")


if __name__ == "__main__":
    main()
