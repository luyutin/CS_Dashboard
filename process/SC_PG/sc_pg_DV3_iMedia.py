import pandas as pd
import numpy as np

def split(DV360_df):

    # 找出日期欄位中第一個空值的索引
    first_blank_index = DV360_df['Advertiser Currency'].isna().idxmax()

    # 如果整個欄位都沒有空值，則 idxmax 會返回第一個索引，因此需要額外檢查
    if pd.isna(DV360_df['Advertiser Currency'][first_blank_index]):
        DV360_df = DV360_df.loc[:first_blank_index - 1]
    else:
        pass

    for i in range(len(DV360_df['Insertion Order'])):
        dict_cam = dict()
        try:
            values = DV360_df['Insertion Order'][i].split('_')
            for attr in values:
                dict_cam['Campaign ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        DV360_df['Insertion Order'][i] = dict_cam

    for i in range(len(DV360_df['Line Item'])):
        dict_adset = dict()
        try:
            values = DV360_df['Line Item'][i].split('_')
            for attr in values:
                dict_adset['Adset ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        DV360_df['Line Item'][i] = dict_adset

    for i in range(len(DV360_df['Creative'])):
        dict_adset = dict()
        try:
            values = DV360_df['Creative'][i].split('_')
            for attr in values:
                dict_adset['Ad ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        DV360_df['Creative'][i] = dict_adset
    return DV360_df

def insert_col(DV360_df):
    DV360_df.insert(0, 'Campaign CN', 0)
    DV360_df.insert(0, 'Campaign CH', 0)
    DV360_df.insert(0, 'Campaign OB', 0)
    DV360_df.insert(0, 'Campaign RT', 0)
    DV360_df.insert(0, 'Campaign CY', 0)
    DV360_df.insert(0, 'Campaign DA', 0)

    DV360_df.insert(0, 'Ad group ST', 0)
    DV360_df.insert(0, 'Ad group AS', 0)

    DV360_df.insert(0, 'Ad SZ', 0)


    for i in range(len(DV360_df['Insertion Order'])):
        try:
            DV360_df['Campaign CN'][i] = DV360_df['Insertion Order'][i]['Campaign CN']
        except:
            DV360_df['Campaign CN'][i] = ''
        try:
            DV360_df['Campaign OB'][i] = DV360_df['Insertion Order'][i]['Campaign OB']
        except:
            DV360_df['Campaign OB'][i] = ''
        try:
            DV360_df['Campaign RT'][i] = DV360_df['Insertion Order'][i]['Campaign RT']
        except:
            DV360_df['Campaign RT'][i] = ''
        try:
            DV360_df['Campaign CH'][i] = DV360_df['Insertion Order'][i]['Campaign CH']
        except:
            DV360_df['Campaign CH'][i] = ''
        try:
            DV360_df['Campaign CY'][i] = DV360_df['Insertion Order'][i]['Campaign CY']
        except:
            DV360_df['Campaign CY'][i] = ''
        try:
            DV360_df['Campaign DA'][i] = DV360_df['Insertion Order'][i]['Campaign DA']
        except:
            DV360_df['Campaign DA'][i] = ''

    for i in range(len(DV360_df['Line Item'])):
        try:
            DV360_df['Ad group AS'][i] = DV360_df['Line Item'][i]['Adset AS']
        except:
            DV360_df['Ad group AS'][i] = ''
        try:
            DV360_df['Ad group ST'][i] = DV360_df['Line Item'][i]['Adset ST']
        except:
            DV360_df['Ad group ST'][i] = ''
    for i in range(len(DV360_df['Creative'])):
        try:
            DV360_df['Ad SZ'][i] = DV360_df['Creative'][i]['Ad SZ']
        except:
            DV360_df['Ad SZ'][i] = ''
    return DV360_df

def revised_output(DV360_revised, DV360_df, file_name):
    selected_col = ['Ad SZ', 'Ad group AS', 'Ad group ST', 'Campaign DA', 'Campaign CY',
                 'Campaign RT', 'Campaign OB', 'Campaign CH', 'Campaign CN',
                 'Date', 'Impressions', 'Clicks', 'Revenue (Adv Currency)']

    filled_col = ['Adset MD', 'Adset Free Form', 'Adset name', 'Audience', 'Advertiser Currency',
                   'Buying Type', 'Campaign Objective', 'Campaign Type', 'Campaign name',
                   'Date', 'Impressions', 'Clicks (all)', 'Spent (TWD)']

    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            DV360_revised[dest_col] = DV360_df[src_col]
        except:
            print(f'你是否少了 {dest_col} 欄位呢? 如果沒有，可以忽視這個訊息')
            pass

    DV360_revised['Item (Summary of filter)'] = \
        DV360_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                       'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                       'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    DV360_revised['Region'] = 'APAC'
    DV360_revised['Market'] = 'TWN'
    DV360_revised['BU'] = file_name[0]
    DV360_revised['Customer'] = file_name[2]
    DV360_revised['Media'] = file_name[3]

    DV360_revised['Date'] = pd.to_datetime(DV360_revised['Date'])
    DV360_revised = DV360_revised.sort_values(['Campaign name', 'Campaign Objective', 'Adset name', 'Date'], ignore_index=True)
    return DV360_revised