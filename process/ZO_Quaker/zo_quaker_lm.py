import pandas as pd
import streamlit as st
from process.utils import ask_wrong

def revised_output(lm_revised, lm_df, file_name):
    campaign = lm_df['廣告活動'].str.split('_', expand=True)
    lm_df['Account name'] = campaign[0]
    lm_df['Product'] = campaign[2]
    lm_df['Media'] = campaign[3]
    lm_df['Buying Type'] = campaign[4]
    lm_df['Duration'] = campaign.iloc[:, 5:7].apply(lambda row: "_".join(row.dropna().astype(str)), axis=1)
    lm_df['Campaign name'] = campaign[7]
    lm_df['Budget'] = campaign[8]

    selected_col = ['Ad name', 'Ad Size', 'Date', 'Account name', 'Product', 'Media', 'Buying Type', 'Duration', 'Campaign name', 'Budget',
                    '曝光次數', '點擊次數', '影片播放進度：25%', '影片播放進度：50%', '影片播放進度：75%', '影片播放進度：100%', '費用(TWD)']

    filled_col = ['Message Type', 'Ad Free Form', 'Date', 'Account name', 'Product', 'Media', 'Buying Type', 'Duration', 'Campaign name', 'Budget',
                  'Impressions', 'Clicks (all)', 'Video played to 25%', 'Video played to 50%', 'Video played to 75%', 'Video played to 100%', 'Spent (TWD)']

    ask_wrong(selected_col, filled_col, lm_revised, lm_df)

    lm_revised['Item (Summary of filter)'] = \
        lm_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                    'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                    'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    lm_revised['Region'] = 'APAC'
    lm_revised['Market'] = 'TWN'
    lm_revised['BU'] = file_name[0]
    lm_revised['Customer'] = file_name[1]

    lm_revised['Date'] = pd.to_datetime(lm_revised['Date'])
    lm_revised = lm_revised.sort_values(['Media', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return lm_revised
