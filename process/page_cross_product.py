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
    st.title('🌟跨產品分析🌟')

    if ('cross_product' not in st.session_state) or (not st.session_state.cross_product):
        st.error('#### 🚨 請先到 **【資料上傳：RM+ w/ 格式化數據 或 RM+ 簡易版】** 頁面上傳資料!!')
        st.stop()

    else:
        business_multi_prod = st.session_state.business_cross_prod.copy()
        media = st.session_state.media.copy()

        product_opts_bus = business_multi_prod.keys()
        chosen_prod_bus = st.sidebar.multiselect('#### 💵 請選擇想要觀察產品**銷售**數據：', product_opts_bus)
        business_l = []
        for pro_bus in chosen_prod_bus:
            business_temp = business_multi_prod[pro_bus]
            business_l.append(business_temp)
        # business = business_multi_prod[chosen_prod_bus]
        if business_l:
            business = pd.concat(business_l, axis=0)
        else:
            st.warning('#### 🚨 請在側邊欄選擇要觀察銷售數據的產品!!')
            st.stop()
        business = add_end(business)

        product_opts = media['Product'].unique()
        chosen_prod = st.sidebar.selectbox('#### 📺 請選擇產品**媒體**數據：', product_opts)
        media = media[media['Product'] == chosen_prod]

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
    st.write(f'### **💵銷售資料**：{chosen_prod_bus} / **📺 媒體數據**：{chosen_prod}')

    cor_result, cor_sammury, combo_dict, business_weekly, media_weekly, kpi2media, media_weekly_wide = roi_modeller(business, media_sel_date)
    combined_sel = merge_med_bus(media_weekly_wide, business_weekly)
    min_week_sel, max_week_sel = combined_sel['Week'].min(), combined_sel['Week'].max()
    max_week_sel = max_week_sel + pd.Timedelta(days=6)
    expander = st.expander('選取的媒體數據:')
    expander.write("格式化數據")
    expander.write(media_sel_date)
    expander.write("合併後的媒體與商業數據")
    expander.write(combined_sel)
    if len(combined_sel) < 30:
        st.error('#### ❗應加長選取時間，最少需要 30 周資料才可以使用本分析頁面')
        st.warning('#### ⚠️ 目前選取時間區間內的資料量為 {} 周（從 {} 到 {}）'.format(len(combined_sel), min_week_sel.strftime('%Y/%m/%d'), max_week_sel.strftime('%Y/%m/%d')))
        st.warning('#### ⚠️ 為求模型準確性與可信度，建議至少選取 72 周（18 個月）以上資料')
        st.stop()
    else:
        if 72 > len(combined_sel) > 30:
            st.info('目前選取時間區間內的資料量為 {} 周（從 {} 到 {}）'.format(len(combined_sel), min_week_sel.strftime('%Y/%m/%d'), max_week_sel.strftime('%Y/%m/%d')))
            st.warning('⚠️ 為求模型準確性與可信度，建議至少選取 72 周（18 個月）以上資料')
        else:
            st.success('🌟 目前選取時間區間內的資料量為 {} 周（從 {} 到 {}）'.format(len(combined_sel), min_week_sel.strftime('%Y/%m/%d'), max_week_sel.strftime('%Y/%m/%d')))

        expander = st.expander('相關性強弱程度分類:')
        expander.markdown(
            """
            <h4 style="color:#4c7aaf;">正相關性強弱程度分類：弱：0~0.3、中：0.3~0.7、強：0.7~1 </h3>
            """,
            unsafe_allow_html=True
        )

        if cor_result is None:
            st.warning('#### ⚠️ Business data 時間區間無法與媒體數據對應！')
            st.write('🔍 選取的媒體資料：')
            st.write(media_sel_date)
            st.write('🔍 選取的商業資料：')
            st.write(business)
            st.stop()

        st.subheader('📊 帶動銷售的關鍵媒體組合相關係數')
        st.dataframe(cor_result.sort_values('相關係數', ascending=False).reset_index(drop=True))

        expander = st.expander('原始「周」數據：')
        expander.write(media_weekly_wide)
        expander.write(business_weekly)

        business_options = business.columns[2:]
        tab1, tab2 = st.tabs(["媒體組合分析", "歷史影響力分析"])

        with tab1:
            st.header('💡媒體組合成效分析')

            # ---------- 0. 準備 KPI⇄Media 的對映表 ----------
            # kpi2media 應該在之前已經建立（含單媒體與組合）
            all_kpi   = sorted(kpi2media.keys())
            all_media = sorted({m for s in kpi2media.values() for m in s})
            all_media_order = ['TV', 'Meta', 'Meta_boosting', 'YT', 'YT_boosting', 'Apex-PMP']
            all_media_valid = [c for c in all_media_order if c in all_media]
            # ---------- 1. 建立布林/NaN 矩陣，供 data_editor 顯示 ----------
            df_bool = pd.DataFrame(index=all_media_valid, columns=all_kpi, dtype='object')
            # df_bool = pd.concat([pd.Series(name='全選'), df_bool], axis=1)
            for m in all_media:
                for k in all_kpi:
                    df_bool.loc[m, k] = False if m in kpi2media[k] else np.nan  # 無效格 → NaN
            df_bool = pd.concat([df_bool, pd.Series(name='全選')], axis=1)  # 最後一欄是 Media
            df_bool['全選'] = False
            # df_bool = df_bool.fillna('/')  # 將 NaN 填充為 False
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
            metric_order_valid = [c for c in metric_order if c in df_bool.columns]
            # 2️⃣ 如果有缺漏，提示使用者
            missing = set(metric_order) - set(metric_order_valid)
            if missing:
                st.warning(f"以下欄位在資料集中不存在，已自動忽略：{missing}")
            # 3️⃣ 重新排序
            df_bool = df_bool[metric_order_valid]

            # st.write(df_bool)
            st.write("### 選取欲分析的 Business x KPI × Media 組合")
            # ---------- 3. Business 指標多選 ----------
            w_business = st.selectbox(
                '請選擇想觀察的商業資料：',
                options = list(business_options),
                key='bus_multiselect'
            )

            edited = st.data_editor(
                df_bool,
                num_rows="fixed",            # 僅允許編輯布林值
                use_container_width=True
            )

            # ---------- 2. 解析使用者勾選結果 ----------
            tbl = edited.copy()  # 避免直接修改原始資料
            # 取出欄位名稱
            col_all   = '全選'
            kpi_cols  = [c for c in tbl.columns if c != col_all]   # 其餘都是 KPI

            sel_pairs = []

            for m in tbl.index:                      # 逐列處理
                if tbl.loc[m, col_all]:      # ✔ 勾了「全選」
                    # 把這一列所有 KPI 都加入
                    sel_pairs.extend([(k, m) for k in kpi_cols])
                else:
                    # 只撈該列中，單獨被勾選的 KPI
                    for k in kpi_cols:
                        if tbl.loc[m, k] is True:
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
                expander.dataframe(
                    media_weekly_wide
                )
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
                s_sales = (business_weekly.set_index('Week')[st.session_state.w_business2])

                # -- 對齊週期，去除 NaN/Inf
                kpi_aligned, sales_aligned = s_kpi.align(s_sales, join='inner')
                kpi_aligned  = kpi_aligned.replace([np.inf, -np.inf], np.nan)
                sales_aligned = sales_aligned.replace([np.inf, -np.inf], np.nan)

                # -- 計算即時相關係數
                corr_val = kpi_aligned.corr(sales_aligned)

                st.markdown(f"**{st.session_state.w_media2} – {kpi_sel} 與 {st.session_state.w_business2} 的相關係數：** `{corr_val:.2f}`")

                X = kpi_aligned
                y = sales_aligned
                corr_xy = round(X.corr(y), 2)
                st.session_state.X = X
                st.session_state.y = y

                st.session_state.p = fit_piecewise_linear(st.session_state.X, st.session_state.y)

                if (st.session_state.p[2] < 0) or (st.session_state.p[3] < 0):
                    # 線性回歸分析
                    if corr_xy < 0:
                        st.write(f'#### 此投資量與成效為負相關，相關係數: {corr_xy}')
                    else:
                        st.write(f'#### 投資項與成效的相關係數: {corr_xy}')
                        st.write("#### 該 KPI 在過去期間對於銷售具有正向的影響力，並解釋了過去期間的部分銷售量增長")
                        expander = st.expander('舉例')
                        expander.write("在過去期間， 由以下趨勢圖可以觀察到「 16000  YT Boosting 的 Impression 」的投入，可以解釋過去期間 2000~6000 的銷售量增長")
                    sm_model, y_pred, lower_bound, upper_bound = regression_analysis(st.session_state.X, st.session_state.y)
                    st.session_state.linear_mod = sm_model
                    st.session_state.y_pred_lin = y_pred

                    expander = st.expander("點擊展開回歸分析詳細結果...")
                    expander.write(sm_model.summary())

                    plot_regression_band(st.session_state.X, st.session_state.y, y_pred, lower_bound, upper_bound)
                    trend_chart(st.session_state.X, st.session_state.y, y_pred_linear=y_pred)
                    st.session_state.model = 'linear'
                else:
                    st.write(f'#### 投資量與成效的相關係數: {corr_xy}')
                    if int(st.session_state.p[0]) == 0:
                        st.write(f'#### 本投資指標從 0 開始即具有邊際效益遞減現象')
                    else:
                        st.write(f'#### 投資量由 {"{:,.0f}".format(int(st.session_state.p[0]))} 開始，進入邊際效益遞減')
                    plot_piecewise_linear(st.session_state.X, st.session_state.y, st.session_state.p)
                    trend_chart(st.session_state.X, st.session_state.y, p = st.session_state.p)
                    st.session_state.model = 'piecewise'