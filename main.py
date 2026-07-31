import streamlit as st
from PIL import Image
from process import (
    page_clean_media_data,
    page_cross_product,
    page_data_analysis,
    page_formatter_roi_modeller_plus,
    page_roi_modeller,
)
from process import utils

# 設定頁面基本配置
st.set_page_config(
    page_title="Media Report Dashboard & ROI Modeller+",
    layout="centered",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "### Media Report Dashboard & ROI Modeller+ \n**多來源媒體成效數據分析與預測儀表板**\nMade by Publicis Growth Intelligence Team"
    }
)

# 優化的標題及功能敘述
def media_formatter():
    st.title('📊 Dashboard 資料上傳與格式化')
    st.markdown("#### **✨ 將多媒體數據格式化，打造互動儀表板！✨**")
    st.info('📂 **支援一次上傳多個媒體檔案！**')
    page_formatter_roi_modeller_plus.main()

def ROI_modeller_plus_page():
    st.title('🌈 資料上傳：RM+ w/ 格式化數據')
    st.markdown("#### **✨ 格式化數據助 ROI Modeller+ 更上一層樓！✨**")
    st.warning('請上傳【媒體原始檔案】及【ROI Business】，按下**確認送出**後，'
               '系統成功顯示上傳完成，可至左側選單查看**分析與預測結果**。')

    with st.expander("📋 **ROI Business 檔案格式說明**"):
        instructions = """
        ### ROI Business 檔案格式規範：
        1. 命名格式：`ROI_Business_任意英數文字`，開頭不可變更，且中間用底線分隔。
        2. 上傳格式：**XLSX, CSV** 檔案。
        3. 資料格式：A 欄應填寫 **Start date**，時間間隔限定為 day/week/month。
        4. 最少填寫一欄、最多十欄資料，每欄請以英文和數字命名。
        5. 每個資料集至少含 30 組資料（每日：30 天，每週：30 週，每月：30 個月）。
        6. 系統僅讀取 **第一個頁籤**，請確保資料放置於第一個頁籤中。
        """
        st.markdown(instructions)
        try:
            image = Image.open(utils.get_path('application/Photos/Business data.png'))
            st.image(image, caption='Business data 格式')

        except Exception as e:
            image = Image.open(utils.get_path('Photos/Business data.png'))
            st.image(image, caption='Business data 格式')
            # st.error(f"圖片無法載入：{e}")

    page_formatter_roi_modeller_plus.main()

def ROI_modeller_page():
    st.title('🌟 資料上傳：RM+ 簡易版')
    st.markdown("#### **✨ 無需格式化也能使用 ROI Modeller+！✨**")
    st.warning('請上傳【ROI Media】與【ROI Business】資料，按下**確認送出**，'
               '成功上傳後可至側邊選單查看**分析與預測結果**。')

    with st.expander("📁 **檔案上傳說明**"):
        st.markdown("""
        ### 上傳格式：
        - 上傳格式：**XLSX, CSV** 檔案。
        - 需上傳兩份檔案：Media Data 和 Business Data。
        """)

        tab1, tab2 = st.tabs(["📊 Media", "📈 Business"])
        with tab1:
            st.markdown("""
            #### Media Data 上傳說明：
            1. 命名格式：`ROI_Media_任意英數文字`，開頭不可變更。
            2. 資料格式：A 欄應填寫 **Start date**，時間間隔限定為 day/week/month。
            3. 可填最多十種媒體資料，每種媒體需至少有 30 筆資料。
            4. 僅讀取第一個頁籤，請將所有資料置於該頁籤。
            """)
            try:
                media_image = Image.open(utils.get_path('application/Photos/Media data.png'))
                st.image(media_image, caption='Media data 格式')
            except Exception as e:
                media_image = Image.open(utils.get_path('Photos/Media data.png'))
                st.image(media_image, caption='Media data 格式')
                # st.error(f"圖片無法載入：{e}")

        with tab2:
            st.markdown("""
            #### Business Data 上傳說明：
            1. 命名格式：`ROI_Business_任意英數文字`，開頭不可變更。
            2. 資料格式：A 欄應填寫 **Start date**，且需與 Media Data 的時間間隔一致。
            3. 最少填寫一欄、最多十欄資料，每欄以英文和數字命名。
            4. 至少包含 30 組資料（每日：30 天，每週：30 週，每月：30 個月）。
            5. 系統僅讀取第一個頁籤，請確保資料在第一個頁籤中。
            """)
            try:
                business_image = Image.open(utils.get_path('application/Photos/Business data.png'))
                st.image(business_image, caption='Business data 格式')
            except Exception as e:
                business_image = Image.open(utils.get_path('Photos/Business data.png'))
                st.image(business_image, caption='Business data 格式')

    page_roi_modeller.main()

def Data_analysis():
    page_data_analysis.main()

def Cross_product_analysis():
    page_cross_product.main()

def uncleaned_data_formatter():
    page_clean_media_data.main()


# 側邊選單功能選擇
page = st.sidebar.selectbox(
    '### 🔍 請選擇功能',
    ('Dashboard 資料上傳與格式化', '未清理資料格式化', '資料上傳：RM+ w/ 格式化數據',
     '資料上傳：RM+ 簡易版', 'ROI modeller+ 分析與預測', '跨產品影響比較')
)

# 根據使用者選擇切換頁面
if page == "Dashboard 資料上傳與格式化":
    media_formatter()
elif page == "未清理資料格式化":
    uncleaned_data_formatter()
elif page == "資料上傳：RM+ w/ 格式化數據":
    ROI_modeller_plus_page()
elif page == "資料上傳：RM+ 簡易版":
    ROI_modeller_page()
elif page == "ROI modeller+ 分析與預測":
    Data_analysis()
elif page == "跨產品影響比較":
    Cross_product_analysis()
