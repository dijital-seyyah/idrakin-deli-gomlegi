#!/usr/bin/env python3
"""
İdrakin Deli Gömleği — Açık Bilim & Tekrarlanabilirlik Denetleyicisi (Reproducibility Auditor)
--------------------------------------------------------------------------------------------
Bu betik; 'İdrakin Deli Gömleği' manifestosunun XI. Bölümü (Tekrarlanabilirlik Krizi) ve
XXXII. Bölümü (10 Açık Bilim Şartnamesi) doğrultusunda bir projenin açık kaynak,
tekrarlanabilirlik ve bağımsız doğrulama standartlarına uygunluğunu denetler ve
0-100 arasında bir 'Açık Bilim ve Tekrarlanabilirlik Puanı' üretir.

Kullanım:
    python scripts/verify_reproducibility.py --path .
    python scripts/verify_reproducibility.py --path /path/to/project --json
"""

import argparse
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

CRITERIA = [
    {
        "id": "open_license",
        "name": "Açık Kaynak Lisansı (Open License)",
        "desc": "Projede tanınmış bir açık kaynak/erişim lisansı (MIT, Apache-2.0, GPL, CC BY-NC-SA, vb.) bulunmalıdır.",
        "weight": 15,
        "check": lambda path: any(os.path.exists(os.path.join(path, f)) for f in ["LICENSE", "LICENSE.md", "LICENSE.txt", "LICENCE"])
    },
    {
        "id": "readme_docs",
        "name": "Açıklayıcı Dokümantasyon & Amaç (README)",
        "desc": "Projenin ne yaptığını, nasıl kurulacağını ve çalıştırılacağını anlatan kapsamlı README belgesi.",
        "weight": 15,
        "check": lambda path: any(os.path.exists(os.path.join(path, f)) for f in ["README.md", "README.txt", "README.rst"])
    },
    {
        "id": "env_reproducibility",
        "name": "Çevre ve Bağımlılık Kilidi (Environment & Lockfile)",
        "desc": "Bağımlılıkların kesin sürümleriyle kilitlenmesi (requirements.txt, package.json, pyproject.toml, Cargo.toml, Dockerfile).",
        "weight": 15,
        "check": lambda path: any(os.path.exists(os.path.join(path, f)) for f in [
            "requirements.txt", "Pipfile.lock", "pyproject.toml", "package.json", "Cargo.toml", "Dockerfile", "environment.yml", "go.mod"
        ])
    },
    {
        "id": "reproducible_scripts",
        "name": "Çalıştırılabilir Kod ve Otomasyon (Executable Scripts)",
        "desc": "Analiz ve derleme süreçlerinin tek komutla veya betiklerle otomatikleştirilmesi (scripts/, Makefile, Justfile, Taskfile).",
        "weight": 15,
        "check": lambda path: os.path.exists(os.path.join(path, "scripts")) or any(os.path.exists(os.path.join(path, f)) for f in ["Makefile", "Justfile", "build.py", "run.sh"])
    },
    {
        "id": "testing_suite",
        "name": "Doğrulama ve Test Paketi (Automated Tests)",
        "desc": "Kodun doğruluğunu ve iddiaları test eden birim/entegrasyon testleri (tests/, test/ klasörleri veya test_*.py).",
        "weight": 15,
        "check": lambda path: os.path.exists(os.path.join(path, "tests")) or os.path.exists(os.path.join(path, "test")) or any("test" in f.lower() for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)))
    },
    {
        "id": "ci_pipeline",
        "name": "Sürekli Entegrasyon (CI Pipeline)",
        "desc": "Otomatik derleme ve testleri her değişiklikte çalıştıran CI konfigürasyonu (.github/workflows, .gitlab-ci.yml).",
        "weight": 15,
        "check": lambda path: os.path.exists(os.path.join(path, ".github", "workflows")) or os.path.exists(os.path.join(path, ".gitlab-ci.yml"))
    },
    {
        "id": "contribution_guide",
        "name": "Açık Akran Katkı Rehberi (Contributing Protocol)",
        "desc": "Dışarıdan bağımsız zihinlerin katkı sunabilmesi için rehber (CONTRIBUTING.md).",
        "weight": 10,
        "check": lambda path: any(os.path.exists(os.path.join(path, f)) for f in ["CONTRIBUTING.md", "CONTRIBUTING.txt"])
    }
]


def audit_repository(target_path="."):
    target_path = os.path.abspath(target_path)
    total_score = 0
    results = []

    for crit in CRITERIA:
        try:
            passed = crit["check"](target_path)
        except Exception:
            passed = False

        score = crit["weight"] if passed else 0
        total_score += score
        results.append({
            "id": crit["id"],
            "name": crit["name"],
            "desc": crit["desc"],
            "weight": crit["weight"],
            "passed": passed,
            "earned_score": score
        })

    grade = "F"
    if total_score >= 90:
        grade = "A+ (Kusursuz Açık Bilim & Otonom Tezgâh)"
    elif total_score >= 75:
        grade = "A (Yüksek Tekrarlanabilirlik)"
    elif total_score >= 55:
        grade = "B (Geliştirilmeye Açık)"
    elif total_score >= 35:
        grade = "C (Fildişi Kule Zaafiyeti)"
    else:
        grade = "F (Tekrarlanamaz / Kapalı Kutuda Kargo Kültü)"

    return {
        "target_path": target_path,
        "score": total_score,
        "grade": grade,
        "results": results
    }


def print_report(audit_data):
    print("=" * 72)
    print(" [IDRAKIN DELI GOMLEGI] - ACIK BILIM & TEKRARLANABILIRLIK DENETIMI")
    print("=" * 72)
    print(f"Dizin             : {audit_data['target_path']}")
    print(f"Toplam Puan       : {audit_data['score']} / 100")
    print(f"Liyakat Derecesi  : {audit_data['grade']}")
    print("-" * 72)

    for r in audit_data["results"]:
        status_icon = "[V] GECTI" if r["passed"] else "[X] EKSIK"
        print(f"{status_icon:10} {r['name']} ({r['earned_score']}/{r['weight']} Puan)")
        print(f"           {r['desc']}")

    print("=" * 72)
    if audit_data["score"] >= 80:
        print("Sonuc: Tebrikler! Eseriniz amfilerin kargo kultu duvarlarini asmis,")
        print("gercek dunyada bagimsizca dogrulanabilir acik bilim ilkelerine uygundur.")
    else:
        print("Tavsiye: Tekrarlanabilirligi ve guvenilirligi artirmak icin eksik")
        print("kriterleri tamamlayin ve acik standartlari uygulayin.")
    print("=" * 72)


def main():
    parser = argparse.ArgumentParser(description="Açık Bilim & Tekrarlanabilirlik Denetleyicisi")
    parser.add_argument("--path", "-p", default=".", help="Denetlenecek proje dizini")
    parser.add_argument("--json", "-j", action="store_true", help="JSON formatında çıktı")

    args = parser.parse_args()
    audit = audit_repository(args.path)

    if args.json:
        print(json.dumps(audit, ensure_ascii=False, indent=2))
    else:
        print_report(audit)


if __name__ == "__main__":
    main()
