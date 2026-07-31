import pandas as pd
import streamlit as st
from process.utils import ask_wrong
import numpy as np

def split(df):
    if '廣告活動' in df.columns:
        pass
    else:
        df.columns = df.iloc[1, :]
        df = df.iloc[2:, :]

    campaign = df['廣告活動'].str.split('_', expand=True)
    df['Account name'] = campaign[0]
    df['Campaign Name'] = campaign.iloc[:, 4:8].apply(lambda row: "-".join(row.dropna().astype(str)), axis=1)
    df['Duration'] = campaign[5] + campaign[6]

    df['Budget'] = campaign[8]

    adset = df['廣告群組'].str.split('_', expand=True)
    df['Campaign Objective'] = adset[0]
    df['Audience'] = adset[1]
    df['Adset name'] = adset[3]
    df['Adset Free Form'] = adset.iloc[:, 4:].apply(lambda row: "-".join(row.dropna().astype(str)), axis=1)

    df['Product'] = campaign[2]
    df['Buying Type'] = campaign[4]
    df['Message Type'] = campaign[7]
    return df

def revised_output(yt_revised, yt_df, file_name):
    selected_col = ['日期', 'Account name', 'Campaign Name', 'Campaign Type', 'Campaign Free Form', 'Duration',
                    'Adset name', 'Message Type', 'Campaign Objective', 'Audience', 'Adset Free Form', 'Product', 'Buying Type',
                    '曝光', '點擊', '觀看次數',
                    '影片播放進度：25%', '影片播放進度：50%', '影片播放進度：75%', '影片播放進度：100%', '貨幣代碼', '費用']

    filled_col = ['Date', 'Account name', 'Campaign name', 'Campaign Type', 'Campaign Free Form', 'Duration',
                  'Adset name', 'Message Type', 'Campaign Objective', 'Audience', 'Adset Free Form', 'Product', 'Buying Type',
                  'Impressions', 'Clicks (all)', 'Views',
                  'Video played to 25%', 'Video played to 50%', 'Video played to 75%', 'Video played to 100%', 'Advertiser Currency', 'Spent (TWD)']

    ask_wrong(selected_col, filled_col, yt_revised, yt_df)

    yt_revised['Item (Summary of filter)'] = \
        yt_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                      'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                      'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    yt_revised['Region'] = 'APAC'
    yt_revised['Market'] = 'TWN'
    yt_revised['BU'] = file_name[0]
    yt_revised['Customer'] = file_name[1]
    yt_revised['Media'] = np.where(
        yt_revised['Message Type'].str.contains('Boosting', case=False, na=False),
        'YT_boosting',
        'YT'
    )

    yt_revised['Date'] = pd.to_datetime(yt_revised['Date'])
    yt_revised = yt_revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return yt_revised