import pandas as pd
import streamlit as st
from process.utils import ask_wrong
import numpy as np

def split(meta_df):
    campaign = meta_df['行銷活動名稱'].str.split('_', expand=True)
    meta_df['Account name'] = campaign[0]
    meta_df['Campaign Name'] = campaign.iloc[:, 4:8].apply(lambda row: "-".join(row.dropna().astype(str)), axis=1)
    meta_df['Duration'] = campaign[5] + campaign[6]

    meta_df['Budget'] = campaign[8]

    adset = meta_df['廣告組合名稱'].str.split('_', expand=True)
    meta_df['Campaign Objective'] = adset[0]
    meta_df['Audience'] = adset[1]
    meta_df['Adset name'] = adset[3]
    meta_df['Adset Free Form'] = adset.iloc[:, 4:].apply(lambda row: "-".join(row.dropna().astype(str)), axis=1)

    meta_df['Product'] = campaign[2]
    meta_df['Buying Type'] = campaign[4]
    meta_df['Message Type'] = campaign[7]
    return meta_df

def revised_output(meta_revised, meta_df, file_name):
    selected_col = ['分析報告開始', 'Account name', 'Duration', 'Buying Type', 'Campaign Name', 'Campaign Free Form',
                    '廣告名稱', 'Adset name', 'Audience', 'Placement', 'Product', 'Message Type', 'Budget',
                    'Campaign Objective', 'Adset Free Form',
                    '觸及人數', '曝光次數', '點擊次數（全部）', "連結點擊次數", '貼文互動次數', 'ThruPlay 次數',
                    '花費金額 (TWD)', '影片播放到 25% 的次數', '影片播放到 50% 的次數', '影片播放到 75% 的次數', '影片播放到 100% 的次數']
    filled_col = ['Date', 'Account name', 'Duration', 'Buying Type', 'Campaign name', 'Campaign Free Form',
                  'Ad Free Form', 'Adset name', 'Audience', 'Placement', 'Product', 'Message Type', 'Budget',
                  'Campaign Objective', 'Adset Free Form',
                  'Reach', 'Impressions', 'Clicks (all)', 'Link clicks (Web Clicks)', 'Post engagements', '15" Video Views (ThruPlays)',
                  'Spent (TWD)', 'Video played to 25%', 'Video played to 50%', 'Video played to 75%', 'Video played to 100%']

    ask_wrong(selected_col, filled_col, meta_revised, meta_df)

    meta_revised['Item (Summary of filter)'] = \
        meta_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                      'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                      'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    meta_revised['Region'] = 'APAC'
    meta_revised['Market'] = 'TWN'
    meta_revised['BU'] = file_name[0]
    meta_revised['Customer'] = file_name[1]

    meta_revised['Media'] = np.where(
        meta_revised['Message Type'].str.contains('Boosting', case=False, na=False),
        'Meta_boosting',
        'Meta'
    )

    meta_revised['Date'] = pd.to_datetime(meta_revised['Date'])
    meta_revised = meta_revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return meta_revised