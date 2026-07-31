import pandas as pd
import streamlit as st

def split(ttd_df):
    for i in range(len(ttd_df['Campaign'])):
        dict_cam = dict()
        try:
            values = ttd_df['Campaign'][i].split('_')
            for attr in values:
                dict_cam['Campaign ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        ttd_df['Campaign'][i] = dict_cam

    for i in range(len(ttd_df['Ad Group'])):
        dict_adset = dict()
        try:
            values = ttd_df['Ad Group'][i].split('_')
            for attr in values:
                dict_adset['Adset ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        ttd_df['Ad Group'][i] = dict_adset

    for i in range(len(ttd_df['Advertiser'])):
        dict_ad = dict()
        try:
            values = ttd_df['Advertiser'][i].split('_')
            for attr in values:
                dict_ad['Ad ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        ttd_df['Advertiser'][i] = dict_ad
    return ttd_df

def insert_col(ttd_df):
    ttd_df.insert(0, 'Campaign CN', 0)
    ttd_df.insert(0, 'Campaign OB', 0)
    ttd_df.insert(0, 'Campaign PR', 0)
    ttd_df.insert(0, 'Ad group AG', 0)
    ttd_df.insert(0, 'Ad group TG', 0)
    ttd_df.insert(0, 'Ad group FF', 0)
    ttd_df.insert(0, 'Ad group CH', 0)
    ttd_df.insert(0, 'Ad MG', 0)
    ttd_df.insert(0, 'Ad FF', 0)

    for i in range(len(ttd_df['Campaign'])):
        try:
            ttd_df['Campaign CN'][i] = ttd_df['Campaign'][i]['Campaign CN']
        except:
            ttd_df['Campaign CN'][i] = ''
        try:
            ttd_df['Campaign OB'][i] = ttd_df['Campaign'][i]['Campaign OB']
        except:
            ttd_df['Campaign OB'][i] = ''
        try:
            ttd_df['Campaign PR'][i] = ttd_df['Campaign'][i]['Campaign PR']
        except:
            ttd_df['Campaign PR'][i] = ''

    for i in range(len(ttd_df['Ad Group'])):
        try:
            ttd_df['Ad group AG'][i] = ttd_df['Ad Group'][i]['Adset AG']
        except:
            ttd_df['Ad group AG'][i] = ''
        try:
            ttd_df['Ad group TG'][i] = ttd_df['Ad Group'][i]['Adset TG']
        except:
            ttd_df['Ad group TG'][i] = ''
        try:
            ttd_df['Ad group FF'][i] = ttd_df['Ad Group'][i]['Adset FF']
        except:
            ttd_df['Ad group FF'][i] = ''
        try:
            ttd_df['Ad group CH'][i] = ttd_df['Ad Group'][i]['Adset CH']
        except:
            ttd_df['Ad group CH'][i] = ''

    for i in range(len(ttd_df['Advertiser'])):
        try:
            ttd_df['Ad MG'][i] = ttd_df['Advertiser'][i]['Ad MG']
        except:
            ttd_df['Ad MG'][i] = ''
        try:
            ttd_df['Ad FF'][i] = ttd_df['Advertiser'][i]['Ad FF']
        except:
            ttd_df['Ad FF'][i] = ''
    return ttd_df

def revised_output(ttd_revised, ttd_df, file_name):
    selected_col = ['Date', 'Impressions', 'Clicks',
                    'Ad FF', 'Ad group TG', 'Campaign OB', 'Campaign CN', 'Ad group FF',
                    'Campaign PR', 'Ad group CH',
                    'Advertiser Cost (Adv Currency)',
                    'Player Completed Views', 'Player 25% Complete', 'Player 50% Complete', 'Player 75% Complete', 'Player Completed Views']

    filled_col = ['Date', 'Impressions', 'Clicks (all)',
                  'Message Type', 'Audience', 'Campaign Objective', 'Campaign name', 'Adset name',
                  'Product', 'Ad Free Form',
                  'Spent (TWD)',
                  '15" Video Views (ThruPlays)', 'Video played to 25%', 'Video played to 50%', 'Video played to 75%', 'Video played to 100%']

    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            ttd_revised[dest_col] = ttd_df[src_col]
        except:
            st.error(f'你是否少了 {dest_col} 欄位呢? 如果沒有，可以忽視這個訊息')
            pass

    ttd_revised['Item (Summary of filter)'] = \
        ttd_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                      'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                      'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    ttd_revised['Region'] = 'APAC'
    ttd_revised['Market'] = 'TWN'
    ttd_revised['BU'] = file_name[0]
    ttd_revised['Customer'] = file_name[1]
    ttd_revised['Media'] = file_name[2]

    ttd_revised['Date'] = pd.to_datetime(ttd_revised['Date'])
    ttd_revised = ttd_revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return ttd_revised