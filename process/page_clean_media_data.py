import io
import tempfile
import zipfile
from pathlib import Path

import streamlit as st

import clean_media_data


def main():
    st.title('🧹 未清理資料格式化')
    st.markdown("#### **自動偵測未知 Excel 報表的表頭，並統一媒體資料欄位。**")
    st.info('可一次上傳多個 XLSX 檔案；完成後可下載格式化檔案與稽核報告。')

    default_dictionary = (
        Path(__file__).resolve().parent.parent
        / "Report Template & All Format 字典.xlsx"
    )
    uploaded_files = st.file_uploader(
        "上傳未清理的媒體 Excel 檔案",
        type=["xlsx"],
        accept_multiple_files=True,
        key="uncleaned_media_files",
    )

    with st.expander("⚙️ 進階設定"):
        scan_rows = st.number_input(
            "每張工作表最多掃描幾列尋找表頭",
            min_value=1,
            max_value=1000,
            value=100,
            step=10,
        )
        sheet_name = st.text_input(
            "指定工作表名稱（留空時使用 Excel 目前選取的工作表）"
        ).strip()
        dictionary_file = st.file_uploader(
            "自訂欄位字典（選填，XLSX）",
            type=["xlsx"],
            accept_multiple_files=False,
            key="uncleaned_media_dictionary",
        )
        if default_dictionary.exists():
            st.download_button(
                "📥 下載自訂欄位字典範本",
                data=default_dictionary.read_bytes(),
                file_name="自訂欄位字典_範本.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_media_dictionary_template",
            )
            st.caption(
                "填寫時請保留「字典欄位說明」工作表與 B/C、H–L 欄位結構；"
                "在對應的系統欄位列填入來源報表欄名。"
            )
        else:
            st.warning("找不到預設欄位字典範本，請聯絡系統管理者。")
        use_ollama = st.checkbox(
            "使用本機 Ollama 協助辨識表頭",
            value=True,
            help="Ollama 無法連線時，會自動改用原本的規則判別。",
        )
        if use_ollama:
            ollama_model = st.text_input("Ollama 模型", value="qwen3.5:9b")
            ollama_url = st.text_input(
                "Ollama API 網址", value="http://127.0.0.1:11434"
            )
            ollama_timeout = st.number_input(
                "Ollama 等待秒數",
                min_value=1.0,
                max_value=600.0,
                value=120.0,
                step=5.0,
            )
        else:
            ollama_model = "qwen3.5:9b"
            ollama_url = "http://127.0.0.1:11434"
            ollama_timeout = 120.0

    if st.button("開始格式化", type="primary", key="clean_uncleaned_media"):
        if not uploaded_files:
            st.error("請先上傳至少一個 XLSX 檔案。")
        else:
            st.session_state.pop("uncleaned_media_results", None)
            with st.spinner("正在偵測表頭並格式化資料，請稍候…"):
                with tempfile.TemporaryDirectory(prefix="media_cleaner_") as temp_dir:
                    temp_root = Path(temp_dir)
                    output_dir = temp_root / "cleaned_output"
                    output_dir.mkdir()

                    if dictionary_file is not None:
                        dictionary_path = temp_root / "dictionary.xlsx"
                        dictionary_path.write_bytes(dictionary_file.getvalue())
                    else:
                        dictionary_path = (
                            default_dictionary if default_dictionary.exists() else None
                        )

                    try:
                        aliases = clean_media_data.read_dictionary(dictionary_path)
                    except Exception as exc:
                        st.error(f"欄位字典無法讀取：{exc}")
                        return
                    ollama = clean_media_data.OllamaConfig(
                        model=ollama_model,
                        url=ollama_url,
                        timeout=float(ollama_timeout),
                        enabled=use_ollama,
                    )
                    all_audit = []
                    cleaned_files = []
                    used_output_names = set()

                    for index, uploaded_file in enumerate(uploaded_files, start=1):
                        safe_name = Path(uploaded_file.name).name
                        input_dir = temp_root / f"input_{index}"
                        input_dir.mkdir()
                        input_path = input_dir / safe_name
                        input_path.write_bytes(uploaded_file.getvalue())

                        output_name = f"{Path(safe_name).stem}_cleaned.xlsx"
                        if output_name in used_output_names:
                            output_name = (
                                f"{Path(safe_name).stem}_cleaned_{index}.xlsx"
                            )
                        used_output_names.add(output_name)
                        output_path = output_dir / output_name

                        try:
                            audit, rows = clean_media_data.clean_workbook(
                                input_path=input_path,
                                output_path=output_path,
                                aliases=aliases,
                                scan_rows=int(scan_rows),
                                sheet_name=sheet_name or None,
                                ollama=ollama,
                            )
                        except Exception as exc:
                            audit = [
                                clean_media_data.AuditRecord(
                                    input_file=safe_name,
                                    sheet=sheet_name,
                                    header_row=None,
                                    status=f"處理失敗：{exc}",
                                    score=None,
                                    data_rows=0,
                                    mapped_columns={},
                                    unmapped_columns=[],
                                    output_file=None,
                                )
                            ]
                            rows = 0

                        for record in audit:
                            record.input_file = safe_name
                            record.output_file = output_name if rows else None
                        all_audit.extend(audit)
                        if rows and output_path.exists():
                            cleaned_files.append(
                                {
                                    "name": output_name,
                                    "data": output_path.read_bytes(),
                                    "rows": rows,
                                }
                            )

                    clean_media_data.write_audit(all_audit, output_dir)
                    audit_json = (output_dir / "cleaning_audit.json").read_bytes()
                    unmapped_csv = (output_dir / "unmapped_columns.csv").read_bytes()

                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(
                        zip_buffer, "w", compression=zipfile.ZIP_DEFLATED
                    ) as archive:
                        for cleaned_file in cleaned_files:
                            archive.writestr(
                                cleaned_file["name"], cleaned_file["data"]
                            )
                        archive.writestr("cleaning_audit.json", audit_json)
                        archive.writestr("unmapped_columns.csv", unmapped_csv)

                    st.session_state.uncleaned_media_results = {
                        "files": cleaned_files,
                        "audit": [
                            {
                                "檔案": record.input_file,
                                "工作表": record.sheet,
                                "表頭列": record.header_row,
                                "狀態": record.status,
                                "分數": record.score,
                                "有效資料列": record.data_rows,
                                "欄位對應": record.mapped_columns,
                                "未對應欄位": record.unmapped_columns,
                            }
                            for record in all_audit
                        ],
                        "audit_json": audit_json,
                        "unmapped_csv": unmapped_csv,
                        "zip": zip_buffer.getvalue(),
                        "total": len(uploaded_files),
                    }

    results = st.session_state.get("uncleaned_media_results")
    if not results:
        return

    succeeded = len(results["files"])
    if succeeded:
        st.success(f"格式化完成：{succeeded}/{results['total']} 個檔案成功輸出。")
    else:
        st.warning("處理完成，但沒有檔案產生有效的格式化資料。請查看稽核結果。")

    st.subheader("處理結果")
    summary_rows = [
        {
            key: (
                "、".join(value)
                if key == "未對應欄位" and isinstance(value, list)
                else value
            )
            for key, value in record.items()
            if key != "欄位對應"
        }
        for record in results["audit"]
    ]
    st.dataframe(summary_rows, use_container_width=True, hide_index=True)

    for record in results["audit"]:
        if record["欄位對應"]:
            with st.expander(f"欄位對應：{record['檔案']}"):
                st.json(record["欄位對應"])

    st.subheader("下載")
    if results["files"]:
        st.download_button(
            "📦 下載全部結果（ZIP）",
            data=results["zip"],
            file_name="cleaned_media_results.zip",
            mime="application/zip",
            key="download_all_cleaned_media",
        )
        for index, cleaned_file in enumerate(results["files"], start=1):
            st.download_button(
                f"下載 {cleaned_file['name']}（{cleaned_file['rows']} 列）",
                data=cleaned_file["data"],
                file_name=cleaned_file["name"],
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"download_cleaned_media_{index}",
            )

    audit_col, unmapped_col = st.columns(2)
    with audit_col:
        st.download_button(
            "下載完整稽核報告（JSON）",
            data=results["audit_json"],
            file_name="cleaning_audit.json",
            mime="application/json",
            key="download_cleaning_audit",
        )
    with unmapped_col:
        st.download_button(
            "下載未對應欄位（CSV）",
            data=results["unmapped_csv"],
            file_name="unmapped_columns.csv",
            mime="text/csv",
            key="download_unmapped_columns",
        )
