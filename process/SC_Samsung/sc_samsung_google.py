from datetime import datetime
import streamlit as st

import pandas as pd

def split(google_df):
    google_df.columns = google_df.iloc[1]
    google_df = google_df.iloc[2:]
    google_df = google_df.reset_index(drop=True)

    for i in range(len(google_df['帳戶名稱'])):
        dict_acc = dict()
        try:
            values = google_df['帳戶名稱'][i].split('_')
            for attr in values:
                dict_acc['帳戶名稱 ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        google_df['帳戶名稱'][i] = dict_acc

    for i in range(len(google_df['廣告活動'])):
        dict_cam = dict()
        try:
            values = google_df['廣告活動'][i].split('_')
            for attr in values:
                dict_cam['Campaign ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        google_df['廣告活動'][i] = dict_cam

    for i in range(len(google_df['廣告群組'])):
        dict_adset = dict()
        try:
            values = google_df['廣告群組'][i].split('_')
            for attr in values:
                dict_adset['Adset ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        google_df['廣告群組'][i] = dict_adset

    for i in range(len(google_df['廣告名稱'])):
        dict_ad = dict()
        try:
            values = google_df['廣告名稱'][i].split('_')
            for attr in values:
                dict_ad['Ad ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        google_df['廣告名稱'][i] = dict_ad
    return google_df

def insert_col(google_df):
    google_df.insert(0, 'Account name', 0)
    google_df.insert(0, 'Campaign CN', 0)
    google_df.insert(0, 'Campaign OB', 0)
    google_df.insert(0, 'Campaign PR', 0)
    google_df.insert(0, 'Ad group AG', 0)
    google_df.insert(0, 'Ad group SA', 0)
    google_df.insert(0, 'Ad group FF', 0)
    google_df.insert(0, 'Ad group MD', 0)
    google_df.insert(0, 'Ad group CH', 0)
    google_df.insert(0, 'Ad group PB', 0)
    google_df.insert(0, 'Ad FF', 0)

    for i in range(len(google_df['帳戶名稱'])):
        try:
            google_df['Account name'][i] = google_df['帳戶名稱'][i]['帳戶名稱 FF']
        except:
            google_df['Account name'][i] = ''

    for i in range(len(google_df['廣告活動'])):
        try:
            google_df['Campaign CN'][i] = google_df['廣告活動'][i]['Campaign CN']
        except:
            google_df['Campaign CN'][i] = ''
        try:
            google_df['Campaign OB'][i] = google_df['廣告活動'][i]['Campaign OB']
        except:
            google_df['Campaign OB'][i] = ''
        try:
            google_df['Campaign PR'][i] = google_df['廣告活動'][i]['Campaign PR']
        except:
            google_df['Campaign PR'][i] = ''

    for i in range(len(google_df['廣告群組'])):
        try:
            google_df['Ad group AG'][i] = google_df['廣告群組'][i]['Adset AG']
        except:
            google_df['Ad group AG'][i] = ''
        try:
            google_df['Ad group SA'][i] = google_df['廣告群組'][i]['Adset SA']
        except:
            google_df['Ad group SA'][i] = ''
        try:
            google_df['Ad group MD'][i] = google_df['廣告群組'][i]['Adset MD']
        except:
            google_df['Ad group FF'][i] = ''
        try:
            google_df['Ad group FF'][i] = google_df['廣告群組'][i]['Adset FF']
        except:
            google_df['Ad group FF'][i] = ''
        try:
            google_df['Ad group CH'][i] = google_df['廣告群組'][i]['Adset CH']
        except:
            google_df['Ad group CH'][i] = ''
        try:
            google_df['Ad group PB'][i] = google_df['廣告群組'][i]['Adset PB']
        except:
            google_df['Ad group PB'][i] = ''

    for i in range(len(google_df['廣告名稱'])):
        try:
            google_df['Ad FF'][i] = google_df['廣告名稱'][i]['Ad FF']
        except:
            google_df['Ad FF'][i] = ''

    return google_df

def revised_output(revised, df, file_name):
    selected_col = ['日期', '貨幣代碼', 'Account name', '廣告活動類型', 'Campaign CN', 'Campaign OB', 'Ad FF',
                    'Ad group AG', 'Ad group SA', 'Ad group MD', 'Ad group FF', 'Campaign PR', 'Ad group CH', 'Ad group PB', 'Ad FF',
                    '觀看次數', '觀看次數','影片播放進度：25%', '影片播放進度：50%', '影片播放進度：75%', '影片播放進度：100%',
                    '曝光', '點擊', '費用', 'MV>5', 'SE']
    filled_col = ['Date', 'Advertiser Currency', 'Account name', 'Campaign Type', 'Campaign name', 'Campaign Objective', 'Message Type',
                  'Adset name', 'Audience', 'Adset MD', 'Adset Free Form', 'Product', 'Channel', 'InName Site','Ad Free Form',
                  '15" Video Views (ThruPlays)', 'Views', 'Video played to 25%', 'Video played to 50%', 'Video played to 75%', 'Video played to 100%',
                  'Impressions', 'Clicks (all)', 'Spent (TWD)', 'MV>5', 'Sales Engagement']

    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            revised[dest_col] = df[src_col]
        except:
            st.error(f'你是否少了 {dest_col} 欄位呢? 如果沒有，可以忽視這個訊息')
            pass

    def video_adset(row):
        if row['Campaign Type'] == '影片':
            row['Adset name'] = row['Adset Free Form']
        return row
    revised = revised.apply(video_adset, axis = 1)

    revised['Item (Summary of filter)'] = \
        revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                 'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                 'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    revised['Region'] = 'APAC'
    revised['Market'] = 'TWN'
    revised['BU'] = file_name[0]
    revised['Customer'] = file_name[1]
    revised['Media'] = file_name[2]

    revised['Date'] = pd.to_datetime(revised['Date'], format='%Y-%m-%d')
    revised = revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return revised