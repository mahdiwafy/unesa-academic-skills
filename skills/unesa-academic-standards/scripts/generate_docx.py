#!/usr/bin/env python3
"""
Script Pembantu Pembuatan Dokumen Akademik Standar UNESA (.docx)
Memastikan ukuran kertas A4, margin 4-4-3-3 / 3-3-3-3, font TNR 12pt, spasi 1.5,
dan perataan paragraf yang sesuai standar karya ilmiah.
"""

import sys
import argparse
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Cm, Pt, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import OxmlElement, parse_xml
    from docx.oxml.ns import nsdecls, qn
except ImportError:
    print("[ERROR] python-docx belum terinstall. Jalankan: pip install python-docx", file=sys.stderr)
    sys.exit(1)


def create_academic_document(title: str, author: str, nim: str, prodi: str, output_path: str, is_skripsi: bool = False):
    doc = Document()

    # Set default font to Times New Roman
    style_normal = doc.styles['Normal']
    font = getattr(style_normal, 'font', None)
    if font is not None:
        font.name = 'Times New Roman'
        font.size = Pt(12)
        font.color.rgb = RGBColor(0, 0, 0)

    # Set Page Setup (A4 & Margin Baku)
    for sec in doc.sections:
        sec.page_width = Cm(21.0)
        sec.page_height = Cm(29.7)
        
        if is_skripsi:
            # Standar Laporan/Skripsi (4-4-3-3)
            sec.top_margin = Cm(4.0)
            sec.left_margin = Cm(4.0)
            sec.right_margin = Cm(3.0)
            sec.bottom_margin = Cm(3.0)
        else:
            # Standar Makalah/Tugas (3-3-3-3 atau 4-3-3-3)
            sec.top_margin = Cm(3.0)
            sec.left_margin = Cm(4.0)
            sec.right_margin = Cm(3.0)
            sec.bottom_margin = Cm(3.0)

    # Cover Page
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(36)
    p_title.paragraph_format.space_after = Pt(24)
    p_title.paragraph_format.line_spacing = 1.15
    run_title = p_title.add_run(title.upper())
    run_title.bold = True
    run_title.font.size = Pt(14)

    p_type = doc.add_paragraph()
    p_type.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_type.paragraph_format.space_after = Pt(72)
    run_type = p_type.add_run("MAKALAH / LAPORAN AKADEMIK\nDisusun untuk Memenuhi Tugas Perkuliahan")
    run_type.font.size = Pt(12)

    p_author = doc.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_author.paragraph_format.space_after = Pt(72)
    p_author.paragraph_format.line_spacing = 1.15
    run_author = p_author.add_run(f"Oleh:\n{author}\nNIM. {nim}")
    run_author.bold = True
    run_author.font.size = Pt(12)

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.line_spacing = 1.15
    run_inst = p_inst.add_run(f"PROGRAM STUDI {prodi.upper()}\nUNIVERSITAS NEGERI SURABAYA\n2026")
    run_inst.bold = True
    run_inst.font.size = Pt(12)

    # Page Break for Main Content
    doc.add_page_break()

    # Section 1: BAB I PENDAHULUAN
    add_heading_bab(doc, "BAB I", "PENDAHULUAN")
    
    add_subheading(doc, "A. Latar Belakang")
    add_academic_paragraph(doc, "Perkembangan ilmu pengetahuan dan teknologi menuntut pemahaman yang komprehensif terhadap landasan teori dan implementasi praktis. Masalah yang sering dihadapi dalam konteks ini adalah perlunya standardisasi metodologi yang terstruktur dan terukur.")
    add_academic_paragraph(doc, "Berdasarkan permasalahan tersebut, penyusunan laporan ini difokuskan pada analisis mendalam mengenai objek kajian, perancangan solusi yang relevan, serta pengujian hasil yang dapat dipertanggungjawabkan secara akademik.")

    add_subheading(doc, "B. Rumusan Masalah")
    add_academic_paragraph(doc, "Berdasarkan latar belakang di atas, rumusan masalah dalam penulisan ini adalah:")
    add_list_item(doc, "1.", "Bagaimana konsep dasar dan landasan teori terkait topik yang dikaji?")
    add_list_item(doc, "2.", "Bagaimana implementasi serta analisis hasil yang diperoleh dari studi ini?")

    add_subheading(doc, "C. Tujuan Penulisan")
    add_academic_paragraph(doc, "Tujuan yang ingin dicapai melalui penulisan ini adalah:")
    add_list_item(doc, "1.", "Memahami konsep dan landasan teori secara mendalam.")
    add_list_item(doc, "2.", "Menganalisis hasil implementasi dan merumuskan kesimpulan berbasis data.")

    # Section 2: BAB II PEMBAHASAN
    doc.add_page_break()
    add_heading_bab(doc, "BAB II", "PEMBAHASAN")
    add_subheading(doc, "A. Kajian Teori")
    add_academic_paragraph(doc, "Landasan teori merupakan fondasi utama dalam menganalisis permasalahan yang diangkat. Dalam literatur terkini, pendekatan sistematis terbukti mampu meningkatkan efektivitas pemecahan masalah.")

    add_subheading(doc, "B. Analisis dan Hasil")
    add_academic_paragraph(doc, "Hasil analisis menunjukkan bahwa penerapan metode yang tepat mampu memberikan peningkatan performa dan efisiensi yang signifikan.")

    # Section 3: BAB III PENUTUP
    doc.add_page_break()
    add_heading_bab(doc, "BAB III", "PENUTUP")
    add_subheading(doc, "A. Kesimpulan")
    add_academic_paragraph(doc, "Berdasarkan pembahasan yang telah diuraikan pada bab sebelumnya, dapat disimpulkan bahwa penerapan metode terstruktur memberikan hasil yang valid dan sesuai dengan tujuan awal penulisan.")

    add_subheading(doc, "B. Saran")
    add_academic_paragraph(doc, "Untuk pengembangan selanjutnya, disarankan agar penelitian lanjutan dapat memperluas cakupan data dan mengeksplorasi parameter tambahan.")

    # Section 4: DAFTAR PUSTAKA
    doc.add_page_break()
    p_dp = doc.add_paragraph()
    p_dp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dp.paragraph_format.space_after = Pt(18)
    run_dp = p_dp.add_run("DAFTAR PUSTAKA")
    run_dp.bold = True
    run_dp.font.size = Pt(12)

    add_bibliography_item(doc, "Prasetyo, A. B., & Wibowo, D. (2024). Penerapan Metodologi Modern dalam Pendidikan Tinggi. Jurnal Pendidikan dan Teknologi, 12(2), 145–158.")
    add_bibliography_item(doc, "Suryanto, E. (2023). Panduan Penulisan Karya Ilmiah dan Laporan Akademik. Surabaya: UNESA University Press.")

    # Save
    doc.save(output_path)
    print(f"[SUCCESS] Dokumen akademik berhasil dibuat: {output_path}")


