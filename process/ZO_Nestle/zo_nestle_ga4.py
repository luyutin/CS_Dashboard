import pandas as pd
import streamlit as st

def split(df):
    my_list = df.columns
    index_of_first_english = None
    for i, item in enumerate(my_list):
        if (u'\u0041'<= item[0] <= u'\u005a') or (u'\u0061'<= item[0] <= u'\u007a'):
            index_of_first_english = i
            break

    try:
        try:
            df2 = df[['廣告活動', '廣告素材', '日期']]
        except:
            df = df.rename(columns = {'廣告內容': '廣告素材'})
            df2 = df[['廣告活動', '廣告素材', '日期']]
        df2 = pd.concat([df2, df.iloc[:, index_of_first_english:]], axis=1)
        df2 = pd.melt(df2, id_vars=['廣告活動', '廣告素材', '日期'], var_name='GA Session name', value_name='GA Session 數量')
        df = df.iloc[:, :index_of_first_english]
        df2 = pd.concat([df, df2], axis = 0)
        df2['GA Session Type'] = df2['GA Session name'].str.split('_', expand=True)[1].str.split('(', expand=True)[0]
        df2 = df2.dropna(subset=['GA Session name'])

    except:
        df2 = df
    camp = df2['廣告活動'].str.split('_', expand=True)
    df2.insert(0, 'Campaign name', camp[0])
    df2.insert(0, 'Product', camp[[4, 5, 6]].fillna('').apply("_".join, axis=1))
    df2.insert(0, 'Campaign Objective', camp[[7, 8]].fillna('').apply("_".join, axis=1))

    def merge_columns(row):
        # 将每个值转换为字符串，如果是空值则替换为空字符串
        values = [str(val) if pd.notnull(val) else '' for val in row]
        # 如果最后一个值是空的，则不要添加连接符号
        while values and values[-1] == '':
            values.pop()
        # 使用 '-' 连接字符串
        return '-'.join(values)

    df2.insert(0, 'Campaign Free Form', camp.iloc[:, 11:].apply(merge_columns, axis=1))
    df2['廣告素材'] = df2['廣告素材'].str.replace('_', '-')
    return df2

def revised_output(revised, df, file_name):
    selected_col = ['Campaign name', '廣告素材', '日期', '使用者',  '總人數', '新使用者', '工作階段', '跳出率',
                    'GA Session name', 'GA Session Type', 'GA Session 數量', '平均單次工作階段參與時間', '平均工作階段時間長度',
                    'Campaign Objective', 'Campaign Free Form']
    filled_col = ['Campaign name', 'Message Type', 'Date', 'User number', 'Total PPL', 'New user', 'Working session', 'Bounce Rate',
                  'GA Session name', 'GA Session Type', 'GA Session Qty', 'Avg engagement time per session', 'Avg Working session time',
                  'Campaign Objective', 'Campaign Free Form']

    errors = []
    for src_col, dest_col in zip(selected_col, filled_col):
        try:
            revised[dest_col] = df[src_col]
        except:
            if dest_col == '廣告內容':
                revised['廣告素材'] = df[src_col]
            errors.append(src_col)
    st.error(f"你是否少了「 {'、'.join(errors)} 」欄位呢? \n 如果沒有，可以忽視這個訊息")

    revised['Item (Summary of filter)'] = \
        revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    revised['Region'] = 'APAC'
    revised['Market'] = 'TWN'
    revised['BU'] = file_name[0]
    revised['Customer'] = file_name[2]
    revised['Media'] = file_name[3]

    revised['Date'] = pd.to_datetime(revised['Date'], format='%Y%m%d')
    revised = revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return revised