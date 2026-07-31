import pandas as pd
import streamlit as st

def revised_output(lm_revised, lm_df, file_name):
    selected_col = ['Media', 'Date', 'Placement', 'Campaign Name', 'Creative',
                    'URL', 'Impressions', 'Clicks', 'Link Clicks', 'CV', '工作階段',
                    'Conversion', '瀏覽後轉換', 'click 轉換', 'view 轉換',
                    'Video Views', 'Video Views 25%', 'Video Views 50%', 'Video Views 75%', 'Video Views 100%',
                    'Conversion', 'Leads', 'Action', 'Costs']

    filled_col = ['Media', 'Date', 'Placement', 'Campaign name', 'Message Type',
                  'Final URL', 'Impressions', 'Clicks (all)', 'Link clicks (Web Clicks)', 'Conversion Value', 'Working session',
                  'Conversions', 'View-through conversion', 'Clicks conversion', 'View conversion',
                  'Views', 'Video played to 25%', 'Video played to 50%', 'Video played to 75%', 'Video played to 100%',
                  'Conversions', 'Leads', 'Actions', 'Spent (TWD)']

    errors = []
    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            lm_revised[dest_col] = lm_df[src_col]
        except:
            errors.append(src_col)
    st.error(f"你是否少了「 {'、'.join(errors)} 」欄位呢? \n 如果沒有，可以忽視這個訊息")

    try:
        lm_revised['Audience'] = lm_df[['Audience', 'Audience.1']].astype(str).apply("_".join, axis=1)
    except:
        pass

    lm_revised['Item (Summary of filter)'] = \
        lm_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                    'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                    'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    lm_revised['Region'] = 'APAC'
    lm_revised['Market'] = 'TWN'
    lm_revised['BU'] = file_name[0]
    lm_revised['Customer'] = file_name[2]

    lm_revised['Date'] = pd.to_datetime(lm_revised['Date'])
    lm_revised = lm_revised.sort_values(['Media', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return lm_revised
