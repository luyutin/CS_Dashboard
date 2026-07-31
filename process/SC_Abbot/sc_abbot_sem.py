import pandas as pd
import numpy as np

def split(sem_df):
    sem_df.columns = sem_df.iloc[1,:]
    sem_df = sem_df.iloc[2:]

    sem_df['Campaign Type'] = sem_df['廣告活動'].str.split('_', expand=True)[8].str.split('-', expand=True)[3]
    sem_df['Campaign name'] = sem_df['廣告活動'].str.split('_', expand=True)[8].str.split('-', expand=True)[7]
    sem_df['Adset name'] = sem_df['廣告群組'].str.split('_', expand=True)[3]

    adgroup_mapping = {
        "[PDS BRAND]": "小安素品牌字",
        "[COMP-CHILDREN PROTISON]": "補體素",
        "[COMP-HEALTHSCIENCE]": "佳膳",
        "[COMP-MEADJOHNSON]": "美強生",
        "[COMP-QUAKER]": "桂格",
        "[COMP-S26]": "S26",
        "[BOOST IMMUNITY]": "小孩免疫力增加需求",
        "[DEMAND- STIMULATE APPETITE]": "消費者需求-促進食慾",
        "[DEMAND-GAIN WEIGHT]": "消費者需求-長胖",
        "[DEMAND-GROW UP]": "消費者需求-成長",
        "[GROW PROTECTION]": "保護力增加需求",
        "[NUTRITION-ARGININE]": "營養補充需求-精胺酸",
        "[NUTRITION-CA+]": "營養補充需求-鈣",
        "[NUTRITION-DHA]": "營養補充需求-DHA",
        "[NUTRITION-PROBIOTICS]": "營養補充需求-益生菌",
        "[NUTRITION-PROTEIN]": "營養補充需求-蛋白質",
        "[NUTRITION-VITAMIN]": "營養補充需求-維他命",
        "[NUTRITIONAL SUPPLEMENT]": "營養補充需求",
        "[CHILDREN MILK]": "奶粉_兒童奶粉",
        "[GROW UP MILK]": "奶粉_成長奶粉",
        "[MILK RELATED]": "兒童_牛奶相關",
        "[MILK TRIAL]": "奶粉_試用相關字",
        "[TODDLER MILK]": "奶粉_幼兒奶粉",
        "[PND-KIDS DIET]": "kids diet",
        "[PND-SOLID FOOD]": "solid food",
        "[SALES CHANNEL- COSTCO]": "Costco",
        "[SALES CHANNEL- DRUGSTORE]": "drugstore",
        "[SALES CHANNEL- PXMART]": "Pxmart",
        "[BAD APPETITE]": "症狀_食慾不佳",
        "[PICKY EATER]": "症狀_挑食",
        "[POOR RESISTANCE]": "症狀_抵抗力差",
        "[THIN AND SMALL]": "症狀_瘦小"
    }
    sem_df['Adset name'] = sem_df['Adset name'].map(adgroup_mapping)
    return sem_df

def revised_output(sem_revised, sem_df, file_name):
    selected_col = ['Campaign name', 'Campaign Type', 'Adset name',
                    '日期', '貨幣代碼', '曝光', '點擊', '點閱率',
                    '平均單次點擊出價', '費用', '轉換', '單次轉換費用', '轉換率']

    filled_col = ['Campaign name', 'Campaign Type', 'Adset name',
                  'Date', 'Advertiser Currency', 'Impressions', 'Clicks (all)', 'CTR (All)',
                  'CPC (All)', 'Spent (TWD)', 'Conversions', 'CPA', 'CVR']

    sem_revised[filled_col] = sem_df[selected_col]
    sem_revised['Item (Summary of filter)'] = \
        sem_revised['Campaign Type'].astype(str) + "_" + sem_revised['Campaign name'].astype(str) + "_" + \
        sem_revised['Adset name'].astype(str)

    sem_revised['Region'] = 'APAC'
    sem_revised['Market'] = 'TWN'
    sem_revised['BU'] = file_name[0]
    sem_revised['Customer'] = file_name[1]
    sem_revised['Media'] = file_name[2]

    sem_revised = sem_revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return sem_revised