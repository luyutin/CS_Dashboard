import pandas as pd
import streamlit as st

def split(meta_df):
    campaign = meta_df['行銷活動名稱'].str.split('_', expand=True)
    meta_df['Account name'] = campaign[0]
    meta_df['Product'] = campaign[1]
    meta_df['Campaign Name'] = campaign[2]
    meta_df['Buying Type'] = campaign[3]
    meta_df['Duration'] = campaign[4]
    meta_df['Campaign Free Form'] = campaign[5]

    adset = meta_df['廣告組合名稱'].str.split('_', expand=True)
    meta_df['Adset name'] = adset[0]
    meta_df['Audience'] = adset[1]
    meta_df['Placement'] = adset[2]

    adname = meta_df['廣告名稱'].str.split('_', expand=True)
    meta_df['Message Type'] = adname[1]
    meta_df['Ad Free Form'] = adname.iloc[:, 2:].apply(lambda row: "_".join(row.dropna().astype(str)), axis=1)

    return meta_df

def revised_output(meta_revised, meta_df, file_name):
    selected_col = ['分析報告開始', 'Account name', 'Duration', 'Buying Type', 'Campaign Name', 'Campaign Free Form',
                    'Adset name', 'Audience', 'Placement', 'Product', 'Message Type',
                    '觸及人數', '曝光次數', '點擊次數（全部）', '影片播放 3 秒以上的次數',
                    '連結點擊次數', '貼文互動次數', '花費金額 (TWD)']
    filled_col = ['Date', 'Account name', 'Duration', 'Buying Type', 'Campaign name', 'Campaign Free Form',
                  'Adset name', 'Audience', 'Placement', 'Product', 'Message Type',
                  'Reach', 'Impressions', 'Clicks (all)', '3" Video Views',
                  'Link clicks (Web Clicks)', 'Post engagements', 'Spent (TWD)']

    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            meta_revised[dest_col] = meta_df[src_col]
        except:
            st.error(f'你是否少了 {dest_col} 欄位呢? 如果沒有，可以忽視這個訊息')
            pass

    meta_revised['Item (Summary of filter)'] = \
        meta_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                      'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                      'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    meta_revised['Region'] = 'APAC'
    meta_revised['Market'] = 'TWN'
    meta_revised['BU'] = file_name[0]
    meta_revised['Customer'] = file_name[1]
    meta_revised['Media'] = file_name[2]

    meta_revised['Date'] = pd.to_datetime(meta_revised['Date'])
    meta_revised = meta_revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return meta_revised