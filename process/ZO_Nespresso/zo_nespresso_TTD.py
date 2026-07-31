import pandas as pd
import streamlit as st

def split(df):
    first_blank_index = df['Advertiser Currency'].isna().idxmax()

    # 如果整個欄位都沒有空值，則 idxmax 會返回第一個索引，因此需要額外檢查
    if pd.isna(df['Advertiser Currency'][first_blank_index]):
        df = df.loc[:first_blank_index - 1]
    else:
        pass

    df['Adset name'] = df['Line Item'].str.split('_', expand=True)[6]
    df['Campaign Type'] = df['Line Item'].str.split('_', expand=True)[5]

    try:
        df['Audience'] = df['Creative'].str.split('_', expand=True)[1] + df['Creative'].str.split('_', expand=True)[2]
        df['Buying Type'] = df['Creative'].str.split('_', expand=True)[3] + df['Creative'].str.split('_', expand=True)[4]
        df['Ad Free Form'] = df['Creative'].str.split('_', expand=True)[10]
        df['Message Type'] = df['Creative'].str.split('_', expand=True)[12]
    except:
        pass

    df['Campaign Objective'] = df['Insertion Order'].str.split('_', expand=True)[8] + df['Insertion Order'].str.split('_', expand=True)[9]
    try:
        df['Campaign Free Form'] = df['Insertion Order'].str.split('_', expand=True)[10]
    except:
        pass
    df['Campaign name'] = df['Insertion Order'].str.split('_', expand=True)[1]
    return df

def revised_output(revised, df, file_name):
    selected_col = ['Date', 'Advertiser Currency', 'Impressions', 'Clicks',
                    'Total Conversions', 'Total Media Cost (Advertiser Currency)',
                    'Adset name', 'Campaign Type', 'Audience', 'Buying Type', 'Ad Free Form',
                    'Message Type', 'Campaign Objective', 'Campaign Free Form', 'Campaign name']

    filled_col = ['Date', 'Advertiser Currency', 'Impressions', 'Clicks (all)',
                  'Conversions', 'Spent (TWD)',
                  'Adset name', 'Campaign Type', 'Audience', 'Buying Type', 'Ad Free Form',
                  'Message Type', 'Campaign Objective', 'Campaign Free Form', 'Campaign name']

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
    revised['Customer'] = file_name[2]
    revised['Media'] = file_name[3]

    revised['Date'] = pd.to_datetime(revised['Date'])

    revised = revised.sort_values(['Media', 'Message Type', 'Campaign name', 'Audience', 'Adset name', 'Message Type', 'Date'], ignore_index=True)
    return revised