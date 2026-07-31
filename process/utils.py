import streamlit as st
import pandas as pd
import base64
import io

import sys
import os

def upload_files():
    files = st.file_uploader("### 請上傳你的檔案", type=["csv", "xlsx"], accept_multiple_files=True)
    return files

def download_files(dataframes, filename):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if len(dataframes) > 1:
            dataframes[0].to_excel(writer, sheet_name='All Corr', index=False)
            dataframes[1].to_excel(writer, sheet_name='All Corr Top 5', index=False)
        else:
            dataframes[0].to_excel(writer, sheet_name='格式化數據', index=False)
    output.seek(0)
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    return f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}">Download {filename}</a>'

def get_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def add_end(df):
    df1 = df.copy()
    df1.reset_index(drop=True, inplace=True)
    df1.insert(1, 'End date', 0)
    date_diff = df1['Start date'][1] - df1['Start date'][0]
    for i in range(len(df1)):
        df1.at[i, 'End date'] = df1.at[i, 'Start date'] + date_diff - pd.Timedelta(days=1)
    return df1

def ask_wrong(selected_col, filled_col, revised, df):
    errors = []
    for src_col, dest_col in zip(selected_col, filled_col):

        try:
            revised[dest_col] = df[src_col]
        except:
            errors.append(src_col)
    if len(errors) > 0:
        st.error(f"你是否少了「 {'、'.join(errors)} 」欄位呢? \n 如果沒有，可以忽視這個訊息")
    else:
        pass

def meta_cn2en(df):
    # 1️⃣ 建立中→英對照表（dict）
    cn2en = {
        "分析報告開始": "Reporting starts",
        "分析報告結束": "Reporting ends",
        "廣告名稱": "Ad name",
        "廣告組合名稱": "Ad Set Name",
        "行銷活動名稱": "Campaign name",
        "曝光次數": "Impressions",
        "點擊次數（全部）": "Clicks (all)",
        "連結點擊次數": "Link clicks",
        "影片播放 3 秒以上的次數": "3-second video plays",
        "花費金額 (TWD)": "Amount spent (TWD)",
        "貼文互動次數": "Post reactions",
        "貼文留言數": "Post comments",
        "貼文分享次數": "Post shares",
        "貼文心情數": "Post engagements",
        "連結頁面瀏覽次數": "Landing Page Views",
        "觸及人數": "Reach",
    }
    df = df.rename(columns=cn2en)
    return df
