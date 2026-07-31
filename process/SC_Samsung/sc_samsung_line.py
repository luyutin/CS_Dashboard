import pandas as pd
import streamlit as st

def revised_output(revised, df, file_name):
    selected_col = ['Day', 'Currency', 'Campaign name', 'Campaign objective', 'Ad account name', 'Ad group name',
                    'Reach (estimated)', 'Impressions', 'Clicks', 'Frequency', 'Cost', 'CV (conversions)',
                    'Video (25% watched)', 'Video (50% watched)', 'Video (75% watched)', 'Video (100% watched)', 'Video (100% watched)',
                    'Add-to-cart']
    filled_col = ['Date', 'Advertiser Currency', 'Campaign name', 'Campaign Objective', 'Account name', 'Adset name',
                  'Reach', 'Impressions', 'Clicks (all)', 'Frequency', 'Spent (TWD)', 'Conversions',
                  'Video played to 25%', 'Video played to 50%', 'Video played to 75%', 'Video played to 100%', '15" Video Views (ThruPlays)',
                  'Adds to cart']

    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            revised[dest_col] = df[src_col]
        except:
            st.error(f'你是否少了 {dest_col} 欄位呢? 如果沒有，可以忽視這個訊息')
            pass

    revised['Item (Summary of filter)'] = \
        revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    revised['Region'] = 'APAC'
    revised['Market'] = 'TWN'
    revised['BU'] = file_name[0]
    revised['Customer'] = file_name[1]
    revised['Media'] = file_name[2]

    #revised['Date'] = pd.to_datetime(revised['Date'], format='%Y/%m/%d')
    revised = revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return revised