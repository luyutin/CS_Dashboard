import pandas as pd
from itertools import combinations
import streamlit as st
import numpy as np

# 格式化數據與 Business data 對齊
def match_time(media, business):
    # --- ① 先把日期欄位轉成 datetime -----------------------
    media['Date'] = pd.to_datetime(media['Date'])
    business['Start date'] = pd.to_datetime(business['Start date'])

    for i in range(len(media.columns)):
        if media.columns[i] in ['Impressions', '曝光']:
            effect_start = i
            break
        else:
            effect_start = 2
    try:
        media = media.drop(columns = ['Budget'])
    except:
        pass

    eff_cols = media.columns[effect_start:]           # 更多維度
    # 0️⃣ 先把效益欄位轉成 numeric；非數字自動變 NaN
    media[eff_cols] = media[eff_cols].apply(
        pd.to_numeric, errors='coerce'
    )
    media = media[['Date', 'Media'] + list(eff_cols)]

    # --- ② media 直接彙整成「每週總量」 -----------------------
    media_w = (
        media.set_index('Date')
            .groupby('Media')
            .resample('W-MON', label='left', closed='left')
            .sum(min_count=1, numeric_only=True)   # ★一定要加 numeric_only=True
            .unstack('Media')
            .asfreq('W-MON')
            .fillna(0)
            .stack('Media')
            .reset_index()                         # 現在不會衝突
            .rename(columns={'Date': 'Week'})
    )

    # 同時備好 Start / End 兩欄，方便後面 merge
    # media_w['Start date'] = media_w['Week']                         # 週一
    # media_w['End date']   = media_w['Week'] + pd.Timedelta(days=6)  # 週日

    # --- ③ business：因為它有「期間」，需先攤平成『逐日』或『逐週』 ----
    # 這裡示範：把每一筆活動切成逐週資料，再彙整
    business_w = (
        business
        .assign(Date = pd.to_datetime(business['Start date']))   # 取 Start 作代表日
        .groupby(pd.Grouper(key='Date',
                            freq='W-MON',        # 週期：週一起算
                            label='left',        # 標籤：週一
                            closed='left'))      # 區間含週一
        .sum(numeric_only=True)                  # 匯總所有數值欄
        .reset_index()
        .rename(columns={'Date': 'Start date'})  # 週首
    )

    # 補上 End date (= Start + 6 天)，方便後面 merge
    # business_w['End date'] = business_w['Start date'] + pd.Timedelta(days=6)

    # ⇩ 你的原始週級資料
    media_w_std = media_w.copy()        # Week, Media, KPI1, KPI2, ...
    media_w_std.fillna(0, inplace=True)  # NaN 變 0
    # 1️⃣ 先找出數值欄 (排除非 KPI 欄位)
    num_cols = media_w_std.select_dtypes(include='number').columns
    # 2️⃣ 定義 z‑score 函式
    zscore = lambda x: (x - x.mean()) / x.std(ddof=1)
    # 3️⃣ 以 Media 分組，對每個數值欄做 transform
    media_w_std[num_cols] = (
        media_w_std.groupby('Media')[num_cols].transform(zscore)
    )
    business_w = business_w.rename(columns={'Start date': 'Week'})

    return business_w, media_w, media_w_std

def wide_for_comb(media_):
    # 2️⃣ 把 MultiIndex 欄位攤平成單層，並且規定欄位命名規則
    # media_.drop(columns=['Start date', 'End date'], inplace=True)
    # st.write('media_', media_)
    media_wide = (
        media_.pivot_table(
            index="Week",                # 列索引
            columns="Media",             # 欄索引
            values=media_.columns[2:],
            aggfunc="sum",               # 若同一天同媒體多筆，先 sum
            fill_value=0                 # 缺值補 0（可改成 NaN 再 fillna）
        )
    )

    media_wide.columns = [
        f"{media_}~{metric}"
        for metric, media_ in media_wide.columns
    ]

    # 3️⃣（可選）依日期排序、重設索引
    media_wide = media_wide.sort_values("Week").reset_index()

    # ① 先把「日期」欄保留，其餘欄位做加總檢查
    num_cols = media_wide.columns.drop('Week')  # 取出數值欄
    cols_to_keep = ['Week'] + [c for c in num_cols if media_wide[c].sum() != 0]
    media_wide = media_wide[cols_to_keep]
    #st.write(media_wide)
    return media_wide

def build_media_combo(media_weekly: pd.DataFrame,
                      kpi2media: dict) -> dict:
    combo_dict = {}

    for kpi, medias in kpi2media.items():
        sub_dict = {}
        medias = sorted(medias)                # 保持可預期順序

        # 產生所有非空子集合
        for r in range(1, len(medias) + 1):
            for combo in combinations(medias, r):
                combo_name = ' + '.join(combo)

                # ① 篩出 combo 內的媒體與 KPI
                s = (media_weekly.loc[
                         media_weekly['Media'].isin(combo),
                         ['Week', 'Media', kpi]
                     ]
                     .groupby('Week')[kpi]      # → 每週加總
                     .sum())

                sub_dict[combo_name] = s
        combo_dict[kpi] = sub_dict
    return combo_dict

