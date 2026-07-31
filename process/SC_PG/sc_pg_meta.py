import pandas as pd
import numpy as np

def split(meta_df):
    for i in range(len(meta_df['Campaign name'])):
        dict_cam = dict()
        try:
            values = meta_df['Campaign name'][i].split('_')
            for attr in values:
                dict_cam['Campaign ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        meta_df['Campaign name'][i] = dict_cam

    for i in range(len(meta_df['Ad Set Name'])):
        dict_adset = dict()
        try:
            values = meta_df['Ad Set Name'][i].split('_')
            for attr in values:
                dict_adset['Adset ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        meta_df['Ad Set Name'][i] = dict_adset

    for i in range(len(meta_df['Ad name'])):
        dict_ad = dict()
        try:
            values = meta_df['Ad name'][i].split('_')
            for attr in values:
                dict_ad['Ad ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        meta_df['Ad name'][i] = dict_ad
    return meta_df

def insert_col(meta_df):
    meta_df.insert(0, 'Campaign CN', 0)
    meta_df.insert(0, 'Campaign OB', 0)
    meta_df.insert(0, 'Campaign RT', 0)
    meta_df.insert(0, 'Campaign CY', 0)

    meta_df.insert(0, 'Ad group ST', 0)
    meta_df.insert(0, 'Ad group AG', 0)
    meta_df.insert(0, 'Ad group AS', 0)
    meta_df.insert(0, 'Ad group DA', 0)

    meta_df.insert(0, 'Ad CH', 0)
    meta_df.insert(0, 'Ad AS', 0)

    for i in range(len(meta_df['Campaign name'])):
        try:
            meta_df['Campaign CN'][i] = meta_df['Campaign name'][i]['Campaign CN']
        except:
            meta_df['Campaign CN'][i] = ''
        try:
            meta_df['Campaign OB'][i] = meta_df['Campaign name'][i]['Campaign OB']
        except:
            meta_df['Campaign OB'][i] = ''
        try:
            meta_df['Campaign RT'][i] = meta_df['Campaign name'][i]['Campaign RT']
        except:
            meta_df['Campaign RT'][i] = ''
        try:
            meta_df['Campaign CY'][i] = meta_df['Campaign name'][i]['Campaign CY']
        except:
            meta_df['Campaign CY'][i] = ''

    for i in range(len(meta_df['Ad Set Name'])):
        try:
            meta_df['Ad group AG'][i] = meta_df['Ad Set Name'][i]['Adset AG']
        except:
            meta_df['Ad group AG'][i] = ''
        try:
            meta_df['Ad group AS'][i] = meta_df['Ad Set Name'][i]['Adset AS']
        except:
            meta_df['Ad group AS'][i] = ''
        try:
            meta_df['Ad group ST'][i] = meta_df['Ad Set Name'][i]['Adset ST']
        except:
            meta_df['Ad group ST'][i] = ''
        try:
            meta_df['Ad group DA'][i] = meta_df['Ad Set Name'][i]['Adset DA']
        except:
            meta_df['Ad group DA'][i] = ''

    for i in range(len(meta_df['Ad name'])):
        try:
            meta_df['Ad CH'][i] = meta_df['Ad name'][i]['Ad CH']
        except:
            meta_df['Ad CH'][i] = ''
        try:
            meta_df['Ad AS'][i] = meta_df['Ad name'][i]['Ad AS']
        except:
            meta_df['Ad AS'][i] = ''
    return meta_df

def revised_output(meta_revised, meta_df, file_name):
    selected_col = ['Campaign CN', 'Campaign OB', 'Campaign RT', 'Campaign CY',
                'Ad group ST', 'Ad group AG', 'Ad group AS', 'Ad group DA', 'Ad AS','Ad CH',
                'Placement', 'Platform', 'Day'
                'Reach', 'Impressions', 'Clicks (all)', 'Link clicks', 'Amount spent (TWD)',
                '3-second video plays', 'ThruPlays',
                'Post comments', 'Post engagements', 'Post reactions', 'Post shares']
    filled_col = ['Campaign name', 'Campaign Objective', 'Buying Type', 'Advertiser Currency',
                  'Adset name', 'Audience', 'Message Type', 'Adset Free Form', 'Ad Free Form', 'Campaign Type',
                  'Placement', 'Platform', 'Date'
                  'Reach', 'Impressions', 'Clicks (all)', 'Link clicks (Web Clicks)', 'Spent (TWD)',
                  '3" Video Views', '15" Video Views (ThruPlays)',
                  'Post comments', 'Post engagements', 'Post reactions', 'Post shares']

    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            meta_revised[dest_col] = meta_df[src_col]
        except:
            print(f'你是否少了 {dest_col} 欄位呢? 如果沒有，可以忽視這個訊息')
            pass

    meta_revised['Item (Summary of filter)'] = \
        meta_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                    'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                    'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    meta_revised['Region'] = 'APAC'
    meta_revised['Market'] = 'TWN'
    meta_revised['BU'] = file_name[0]
    meta_revised['Customer'] = file_name[2]
    meta_revised['Media'] = file_name[3]
    meta_revised['Date'] = meta_df['Day']

    meta_revised['Date'] = pd.to_datetime(meta_revised['Date'])
    meta_revised = meta_revised.sort_values(['Campaign name', 'Campaign Objective', 'Adset name', 'Date'], ignore_index=True)
    return meta_revised