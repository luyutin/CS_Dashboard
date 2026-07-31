import statsmodels.api as sm
import altair as alt
import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import curve_fit

# 線性回歸
def regression_analysis(X, y):
    """
    對 X 與 y 做線性回歸，並加入 y 的一期滯後作為控制變數 y_diff。

    回傳:
      model,
      y_pred_full (與原始 y 同 index 的 Series；第一筆為 NaN),
      lower_bound_full,
      upper_bound_full,
      pred_grid (可選：用來畫掃描曲線的 DataFrame，含 y_hat)
    """

    # ---- 1) 轉型：確保 y 是 Series、X 是 DataFrame ----
    if isinstance(X, pd.Series):
        X = X.to_frame()
    if isinstance(y, pd.DataFrame):
        if y.shape[1] != 1:
            raise ValueError("y 必須只有一欄，或請先選定目標欄位。")
        y = y.iloc[:, 0]
    y = y.astype(float)

    # ---- 2) 依 index 對齊 + 排序（這就是你說的 index mapping）----
    df = X.join(y.rename("y"), how="inner").sort_index()

    # ---- 3) 建立滯後 ----
    df["y(t-1)"] = df["y"].shift(1)
    # df["y_diff"] = df["y"].diff()

    # 有效樣本：滯後不為 NaN
    df_train = df.dropna(subset=["y(t-1)"])
    y_train = df_train["y"]
    X_train = df_train.drop(columns=["y"])

    # ---- 4) OLS ----
    X_train_const = sm.add_constant(X_train, has_constant="add")
    model = sm.OLS(y_train, X_train_const).fit(
            cov_type="HAC",
            cov_kwds={"maxlags": 4}   # 週資料，4 或 8 都可以試
        )

    # ---- 5) in-sample 預測：回填成與原始 y 同 index ----
    y_hat_train = model.predict(X_train_const)

    y_pred_full = pd.Series(index=df.index, dtype=float)
    y_pred_full.loc[df_train.index] = y_hat_train

    # ---- 6) 預測區間（對訓練樣本點）回填 ----
    pred_summary = model.get_prediction(X_train_const).summary_frame(alpha=0.05)

    lower_bound_full = pd.Series(index=df.index, dtype=float)
    upper_bound_full = pd.Series(index=df.index, dtype=float)

    lower_bound_full.loc[df_train.index] = pred_summary["obs_ci_lower"].values
    upper_bound_full.loc[df_train.index] = pred_summary["obs_ci_upper"].values

    # ---- 7) 掃描曲線：x 從 0 到 max(sample x)，步長=1 ----
    pred_grid = None
    X_cols = [c for c in X_train.columns if c != "y(t-1)"]

    if len(X_cols) > 0:
        scan_col = X_cols[0]
        max_x = X_train[scan_col].max()
        x_end = int(np.ceil(max_x))
        x_vals = np.arange(0, x_end + 1, 1)

        # 其他欄位固定平均
        grid = pd.DataFrame(
            {col: X_train[col].mean() for col in X_train.columns},
            index=range(len(x_vals))
        )
        grid[scan_col] = x_vals

        grid_const = sm.add_constant(grid, has_constant="add")

        # y_hat
        grid["預期成效"] = model.predict(grid_const).values

        # 95% prediction interval（跟你原本用 obs_ci_* 一樣）
        grid_pred = model.get_prediction(grid_const).summary_frame(alpha=0.05)
        grid["下界"] = grid_pred["obs_ci_lower"].values
        grid["上界"] = grid_pred["obs_ci_upper"].values

        # 只保留畫圖需要的欄位，並把掃描欄統一命名成 投資量
        pred_grid = grid[[scan_col, "預期成效", "下界", "上界"]].rename(columns={scan_col: "投資量"})
    return model, y_pred_full, lower_bound_full, upper_bound_full, pred_grid

