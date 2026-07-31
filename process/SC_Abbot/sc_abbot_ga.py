import pandas as pd
import numpy as np

def split(ga_df):
    ga_df.columns = ga_df.iloc[6, :]
    ga_df = ga_df.iloc[7:, :]

    ga_df['media'] = ga_df['來源/媒介'].str.split(' / ', expand=True)[0]
    ga_df['buying type'] = ga_df['來源/媒介'].str.split(' / ', expand=True)[1]
    ga_df['Conversions'] = ga_df.iloc[:, 6]
    ga_df["日期"] = pd.to_datetime(ga_df["日期"], format="%Y%m%d")
    return ga_df

def revised_output(ga_revised, ga_df, file_name):
    selected_col = ['廣告活動', 'buying type', '工作階段手動廣告素材', 'media', 'Google Ads 廣告群組名稱',
                    '日期', 'Conversions']

    filled_col = ['Campaign name', 'Buying Type', 'Adset name', 'Media', 'Ad Free Form',
                  'Date', 'Conversions']

    ga_revised[filled_col] = ga_df[selected_col]
    ga_revised['Item (Summary of filter)'] = \
        ga_revised['Media'].astype(str) + "_" + ga_revised['Buying Type'].astype(str) + "_" + \
        ga_revised['Campaign name'].astype(str) +  "_" + ga_revised['Adset name'].astype(str)

    ga_revised['Region'] = 'APAC'
    ga_revised['Market'] = 'TWN'
    ga_revised['BU'] = file_name[0]
    ga_revised['Customer'] = file_name[1]

    ga_revised = ga_revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return ga_revised