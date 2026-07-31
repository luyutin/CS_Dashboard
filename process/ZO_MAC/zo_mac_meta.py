import pandas as pd
import numpy as np

def split(meta_df):
    meta_df['Creative'] = meta_df['Ad name'].str.split('_', expand=True)[2] + '_' + meta_df['Ad name'].str.split('_', expand=True)[3]
    meta_df[['class', 'period', 'FF', 'budget']] = meta_df['Ad Set Name'].str.split('_', expand=True)
    meta_df[['Position', 'code', 'Objective', 'TA', 'temp']] = meta_df['FF'].str.split('#', expand=True)

    mask = meta_df['TA'] == 'All6'
    meta_df.loc[mask, ['TA', 'temp']] = meta_df.loc[mask, ['temp', 'TA']].values

    mask = meta_df['code'] == 'Traffic(LPV)'
    meta_df.loc[mask, ['code', 'Objective']] = meta_df.loc[mask, ['Objective', 'code']].values

    # meta_df['Objective'] = meta_df['Objective'] + '_' + meta_df['code']
    KOL = meta_df['FF'].apply(lambda x: 'KOL' if 'KOL' in x else '')
    RF = meta_df['class'].apply(lambda x: '[R&F]' if '[R&F]' in x else '')
    meta_df['Type'] = pd.Series(np.where(KOL == '', RF, KOL))

    return meta_df

def revised_output(meta_revised, meta_df, file_name):
    selected_col = ['Day', 'Impressions', 'Clicks (all)', 'Link clicks', '3-second video plays', 'ThruPlays',
              'Amount spent (TWD)', 'Post reactions', 'Post comments', 'Post shares',
              'Post engagements', 'CTR (all)', 'CTR (link click-through rate)',
              'CPM (cost per 1,000 impressions)', 'CPC (All)',
              'CPC (cost per link click)', 'Cost per 3-second video play',
              'Cost per ThruPlay', 'Adds to cart', 'Purchases',
              'Purchases conversion value', 'Purchase ROAS (return on ad spend)',
              'Creative', 'period', 'Position', 'Objective', 'TA', 'Type']
    filled_col = ['Date', 'Impressions', 'Clicks (all)', 'Link clicks', '3-second video plays', 'ThruPlays',
              'Amount spent (TWD)', 'Post reactions', 'Post comments', 'Post shares',
              'Post engagements', 'CTR (all)', 'CTR (link click-through rate)',
              'CPM (cost per 1,000 impressions)', 'CPC (All)',
              'CPC (cost per link click)', 'Cost per 3-second video play',
              'Cost per ThruPlay', 'Adds to cart', 'Purchases',
              'Purchases conversion value', 'Purchase ROAS (return on ad spend)',
              'Message Type', 'Duration', 'Campaign name', 'Campaign Objective', 'Audience', 'Campaign Type']

    meta_revised[filled_col] = meta_df[selected_col]
    meta_revised['Item (Summary of filter)'] = \
        meta_revised['Campaign Type'].astype(str) + "_" + meta_revised['Campaign name'].astype(str) + "_" + \
        meta_revised['Campaign Objective'].astype(str) + "_" + meta_revised['Audience'].astype(str)

    meta_revised['Region'] = 'APAC'
    meta_revised['Market'] = 'TWN'
    meta_revised['BU'] = file_name[0]
    meta_revised['Customer'] = file_name[1]
    meta_revised['Media'] = file_name[2]

    meta_revised = meta_revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return meta_revised

def report(revised_data, revised_file_name):
    result_df = pd.DataFrame()
    result_df['Impressions'] = revised_data.groupby(['Media', 'Campaign Type', 'Campaign name', 'Campaign Objective',\
                                                      'Audience', 'Message Type', 'Item (Summary of filter)', 'Duration'], dropna=False)['Impressions'].sum()
    result_df['Clicks'] = revised_data.groupby(['Media', 'Campaign Type', 'Campaign name', 'Campaign Objective',\
                                                 'Audience', 'Message Type', 'Item (Summary of filter)', 'Duration'], dropna=False)['Clicks (all)'].sum()

    def divide_func_CTR(row):
        if row['Impressions'] > 0:
            return row['Clicks'] / row['Impressions']
        return
    result_df['CTR'] = result_df.apply(divide_func_CTR, axis = 1)
    result_df['Cost'] = revised_data.groupby(['Media', 'Campaign Type', 'Campaign name', 'Campaign Objective',\
                                               'Audience', 'Message Type', 'Item (Summary of filter)', 'Duration'], dropna=False)['Amount spent (TWD)'].sum()
    def divide_func_CPM(row):
        if row['Impressions'] > 0:
            return row['Cost'] / row['Impressions'] * 1000
        return
    result_df['CPM'] = result_df.apply(divide_func_CPM, axis = 1)

    result_df = result_df.reset_index()
    result_df.insert(1, 'Data Start & End', revised_file_name[4][:-5])
    return result_df