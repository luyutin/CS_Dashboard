import pandas as pd
import streamlit as st

def split(line_df):
    line_df['Campaign Objective'] = line_df['Campaign name'].str.split('_', expand=True)[6].str.split('#', expand=True)[1]
    line_df['Duration'] = line_df['Campaign name'].str.split('_', expand=True)[4]
    line_df['Campaign name CN'] = line_df['Campaign name'].str.split('_', expand=True)[[1, 2, 3]].astype(str).apply("-".join, axis=1)
    line_df['Buying Type'] = line_df['Ad name'].str.split('_', expand=True)[4]
    return line_df

def revised_output(line_revised, line_df, file_name):
    selected_col = ['Day', 'Impressions', 'Clicks', 'Video (viewed for at least three seconds)',
                    'Cost', 'Frequency', 'CV (conversions)', 'Currency',
                    'Video (25% watched)', 'Video (50% watched)', 'Video (75% watched)', 'Video (100% watched)',
                    'Add-to-cart', 'Purchase', 'Reach (estimated)',
                    'Campaign Objective', 'Duration', 'Campaign name CN', 'Ad account name', 'Ad group name', 'Title',
                    'Ad name', 'Buying Type']

    filled_col = ['Date', 'Impressions', 'Clicks (all)', '3" Video Views',
                  'Spent (TWD)', 'Frequency', 'Conversions', 'Advertiser Currency',
                  'Video played to 25%', 'Video played to 50%', 'Video played to 75%', 'Video played to 100%',
                  'Adds to cart', 'Purchases', 'Reach',
                  'Campaign Objective', 'Duration','Campaign name', 'Account name', 'Audience',  'Message Type',
                  'Ad Free Form', 'Buying Type']

    errors = []
    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            line_revised[dest_col] = line_df[src_col]
        except:
            if dest_col == '廣告內容':
                line_revised['廣告素材'] = line_df[src_col]
            errors.append(src_col)
    st.error(f"你是否少了「 {'、'.join(errors)} 」欄位呢? \n 如果沒有，可以忽視這個訊息")


    line_revised['Item (Summary of filter)'] = \
        line_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                      'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                      'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    line_revised['Region'] = 'APAC'
    line_revised['Market'] = 'TWN'
    line_revised['BU'] = file_name[0]
    line_revised['Customer'] = file_name[2]
    line_revised['Media'] = file_name[3]

    line_revised['Date'] = pd.to_datetime(line_revised['Date'])
    line_revised = line_revised.sort_values(['Media', 'Message Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return line_revised