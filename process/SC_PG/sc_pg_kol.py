import pandas as pd
import numpy as np

def split(kol_df):
    kol_df['Adset Free Form'] = kol_df['行銷活動名稱'].str.split('_', expand=True)[2]
    kol_df['Campaign Objective'] = kol_df['行銷活動名稱'].str.split('_', expand=True)[3]
    kol_df['Duration'] = kol_df['行銷活動名稱'].str.split('_', expand=True)[5]
    return kol_df

def revised_output(kol_revised, kol_df, file_name):
    selected_col = ['廣告名稱', '廣告組合名稱', 'Duration', '版位', 'Campaign Objective', 'Adset Free Form',
                    '分析報告開始', '觸及人數', '頻率', '花費金額 (TWD)', '曝光次數', '點擊次數（全部）', '連結點擊次數',
                    'ThruPlay 次數',
                    '影片播放到 25% 的次數', '影片播放到 50% 的次數', '影片播放到 75% 的次數', '影片播放到 100% 的次數',
                    '影片播放 3 秒以上的次數', '貼文互動次數',	'貼文留言數', '貼文分享次數', '貼文心情數']

    filled_col = ['Campaign name', 'Adset name', 'Duration', 'Placement', 'Campaign Objective', 'Adset Free Form',
                  'Date', 'Reach', 'Frequency', 'Spent (TWD)', 'Impressions', 'Clicks (all)', 'Link clicks (Web Clicks)',
                  '15" Video Views (ThruPlays)',
                  'Video played to 25%', 'Video played to 50%', 'Video played to 75%', 'Video played to 100%',
                  '3" Video Views', 'Post engagements', 'Post comments', 'Post shares', 'Post reactions']

    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            kol_revised[dest_col] = kol_df[src_col]
        except:
            print(f'你是否少了 {dest_col} 欄位呢? 如果沒有，可以忽視這個訊息')
            pass

    kol_revised['Item (Summary of filter)'] = \
        kol_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                    'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                    'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    kol_revised['Region'] = 'APAC'
    kol_revised['Market'] = 'TWN'
    kol_revised['BU'] = file_name[0]
    kol_revised['Customer'] = file_name[2]
    kol_revised['Media'] = file_name[3]

    kol_revised['Date'] = pd.to_datetime(kol_revised['Date'])
    kol_revised = kol_revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return kol_revised