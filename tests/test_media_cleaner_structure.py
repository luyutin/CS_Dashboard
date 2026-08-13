import io
import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook, load_workbook

from process import media_cleaner
from process.media_cleaner.settings import render_ollama_user_prompt


class MediaCleanerStructureTests(unittest.TestCase):
    def test_text_schema_is_loaded_through_public_package(self):
        self.assertEqual(media_cleaner.TARGET_COLUMNS[0], "date")
        self.assertIn("ad_name", media_cleaner.TARGET_COLUMNS)
        self.assertEqual(
            set(media_cleaner.TARGET_COLUMNS),
            set(media_cleaner.TARGET_DESCRIPTIONS),
        )

    def test_editable_prompt_placeholders_render(self):
        prompt = render_ollama_user_prompt(
            target_descriptions='{"date": "reporting date"}',
            options='[{"row": 1}]',
        )
        self.assertIn("reporting date", prompt)
        self.assertIn('"row": 1', prompt)

    def test_selected_sheets_are_cleaned_and_audited_independently(self):
        workbook = Workbook()
        first = workbook.active
        first.title = "Meta"
        first.append(["日期", "廣告活動名稱", "曝光次數"])
        first.append(["2026-08-01", "Campaign A", 100])
        second = workbook.create_sheet("Google")
        second.append(["Date", "Campaign name", "Impressions"])
        second.append(["2026-08-02", "Campaign B", 200])

        memory_file = io.BytesIO()
        workbook.save(memory_file)
        workbook.close()
        workbook_bytes = memory_file.getvalue()

        self.assertEqual(
            media_cleaner.list_workbook_sheets(workbook_bytes),
            ["Meta", "Google"],
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / "vendor_report.xlsx"
            output_path = Path(temp_dir) / "vendor_report_cleaned.xlsx"
            input_path.write_bytes(workbook_bytes)

            audit, row_count = media_cleaner.clean_workbook_sheets(
                input_path=input_path,
                output_path=output_path,
                aliases=media_cleaner.read_dictionary(None),
                scan_rows=20,
                sheet_names=["Google", "Meta"],
                ollama=media_cleaner.OllamaConfig(enabled=False),
            )

            self.assertEqual(row_count, 2)
            self.assertEqual([record.sheet for record in audit], ["Google", "Meta"])
            self.assertTrue(all(record.status == "成功" for record in audit))

            cleaned = load_workbook(output_path, data_only=True, read_only=True)
            try:
                rows = list(cleaned["cleaned_data"].iter_rows(values_only=True))
            finally:
                cleaned.close()
            source_index = rows[0].index("source")
            self.assertEqual(
                [row[source_index] for row in rows[1:]],
                ["vendor_report [Google]", "vendor_report [Meta]"],
            )


if __name__ == "__main__":
    unittest.main()
