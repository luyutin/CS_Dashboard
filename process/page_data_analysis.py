from collections import defaultdict
import streamlit as st
import pandas as pd
import numpy as np
import statsmodels.api as sm
from datetime import timedelta

from process.utils import add_end
from process.ROI_Modeller import roi_modeller, merge_med_bus
import process.ROI_Modeller as RM
from process.pre_models import ( fit_piecewise_linear, regression_analysis, plot_regression_band, trend_chart,
                                 plot_piecewise_linear, piecewise_linear, plot_corr_results, multiplereg,plot_regression_temp )
from itertools import combinations

def main():
    st.title('🌟分析與預測結果🌟')

    if ('roi_data' not in st.session_state) or (not st.session_state.roi_data):
        st.error('#### 🚨 請先到 **【資料上傳：RM+ w/ 格式化數據 或 RM+ 簡易版】** 頁面上傳資料!!')
        st.stop()

    else:
        business = st.session_state.business.copy()
        business = add_end(business)
        media = st.session_state.media.copy()

        if (not st.session_state.roi_modeller_plus):
            pass
        else:
            product_opts = media['Product'].unique()
            chosen_prod = st.sidebar.selectbox('#### 📦 請選擇想要觀察產品：', product_opts)
            media = media[media['Product'] == chosen_prod]
            st.session_state.product = chosen_prod

        # 時間區間....
        _, _, _, bus_w, _, _, m_w_w = roi_modeller(business, media)
        combined = merge_med_bus(m_w_w, bus_w)
        min_week, max_week = combined['Week'].min(), combined['Week'].max()

        if len(combined) < 30:
            st.error('#### ❗資料不足，最少需要 30 周資料才可以使用本分析頁面')
            st.warning('#### ⚠️ 為求模型準確性與可信度，建議放入 72 周（18 個月）以上資料')
            st.stop()
        else:
            pass

        selected_dates = st.sidebar.date_input(
            "#### 📅 請選擇欲觀察的時間區間：",
            (min_week, max_week + pd.Timedelta(days=6)),        # default date
            min_week, max_week + pd.Timedelta(days=6),          # 可選擇的 min, max date
            format="YYYY/MM/DD"
        )
        try:
            selected_min, selected_max = selected_dates
            if (not st.session_state.roi_modeller_plus):
                st.info('你使用的是簡易版的 ROI Modeller')
            media_sel_date = media[(selected_min < media['Date']) & (media['Date']< selected_max)]
            if len(media_sel_date) == 0:
                media_sel_date = media[(media['Date'].min() < media['Date']) & (media['Date']< media['Date'].max())]
        except:
            st.warning('#### ⚠️ 左側「時間區間」選取不完整！')
            st.stop()

    cor_result, cor_sammury, combo_dict, business_weekly, media_weekly, kpi2media, media_weekly_wide = roi_modeller(business, media_sel_date)

    if cor_result is None:
        st.warning('#### ⚠️ Business data 時間區間無法與媒體數據對應！')
        st.write('🔍 選取的媒體資料：')
        st.write(media_sel_date)
        st.write('🔍 選取的商業資料：')
        st.write(business)
        st.stop()

    combined_sel = merge_med_bus(media_weekly_wide, business_weekly)
    min_week_sel, max_week_sel = combined_sel['Week'].min(), combined_sel['Week'].max()
    max_week_sel = max_week_sel + pd.Timedelta(days=6)
    if len(combined_sel) < 30:
        st.error('#### ❗應加長選取時間，最少需要 30 周資料才可以使用本分析頁面')
        st.warning('#### ⚠️ 目前選取時間區間內的資料量為 {} 周（從 {} 到 {}）'.format(len(combined_sel), min_week_sel.strftime('%Y/%m/%d'), max_week_sel.strftime('%Y/%m/%d')))
        st.warning('#### ⚠️ 為求模型準確性與可信度，建議至少選取 72 周（18 個月）以上資料')
        st.stop()
    elif 72 > len(combined_sel) > 30:
        st.info('目前選取時間區間內的資料量為 {} 周（從 {} 到 {}）'.format(len(combined_sel), min_week_sel.strftime('%Y/%m/%d'), max_week_sel.strftime('%Y/%m/%d')))
        st.warning('⚠️ 為求模型準確性與可信度，建議至少選取 72 周（18 個月）以上資料')
    else:
        st.success('🌟 目前選取時間區間內的資料量為 {} 周（從 {} 到 {}）'.format(len(combined_sel), min_week_sel.strftime('%Y/%m/%d'), max_week_sel.strftime('%Y/%m/%d')))

    expander = st.expander('本頁分析報告數據總覽')
    expander.write("格式化數據")
    expander.write(media_sel_date)
    expander.write("商業數據")
    expander.write(business)
    expander.write("合併後的媒體與商業數據")
    expander.write(combined_sel)

    st.subheader('📊 帶動銷售的關鍵媒體組合相關係數')
    # expander = st.expander('相關性強弱程度分類:')
    st.markdown(
        """
        <h4 style="color:#4c7aaf;">正相關性強弱程度分類：弱：0~0.3、中：0.3~0.7、強：0.7~1 </h3>
        """,
        unsafe_allow_html=True
    )
    st.dataframe(cor_result.sort_values('相關係數', ascending=False).reset_index(drop=True))

    business_options = business.columns[2:]
    tab1, tab2, tab3, tab5 = st.tabs(["媒體組合分析", "歷史影響力分析", "投資成效模擬", "媒體重要成效多因子回歸分析"])

    with tab1:
        st.header('💡媒體組合成效分析')

        # ---------- 0. 準備 KPI⇄Media 的對映表 ----------
        # kpi2media 應該在之前已經建立（含單媒體與組合）
        all_kpi   = sorted(kpi2media.keys())
        all_media = sorted({m for s in kpi2media.values() for m in s})
        all_media_order = ['TV', 'Meta', 'Meta_boosting', 'YT', 'YT_boosting', 'Apex-PMP']
        all_media_valid = [c for c in all_media_order if c in all_media]

        # ////////////////////////////////////////////////////////////
        # ---------- 1. 建立布林/NaN 矩陣，供 data_editor 顯示 ----------
        option_metrix = pd.DataFrame(index=all_media_valid, columns=all_kpi, dtype='object')
        # selected_metrix = pd.concat([pd.Series(name='全選'), selected_metrix], axis=1)
        for m in all_media:
            for k in all_kpi:
                option_metrix.loc[m, k] = False if m in kpi2media[k] else np.nan  # 無效格 → NaN
        option_metrix = pd.concat([option_metrix, pd.Series(name='全選')], axis=1)  # 最後一欄是 Media
        option_metrix['全選'] = False
        # option_metrix = option_metrix.fillna('/')  # 將 NaN 填充為 False
        # 可能需要擴充使得 metric_order 必須包含所有 kpi2media 的 kpi
        metric_order = [ '全選',
            # TV
            'TVR', 'TVR carryon', '10 Second TVR', 'Reach 000s',
            # Digital funnel
            'Impressions', 'Spent (TWD)', 'Views',
            'Clicks (all)', 'Link clicks (Web Clicks)', 'Post engagements',
            # Video depth
            '15" Video Views (ThruPlays)',
            'Video played to 25%', 'Video played to 50%',
            'Video played to 75%', 'Video played to 100%'
        ]
        metric_order_valid = [c for c in metric_order if c in option_metrix.columns]
        # 如果有缺漏，提示使用者
        missing = set(metric_order) - set(metric_order_valid)
        if missing:
            st.warning(f"以下欄位在資料集中不存在，已自動忽略：{missing}")
        # 重新排序
        option_metrix = option_metrix[metric_order_valid]
        # ////////////////////////////////////////////////////////////
        st.write("### 選取欲分析的 Business x KPI × Media 組合")
        # ---------- 2. Business 指標多選 ----------
        w_business = st.selectbox(
            '請選擇想觀察的商業資料：',
            options = list(business_options),
            key='bus_multiselect'
        )

        selected_metrix = st.data_editor(
            option_metrix,
            num_rows="fixed",
            use_container_width=True
        )

        # ---------- 2. 解析使用者勾選結果 ----------
        sel_metrix = selected_metrix.copy()  # 避免直接修改原始資料
        # 取出欄位名稱
        col_all   = '全選'
        kpi_cols  = [c for c in sel_metrix.columns if c != col_all]   # 其餘都是 KPI

        sel_pairs = []

        for m in sel_metrix.index:                 # 逐列處理
            if sel_metrix.loc[m, col_all]:         # ✔ 勾了「全選」
                # 把這一列所有 KPI 都加入
                sel_pairs.extend([(k, m) for k in kpi_cols])
            else:
                # 只撈該列中，單獨被勾選的 KPI
                for k in kpi_cols:
                    if sel_metrix.loc[m, k] is True:
                        sel_pairs.append((k, m))

        # ------ 3. 取得最後的 KPI / Media 清單 -------
        if sel_pairs:
            w_eff   = sorted({k for k, _ in sel_pairs})
            w_media = sorted({m for _, m in sel_pairs})
            st.markdown(f"""
                - 已勾選 KPI: {w_eff}
                - 已勾選 Media: {w_media}
            """)
        else:
            w_eff   = all_kpi          # 若沒選任何格子 → 全部
            w_media = all_media
            st.info("尚未勾選任何有效組合，系統將預設選取所有 KPI 與 Media")

        # ---------- 4. 送出按鈕 ----------
        if st.button('送出', key='submit_combo'):

            mask_combo = cor_result['Media'].apply(
                lambda c: set(map(str.strip, c.split('+'))).issubset(w_media)
            )
            # --- 篩選 cor_result ---
            corr_sel = cor_result[
                mask_combo &
                (cor_result['Business'] == (w_business)) &
                (cor_result['Metric'].isin(w_eff))
            ]

            # --- 展示結果 ---
            expander = st.expander('展開查看媒體組合成效排行')
            expander.dataframe(
                corr_sel.sort_values('相關係數', ascending=False)
                        .reset_index(drop=True)
            )
            # --- 原始資料 ---
            expander = st.expander('展開查看原始數據')
            expander.dataframe(media_weekly_wide)

            # --- 畫圖 (沿用既有函式) ---
            if not corr_sel.empty:
                plot_corr_results(corr_sel.fillna(0))
            else:
                st.warning('找不到符合條件的資料，請重新選擇。')

    with tab2:
        st.header('🕵️‍♂️ 歷史投資影響力')
        with st.form(key='歷史投資影響力分析'):
            st.write('#### 請先選 KPI → 媒體組合 → 商業指標，系統將展示影響力曲線')

            # -- KPI
            kpi_sel = st.selectbox(
                'KPI：', sorted(combo_dict.keys()),
                key='kpi2'
            )

            # -- Combination (由 KPI 動態決定)
            combo_options = sorted(combo_dict[kpi_sel].keys())
            st.session_state.w_media2 = st.selectbox(
                '媒體組合：', combo_options,
                key='media_combo2'
            )

            # -- Business 指標
            bus_cols = list(business_weekly.columns[1:])   # 去掉 Week
            st.session_state.w_business2 = st.selectbox(
                '商業指標：', bus_cols,
                key='bus2'
            )

            submit2 = st.form_submit_button('送出')

        # 2️⃣ 計算並視覺化
        if submit2:
            # -- 取 KPI 與 Sales 的週別 Series
            s_kpi   = combo_dict[kpi_sel][st.session_state.w_media2]               # 已是 Series(index=Week)
            last_valid_idx = s_kpi[s_kpi != 0].index[-1]
            s_kpi_trimmed = s_kpi.loc[:last_valid_idx]

            s_sales = (business_weekly.set_index('Week')[st.session_state.w_business2])

            # -- 對齊週期，去除 NaN/Inf
            kpi_aligned, sales_aligned = s_kpi_trimmed.align(s_sales, join='inner')
            kpi_aligned  = kpi_aligned.replace([np.inf, -np.inf], np.nan)
            sales_aligned = sales_aligned.replace([np.inf, -np.inf], np.nan)

            # -- 計算即時相關係數
            corr_xy = round(kpi_aligned.corr(sales_aligned), 2)
            # st.markdown(f"**{st.session_state.w_media2} – {kpi_sel} 與 {st.session_state.w_business2} 的相關係數：** `{corr_val:.2f}`")

            st.session_state.X = kpi_aligned.copy()
            st.session_state.y = sales_aligned.copy()
            st.write(f'#### 分析期間：從 {kpi_aligned.index.min().strftime("%Y/%m/%d")} 到 {kpi_aligned.index.max().strftime("%Y/%m/%d")}')

            # 先跑一個兩段式回歸，看看有沒有是否適用。
            # 若兩段式回歸的斜率有一個是負的，表示沒有邊際效益遞減，改用線性回歸。
            st.session_state.p = fit_piecewise_linear(st.session_state.X, st.session_state.y)

            if (st.session_state.p[2] < 0) or (st.session_state.p[3] < 0) or int(st.session_state.p[0]) == 0:
                # 線性回歸分析
                if corr_xy < 0:
                    st.write(f'#### 此投資量與成效為負相關，相關係數: {corr_xy}')
                else:
                    st.write(f'#### 投資項與成效的相關係數: {corr_xy}')
                    st.write("#### 該 KPI 在過去期間對於銷售具有正向的影響力，並解釋了過去期間的部分銷售量增長")
                    expander = st.expander('舉例')
                    expander.write("在過去期間， 由以下趨勢圖可以觀察到「 16000  YT Boosting 的 Impression 」的投入，可以解釋過去期間 2000~6000 的銷售量增長")

                # st.write(st.session_state.X) : index is 'Week', only one column, type is float64
                # st.write(st.session_state.y) : index is 'Week', only one column, type is int64
                sm_model, y_pred, lower_bound, upper_bound, pred_grid = regression_analysis(st.session_state.X, st.session_state.y)
                st.session_state.linear_mod = sm_model
                st.session_state.y_pred_lin = y_pred

                expander = st.expander("點擊展開回歸分析詳細結果...")
                expander.write(sm_model.summary())

                # plot_regression_band(st.session_state.X, st.session_state.y, y_pred, lower_bound, upper_bound)
                plot_regression_band(st.session_state.X, st.session_state.y, pred_grid)

                trend_chart(st.session_state.X, st.session_state.y, y_pred=y_pred
                            , lower=lower_bound, upper=upper_bound)

                st.session_state.model = 'linear'
            else:
                st.write(f'#### 投資量與成效的相關係數: {corr_xy}')
                st.write(f'#### 投資量由 {"{:,.0f}".format(int(st.session_state.p[0]))} 開始，進入邊際效益遞減')
                plot_piecewise_linear(st.session_state.X, st.session_state.y, st.session_state.p)
                trend_chart(st.session_state.X, st.session_state.y, p = st.session_state.p)
                st.session_state.model = 'piecewise'

    with tab3:
        st.header('📈 投資成效模擬')
        with st.form(key='投資成效模擬'):
            st.warning('市場競爭激烈且變化迅速，本模型僅考量單一因子的影響，因此結果僅供初步評估該組合與 KPI 選擇之參考。此模型不適用於全面性的投放策略建議，亦無法保證實際成效。')
            st.write('#### 請填入未來預計投資量，每填入一列數字，系統將依據Business Data區間，新增一天/週/月的成效模擬。')

            expander = st.expander("點擊展開操作說明...")
            instruction = """
            1. 直接在下方表格中填入預算數字，亦可以透過複製貼上一次填入多筆數字。
            2. 點選表格右上方或左下方的 + 號，表格會增加一列，並增加一個時間區間的成效模擬。
            3. 若希望刪除部分表格，每次以一列為單位，可將滑鼠移置該列左方，勾選後按鍵盤「Delete鍵」，即可完成刪除。
            4. 若出現「Error during cell creation」，可直接無視，不會影響計算與圖表的產出，若需要編輯該格，僅需點擊該格並按 delete 鍵即可。
            """
            expander.write(instruction)

            cols = st.session_state.w_media2.split('+')
            # temp = pd.DataFrame([{'Start date': "2000/01/01"}])
            temp = pd.DataFrame(np.zeros((1, len(cols))), columns = cols)
            edited_df = st.data_editor(temp, num_rows="dynamic", use_container_width=True)
            submit_button3 = st.form_submit_button(label='送出')

        if submit_button3:
            if ('model' not in st.session_state) :
                st.error('🚨 請先到上一步選擇要觀察的媒體組合與 KPI!!')
                st.stop()
            else:
                df = st.session_state.X
                df = df.reset_index()
                n = len(edited_df)
                new_rows = []
                interval = df['Week'].diff().mode()[0]
                last_end_date = df['Week'].iloc[-1]
                for i in range(n):
                    new_start_date = last_end_date + pd.Timedelta(days=7)
                    new_end_date = new_start_date + interval
                    new_rows.append({'Week': new_start_date})
                    last_end_date = new_end_date
                # 将新行添加到 DataFrame
                edited_df = pd.concat([pd.DataFrame(new_rows), edited_df], axis=1)
                edited_df = edited_df.rename(columns={'Week':'時間區間'})
                edited_df['新投資'] = edited_df.iloc[:, 1:].sum(axis = 1)
                edited_df['時間區間'] = pd.to_datetime(edited_df['時間區間']).dt.date

                if st.session_state.model == 'piecewise':
                    X_addition = edited_df['新投資'].values
                    edited_df['預期成效'] = piecewise_linear(X_addition, *st.session_state.p)
                    trend_chart(st.session_state.X, st.session_state.y, p = st.session_state.p, edited_df = edited_df)
                else:
                    X_addition = edited_df['新投資'].values
                    X_add_con = sm.add_constant(X_addition, has_constant='add')
                    edited_df['預期成效'] = st.session_state.linear_mod.predict(X_add_con)
                    trend_chart(st.session_state.X, st.session_state.y, y_pred_linear = st.session_state.y_pred_lin, edited_df = edited_df)

    with tab5:
        st.header('📈 媒體重要成效多因子回歸分析')
        if ('roi_modeller_plus' not in st.session_state) or (not st.session_state.roi_modeller_plus):
            st.write('你使用的是簡易版的 ROI Modeller，無法使用此功能')
            st.stop()
        merged_weekly = media_weekly_wide.copy()
        merged_weekly = merged_weekly.merge(business_weekly, on='Week', how='left')
        merged_weekly = merged_weekly.reset_index(drop=True)
        try:
            sel_bus = business_weekly.columns[3]
        except:
            sel_bus = business_weekly.columns[1]

        results, X, y, confidence_df = multiplereg(merged_weekly, sel_bus)

        # --- 3️⃣ 查看回歸結果 ------------------------------------------------
        expander = st.expander("點擊展開回歸分析詳細結果...")
        expander.write(results.summary())
        st.success("表示該重要因子在＿＿信心水準下，具有顯著性，普遍建議以 90% 信心水準為通過標準，分析結果如下表。")
        perc_cols = ['信心水準']      # 👉 你要顯示為百分比的欄位
        styler = confidence_df.reset_index(drop=True).style.format({col: '{:.2%}' for col in perc_cols})
        # Streamlit
        st.dataframe(styler)      # 或 st.write(styler)

        if results is not None:
            var = 'TV~TVR'
            plot_regression_temp(var, X, y, results, sel_bus)
        else:
            st.error('🚨 無法進行多因子回歸分析，請檢查資料是否完整。')
