import pandas as pd
import streamlit as st

def split(df):
    df['Adset Free Form'] = df['廣告群組'].str.split('_', expand=True)[6]
    df['Campaign Type'] = df['廣告群組'].str.split('_', expand=True)[15]
    df['Audience'] = df['廣告群組'].str.split('_', expand=True)[[17, 18, 19]].apply("_".join, axis=1)

    df['Campaign name'] = df['廣告活動'].str.split('_', expand=True)[1]
    df['Placement'] = df['廣告活動'].str.split('_', expand=True)[6]
    df['Buying Type'] = df['廣告活動'].str.split('_', expand=True)[15]

    df['Message Type'] = df['廣告標籤'].str.split('_', expand=True)[15]
    return df

def revised_output(revised, df, file_name):
    selected_col = ['Date', 'Advertiser Currency', 'Impressions', 'Clicks',
                    'Total Media Cost (Advertiser Currency)', 'TrueView: Views',
                    'First-Quartile Views (Video)',	'Midpoint Views (Video)', 'Third-Quartile Views (Video)', 'Complete Views (Video)',
                    'Adset name', 'Campaign Type', 'Campaign Objective', 'Campaign Free Form', 'Campaign name']

    filled_col = ['Date', 'Advertiser Currency', 'Impressions', 'Clicks (all)',
                  'Spent (TWD)', 'TrueView: Views',
                  'Video played to 25%', 'Video played to 50%', 'Video played to 75%', 'Video played to 100%',
                  'Adset name', 'Campaign Type', 'Campaign Objective', 'Campaign Free Form', 'Campaign name']

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