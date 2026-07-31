import streamlit as st
import pandas as pd

from process.ROI_Modeller import roi_modeller
from process.utils import upload_files, download_files


def upload_files():
    files = st.file_uploader("上傳你的檔案", type=["csv", "xlsx"], accept_multiple_files=True)
    return files

def main():
    uploaded_file = upload_files()
    business_uploaded = False
    media_uploaded = False
    st.session_state.roi_data = False

    if uploaded_file:
        if st.button('確認送出'):
            for file in uploaded_file:
                try:
                    df = pd.read_excel(file)
                except:
                    df = pd.read_csv(file)
                st.success(f'檔案 {file.name} 上傳成功!')

                file_name = file.name.split('_')
                if file_name[1] == 'Business':
                    business = df.copy()
                    business_uploaded = True
                    business['Start date'] = pd.to_datetime(business['Start date']).dt.date
                    business = business.sort_values(by='Start date')
                    st.session_state.business = business
                    continue

                elif file_name[1] == 'Media':
                    media = df.copy()
                    Customer = file_name[2]
                    media_uploaded = True
                    media['Start date'] = pd.to_datetime(media['Start date']).dt.date
                    media = media.sort_values(by='Start date')
                    media.rename(columns={'Start date': 'Date'}, inplace=True)
                    continue

            if business_uploaded and media_uploaded:
                cor_result, cor_sammury, combo_dict, business_weekly, media_weekly, kpi2media, media_weekly_wide = roi_modeller(business, media)
                st.session_state.business = business
                st.session_state.media = media
                st.session_state.roi_data = True
                st.session_state.roi_data_plus = False
                st.success('#### 🌟 載入成功，請前往「分析與預測結果」分頁')
                new_file_name = 'ROI結果_' + Customer + '_日期'
                st.markdown(download_files([cor_result, cor_sammury], new_file_name), unsafe_allow_html=True)
            else:
                missing_files = []
                if not business_uploaded:
                    missing_files.append('ROI Business')
                if not media_uploaded:
                    missing_files.append('ROI Media')
                st.warning(f"缺少以下文件: {', '.join(missing_files)}")
