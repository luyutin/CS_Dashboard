from datetime import datetime
import streamlit as st

import pandas as pd

def revised_output(revised, df, file_name):

    selected_col = ['Date', 'Campaign', 'Manual term', 'Medium', 'Source', 'Manual ad content',
                    'Purchase revenue', 'Sessions', 'Engaged sessions', 'Engagement rate']
    filled_col = ['Date', 'Campaign name', 'Adset name', 'Channel', 'InName Site', 'Message Type',
                  'Revenue', 'Sessions', 'Engaged sessions', 'Engagement rate']

    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            revised[dest_col] = df[src_col]
        except:
            st.error(f'你是否少了 {dest_col} 欄位呢? 如果沒有，可以忽視這個訊息')
            pass

    revised['Item (Summary of filter)'] = \
        revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                 'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                 'Placement', 'SEM Status']].astype(str).apply("_".join, axis=1)

    revised['Region'] = 'APAC'
    revised['Market'] = 'TWN'
    revised['BU'] = file_name[0]
    revised['Customer'] = file_name[1]
    revised['Media'] = file_name[2]

    revised['Date'] = pd.to_datetime(revised['Date'], format='%Y-%m-%d')
    revised = revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return revised