def plot_regression_band(X, y, pred_grid):
    # --- 0) 把 X / y 壓成 Series（避免 X.values 變成 (n,1) 陣列）---
    if isinstance(X, pd.DataFrame):
        if X.shape[1] != 1:
            raise ValueError("目前的畫圖函數假設 X 只有一欄（投資量）。")
        x = X.iloc[:, 0]
    else:
        x = pd.Series(X)

    if isinstance(y, pd.DataFrame):
        if y.shape[1] != 1:
            raise ValueError("y 必須只有一欄，或請先選定目標欄位。")
        y = y.iloc[:, 0]
    else:
        y = pd.Series(y)

    # --- 1) 散點資料（原始觀測）---
    df_scatter = pd.DataFrame({
        "投資量": x,
        "實際成效": y
    }).dropna()

    df_scatter["圖例"] = "實際成效"

    # --- 2) 預測線 + 區間（用 pred_grid：x=0~max、步長=1）---
    df_line = pred_grid[["投資量", "預期成效"]].copy().dropna()
    df_line["圖例"] = "預期成效"

    df_band = pred_grid[["投資量", "下界", "上界"]].copy().dropna()
    df_band["圖例"] = "信賴區間"

    # 合併（用圖例統一顏色與 legend）
    df_full = pd.concat([df_scatter, df_line, df_band], ignore_index=True)

    color_scale = alt.Scale(
        domain=["實際成效", "預期成效", "信賴區間"],
        range=["blue", "red", "orange"]
    )

    base = alt.Chart(df_full).encode(
        x=alt.X("投資量:Q", sort="ascending"),
        color=alt.Color("圖例:N", scale=color_scale, legend=alt.Legend(title="圖例"))
    )

    scatter = base.transform_filter(
        alt.datum.圖例 == "實際成效"
    ).mark_circle(size=60).encode(
        y="實際成效:Q",
        tooltip=["投資量:Q", "實際成效:Q"]
    )

    band = base.transform_filter(
        alt.datum.圖例 == "信賴區間"
    ).mark_area(opacity=0.25).encode(
        y="下界:Q",
        y2="上界:Q",
        tooltip=["投資量:Q", "下界:Q", "上界:Q"]
    )

    line = base.transform_filter(
        alt.datum.圖例 == "預期成效"
    ).mark_line().encode(
        y="預期成效:Q",
        tooltip=["投資量:Q", "預期成效:Q"]
    )

    chart = band + line + scatter
    st.altair_chart(chart, use_container_width=True)

#### 分段回歸
def piecewise_linear(x, x0, y0, k1, k2):
    epsilon = 1e-10
    return np.piecewise(x, [x < x0, x >= x0],
                        [lambda x: k1*x + y0 - k1*x0,
                         lambda x: k2*np.log(x+epsilon) + y0 - k2*np.log(x0+epsilon)])

def fit_piecewise_linear(X, y):
    X = X.values
    y = y.values
    p, _ = curve_fit(piecewise_linear, X, y, p0=[np.median(X), np.median(y), 1, 1])
    return p

def plot_piecewise_linear(X, y, p):
    df = pd.DataFrame({'投資量': X, '實際成效': y})
    X = X.values
    df['預期成效'] = piecewise_linear(X, *p)

    # 分段點
    x0, y0 = p[0], p[1]

    breakpoint_df = pd.DataFrame({'投資量': [x0], '實際成效': [y0], '預期成效': [y0]})
    # 線性回歸
    linear_part = df[df['投資量'] <= x0].copy()
    linear_part['預期成效'] = linear_part['投資量'] * p[2] + y0 - p[2] * x0
    linear_part = pd.concat([linear_part, breakpoint_df], ignore_index=True)

    # 對數回歸
    X_in_log = np.linspace(x0, df['投資量'].max(), 1000)
    y_in_log = piecewise_linear(X_in_log, *p)
    log_part = pd.DataFrame({'投資量': X_in_log, '預期成效': y_in_log})

    scatter = alt.Chart(df).mark_circle(size=60).encode(
        x=alt.X('投資量:Q', axis=alt.Axis(title='投資量')),
        y=alt.Y('實際成效:Q', axis=alt.Axis(title='實際成效')),
        tooltip=['投資量', '實際成效']
    ).properties(
        title=''
    )

    line_linear = alt.Chart(linear_part).mark_line(color='red').encode(
        x=alt.X('投資量:Q', axis=alt.Axis(title='投資量')),
        y='預期成效'
    )

    line_log = alt.Chart(log_part).mark_line(color='red').encode(
        x=alt.X('投資量:Q', axis=alt.Axis(title='投資量')),
        y='預期成效'
    )

    breakpoint = alt.Chart(pd.DataFrame({'投資量': [x0], '實際成效': [y0]})).mark_point(size=100, color='blue').encode(
        x='投資量',
        y='實際成效',
        tooltip=['投資量', '實際成效']
    ).properties(
        title=''
    )

    chart = scatter + line_linear + line_log + breakpoint
    st.altair_chart(chart, use_container_width=True)

