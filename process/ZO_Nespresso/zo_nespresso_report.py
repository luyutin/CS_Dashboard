import pandas as pd
import numpy as np

def report(revised_data, revised_file_name):
    result_df = pd.DataFrame()
    revised_data['Date'] = pd.to_datetime(revised_data['Date'])

    result_df['Impressions'] = revised_data.groupby(['Media', 'Campaign name', 'Campaign Objective',\
                                                        'Adset name', 'Audience', 'Message Type', 'Buying Type', 'Ad Free Form', 'Item (Summary of filter)', 'Date'], dropna=False)['Impressions'].sum()
    result_df['Clicks'] = revised_data.groupby(['Media', 'Campaign name', 'Campaign Objective',\
                                                        'Adset name', 'Audience', 'Message Type', 'Buying Type', 'Ad Free Form', 'Item (Summary of filter)', 'Date'], dropna=False)['Clicks (all)'].sum()
    result_df['Link Clicks'] = revised_data.groupby(['Media', 'Campaign name', 'Campaign Objective',\
                                                        'Adset name', 'Audience', 'Message Type', 'Buying Type', 'Ad Free Form', 'Item (Summary of filter)', 'Date'], dropna=False)['Link clicks (Web Clicks)'].sum()
    result_df['3" Video Views'] = revised_data.groupby(['Media', 'Campaign name', 'Campaign Objective',\
                                                        'Adset name', 'Audience', 'Message Type', 'Buying Type', 'Ad Free Form', 'Item (Summary of filter)', 'Date'], dropna=False)['3" Video Views'].sum()

    result_df['Spending'] = revised_data.groupby(['Media', 'Campaign name', 'Campaign Objective',\
                                                        'Adset name', 'Audience', 'Message Type', 'Buying Type', 'Ad Free Form', 'Item (Summary of filter)', 'Date'], dropna=False)['Spent (TWD)'].sum()

    result_df['CTR (All)'] = \
        np.where(result_df['Impressions'] > 0,
                 result_df['Clicks'] / result_df['Impressions'], np.nan)

    result_df['3" VTR (View Through Rate)'] = \
        np.where(result_df['Impressions'] > 0,
                 result_df['3" Video Views'] / result_df['Impressions'], np.nan)

    result_df['CPM'] = \
        np.where(result_df['Impressions'] > 0,
                 result_df['Spending'] / result_df['Impressions']* 1000, np.nan)

    result_df = result_df.reset_index()
    return result_df
