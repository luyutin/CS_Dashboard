import pandas as pd
import streamlit as st
from process.utils import ask_wrong

def revised_output(revised, tv_df, file_name):
    df = tv_df.iloc[3:, :]
    df.columns = ['Product', 'Metric'] + list(tv_df.iloc[2, 2:])
    df.loc[:, 'Product'] = df['Product'].ffill()

    # st.write(df)
    # 檢查每個欄位
    cols_to_drop = []
    cols_with_missing = []
    for col in df.columns:
        if df[col].isna().all():
            cols_to_drop.append(col)
        elif df[col].isna().any():
            cols_with_missing.append(col)
    # 刪除全為空值的直欄
    if cols_to_drop:
        df = df.drop(columns=cols_to_drop)
        st.info(f"已刪除全為空值的欄位: {cols_to_drop}")
    # 警告有缺值但非全空的直欄
    if cols_with_missing:
        st.warning(f"以下欄位有缺值: {cols_with_missing}")

    metrics = df['Metric'].unique()

    df_long = df.melt(
        id_vars=['Product', 'Metric'],  # 不變的欄位
        var_name='Date',                 # 新的日期欄位名稱
        value_name='Value'               # 新的數值欄位名稱
    )
    df_pivot = df_long.pivot(
        index=['Product', 'Date'],  # 新的索引欄位
        columns='Metric',           # 將 Metric 的值轉為直欄名稱
        values='Value'              # 將數值填入新的欄位
    )
    df_cleaned = df_pivot.dropna(subset = metrics, how='all').reset_index()
    df_cleaned['Impressions'] = df_cleaned['Universe']*0.01*df_cleaned['TVR']/1000
    df_cleaned['Spent (TWD)'] = df_cleaned['10 Second TVR']*df_cleaned['10sec CPRP']

    # df_cleaned 已經有一欄 'TVR'，保證為數值型別
    decay = 0.5                                 # 衰減係數 λ

    def adstock(series, decay=0.5):
        """
        將一條 TVR 序列轉成 carry-over (adstock) 序列。
        y[t] = x[t] + decay * y[t-1]
        """
        carry = 0
        out = []
        for x in series:
            carry = x + decay * carry
            out.append(carry)
        return pd.Series(out, index=series.index)

    df_cleaned['TVR carryon'] = adstock(df_cleaned['TVR'], decay)

    selected_col = ['Product', 'Date'] + list(metrics[:3]) + ['Impressions', 'Spent (TWD)', 'TVR carryon']
    filled_col = ['Product', 'Date'] + list(metrics[:3]) + ['Impressions', 'Spent (TWD)', 'TVR carryon']

    ask_wrong(selected_col, filled_col, revised, df_cleaned)

    revised['Item (Summary of filter)'] = \
        revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                    'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                    'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    revised['Region'] = 'APAC'
    revised['Market'] = 'TWN'
    revised['BU'] = file_name[0]
    revised['Customer'] = file_name[1]
    revised['Media'] = 'TV'

    revised['Date'] = pd.to_datetime(revised['Date'])
    revised = revised.sort_values(['Media', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return revised