#!/usr/bin/env python3
"""
İdrakin Deli Gömleği — Otonom Polimat Müfredat Üreteci (Curriculum Generator)
-----------------------------------------------------------------------------
Bu betik; amfilerin sararmış, 30 yıllık müfredatlarını bir kenara bırakıp,
seçilen teknik ve felsefi alanda ilk ilkeler (First Principles), açık kaynak projeler,
arXiv literatürü ve somut "Proof of Work" aşamalarından oluşan 30/60/90 günlük
kişiselleştirilmiş otonom çalışma izlenceleri üretir.

Kullanım:
    python scripts/polymat_curriculum_gen.py --domain "yapay-zeka" --duration 30
    python scripts/polymat_curriculum_gen.py --domain "gomulu-sistemler" --duration 60 --output-dir curriculums
"""

import argparse
import datetime
import os
import sys

CURRICULUM_TEMPLATES = {
    "yapay-zeka": {
        "title": "Yapay Zekâ, LLM Mimarisi ve Otonom Sistemler",
        "philosophy": "Kütüphane çağıran değil, transformatörün matematiksel gradyanını ve tensör akışını sıfırdan inşa eden otonom polimat.",
        "milestones": [
            {
                "phase": "Faz 1: İlk İlkeler & Matematiksel Temel (Lineer Cebir & Gradyanlar)",
                "days": "1 - 10",
                "topics": [
                    "Matris çarpımı, Özdeğerler/Özvektörler, SVD ayrışımı",
                    "Geriye doğru yayılım (Backpropagation) algoritmasının elle ve saf Python ile türetilmesi",
                    "Loss fonksiyonları: Cross-Entropy, KL Divergence ve Entropi kavramı"
                ],
                "pow": "Saf C/Python ile hiçbir kütüphane olmadan çalışan 2 katmanlı sinir ağı motoru reposu."
            },
            {
                "phase": "Faz 2: Dikkat Mekanizması & Transformer Çekirdeği",
                "days": "11 - 20",
                "topics": [
                    "Attention Is All You Need (Vaswani et al., 2017) orijinal makale analizi",
                    "Scaled Dot-Product Attention ve Multi-Head Attention mekanizması",
                    "RoPE (Rotary Positional Embedding), FlashAttention ve KV-Cache optimizasyonları"
                ],
                "pow": "PyTorch/JAX ile sıfırdan yazılmış nano-GPT / mikro-LLM modeli ve ağırlık transferi."
            },
            {
                "phase": "Faz 3: Yerel Çalıştırma, Fine-Tuning ve Ajan Mimarileri",
                "days": "21 - 30",
                "topics": [
                    "Llama.cpp, Ollama, GGUF kuantizasyonu (4-bit, 8-bit)",
                    "LoRA / QLoRA parametre verimli ince ayar matematiği",
                    "ReAct döngüsü, Function Calling ve otonom araç kullanan yerel ajan zincirleri"
                ],
                "pow": "Yerel GPU/CPU üzerinde çalışan, web araması yapabilen ve kod çalıştıran otonom araştırma ajanı."
            }
        ]
    },
    "gomulu-sistemler": {
        "title": "Açık Donanım, RISC-V ve Gömülü Sistemler Tezgâhı",
        "philosophy": "Sararmış slaytları izlemek yerine havya tutan, osiloskop sinyali okuyan ve silikon mimarisini sorgulayan usta mühendis.",
        "milestones": [
            {
                "phase": "Faz 1: Temel Elektronik, Şematik Tasarım ve PCB",
                "days": "1 - 10",
                "topics": [
                    "Ohm, Kirchhoff kanunları, RLC devreleri, Transistör ve MOSFET anahtarlama",
                    "KiCad ile açık şematik ve çift katmanlı PCB tasarımı",
                    "Güç regülatörleri (LDO ve Buck dönüştürücüler), dekuplaj kondansatörleri"
                ],
                "pow": "KiCad ile tasarlanmış, Gerber çıktısı alınmış açık kaynak ESP32/RP2040 geliştirme kartı şeması."
            },
            {
                "phase": "Faz 2: Düşük Seviye Sürücüler (Bare-Metal) ve Protokoller",
                "days": "11 - 20",
                "topics": [
                    "UART, SPI, I2C, CAN Bus protokollerinin osiloskop / mantık analizörü ile incelenmesi",
                    "C ve Rust ile Bare-Metal Register düzeyinde sürücü (HAL-free) kodlama",
                    "Kesmeler (Interrupts), DMA (Direct Memory Access) ve Donanımsal Zamanlayıcılar"
                ],
                "pow": "Register seviyesinde I2C OLED ekran ve IMU sensör sürücüsü kütüphanesi."
            },
            {
                "phase": "Faz 3: RISC-V Mimarisi & Gömülü RTOS / Linux",
                "days": "21 - 30",
                "topics": [
                    "RISC-V ISA (RV32I/RV64I) buyruk kümesi ve assembly komutları",
                    "FreeRTOS ile görev zamanlama, semaforlar ve kuyruk yönetimi",
                    "Gömülü Linux (Buildroot / Yocto) temel çekirdek derleme"
                ],
                "pow": "FreeRTOS üzerinde çalışan çok görevli sensör füzyon ve telemetri telekomünikasyon istasyonu."
            }
        ]
    },
    "sistem-muhendisligi": {
        "title": "Linux Çekirdeği, İşletim Sistemleri ve Düşük Seviye Güvenlik",
        "philosophy": "Kullanıcı alanının ötesine geçip kernel alanında, bellek yönetiminde ve assembly düzeyinde hükmeden zihin.",
        "milestones": [
            {
                "phase": "Faz 1: Bellek Modeli, Pointer Aritmetiği ve POSIX",
                "days": "1 - 10",
                "topics": [
                    "Sanal bellek, Page Table, MMU mimarisi, Stack ve Heap dinamikleri",
                    "POSIX sistem çağrıları (fork, execve, pipe, mmap, epoll)",
                    "GDB ve Valgrind ile bellek sızıntısı ve çökme analizi"
                ],
                "pow": "POSIX uyumlu, boru hatlarını (pipe) ve arka plan süreçleri destekleyen özel bir Shell (Kabuk)."
            },
            {
                "phase": "Faz 2: Linux Çekirdek Modülleri ve eBPF",
                "days": "11 - 20",
                "topics": [
                    "LKM (Loadable Kernel Module) yazımı ve dmesg / procfs etkileşimi",
                    "eBPF (Extended Berkeley Packet Filter) ile çekirdek seviyesinde telemetri ve ağ paket filtreleme",
                    "Kernel senkronizasyon mekanizmaları: spinlock, mutex, RCU"
                ],
                "pow": "Çekirdeğe dinamik bağlanan ve ağ trafiğini analiz eden çalışan bir eBPF programı."
            },
            {
                "phase": "Faz 3: Tersine Mühendislik ve İkili Analiz",
                "days": "21 - 30",
                "topics": [
                    "Ghidra ve IDA Pro ile ELF ikililerinin tersine mühendisliği",
                    "x86_64 ve ARM64 Calling Conventions, Stack Frame analizi",
                    "Buffer Overflow, ROP (Return-Oriented Programming) ve ASLR/DEP koruma mekanizmaları"
                ],
                "pow": "CTF seviyesinde tersine mühendislik çözüm raporu ve exploit koruma analizi."
            }
        ]
    },
    "matematik-felsefe": {
        "title": "İlk İlkeler Matematiği, Mantık ve Bilim Felsefesi",
        "philosophy": "Formülleri ezberlemeyi reddedip, aksiyomatik inşa ve epistemolojik doğrulamayla hakikati arayan düşünce.",
        "milestones": [
            {
                "phase": "Faz 1: Aksiyomatik Sistemler & Matematiksel Mantık",
                "days": "1 - 10",
                "topics": [
                    "Önermeler ve Yüklemler mantığı, İspat yöntemleri (Tümevarım, Çelişki, Diyagonalizasyon)",
                    "Gödel'in Eksiklik Teoremleri ve Turing Hesaplanabilirlik Sınırları",
                    "Kümeler Kuramı (ZFC) ve Russell Paradoksu"
                ],
                "pow": "LaTeX ile yazılmış aksiyomatik ispatlar koleksiyonu ve mantık çözümleme raporu."
            },
            {
                "phase": "Faz 2: Epistemoloji & Bilimsel İflas Analizleri",
                "days": "11 - 20",
                "topics": [
                    "Karl Popper (Yanlışlanabilirlik) ve Thomas Kuhn (Paradigma Kaymaları)",
                    "Paul Feyerabend (*Yönteme Hayır*) ve Epistemolojik Anarşizm",
                    "Ioannidis'in Tekrarlanabilirlik Krizi ve İstatistiksel p-hacking tuzakları"
                ],
                "pow": "Hakemli bir makalenin tekrarlanabilirlik ve metodolojik zaafiyet analiz raporu."
            },
            {
                "phase": "Faz 3: Doğu & Batı Maarif Diyalektiği",
                "days": "21 - 30",
                "topics": [
                    "Farabi, İbn Sina ve Biruni'nin ampirik araştırma felsefesi",
                    "Cemil Meriç, Nurettin Topçu ve Kâtip Çelebi'nin medrese/amfi eleştirileri",
                    "Skin in the Game: Taleb'in derisi masada ahlakı"
                ],
                "pow": "Açık erişimli, kaynakçalı ve bağımsız bir düşünce denemesi / manifesto eki."
            }
        ]
    }
}