# 投資預測圖
def trend_chart(X, y, y_pred=None, lower=None, upper=None, edited_df=None):
    """
    總投資 vs 成效（含預測線與上下界 band）
    - X, y: Series 或 單欄 DataFrame，index 為時間（例如 Week）
    - y_pred/lower/upper: 與 y 同 index 的 Series（可包含 NaN）
    - edited_df: 先保留參數（你原本的新投資邏輯之後可再接回來）
    """

    # ---------- 1) 轉成 Series（避免單欄 DataFrame 造成 shape/欄位怪問題） ----------
    if isinstance(X, pd.DataFrame):
        if X.shape[1] != 1:
            raise ValueError("trend_chart 目前假設 X 只有一欄（總投資）。")
        Xs = X.iloc[:, 0]
    else:
        Xs = pd.Series(X)

    if isinstance(y, pd.DataFrame):
        if y.shape[1] != 1:
            raise ValueError("trend_chart 目前假設 y 只有一欄（實際成效）。")
        ys = y.iloc[:, 0]
    else:
        ys = pd.Series(y)

    # y_pred / lower / upper 若不是 Series，就套用 y 的 index
    if y_pred is not None and not isinstance(y_pred, pd.Series):
        y_pred = pd.Series(y_pred, index=ys.index)
    if lower is not None and not isinstance(lower, pd.Series):
        lower = pd.Series(lower, index=ys.index)
    if upper is not None and not isinstance(upper, pd.Series):
        upper = pd.Series(upper, index=ys.index)

    # ---------- 2) 以 index 對齊 + 排序 ----------
    parts = [Xs.rename("總投資"), ys.rename("實際成效")]
    if y_pred is not None:
        parts.append(y_pred.rename("預期成效"))
    if lower is not None:
        parts.append(lower.rename("下界"))
    if upper is not None:
        parts.append(upper.rename("上界"))

    df = pd.concat(parts, axis=1).sort_index()

    # ---------- 3) reset_index 後把時間欄統一命名為「時間區間」 ----------
    # 兼容 index name 可能是 Week 或 None（變成 index）
    df = df.reset_index()
    if "Week" in df.columns:
        df = df.rename(columns={"Week": "時間區間"})
    elif "index" in df.columns:
        df = df.rename(columns={"index": "時間區間"})
    else:
        # 如果 index 原本有名字（例如已經叫 時間區間），就不動
        pass

    # ---------- 9) 展開原始資料 ----------
    expander = st.expander("點擊展開預測圖的原始資料...")
    expander.write(df)

    # ---------- 4) x 軸型態：能轉 datetime 就用 T，否則用 O ----------
    time_parsed = pd.to_datetime(df["時間區間"], errors="coerce")
    if time_parsed.notna().sum() > 0:
        df["時間區間"] = time_parsed
        x_enc = alt.X("時間區間:T", title="時間區間")
    else:
        x_enc = alt.X("時間區間:O", title="時間區間")

    # ---------- 5) 準備 bar（總投資） ----------
    # 用 mark_bar(color=...) 指定常數色，避免你遇到的 alt.value/field error
    bar = alt.Chart(df).mark_bar(color="blue").encode(
        x=x_enc,
        y=alt.Y("總投資:Q", title="總投資"),
        tooltip=["時間區間", "總投資"]
    ).interactive()

    # ---------- 6) 準備 line（實際/預期） ----------
    line_cols = ["實際成效"]
    if "預期成效" in df.columns:
        line_cols.append("預期成效")

    df_lines = df[["時間區間"] + line_cols].melt(
        id_vars=["時間區間"],
        var_name="圖例",
        value_name="值"
    )

    # 顏色：實際橘、預期紅（你原本的配色）
    line_scale = alt.Scale(domain=["實際成效", "預期成效"], range=["orange", "red"])

    lines = alt.Chart(df_lines).mark_line().encode(
        x=x_enc,
        y=alt.Y("值:Q", title="成效"),
        color=alt.Color("圖例:N", scale=line_scale, legend=alt.Legend(title="圖例")),
        tooltip=["時間區間", "圖例", "值"]
    ).interactive()

    # ---------- 7) Band（可選）：上下界 ----------
    band = None
    if ("下界" in df.columns) and ("上界" in df.columns):
        df_band = df.dropna(subset=["下界", "上界"])

        # band 不塞到 df_lines 的 melt，直接獨立一層，最穩
        band = alt.Chart(df_band).mark_area(opacity=0.20, color="orange").encode(
            x=x_enc,
            y=alt.Y("下界:Q"),
            y2="上界:Q",
            tooltip=["時間區間", "下界", "上界"]
        )

    # ---------- 8) 合併圖層：投資軸與成效軸分開 ----------
    perf_layer = (band + lines) if band is not None else lines

    chart = alt.layer(
        bar,
        perf_layer
    ).resolve_scale(
        y="independent"
    ).properties(
        width=600,
        height=400
    ).configure_legend(
        strokeColor="gray",
        labelFontSize=12
    )

    st.altair_chart(chart, use_container_width=True)