def add_heading_bab(doc, bab_num: str, bab_title: str):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(18)
    p.paragraph_format.line_spacing = 1.15
    run = p.add_run(f"{bab_num}\n{bab_title}")
    run.bold = True
    run.font.size = Pt(12)


def add_subheading(doc, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    run.bold = True
    run.font.size = Pt(12)


def add_academic_paragraph(doc, text: str):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Cm(1.0)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.5
    run = p.add_run(text)
    run.font.size = Pt(12)


def add_list_item(doc, num: str, text: str):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(1.0)
    p.paragraph_format.first_line_indent = Cm(-0.5)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.5
    run_num = p.add_run(f"{num} ")
    run_text = p.add_run(text)
    run_text.font.size = Pt(12)


def add_bibliography_item(doc, text: str):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.first_line_indent = Cm(-1.27)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.5
    p.add_run(text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Dokumen Akademik Standar UNESA")
    parser.add_argument("--title", default="Judul Makalah / Tugas Perkuliahan", help="Judul Dokumen")
    parser.add_argument("--author", default="Nama Mahasiswa", help="Nama Penulis")
    parser.add_argument("--nim", default="26050974000", help="NIM Mahasiswa")
    parser.add_argument("--prodi", default="Pendidikan Teknologi Informasi", help="Program Studi")
    parser.add_argument("--out", default="Dokumen_Akademik.docx", help="Path Output DOCX")
    parser.add_argument("--skripsi", action="store_true", help="Gunakan margin laporan/skripsi (4-4-3-3)")

    args = parser.parse_args()
    create_academic_document(args.title, args.author, args.nim, args.prodi, args.out, args.skripsi)
