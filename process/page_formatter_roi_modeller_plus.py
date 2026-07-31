# 這是格式化數據與ROI Modeller + 共用！！！
import streamlit as st
import pandas as pd

from process.template import process_map, general_process
from process.utils import download_files, upload_files

# def upload_files():
#     files = st.file_uploader("上傳你的檔案", type=["csv", "xlsx"], accept_multiple_files=True)
#     return files

def main():
    uploaded_files = upload_files()

    # --- 只在尚未存在時初始化，避免每次 rerun 都被清掉 ---
    ss = st.session_state
    ss.setdefault('roi_data', False)
    ss.setdefault('roi_modeller_plus', False)
    ss.setdefault('cross_product', False)
    ss.setdefault('business', None)
    ss.setdefault('business_cross_prod', None)
    ss.setdefault('media', None)

    if not uploaded_files:
        return

    if st.button('確認送出'):
        # 當次處理的局部狀態
        formed_uploaded = False
        business_uploaded = False
        has_business_multi = False
        all_result = []
        business_multi_dict_acc = {}
        formed_df = None
        last_customer = None

        # 避免遮蔽內建 map()
        proc_map = process_map()

        # 安全取檔名片段
        def safe_get(parts, idx, default=None):
            return parts[idx] if len(parts) > idx else default

        for file in uploaded_files:
            try:
                parts = file.name.replace('.xlsx', '').split('_')
                xls = pd.ExcelFile(file)
                sheet_names = xls.sheet_names

                # ① 直接上傳的「格式化數據_*」
                if safe_get(parts, 0) == '格式化數據':
                    df = pd.read_excel(xls, sheet_name=sheet_names[0])
                    formed_df = df.copy()
                    formed_uploaded = True
                    # 預設抓客戶名（優先第 3 段，退而求其次第 2 段）
                    last_customer = safe_get(parts, 2) or safe_get(parts, 1) or 'Unknown'
                    st.success(f'檔案 {file.name} 上傳成功!')

                # ② Business 檔（允許多 sheet）
                elif safe_get(parts, 1) == 'Business':
                    for name in sheet_names:
                        try:
                            df_temp = pd.read_excel(xls, sheet_name=name)
                            df_temp['Start date'] = pd.to_datetime(df_temp['Start date']).dt.date
                            df_temp = df_temp.sort_values('Start date')
                            business_multi_dict_acc[name] = df_temp
                        except Exception as e:
                            # st.error(f"無法讀取工作表 {name}：{e}")
                            continue
                    if len(business_multi_dict_acc.keys()) > 1:
                        # 多工作表：先全讀起來，迴圈結束後再讓使用者選其中一個產品
                        has_business_multi = True
                        business_uploaded = True
                    else:
                        selected_prod = list(business_multi_dict_acc.keys())[0]
                        ss.business = business_multi_dict_acc[selected_prod]
                        business_uploaded = True

                    st.success(f'檔案 {file.name} 上傳成功!')

                # ③ 其他：原始媒體檔，需經處理流程
                else:
                    df_raw = pd.read_excel(xls, sheet_name=sheet_names[0])
                    BU = safe_get(parts, 0) or 'UnknownBU'
                    Customer = safe_get(parts, 1) or 'UnknownCustomer'
                    # 你的特例：部分客戶 media 放在第 4 段
                    if Customer in ['PG', 'Nestle', '葡萄王', '金車']:
                        media = safe_get(parts, 3)
                    else:
                        media = safe_get(parts, 2)

                    if media is None:
                        raise IndexError('檔名無法判定 media 類型（檔名段數不足）')

                    try:
                        process_func = proc_map[BU][Customer][media]
                    except KeyError as e:
                        raise KeyError(f'對應不到處理函式：BU={BU}, Customer={Customer}, media={media}；{e}')

                    df_processed = general_process(process_func, df_raw, parts)
                    st.expander('處理後的數據:').write(df_processed)
                    all_result.append(df_processed)

                    last_customer = Customer  # 供合併檔命名使用
                    st.success(f'檔案 {file.name} 上傳成功!')

            except (KeyError, IndexError) as e:
                st.error(f"無法處理檔案 {file.name}：{e}")
                st.warning("請檢查檔名格式是否正確、以及檔案是否為 Excel。")
                continue

        # --- 多 sheet 的 Business：在迴圈結束後，統一讓使用者選產品 ---
        if has_business_multi and business_multi_dict_acc:
            ss.business_cross_prod = business_multi_dict_acc
            selected_prod = list(business_multi_dict_acc.keys())[0]
            ss.business = business_multi_dict_acc[selected_prod]
            ss.cross_product = True
        else:
            ss.cross_product = False

        # --- 產出 formed_df_final 與下載 ---
        formed_df_final = None
        if not formed_uploaded:
            if len(all_result) > 0:
                formed_df_final = pd.concat(all_result, ignore_index=True)
                formed_df_final['Date'] = pd.to_datetime(formed_df_final['Date']).dt.date
                new_file_name = f"格式化數據_{(last_customer or '合併')}_日期"
                st.markdown(download_files([formed_df_final], new_file_name), unsafe_allow_html=True)
            else:
                st.warning('沒有任何可用的處理後數據（all_result 為空）。')
        else:
            formed_df_final = formed_df.copy()
            formed_df_final['Date'] = pd.to_datetime(formed_df_final['Date']).dt.date

        # --- 寫入 session_state 並引導後續頁籤 ---
        if formed_df_final is not None:
            formed_df_final = formed_df_final.dropna(axis=1, how='all')
            ss.media = formed_df_final

            if business_uploaded:
                if has_business_multi:
                    st.success('#### 🌟 載入成功，可以前往「跨產品分析」分頁')
                ss.roi_data = True
                ss.roi_modeller_plus = True
                st.success('#### 🌟 載入成功，請前往「分析與預測結果」分頁')
            else:
                pass
                # st.warning("缺少以下文件：ROI Business")
