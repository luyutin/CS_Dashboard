import pandas as pd
import streamlit as st
from process.utils import ask_wrong

def split(df):
    campaign = df['廣告活動'].str.split('_', expand=True)
    df['Campaign name']          = campaign[0]
    df['Market']                 = campaign[1]
    df['Business Unit']          = campaign[2]
    df['Category']               = campaign[3]
    df['Master Brand']           = campaign[4]
    df['Product name']           = campaign[5]
    df['Audience']               = campaign[6]
    df['Placement']              = campaign[7]
    df['Campaign Objective']     = campaign[8]
    df['Funnel Stage']           = campaign[9]
    df['Message Type']           = campaign[11]
    df['Campaign Free Form']     = campaign[10]
    return df

def revised_output(revised, df, file_name):
    selected_col = [
        '日期', 'Campaign name', 'Product name', 'Audience', 'Placement', 'Campaign Objective', 'Message Type', 'Campaign Free Form',
        # ─── 互動 & 曝光類 ────────────────────────────────
        "曝光",                         # Impressions
        "點擊",                         # Clicks (all)
        "費用",                         # Spent (TWD) → 資料來源以「費用」為代表
        "瀏覽後轉換",                   # View-through conversion
        "轉換",                         # Conversions
        "轉換價值",                     # Conversion Value
        "觀看次數",                     # Views
        # ─── 影片播放深度 ────────────────────────────────
        "影片播放 3 秒以上的次數",       # 3" Video Views
        "影片播放 15 秒以上的次數",      # 15" Video Views (ThruPlays)
        "影片播放達30秒的觀看數",        # TrueView: Views
        "影片播放進度：25%",            # Video played to 25%
        "影片播放進度：50%",            # Video played to 50%
        "影片播放進度：75%",            # Video played to 75%
        "影片播放進度：100%",           # Video played to 100%
        # ─── 貼文互動 ─────────────────────────────────
        "貼文留言數",                   # Post comments
        "貼文互動次數",                 # Post engagements
        "貼文心情數",                   # Post reactions
        "貼文分享次數",                 # Post shares
        # ─── 電商 / 成效 ────────────────────────────────
        "收益"                         # Revenue
    ]

    filled_col = [
        'Date', 'Campaign name', 'Product', 'Audience', 'Placement', 'Campaign Objective', 'Message Type', 'Campaign Free Form',
        "Impressions", "Clicks (all)", "Spent (TWD)", "View-through conversion", "Conversions","Conversion Value",
        "Views", '3" Video Views', '15" Video Views (ThruPlays)',
        "TrueView: Views", "Video played to 25%", "Video played to 50%", "Video played to 75%", "Video played to 100%",
        "Post comments", "Post engagements", "Post reactions", "Post shares", "Revenue"
    ]

    ask_wrong(selected_col, filled_col, revised, df)

    revised['Item (Summary of filter)'] = \
        revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    revised['Region'] = 'APAC'
    revised['Market'] = 'TWN'
    revised['BU'] = file_name[0]
    revised['Customer'] = file_name[2]
    revised['Media'] = file_name[3]

    revised['Date'] = pd.to_datetime(revised['Date'], format='%Y-%m-%d')
    revised = revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return revised