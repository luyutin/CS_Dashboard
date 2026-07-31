import pandas as pd
import streamlit as st

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
    return google_df

def insert_col(google_df):
    google_df.insert(0, 'Account name', 0)
    google_df.insert(0, 'Campaign CN', 0)
    google_df.insert(0, 'Campaign OB', 0)
    google_df.insert(0, 'Ad group AG', 0)
    google_df.insert(0, 'Ad group SA', 0)
    google_df.insert(0, 'Ad group FF', 0)
    google_df.insert(0, 'Ad group MD', 0)
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

    return google_df

def revised_output(revised, df, file_name):
    selected_col = ['貨幣代碼', 'Account name', '廣告活動類型', 'Campaign CN', 'Campaign OB',
                    '曝光', '點擊', '費用', 'MV>5', 'SE']

    filled_col = ['Advertiser Currency', 'Account name', 'Campaign Type', 'Campaign name', 'Campaign Objective',
                  'Impressions', 'Clicks (all)', 'Spent (TWD)', 'MV>5', 'Sales Engagement']

    errors = []
    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            revised[dest_col] = df[src_col]
        except:
            if dest_col == '廣告內容':
                revised['廣告素材'] = df[src_col]
            errors.append(src_col)
    st.error(f"你是否少了「 {'、'.join(errors)} 」欄位呢? \n 如果沒有，可以忽視這個訊息")

    revised['Item (Summary of filter)'] = \
        revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    revised['Region'] = 'APAC'
    revised['Market'] = 'TWN'
    revised['BU'] = file_name[0]
    revised['Customer'] = file_name[1]
    revised['Media'] = file_name[2]
    revised['Date'] = df['日期']

    revised['Date'] = pd.to_datetime(revised['Date'], format='%Y%m%d')
    revised = revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return revised