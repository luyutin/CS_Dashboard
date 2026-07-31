import pandas as pd
import streamlit as st

def split(DV360_df):
    first_blank_index = DV360_df['Advertiser Currency'].isna().idxmax()

    # 如果整個欄位都沒有空值，則 idxmax 會返回第一個索引，因此需要額外檢查
    if pd.isna(DV360_df['Advertiser Currency'][first_blank_index]):
        DV360_df = DV360_df.loc[:first_blank_index - 1]
    else:
        pass

    DV360_df['Adset name'] = DV360_df['Line Item'].str.split('_', expand=True)[6]
    DV360_df['Campaign Type'] = DV360_df['Line Item'].str.split('_', expand=True)[5]

    try:
        DV360_df['Audience'] = DV360_df['Creative'].str.split('_', expand=True)[1] + DV360_df['Creative'].str.split('_', expand=True)[2]
        DV360_df['Buying Type'] = DV360_df['Creative'].str.split('_', expand=True)[3] + DV360_df['Creative'].str.split('_', expand=True)[4]
        DV360_df['Ad Free Form'] = DV360_df['Creative'].str.split('_', expand=True)[10]
        DV360_df['Message Type'] = DV360_df['Creative'].str.split('_', expand=True)[12]
    except:
        pass

    DV360_df['Campaign Objective'] = DV360_df['Insertion Order'].str.split('_', expand=True)[8] + DV360_df['Insertion Order'].str.split('_', expand=True)[9]
    try:
        DV360_df['Campaign Free Form'] = DV360_df['Insertion Order'].str.split('_', expand=True)[10]
    except:
        pass
    DV360_df['Campaign name'] = DV360_df['Insertion Order'].str.split('_', expand=True)[1]
    return DV360_df

def revised_output(DV360_revised, DV360_df, file_name):
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
            DV360_revised[dest_col] = DV360_df[src_col]
        except:
            if dest_col == '廣告內容':
                DV360_revised['廣告素材'] = DV360_df[src_col]
            errors.append(src_col)
    st.error(f"你是否少了「 {'、'.join(errors)} 」欄位呢? \n 如果沒有，可以忽視這個訊息")

    DV360_revised['Item (Summary of filter)'] = \
        DV360_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                       'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                       'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    DV360_revised['Region'] = 'APAC'
    DV360_revised['Market'] = 'TWN'
    DV360_revised['BU'] = file_name[0]
    DV360_revised['Customer'] = file_name[2]
    DV360_revised['Media'] = file_name[3]

    DV360_revised['Date'] = pd.to_datetime(DV360_revised['Date'])

    DV360_revised = DV360_revised.sort_values(['Media', 'Message Type', 'Campaign name', 'Audience', 'Adset name', 'Message Type', 'Date'], ignore_index=True)
    return DV360_revised