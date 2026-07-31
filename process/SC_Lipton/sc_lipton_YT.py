import pandas as pd
import streamlit as st

def split(yt_df):

    yt_df.columns = yt_df.iloc[1]
    yt_df = yt_df.iloc[2:]
    yt_df = yt_df.reset_index(drop=True)

    campaign = yt_df['廣告活動'].str.split('_', expand=True)
    yt_df['Account name'] = campaign[0]
    yt_df['Campaign name'] = campaign[1]
    yt_df['Campaign Type'] = campaign[2]
    yt_df['Duration'] = campaign[3]
    yt_df['Campaign Free Form'] = campaign.iloc[:, 4:].apply(lambda row: "_".join(row.dropna().astype(str)), axis=1)

    yt_df['Adset name'] = yt_df['廣告群組']

    adname = yt_df['廣告名稱'].str.split('_', expand=True)
    yt_df['Message Type'] = adname.iloc[:, 2:].apply(lambda row: "_".join(row.dropna().astype(str)), axis=1)
    return yt_df

def revised_output(yt_revised, yt_df, file_name):
    selected_col = ['日期', 'Account name', 'Campaign name', 'Campaign Type', 'Campaign Free Form', 'Duration',
                    'Adset name', 'Message Type',
                    '曝光', '點擊', '觀看次數',
                    '影片播放進度：25%', '影片播放進度：50%', '影片播放進度：75%', '影片播放進度：100%', '貨幣代碼', '費用']

    filled_col = ['Date', 'Account name', 'Campaign name', 'Campaign Type', 'Campaign Free Form', 'Duration',
                  'Adset name', 'Message Type',
                  'Impressions', 'Clicks (all)', 'Views',
                  'Video played to 25%', 'Video played to 50%', 'Video played to 75%', 'Video played to 100%', 'Advertiser Currency', 'Spent (TWD)']

    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            yt_revised[dest_col] = yt_df[src_col]
        except:
            st.error(f'你是否少了 {dest_col} 欄位呢? 如果沒有，可以忽視這個訊息')
            pass

    yt_revised['Item (Summary of filter)'] = \
        yt_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                      'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                      'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    yt_revised['Region'] = 'APAC'
    yt_revised['Market'] = 'TWN'
    yt_revised['BU'] = file_name[0]
    yt_revised['Customer'] = file_name[1]
    yt_revised['Media'] = file_name[2]

    yt_revised['Date'] = pd.to_datetime(yt_revised['Date'])
    yt_revised = yt_revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return yt_revised