import pandas as pd
import streamlit as st

def split(sem_df):
    sem_df.columns = sem_df.iloc[1]
    sem_df = sem_df.iloc[2:]

    first_blank_index = sem_df['關鍵字狀態'].isna().idxmax()
    # 如果整個欄位都沒有空值，則 idxmax 會返回第一個索引，因此需要額外檢查
    if pd.isna(sem_df['關鍵字狀態'][first_blank_index]):
        sem_df = sem_df.loc[:first_blank_index - 1]
    else:
        pass
    sem_df['Campaign Objective'] = sem_df['廣告活動'].str.split('_', expand=True)[8] + sem_df['廣告活動'].str.split('_', expand=True)[9]
    sem_df['Campaign Free Form'] = sem_df['廣告活動'].str.split('_', expand=True)[11]
    sem_df['Campaign name'] = sem_df['廣告活動'].str.split('_', expand=True)[0]
    return sem_df

def revised_output(sem_revised, sem_df, file_name):
    selected_col = ['日期', '曝光', '點擊', '費用', '轉換', '關鍵字狀態', '品質分數',
                    '關鍵字', '廣告群組', 'Campaign Objective', 'Campaign name', 'Campaign Free Form']

    filled_col = ['Date', 'Impressions', 'Clicks (all)', 'Spent (TWD)', 'Conversions', 'SEM Status', 'Quality Score',
                  'Message Type', 'Adset name', 'Campaign Objective', 'Campaign name', 'Campaign Free Form']

    errors = []
    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            sem_revised[dest_col] = sem_df[src_col]
        except:
            if dest_col == '廣告內容':
                sem_revised['廣告素材'] = sem_df[src_col]
            errors.append(src_col)
    st.error(f"你是否少了「 {'、'.join(errors)} 」欄位呢? \n 如果沒有，可以忽視這個訊息")

    sem_revised['Item (Summary of filter)'] = \
        sem_revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                     'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                     'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    sem_revised['Region'] = 'APAC'
    sem_revised['Market'] = 'TWN'
    sem_revised['BU'] = file_name[0]
    sem_revised['Customer'] = file_name[2]
    sem_revised['Media'] = file_name[3]
    sem_revised['Campaign Type'] = '搜尋'

    sem_revised['Date'] = pd.to_datetime(sem_revised['Date'])
    sem_revised = sem_revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return sem_revised