def plot_corr_results(df):
    metric_order = [
        # TV
        'TVR', 'TVR carryon', '10 Second TVR', 'Reach 000s',
        # Video depth
        '15" Video Views (ThruPlays)',
        'Video played to 25%', 'Video played to 50%',
        'Video played to 75%', 'Video played to 100%',
        # Digital funnel
        'Impressions', 'Spent (TWD)', 'Views',
        'Clicks (all)', 'Link clicks (Web Clicks)', 'Post engagements'
    ]
    chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X('Metric:N', sort=metric_order, title='Metric'),
        y=alt.Y('相關係數:Q'),
        color='Media:N',
        tooltip=['Media', 'Metric', '相關係數']
    ).properties(
        width=650, height=400
    ).interactive()

    st.altair_chart(chart, use_container_width=True)


### 多元回歸
import statsmodels.api as sm
# from sklearn.preprocessing import StandardScaler

def multiplereg(merged_weekly, sel_bus):
    merged_weekly = merged_weekly.replace([np.inf, -np.inf], np.nan)#.fillna(0)
    # 選擇需要標準化的數值欄位（排除日期等非數值欄位）
    numeric_cols = merged_weekly.select_dtypes(include=[np.number]).columns
    # 初始化 StandardScaler
    #scaler = StandardScaler()
    # 對數值欄位進行標準化
    #merged_weekly[numeric_cols] = scaler.fit_transform(merged_weekly[numeric_cols])
    # 確認標準化後的 DataFrame
    merged_weekly[sel_bus + '(w-1)'] = merged_weekly.shift(1)[sel_bus]
    merged_weekly.dropna(inplace=True)

    # merged_weekly = merged_weekly[:5]
    # st.write(merged_weekly)

    # --- 1️⃣ 準備數據 ---------------------------------------------------
    # 目標變數 (y) 和 特徵變數 (X)
    y = merged_weekly[sel_bus]                #['sales %']  # 目標變數
    try:
        X = merged_weekly[['Meta~Impressions', 'Meta_boosting~Impressions', 'TV~TVR', 'YT~Views', 'Apex-PMP~Impressions', f"{sel_bus}(w-1)"]]
    except:
        X = merged_weekly[['Meta~Impressions', 'TV~TVR', 'YT~Views', f"{sel_bus}(w-1)"]]

    # X = X.drop(columns=['銷售瓶數(TTL)_t-1'])

    if np.linalg.matrix_rank(X) < X.shape[1]:
        st.warning("樣本不足，模型錯誤")
        if X.shape[1] < 15:
            st.warning(f"樣本數至少大於 **{15} 周**")
        else:
            st.warning(f"樣本數至少大於 **{X.shape[1]}周**")
        #   st.stop()
    # 添加常數項（截距）
    X = sm.add_constant(X)

    # --- 2️⃣ 建立回歸模型 ------------------------------------------------
    model = sm.OLS(y, X)  # 使用 Ordinary Least Squares 建立模型
    results = model.fit()

    # --- 4️⃣ 提取 t-value ------------------------------------------------
    pvalues = results.pvalues
    confidence_df = pd.DataFrame({
        '重要因子': X.columns,
        '信心水準': 1-pvalues
    }).sort_values(by='信心水準', ascending=False)
    confidence_df['是否通過'] = confidence_df.apply(
        lambda row: '通過' if row['信心水準'] >= 0.90 else '未通過', axis=1)
    return results, X, y, confidence_df

