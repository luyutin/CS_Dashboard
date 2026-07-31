import pandas as pd
import streamlit as st

def split(meta_df):
    meta_df['Message Type'] = meta_df['廣告名稱'].str.split('_', expand=True)[2]
    meta_df['Placement'] = meta_df['廣告名稱'].str.split('_', expand=True)[3]

    meta_df['Adset name'] = meta_df['廣告組合名稱'].str.split('_', n=1, expand=True)[1]

    meta_df['Campaign name'] = meta_df['行銷活動名稱'].str.split('_', n=3, expand=True)[1]
    meta_df['Campaign Free Form'] = meta_df['行銷活動名稱'].str.split('_', n=3, expand=True)[2]
    meta_df['Duration'] = meta_df['行銷活動名稱'].str.split('_', n=3, expand=True)[0]
    meta_df['Campaign Objective'] = meta_df['行銷活動名稱'].str.split('_', expand=True)[3]
    return meta_df

def revised_output(meta_revised, meta_df, file_name):
    selected_col = ['分析報告開始', '曝光次數', '點擊次數（全部）', '觸及人數', '連結點擊次數', '影片播放 3 秒以上的次數', 'ThruPlay 次數',
                    '花費金額 (TWD)',
                    '貼文互動次數', '貼文心情數', '貼文留言數', '貼文分享次數', '相片瀏覽次數', '貼文儲存次數',
                    '年齡', '性別', 'Placement',
                    'Message Type', 'Buying Type', 'Audience', 'Campaign Objective', 'Campaign name', 'Campaign Free Form', 'Duration']

    filled_col = ['Date', 'Impressions', 'Clicks (all)', 'Reach', 'Link clicks (Web Clicks)', '3" Video Views', '15" Video Views (ThruPlays)',
                  'Spent (TWD)',
                  'Post engagements', 'Post reactions', 'Post comments', 'Post shares', 'Photo Views', 'Post Saves',
                  'Audience', 'Adset Free Form', 'Placement',
                  'Message Type', 'Buying Type', 'Audience', 'Campaign Objective', 'Campaign name', 'Campaign Free Form', 'Duration']

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
    meta_revised['BU'] = 'LB'
    meta_revised['Customer'] = file_name[2]
    meta_revised['Media'] = file_name[3]

    meta_revised['Date'] = pd.to_datetime(meta_revised['Date'])
    meta_revised = meta_revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return meta_revised