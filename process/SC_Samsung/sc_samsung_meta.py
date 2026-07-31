import pandas as pd
import streamlit as st

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
    meta_df.insert(0, 'Campaign PR', 0)
    meta_df.insert(0, 'Ad group AG', 0)
    meta_df.insert(0, 'Ad group SA', 0)
    meta_df.insert(0, 'Ad group FF', 0)
    meta_df.insert(0, 'Ad group MD', 0)
    meta_df.insert(0, 'Ad group CH', 0)
    meta_df.insert(0, 'Ad group PB', 0)
    meta_df.insert(0, 'Ad group RT', 0)
    meta_df.insert(0, 'Ad MG', 0)
    meta_df.insert(0, 'Ad FF', 0)

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
            meta_df['Campaign PR'][i] = meta_df['Campaign name'][i]['Campaign PR']
        except:
            meta_df['Campaign PR'][i] = ''

    for i in range(len(meta_df['Ad Set Name'])):
        try:
            meta_df['Ad group AG'][i] = meta_df['Ad Set Name'][i]['Adset AG']
        except:
            meta_df['Ad group AG'][i] = ''
        try:
            meta_df['Ad group SA'][i] = meta_df['Ad Set Name'][i]['Adset SA']
        except:
            meta_df['Ad group SA'][i] = ''
        try:
            meta_df['Ad group FF'][i] = meta_df['Ad Set Name'][i]['Adset FF']
        except:
            meta_df['Ad group FF'][i] = ''
        try:
            meta_df['Ad group MD'][i] = meta_df['Ad Set Name'][i]['Adset MD']
        except:
            meta_df['Ad group MD'][i] = ''
        try:
            meta_df['Ad group CH'][i] = meta_df['Ad Set Name'][i]['Adset CH']
        except:
            meta_df['Ad group CH'][i] = ''
        try:
            meta_df['Ad group PB'][i] = meta_df['Ad Set Name'][i]['Adset PB']
        except:
            meta_df['Ad group PB'][i] = ''
        try:
            meta_df['Ad group RT'][i] = meta_df['Ad Set Name'][i]['Adset RT']
        except:
            meta_df['Ad group RT'][i] = ''

    for i in range(len(meta_df['Ad name'])):
        try:
            meta_df['Ad MG'][i] = meta_df['Ad name'][i]['Ad MG']
        except:
            meta_df['Ad MG'][i] = ''
        try:
            meta_df['Ad FF'][i] = meta_df['Ad name'][i]['Ad FF']
        except:
            meta_df['Ad FF'][i] = ''
    return meta_df

def revised_output(meta_revised, meta_df, file_name):
    selected_col = ['Reporting starts', 'Impressions', 'Clicks (all)', 'Reach', 'Link clicks', '3-second video plays', 'ThruPlays',
                    'Amount spent (TWD)', 'Post reactions', 'Post comments', 'Post shares', 'Post engagements',
                    'Adds to cart', 'Purchases', 'Purchases conversion value', 'Purchase ROAS (return on ad spend)',
                    'Ad MG', 'Ad FF', 'Ad group SA', 'Ad group AG', 'Ad group MD', 'Campaign PR', 'Ad group CH', 'Ad group PB',
                    'Campaign OB', 'Campaign CN', 'Ad group FF', 'Ad group RT',
                    'Page Likes or followers']

    filled_col = ['Date', 'Impressions', 'Clicks (all)', 'Reach', 'Link clicks (Web Clicks)', '3" Video Views', '15" Video Views (ThruPlays)',
                  'Spent (TWD)', 'Post reactions', 'Post comments', 'Post shares', 'Post engagements',
                  'Adds to cart', 'Purchases', 'Conversion Value', 'Purchase ROAS',
                  'Message Type', 'Ad Free Form', 'Audience', 'Adset name', 'Adset MD', 'Product',  'Channel', 'InName Site',
                  'Campaign Objective', 'Campaign name', 'Adset Free Form', 'Buying Type',
                  'Page Likes or followers']

    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            meta_revised[dest_col] = meta_df[src_col]
        except:
            st.error(f'你是否少了 {dest_col} 欄位呢? 如果沒有，可以忽視這個訊息')
            pass

    meta_revised['Item (Summary of filter)'] = \
        meta_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                      'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                      'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    meta_revised['Region'] = 'APAC'
    meta_revised['Market'] = 'TWN'
    meta_revised['BU'] = file_name[0]
    meta_revised['Customer'] = file_name[1]
    meta_revised['Media'] = file_name[2]

    meta_revised['Date'] = pd.to_datetime(meta_revised['Date'])
    meta_revised = meta_revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return meta_revised