def plot_regression_temp(var, X, y, results, sel_bus):
    # --- 5️⃣ 繪製預測區間 ------------------------------------------------
    st.write("預測區間圖：")
    # --- ⓵ 產生 TV~TVR 的 x 軸網格 ------------------------------------------
    x_min, x_max = X[var].min(), X[var].max()
    x_grid = np.linspace(x_min, x_max, 100)  # 100 個點讓曲線順滑

    # --- ⓶ 建立「其他變數固定 = 0」的預測資料 -------------------------------
    # 先把所有欄位都設 0，再逐一替換 const 與 TV~TVR
    base_row = {col: X[col].mean() for col in X.columns}
    base_row['const'] = 1

    X_pred = pd.DataFrame([{**base_row, var: v} for v in x_grid])

    # --- ⓷ 取得預測值與信賴區間 -------------------------------------------
    pred_res   = results.get_prediction(X_pred)
    pred_frame = pred_res.summary_frame(alpha=0.05)   # 95 % interval

    df_plot = pd.DataFrame({
        var: x_grid,
        '預期成效':    pred_frame['mean'],
        '下界':        pred_frame['obs_ci_lower'],
        '上界':        pred_frame['obs_ci_upper']
    })

    df_scatter = pd.DataFrame({
        var: X[var],
        '實際成效': y
    })

    # --- ⓸ Altair 視覺化 ---------------------------------------------------
    color_scale = alt.Scale(
        domain=['實際成效', '預期成效', '信賴區間'],
        range=['blue',      'red',     'orange']
    )

    base = alt.Chart().encode(
        x=alt.X(f'{var}:Q', title=var)
    )

    scatter = base.mark_circle(size=60).encode(
        y=alt.Y('實際成效:Q', title=sel_bus),
        color=alt.value('blue'),
        tooltip=[var, '實際成效']
    ).transform_calculate(圖例='"實際成效"').transform_filter(alt.datum.圖例)

    line = base.mark_line(color='red').encode(
        y='預期成效:Q',
        tooltip=[var, '預期成效']
    ).transform_calculate(圖例='"預期成效"').transform_filter(alt.datum.圖例)

    band = base.mark_area(opacity=0.3, color='orange').encode(
        y='下界:Q',
        y2='上界:Q'
    ).transform_calculate(圖例='"信賴區間"').transform_filter(alt.datum.圖例)

    chart = (scatter.add_params()).properties(data=df_scatter) + \
            (band.properties(data=df_plot) + line.properties(data=df_plot))

    st.altair_chart(chart, use_container_width=True)
