import pandas as pd
import numpy as np

def split(DV3_vid_df):
    # 找出日期欄位中第一個空值的索引
    first_blank_index = DV3_vid_df['Advertiser'].isna().idxmax()

    # 如果整個欄位都沒有空值，則 idxmax 會返回第一個索引，因此需要額外檢查
    if pd.isna(DV3_vid_df['Advertiser'][first_blank_index]):
        DV3_vid_df = DV3_vid_df.loc[:first_blank_index - 1]
    else:
        pass

    for i in range(len(DV3_vid_df['Insertion Order'])):
        dict_cam = dict()
        try:
            values = DV3_vid_df['Insertion Order'][i].split('_')
            for attr in values:
                dict_cam['Campaign ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        DV3_vid_df['Insertion Order'][i] = dict_cam

    for i in range(len(DV3_vid_df['Line Item'])):
        dict_adset = dict()
        try:
            values = DV3_vid_df['Line Item'][i].split('_')
            for attr in values:
                dict_adset['Adset ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        DV3_vid_df['Line Item'][i] = dict_adset

    for i in range(len(DV3_vid_df['Creative'])):
        dict_adset = dict()
        try:
            values = DV3_vid_df['Creative'][i].split('_')
            for attr in values:
                dict_adset['Ad ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        DV3_vid_df['Creative'][i] = dict_adset
    return DV3_vid_df

def insert_col(DV3_vid_df):
    DV3_vid_df.insert(0, 'Campaign CN', 0)
    DV3_vid_df.insert(0, 'Campaign OB', 0)
    DV3_vid_df.insert(0, 'Campaign RT', 0)
    DV3_vid_df.insert(0, 'Campaign CY', 0)
    DV3_vid_df.insert(0, 'Campaign CH', 0)
    DV3_vid_df.insert(0, 'Campaign DA', 0)

    DV3_vid_df.insert(0, 'Ad group ST', 0)
    DV3_vid_df.insert(0, 'Ad group AG', 0)
    DV3_vid_df.insert(0, 'Ad group AS', 0)

    DV3_vid_df.insert(0, 'Ad FF', 0)
    DV3_vid_df.insert(0, 'Ad SZ', 0)

    for i in range(len(DV3_vid_df['Insertion Order'])):
        try:
            DV3_vid_df['Campaign CN'][i] = DV3_vid_df['Insertion Order'][i]['Campaign CN']
        except:
            DV3_vid_df['Campaign CN'][i] = ''
        try:
            DV3_vid_df['Campaign OB'][i] = DV3_vid_df['Insertion Order'][i]['Campaign OB']
        except:
            DV3_vid_df['Campaign OB'][i] = ''
        try:
            DV3_vid_df['Campaign RT'][i] = DV3_vid_df['Insertion Order'][i]['Campaign RT']
        except:
            DV3_vid_df['Campaign RT'][i] = ''
        try:
            DV3_vid_df['Campaign CH'][i] = DV3_vid_df['Insertion Order'][i]['Campaign CH']
        except:
            DV3_vid_df['Campaign CH'][i] = ''
        try:
            DV3_vid_df['Campaign CY'][i] = DV3_vid_df['Insertion Order'][i]['Campaign CY']
        except:
            DV3_vid_df['Campaign CY'][i] = ''
        try:
            DV3_vid_df['Campaign DA'][i] = DV3_vid_df['Insertion Order'][i]['Campaign DA']
        except:
            DV3_vid_df['Campaign DA'][i] = ''

    for i in range(len(DV3_vid_df['Line Item'])):
        try:
            DV3_vid_df['Ad group AG'][i] = DV3_vid_df['Line Item'][i]['Adset AG']
        except:
            DV3_vid_df['Ad group AG'][i] = ''
        try:
            DV3_vid_df['Ad group AS'][i] = DV3_vid_df['Line Item'][i]['Adset AS']
        except:
            DV3_vid_df['Ad group AS'][i] = ''
        try:
            DV3_vid_df['Ad group ST'][i] = DV3_vid_df['Line Item'][i]['Adset ST']
        except:
            DV3_vid_df['Ad group ST'][i] = ''

    for i in range(len(DV3_vid_df['Creative'])):
        try:
            DV3_vid_df['Ad FF'][i] = DV3_vid_df['Creative'][i]['Ad FF']
        except:
            DV3_vid_df['Ad FF'][i] = ''
        try:
            DV3_vid_df['Ad SZ'][i] = DV3_vid_df['Creative'][i]['Ad SZ']
        except:
            DV3_vid_df['Ad SZ'][i] = ''
    return DV3_vid_df

def revised_output(DV3_vid_revised, DV3_vid_df, file_name):
    selected_col = ['Campaign DA', 'Ad group AS', 'Ad group AG', 'Ad group ST',
        'Campaign CY', 'Campaign RT', 'Campaign OB', 'Campaign CN',
        'Ad FF', 'Campaign CH', 'Date',
        'Impressions', 'Clicks', 'Revenue (Adv Currency)',
        'First-Quartile Views (Video)', 'Midpoint Views (Video)', 'Third-Quartile Views (Video)', 'Complete Views (Video)']

    filled_col = ['Adset Free Form', 'Adset MD', 'Audience', 'Adset name',
        'Advertiser Currency', 'Buying Type', 'Campaign Objective', 'Campaign name',
        'Ad Free Form', 'Campaign Type', 'Date',
        'Impressions', 'Clicks (all)', 'Spent (TWD)',
        'Video played to 25%', 'Video played to 50%', 'Video played to 75%', 'Video played to 100%']

    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            DV3_vid_revised[dest_col] = DV3_vid_df[src_col]
        except:
            print(f'你是否少了 {dest_col} 欄位呢? 如果沒有，可以忽視這個訊息')
            pass

    DV3_vid_revised['Item (Summary of filter)'] = \
        DV3_vid_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                       'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                       'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    DV3_vid_revised['Region'] = 'APAC'
    DV3_vid_revised['Market'] = 'TWN'
    DV3_vid_revised['BU'] = file_name[0]
    DV3_vid_revised['Customer'] = file_name[2]
    DV3_vid_revised['Media'] = file_name[3]
    DV3_vid_revised['Date'] = DV3_vid_df['Date']

    DV3_vid_revised['Date'] = pd.to_datetime(DV3_vid_revised['Date'])
    DV3_vid_revised = DV3_vid_revised.sort_values(['Campaign name', 'Campaign Objective', 'Adset name', 'Date'], ignore_index=True)
    return DV3_vid_revised