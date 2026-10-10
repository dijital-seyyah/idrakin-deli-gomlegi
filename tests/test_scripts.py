#!/usr/bin/env python3
"""
İdrakin Deli Gömleği — Birim ve Entegrasyon Testleri
---------------------------------------------------
Tüm otomasyon araçlarını, derleyicileri, müfredat üreteçlerini ve
tekrarlanabilirlik denetleyicilerini test eder.
"""

import json
import os
import sys
import unittest

# Ensure scripts dir is in path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import arxiv_polymat_digest
import generate_offline_book
import polymat_curriculum_gen
import verify_reproducibility


class TestIdrakinDeliGomlegiSuite(unittest.TestCase):

    def setUp(self):
        self.test_dir = os.path.join(os.path.dirname(__file__), "tmp_test_output")
        os.makedirs(self.test_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            for f in os.listdir(self.test_dir):
                try:
                    os.remove(os.path.join(self.test_dir, f))
                except Exception:
                    pass
            try:
                os.rmdir(self.test_dir)
            except Exception:
                pass

    def test_arxiv_fallback_and_exports(self):
        sample_papers = arxiv_polymat_digest.generate_fallback_sample_data("deep learning")
        self.assertEqual(len(sample_papers), 1)
        self.assertIn("Autonomous Polymath", sample_papers[0]["title"])

        md_file = arxiv_polymat_digest.export_to_markdown(sample_papers, output_dir=self.test_dir)
        self.assertTrue(os.path.exists(md_file))
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Otonom Polimat", content)
            self.assertIn("First Principles", content)

        json_file = arxiv_polymat_digest.export_to_json(sample_papers, output_dir=self.test_dir)
        self.assertTrue(os.path.exists(json_file))
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["total_papers"], 1)

    def test_curriculum_generation(self):
        for domain in ["yapay-zeka", "gomulu-sistemler", "sistem-muhendisligi", "matematik-felsefe"]:
            cur_file = polymat_curriculum_gen.generate_curriculum(domain, duration_days=30, output_dir=self.test_dir)
            self.assertIsNotNone(cur_file)
            self.assertTrue(os.path.exists(cur_file))
            with open(cur_file, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("Proof of Work", content)
                self.assertIn("İlk İlkeler", content)

    def test_reproducibility_auditor(self):
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        audit_result = verify_reproducibility.audit_repository(repo_root)
        self.assertGreaterEqual(audit_result["score"], 80)
        self.assertIn("target_path", audit_result)
        self.assertIn("results", audit_result)

    def test_offline_book_generation(self):
        generate_offline_book.build_offline_book()
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        dist_file = os.path.join(repo_root, "dist", "idrakin-deli-gomlegi-kitap.html")
        self.assertTrue(os.path.exists(dist_file))
        with open(dist_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("İdrakin Deli Gömleği", content)
            self.assertIn("Cemil Meriç", content)


if __name__ == "__main__":
    unittest.main()
