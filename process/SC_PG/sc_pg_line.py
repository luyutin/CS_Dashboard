import pandas as pd
import numpy as np

def split(line_df):
    for i in range(len(line_df['Campaign name'])):
        dict_cam = dict()
        try:
            values = line_df['Campaign name'][i].split('_')
            for attr in values:
                dict_cam['Campaign ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        line_df['Campaign name'][i] = dict_cam

    for i in range(len(line_df['Ad group name'])):
        dict_adset = dict()
        try:
            values = line_df['Ad group name'][i].split('_')
            for attr in values:
                dict_adset['Adset ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        line_df['Ad group name'][i] = dict_adset
    return line_df

def insert_col(line_df):
    line_df.insert(0, 'Campaign CN', 0)
    line_df.insert(0, 'Campaign OB', 0)
    line_df.insert(0, 'Campaign RT', 0)
    line_df.insert(0, 'Campaign CY', 0)

    line_df.insert(0, 'Ad group ST', 0)
    line_df.insert(0, 'Ad group PD', 0)

    for i in range(len(line_df['Campaign name'])):
        try:
            line_df['Campaign CN'][i] = line_df['Campaign name'][i]['Campaign CN']
        except:
            line_df['Campaign CN'][i] = ''
        try:
            line_df['Campaign OB'][i] = line_df['Campaign name'][i]['Campaign OB']
        except:
            line_df['Campaign OB'][i] = ''
        try:
            line_df['Campaign RT'][i] = line_df['Campaign name'][i]['Campaign RT']
        except:
            line_df['Campaign RT'][i] = ''
        try:
            line_df['Campaign CY'][i] = line_df['Campaign name'][i]['Campaign CY']
        except:
            line_df['Campaign CY'][i] = ''

    for i in range(len(line_df['Ad group name'])):
        try:
            line_df['Ad group ST'][i] = line_df['Ad group name'][i]['Adset ST']
        except:
            line_df['Ad group ST'][i] = ''
        try:
            line_df['Ad group PD'][i] = line_df['Ad group name'][i]['Adset PD']
        except:
            line_df['Ad group PD'][i] = ''

    return line_df

def revised_output(line_revised, line_df, file_name):

    selected_col = ['Ad group PD', 'Ad group ST', 'Campaign CY', 'Campaign RT', 'Campaign OB', 'Campaign CN',
                'Ad name', 'Title', 'Ad account name',
                'Day', 'Impressions', 'Clicks', 'CV (conversions)', 'Cost',
                'Video (viewed for at least three seconds)',
                'Video (25% watched)','Video (50% watched)', 'Video (75% watched)','Video (100% watched)',
                'Add-to-cart','Purchase']

    filled_col = ['Audience', 'Adset name', 'Advertiser Currency', 'Buying Type', 'Campaign Objective', 'Campaign name',
                'Message Type', 'Ad Free Form', 'Account name',
                'Date', 'Impressions', 'Clicks (all)', 'Conversion Value', 'Spent (TWD)',
                '3" Video Views',
                'Video played to 25%', 'Video played to 50%', 'Video played to 75%', 'Video played to 100%',
                'Adds to cart', 'Purchases']

    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            line_revised[dest_col] = line_df[src_col]
        except:
            print(f'你是否少了 {dest_col} 欄位呢? 如果沒有，可以忽視這個訊息')
            pass

    YT_revised['Item (Summary of filter)'] = \
        YT_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                    'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                    'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)


    line_revised['Region'] = 'APAC'
    line_revised['Market'] = 'TWN'
    line_revised['BU'] = file_name[0]
    line_revised['Customer'] = file_name[2]
    line_revised['Media'] = file_name[3]

    line_revised['Date'] = pd.to_datetime(line_revised['Date'])
    line_revised = line_revised.sort_values(['Campaign name', 'Campaign Objective', 'Adset name', 'Date'], ignore_index=True)
    return line_revised