# 生成所有媒體的排列组合
def build_corr_df(media_combo: dict,
                  business_weekly: pd.DataFrame,
                  sales_cols: list | None = None) -> pd.DataFrame:

    business_weekly = business_weekly.set_index('Week')
    results = []

    for sales in list(business_weekly.columns):
        target = business_weekly[sales]
        for kpi, combo_map in media_combo.items():
            for combo_name, s in combo_map.items():
                # 週索引對齊、去除 NaN/Inf
                a, b = s.align(target, join='inner')
                a, b = a.replace([np.inf, -np.inf], np.nan), \
                       b.replace([np.inf, -np.inf], np.nan)
                corr = a.corr(b)
                results.append([kpi, combo_name, sales, corr])

    corr_df = pd.DataFrame(
        results, columns=['Metric', 'Media', 'Business', '相關係數']
    )
    return corr_df

def top5(corr_df):
    # 使用 pivot 進行樞紐分析
    result_pivot = corr_df.pivot_table(index=['Media', 'Business'], columns='Metric', values='相關係數', dropna=False).reset_index()
    result_pivot.columns.name = None
    result_pivot = result_pivot.rename_axis(None, axis=1)

    final = []
    for mex in result_pivot.columns[2:]:
        temp = result_pivot.sort_values(mex, ascending=False).head(5)
        temp.insert(2, 'Sorted by', mex)
        temp.reset_index(drop=True, inplace=True)
        final.append(temp)
    corr_top5 = pd.concat(final)

    def ddd(row):
        return row['Sorted by'], row[row['Sorted by']]
    class_top = corr_top5[corr_top5.index==0].apply(ddd, axis = 1).reset_index(drop = True)
    class_vlaue = pd.DataFrame(class_top.tolist(), columns=['Key', 'Value'])
    sorted_class = class_vlaue.sort_values(by='Value', ascending=False).reset_index(drop=True)
    sorted_dict = {row['Key']: index for index, row in sorted_class.iterrows()}
    corr_top5 = corr_top5.reset_index()
    corr_top5.insert(3, 'KPI Order', corr_top5['Sorted by'].map(sorted_dict))
    corr_top5 = corr_top5.sort_values(['KPI Order', 'index']).reset_index(drop=True)
    corr_top5 = corr_top5.dropna(axis=1, how='all')
    return corr_top5.iloc[:, 1:]

def roi_modeller(business, media, type = 'formed_df'):
    if type == 'formed_df': # 格式化數據
        media = media.dropna(how='all', axis = 1)
        business_weekly, media_weekly, media_w_std = match_time(media, business)
    else:                   # ROI_Media
        result_df = media

    media_weekly_wide = wide_for_comb(media_weekly)
    kpi2media = {}
    for col in media_weekly_wide.columns:
        if '~' in col:
            media_part, kpi_part = col.split('~', 1)
            kpi2media.setdefault(kpi_part, set()).add(media_part)
    combo_dict = build_media_combo(media_weekly, kpi2media)
    corr_df = build_corr_df(combo_dict, business_weekly)
    #st.write(business_weekly)
    if corr_df is not None and not corr_df.empty:
        corr_top5 = top5(corr_df)
        return corr_df, corr_top5, combo_dict, business_weekly, media_weekly, kpi2media, media_weekly_wide
    else:
        return None, None, None

# 將 combo_dict 轉成 dataframe
def combo_dict_to_long(combo_dict: dict) -> pd.DataFrame:
    frames = []
    for kpi, c_map in combo_dict.items():
        # ── 1. 先把同一 KPI 底下所有組合合併成 DataFrame
        #     keys= 產生第一層索引 'Combination'
        df_kpi = (
            pd.concat(c_map, names=['Combination'])    # MultiIndex: (Combination, Week)
            .rename('Value')                           # Series → 給欄位名稱
            .reset_index()                             # 轉回表格
            .rename(columns={'level_1': 'Week'})       # level_1 = 週別
        )
        df_kpi['KPI'] = kpi                            # 補上 KPI 欄
        frames.append(df_kpi[['Week', 'KPI', 'Combination', 'Value']])

    # ── 2. 把所有 KPI 的表格串起來
    long_df = pd.concat(frames, ignore_index=True)
    return long_df

def merge_med_bus(media_w: pd.DataFrame,
                  business_w: pd.DataFrame) -> pd.DataFrame:
    # 1️⃣ 確保兩邊的 Week 都是 datetime
    for df in (business_w, media_w):
        df['Week'] = pd.to_datetime(df['Week'])

    # 2️⃣ 用 merge 對齊
    combined = pd.merge(
        business_w,
        media_w,
        on='Week',          # 兩邊都用欄位 Week
        how='inner',
        suffixes=('_bus', '_media')   # 避免重名欄位衝突
    )
    return combined