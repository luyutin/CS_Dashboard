import pandas as pd
import numpy as np

def split(TTD_imed_df):
    for i in range(len(TTD_imed_df['Campaign'])):
        dict_cam = dict()
        try:
            values = TTD_imed_df['Campaign'][i].split('_')
            for attr in values:
                dict_cam['Campaign ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        TTD_imed_df['Campaign'][i] = dict_cam

    for i in range(len(TTD_imed_df['Ad Group'])):
        dict_adset = dict()
        try:
            values = TTD_imed_df['Ad Group'][i].split('_')
            for attr in values:
                dict_adset['Adset ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        TTD_imed_df['Ad Group'][i] = dict_adset
    return TTD_imed_df

def insert_col(TTD_imed_df):
    TTD_imed_df.insert(0, 'Campaign CN', 0)
    TTD_imed_df.insert(0, 'Campaign OB', 0)
    TTD_imed_df.insert(0, 'Campaign RT', 0)

    TTD_imed_df.insert(0, 'Ad group ST', 0)
    TTD_imed_df.insert(0, 'Ad group AG', 0)
    TTD_imed_df.insert(0, 'Ad group AS', 0)
    TTD_imed_df.insert(0, 'Ad group DA', 0)
    TTD_imed_df.insert(0, 'Ad group CH', 0)

    for i in range(len(TTD_imed_df['Campaign'])):
        try:
            TTD_imed_df['Campaign CN'][i] = TTD_imed_df['Campaign'][i]['Campaign CN']
        except:
            TTD_imed_df['Campaign CN'][i] = ''
        try:
            TTD_imed_df['Campaign OB'][i] = TTD_imed_df['Campaign'][i]['Campaign OB']
        except:
            TTD_imed_df['Campaign OB'][i] = ''
        try:
            TTD_imed_df['Campaign RT'][i] = TTD_imed_df['Campaign'][i]['Campaign RT']
        except:
            TTD_imed_df['Campaign RT'][i] = ''

    for i in range(len(TTD_imed_df['Ad Group'])):
        try:
            TTD_imed_df['Ad group AG'][i] = TTD_imed_df['Ad Group'][i]['Adset AG']
        except:
            TTD_imed_df['Ad group AG'][i] = ''
        try:
            TTD_imed_df['Ad group AS'][i] = TTD_imed_df['Ad Group'][i]['Adset AS']
        except:
            TTD_imed_df['Ad group AS'][i] = ''
        try:
            TTD_imed_df['Ad group ST'][i] = TTD_imed_df['Ad Group'][i]['Adset ST']
        except:
            TTD_imed_df['Ad group ST'][i] = ''
        try:
            TTD_imed_df['Ad group DA'][i] = TTD_imed_df['Ad Group'][i]['Adset DA']
        except:
            TTD_imed_df['Ad group DA'][i] = ''
        try:
            TTD_imed_df['Ad group CH'][i] = TTD_imed_df['Ad Group'][i]['Adset CH']
        except:
            TTD_imed_df['Ad group CH'][i] = ''

    return TTD_imed_df

def revised_output(TTD_imed_revised, TTD_imed_df, file_name):
    selected_col = ['Ad group AS', 'Ad group ST', 'Ad group AG', 'Advertiser Currency Code',
                 'Campaign RT', 'Campaign OB', 'Ad group CH', 'Campaign CN',
                 'Date', 'Impressions', 'Clicks', 'Advertiser Cost (Adv Currency)']

    filled_col = ['Adset Free Form', 'Adset name','Audience', 'Advertiser Currency',
                   'Buying Type', 'Campaign Objective', 'Campaign Type', 'Campaign name',
                   'Date', 'Impressions', 'Clicks (all)', 'Spent (TWD)']

    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            TTD_imed_revised[dest_col] = TTD_imed_df[src_col]
        except:
            print(f'你是否少了 {dest_col} 欄位呢? 如果沒有，可以忽視這個訊息')
            pass

    YT_revised['Item (Summary of filter)'] = \
        YT_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                    'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                    'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)


    TTD_imed_revised['Region'] = 'APAC'
    TTD_imed_revised['Market'] = 'TWN'
    TTD_imed_revised['BU'] = file_name[0]
    TTD_imed_revised['Customer'] = file_name[2]
    TTD_imed_revised['Media'] = file_name[3]
    TTD_imed_revised['Date'] = TTD_imed_df['Date']

    TTD_imed_revised['Date'] = pd.to_datetime(TTD_imed_revised['Date'])
    TTD_imed_revised = TTD_imed_revised.sort_values(['Campaign name', 'Campaign Objective', 'Adset name', 'Date'], ignore_index=True)
    return TTD_imed_revised