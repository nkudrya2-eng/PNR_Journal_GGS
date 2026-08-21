import unittest
from pathlib import Path
from main_md import find_equip_data, build_context_ggs, generate_ggs_report, EQUIP_DIR, GGS_TEMPLATE_FILE


class TestGGSRendering(unittest.TestCase):
    def test_find_equip_data(self):
        data, path = find_equip_data("12006-81-0600")
        self.assertIsNotNone(data)
        self.assertIsNotNone(path)
        self.assertIn("equipment", data)
        self.assertIn("document_context", data)

    def test_build_context_ggs(self):
        data, _ = find_equip_data("12006-81-0600")
        context = build_context_ggs(data, "12006-81-0600-СС1.2")
        self.assertIn("громкоговорящей связи", context["system_name"].lower())
        self.assertEqual(context["project_code"], "12006-81-0600-СС1.2")
        self.assertIn("equipment", context)
        self.assertGreater(len(context["equipment"]), 0)
        self.assertIn("ggs_summary", context)
        self.assertGreater(context["ggs_summary"]["speakers_count"], 0)

    def test_render_ggs_report(self):
        output_file = Path("test_ggs_output.md")
        try:
            rendered = generate_ggs_report(
                project_code="12006-81-0600",
                output_file=output_file,
                template_file=GGS_TEMPLATE_FILE,
            )
            self.assertIsNotNone(rendered)
            self.assertTrue(rendered.exists())
            content = rendered.read_text(encoding="utf-8")

            self.assertIn("ООО «Голд Линк»", content)
            self.assertIn("громкоговорящей связи", content.lower())
            self.assertIn("Список ИТР, занятых в наладочных работах", content)
            self.assertIn("Ведомость оборудования, подвергаемого пусконаладочным работам", content)
            self.assertIn("Коммутатор DCN-16U", content)
            self.assertIn("Громкоговоритель рупорный", content)
            self.assertIn("Чек-листы проверки и испытаний системы ГГС", content)
            self.assertIn("ФОРМА АКТА ПРИЕМКИ ПУСКОНАЛАДОЧНЫХ РАБОТ", content)
        finally:
            if output_file.exists():
                output_file.unlink()


if __name__ == "__main__":
    unittest.main()
