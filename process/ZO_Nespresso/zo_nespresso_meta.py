import pandas as pd
import streamlit as st

def split(meta_df):
    meta_df['Message Type'] = meta_df['廣告名稱'].str.split('_', expand=True)[8]

    adset = meta_df['廣告組合名稱']
    meta_df['Audience'] = adset.str.split('_', expand=True)[6]
    meta_df['Buying Type'] = adset.str.split('_', expand=True)[8]
    try:
        meta_df['Campaign Objective'] = adset.str.split('_', expand=True)[12]
    except:
        pass

    meta_df['Campaign name'] = meta_df['行銷活動名稱'].str.split('_', expand=True)[4]
    return meta_df

def revised_output(meta_revised, meta_df, file_name):
    selected_col = ['分析報告開始', '曝光次數', '點擊次數（全部）', '觸及人數', '連結點擊次數', '影片播放 3 秒以上的次數', 'ThruPlay 次數',
                    '花費金額 (TWD)', '貼文互動次數', '貼文留言數',
                    '加到購物車次數', '加到購物車的轉換值', '購買次數', '購買轉換值',
                    '影片播放到 25% 的次數','影片播放到 50% 的次數', '影片播放到 75% 的次數', '影片播放到 100% 的次數',
                    'Message Type', 'Buying Type', 'Audience', 'Campaign Objective', 'Campaign name']

    filled_col = ['Date', 'Impressions', 'Clicks (all)', 'Reach', 'Link clicks (Web Clicks)', '3" Video Views', '15" Video Views (ThruPlays)',
                  'Spent (TWD)', 'Post reactions', 'Post comments',
                  'Adds to cart', 'Adds to cart Conversion', 'Purchases', 'Purchases Conversion',
                  'Video played to 25%', 'Video played to 50%', 'Video played to 75%', 'Video played to 100%',
                  'Message Type', 'Buying Type', 'Audience', 'Campaign Objective', 'Campaign name']

    errors = []
    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            meta_revised[dest_col] = meta_df[src_col]
        except:
            errors.append(src_col)
    st.error(f"你是否少了「 {'、'.join(errors)} 」欄位呢? \n 如果沒有，可以忽視這個訊息")

    meta_revised['Item (Summary of filter)'] = \
        meta_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                      'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                      'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    meta_revised['Region'] = 'APAC'
    meta_revised['Market'] = 'TWN'
    meta_revised['BU'] = file_name[0]
    meta_revised['Customer'] = file_name[2]
    meta_revised['Media'] = file_name[3]

    meta_revised['Date'] = pd.to_datetime(meta_revised['Date'])
    meta_revised = meta_revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return meta_revised