def generate_curriculum(domain_key: str, duration_days: int = 30, output_dir: str = "curriculums"):
    os.makedirs(output_dir, exist_ok=True)
    domain_data = CURRICULUM_TEMPLATES.get(domain_key)
    if not domain_data:
        print(f"[!] Bilinmeyen alan: {domain_key}. Mevcut alanlar: {', '.join(CURRICULUM_TEMPLATES.keys())}")
        return None

    today = datetime.date.today().isoformat()
    filename = os.path.join(output_dir, f"mufredat_{domain_key}_{duration_days}gun.md")

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# ⚡ Otonom Polimat Müfredatı: {domain_data['title']}\n\n")
        f.write(f"> *\"Müfredatını başkalarına teslim eden, zihnini de teslim eder. İdrakin deli gömleğini yırt ve kendi tezgâhını kur.\"*\n\n")
        f.write(f"- **Oluşturulma Tarihi:** {today}\n")
        f.write(f"- **Hedef Süre:** {duration_days} Gün (Haftada minimum 15 saat odaklanmış inşa)\n")
        f.write(f"- **Temel Felsefe:** {domain_data['philosophy']}\n\n")
        f.write("---\n\n")

        f.write("## 📌 Yol Haritası ve Fazlar\n\n")
        for m in domain_data["milestones"]:
            f.write(f"### 📍 {m['phase']} (Gün: {m['days']})\n\n")
            f.write("#### 🎯 Odak Konuları ve İlk İlkeler:\n")
            for t in m["topics"]:
                f.write(f"- [ ] {t}\n")
            f.write("\n")
            f.write(f"#### 🏆 Proof of Work (Somut Kanıt & Tezgâh Çıktısı):\n")
            f.write(f"> **{m['pow']}**\n\n")
            f.write("---\n\n")

        f.write("## 🛠️ Günlük Otonom Değerlendirme Çizelgesi\n\n")
        f.write("| Gün | İncelenen Orijinal Kaynak / Makale | Yazılan Kod / Devre | Not & Zettelkasten Bağlantısı |\n")
        f.write("| :---: | :--- | :--- | :--- |\n")
        for d in range(1, min(duration_days + 1, 16)):
            f.write(f"| Gün {d:02d} | ... | ... | ... |\n")
        f.write("\n")
        f.write("> *\"Talk is cheap. Show me the code.\"* — **Linus Torvalds**\n")

    print(f"[OK] Müfredat başarıyla oluşturuldu: {filename}")
    return filename


def main():
    parser = argparse.ArgumentParser(description="Otonom Polimat Müfredat Üreteci")
    parser.add_argument("--domain", "-d", choices=list(CURRICULUM_TEMPLATES.keys()), default="yapay-zeka", help="Çalışma alanı")
    parser.add_argument("--duration", "-t", type=int, default=30, choices=[30, 60, 90], help="Müfredat gün sayısı")
    parser.add_argument("--output-dir", "-o", default="curriculums", help="Çıktı klasörü")

    args = parser.parse_args()
    generate_curriculum(args.domain, args.duration, args.output_dir)


if __name__ == "__main__":
    main()
