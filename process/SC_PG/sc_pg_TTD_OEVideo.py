import pandas as pd
import numpy as np

def split(TTD_vid_df):
    for i in range(len(TTD_vid_df['Campaign'])):
        dict_cam = dict()
        try:
            values = TTD_vid_df['Campaign'][i].split('_')
            for attr in values:
                dict_cam['Campaign ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        TTD_vid_df['Campaign'][i] = dict_cam

    for i in range(len(TTD_vid_df['Ad Group'])):
        dict_adset = dict()
        try:
            values = TTD_vid_df['Ad Group'][i].split('_')
            for attr in values:
                dict_adset['Adset ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        TTD_vid_df['Ad Group'][i] = dict_adset

    for i in range(len(TTD_vid_df['Creative'])):
        dict_adset = dict()
        try:
            values = TTD_vid_df['Creative'][i].split('_')
            for attr in values:
                dict_adset['Ad ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        TTD_vid_df['Creative'][i] = dict_adset
    return TTD_vid_df

def insert_col(TTD_vid_df):
    TTD_vid_df.insert(0, 'Campaign CN', 0)
    TTD_vid_df.insert(0, 'Campaign CH', 0)
    TTD_vid_df.insert(0, 'Campaign OB', 0)
    TTD_vid_df.insert(0, 'Campaign RT', 0)
    TTD_vid_df.insert(0, 'Campaign CY', 0)

    TTD_vid_df.insert(0, 'Ad group ST', 0)
    TTD_vid_df.insert(0, 'Ad group AG', 0)
    TTD_vid_df.insert(0, 'Ad group AS', 0)
    TTD_vid_df.insert(0, 'Ad group DA', 0)

    TTD_vid_df.insert(0, 'Ad FF', 0)
    TTD_vid_df.insert(0, 'Ad SZ', 0)

    for i in range(len(TTD_vid_df['Campaign'])):
        try:
            TTD_vid_df['Campaign CN'][i] = TTD_vid_df['Campaign'][i]['Campaign CN']
        except:
            TTD_vid_df['Campaign CN'][i] = ''
        try:
            TTD_vid_df['Campaign OB'][i] = TTD_vid_df['Campaign'][i]['Campaign OB']
        except:
            TTD_vid_df['Campaign OB'][i] = ''
        try:
            TTD_vid_df['Campaign RT'][i] = TTD_vid_df['Campaign'][i]['Campaign RT']
        except:
            TTD_vid_df['Campaign RT'][i] = ''
        try:
            TTD_vid_df['Campaign CH'][i] = TTD_vid_df['Campaign'][i]['Campaign CH']
        except:
            TTD_vid_df['Campaign CH'][i] = ''
        try:
            TTD_vid_df['Campaign CY'][i] = TTD_vid_df['Campaign'][i]['Campaign CY']
        except:
            TTD_vid_df['Campaign CY'][i] = ''

    for i in range(len(TTD_vid_df['Ad Group'])):
        try:
            TTD_vid_df['Ad group AG'][i] = TTD_vid_df['Ad Group'][i]['Adset AG']
        except:
            TTD_vid_df['Ad group AG'][i] = ''
        try:
            TTD_vid_df['Ad group AS'][i] = TTD_vid_df['Ad Group'][i]['Adset AS']
        except:
            TTD_vid_df['Ad group AS'][i] = ''
        try:
            TTD_vid_df['Ad group ST'][i] = TTD_vid_df['Ad Group'][i]['Adset ST']
        except:
            TTD_vid_df['Ad group ST'][i] = ''
        try:
            TTD_vid_df['Ad group DA'][i] = TTD_vid_df['Ad Group'][i]['Adset DA']
        except:
            TTD_vid_df['Ad group DA'][i] = ''

    for i in range(len(TTD_vid_df['Creative'])):
        try:
            TTD_vid_df['Ad FF'][i] = TTD_vid_df['Creative'][i]['Ad FF']
        except:
            TTD_vid_df['Ad FF'][i] = ''
        try:
            TTD_vid_df['Ad SZ'][i] = TTD_vid_df['Creative'][i]['Ad SZ']
        except:
            TTD_vid_df['Ad SZ'][i] = ''
    return TTD_vid_df

def revised_output(TTD_vid_revised, TTD_vid_df, file_name):
    selected_col = ['Ad group DA', 'Ad group AS', 'Ad group AG', 'Ad group ST',
        'Campaign CY', 'Campaign RT', 'Campaign OB', 'Campaign CN',
        'Ad FF', 'Ad SZ', 'Campaign CH', 'Date',
        'Impressions', 'Clicks', 'Advertiser Cost (Adv Currency)',
        'Player 25% Complete', 'Player 50% Complete', 'Player 75% Complete', 'Player Completed Views']

    filled_col = ['Adset Free Form', 'Adset MD', 'Audience', 'Adset name',
        'Advertiser Currency', 'Buying Type', 'Campaign Objective', 'Campaign name',
        'Ad Free Form', 'Message Type', 'Campaign Type', 'Date',
        'Impressions', 'Clicks (all)', 'Spent (TWD)',
        'Video played to 25%', 'Video played to 50%', 'Video played to 75%', 'Video played to 100%']

    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            TTD_vid_revised[dest_col] = TTD_vid_df[src_col]
        except:
            print(f'你是否少了 {dest_col} 欄位呢? 如果沒有，可以忽視這個訊息')
            pass

    TTD_vid_revised['Item (Summary of filter)'] = \
        TTD_vid_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                    'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                    'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)


    TTD_vid_revised['Region'] = 'APAC'
    TTD_vid_revised['Market'] = 'TWN'
    TTD_vid_revised['BU'] = file_name[0]
    TTD_vid_revised['Customer'] = file_name[2]
    TTD_vid_revised['Media'] = file_name[3]
    TTD_vid_revised['Date'] = TTD_vid_df['Date']

    TTD_vid_revised['Date'] = pd.to_datetime(TTD_vid_revised['Date'])
    TTD_vid_revised = TTD_vid_revised.sort_values(['Campaign name', 'Campaign Objective', 'Adset name', 'Date'], ignore_index=True)
    return TTD_vid_revised