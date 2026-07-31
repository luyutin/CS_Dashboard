import pandas as pd
import streamlit as st

def split(df):
    first_blank_index = df.isna().idxmin()
    st.write(first_blank_index)

    df = df.loc[first_blank_index+1:]
    return df

def revised_output(revised, df, file_name):
    selected_col = ['廣告活動', '廣告內容', '日期', '使用者', '工作階段', '跳出率',
                    '平均工作階段時間長度', 'GA Session name', 'GA Session Type', 'GA Session 數量']
    filled_col = ['Campaign name', 'Message Type', 'Date', 'User number', 'Working session', 'Bounce Rate',
                  'Avg Working session time', 'GA Session name', 'GA Session Type', 'GA Session Qty']

    errors = []
    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            revised[dest_col] = df[src_col]
        except:
            if dest_col == '廣告內容':
                revised['廣告素材'] = df[src_col]
            errors.append(src_col)
    st.error(f"你是否少了「 {'、'.join(errors)} 」欄位呢? \n 如果沒有，可以忽視這個訊息")

    revised['Item (Summary of filter)'] = \
        revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    revised['Region'] = 'APAC'
    revised['Market'] = 'TWN'
    revised['BU'] = file_name[0]
    revised['Customer'] = file_name[2]
    revised['Media'] = file_name[3]

    revised['Date'] = pd.to_datetime(revised['Date'], format='%Y%m%d')
    revised = revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return revised