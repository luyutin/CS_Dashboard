import pandas as pd
import streamlit as st

def split(YT_df):
    YT_df_split = YT_df['廣告群組'].str.split('_', expand=True)
    YT_df['Campaign name'] = YT_df_split.iloc[:, 0]
    YT_df['Campaign Objective'] = YT_df_split.iloc[:, 9].astype(str) + "_" + YT_df_split.iloc[:, 10].astype(str)
    YT_df['Buying Type'] = YT_df_split.iloc[:, 14]
    YT_df['Audience'] = YT_df_split.iloc[:, 18].astype(str) + "_" + YT_df_split.iloc[:, 19].astype(str)
    YT_df['Adset name'] = YT_df_split.iloc[:, 1]
    YT_df_split2 = YT_df['廣告標籤'].str.split('_', expand=True)
    YT_df['Ad Free Form'] = YT_df_split2.iloc[:, 1:].apply(lambda x: '_'.join(x.astype(str)), axis=1)
    return YT_df

def revised_output(YT_revised, YT_df, file_name):
    selected_col = ['日期', '曝光', '觀看次數', '收視率', '點擊', '點閱率',
                    '平均單次收視出價', '平均千次曝光出價', '費用', '單次轉換費用', '轉換率', '所有轉換',
                    '影片播放進度：25%', '影片播放進度：50%', '影片播放進度：75%', '影片播放進度：100%',
                    'Campaign name', 'Campaign Objective', 'Buying Type', 'Audience', 'Adset name',
                    'Ad Free Form']
    filled_col = ['Date', 'Impressions', '3" Video Views', 'View rate', 'Clicks (all)', 'CTR (All)',
                  'CPV', 'CPM', 'Spent (TWD)', 'CPA', 'CVR', 'Conversions',
                  'Video played to 25%', 'Video played to 50%', 'Video played to 75%', 'Video played to 100%',
                  'Campaign name', 'Campaign Objective', 'Buying Type', 'Audience', 'Adset name',
                  'Ad Free Form']

    errors = []
    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            YT_revised[dest_col] = YT_df[src_col]
        except:
            if dest_col == '廣告內容':
                YT_revised['廣告素材'] = YT_df[src_col]
            errors.append(src_col)
    st.error(f"你是否少了「 {'、'.join(errors)} 」欄位呢? \n 如果沒有，可以忽視這個訊息")

    YT_revised['Item (Summary of filter)'] = \
        YT_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                    'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                    'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    YT_revised['Region'] = 'APAC'
    YT_revised['Market'] = 'TWN'
    YT_revised['BU'] = file_name[0]
    YT_revised['Customer'] = file_name[2]
    YT_revised['Media'] = file_name[3]

    YT_revised['Date'] = pd.to_datetime(YT_revised['Date'])
    YT_revised = YT_revised.sort_values(['Media', 'Message Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return YT_revised