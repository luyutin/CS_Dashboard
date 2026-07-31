import pandas as pd
import numpy as np

def split(YT_df):
    for i in range(len(YT_df['Insertion Order'])):
        dict_cam = dict()
        try:
            values = YT_df['Insertion Order'][i].split('_')
            for attr in values:
                dict_cam['Campaign ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        YT_df['Insertion Order'][i] = dict_cam

    for i in range(len(YT_df['Line Item'])):
        dict_adset = dict()
        try:
            values = YT_df['Line Item'][i].split('_')
            for attr in values:
                dict_adset['Adset ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        YT_df['Line Item'][i] = dict_adset
    return YT_df

def insert_col(YT_df):
    YT_df.insert(0, 'Campaign CN', 0)
    YT_df.insert(0, 'Campaign CH', 0)
    YT_df.insert(0, 'Campaign OB', 0)
    YT_df.insert(0, 'Campaign RT', 0)
    YT_df.insert(0, 'Campaign CY', 0)

    YT_df.insert(0, 'Ad group ST', 0)
    YT_df.insert(0, 'Ad group AG', 0)
    YT_df.insert(0, 'Ad group AS', 0)
    YT_df.insert(0, 'Ad group DA', 0)

    for i in range(len(YT_df['Insertion Order'])):
        try:
            YT_df['Campaign CN'][i] = YT_df['Insertion Order'][i]['Campaign CN']
        except:
            YT_df['Campaign CN'][i] = ''
        try:
            YT_df['Campaign OB'][i] = YT_df['Insertion Order'][i]['Campaign OB']
        except:
            YT_df['Campaign OB'][i] = ''
        try:
            YT_df['Campaign RT'][i] = YT_df['Insertion Order'][i]['Campaign RT']
        except:
            YT_df['Campaign RT'][i] = ''
        try:
            YT_df['Campaign CH'][i] = YT_df['Insertion Order'][i]['Campaign CH']
        except:
            YT_df['Campaign CH'][i] = ''
        try:
            YT_df['Campaign CY'][i] = YT_df['Insertion Order'][i]['Campaign CY']
        except:
            YT_df['Campaign CY'][i] = ''

    for i in range(len(YT_df['Line Item'])):
        try:
            YT_df['Ad group AG'][i] = YT_df['Line Item'][i]['Adset AG']
        except:
            YT_df['Ad group AG'][i] = ''
        try:
            YT_df['Ad group AS'][i] = YT_df['Line Item'][i]['Adset AS']
        except:
            YT_df['Ad group AS'][i] = ''
        try:
            YT_df['Ad group ST'][i] = YT_df['Line Item'][i]['Adset ST']
        except:
            YT_df['Ad group ST'][i] = ''
        try:
            YT_df['Ad group DA'][i] = YT_df['Line Item'][i]['Adset DA']
        except:
            YT_df['Ad group DA'][i] = ''
    return YT_df

def revised_output(YT_revised, YT_df, file_name):
    selected_col = ['Ad group DA', 'Ad group AS', 'Ad group AG', 'Ad group ST',
        'Campaign CY', 'Campaign RT', 'Campaign OB', 'Campaign CN',
        'Campaign CH', 'YouTube Ad Group',
        'Date', 'Impressions', 'Clicks', 'Revenue (Adv Currency)',
        'TrueView: Views',
        'First-Quartile Views (Video)', 'Midpoint Views (Video)', 'Third-Quartile Views (Video)',
        'Complete Views (Video)']

    filled_col = ['Adset Free Form', 'Adset MD', 'Audience', 'Adset name',
        'Advertiser Currency', 'Buying Type', 'Campaign Objective', 'Campaign name',
        'Campaign Type', 'Message Type',
        'Date', 'Impressions', 'Clicks (all)', 'Spent (TWD)',
        'TrueView: Views',
        'Video played to 25%', 'Video played to 50%', 'Video played to 75%',
        'Video played to 100%']

    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            YT_revised[dest_col] = YT_df[src_col]
        except:
            print(f'你是否少了 {dest_col} 欄位呢? 如果沒有，可以忽視這個訊息')
            pass

    YT_revised['Item (Summary of filter)'] = \
        YT_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                    'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                    'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    YT_revised['Region'] = 'APAC'
    YT_revised['Market'] = 'TWN'
    YT_revised['BU'] = file_name[0]
    YT_revised['Customer'] = file_name[2]
    YT_revised['Media'] = file_name[3]
    YT_revised['Date'] = YT_df['Date']

    YT_revised['Date'] = pd.to_datetime(YT_revised['Date'])
    YT_revised = YT_revised.sort_values(['Campaign name', 'Campaign Objective', 'Adset name', 'Date'], ignore_index=True)
    return YT_revised