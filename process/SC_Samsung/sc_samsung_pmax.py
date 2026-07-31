import pandas as pd

def split(google_df):
    google_df.columns = google_df.iloc[1]
    google_df = google_df.iloc[2:]
    google_df = google_df.reset_index(drop=True)

    for i in range(len(google_df['帳戶名稱'])):
        dict_acc = dict()
        try:
            values = google_df['帳戶名稱'][i].split('_')
            for attr in values:
                dict_acc['帳戶名稱 ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        google_df['帳戶名稱'][i] = dict_acc

    for i in range(len(google_df['廣告活動'])):
        dict_cam = dict()
        try:
            values = google_df['廣告活動'][i].split('_')
            for attr in values:
                dict_cam['Campaign ' + attr.split('~')[0]] = attr.split('~')[1]
        except:
            pass
        google_df['廣告活動'][i] = dict_cam
    return google_df

def insert_col(google_df):
    google_df.insert(0, 'Account name', 0)
    google_df.insert(0, 'Campaign CN', 0)
    google_df.insert(0, 'Campaign OB', 0)
    google_df.insert(0, 'Ad group AG', 0)
    google_df.insert(0, 'Ad group SA', 0)
    google_df.insert(0, 'Ad group FF', 0)
    google_df.insert(0, 'Ad group MD', 0)
    google_df.insert(0, 'Ad FF', 0)

    for i in range(len(google_df['帳戶名稱'])):
        try:
            google_df['Account name'][i] = google_df['帳戶名稱'][i]['帳戶名稱 FF']
        except:
            google_df['Account name'][i] = ''

    for i in range(len(google_df['廣告活動'])):
        try:
            google_df['Campaign CN'][i] = google_df['廣告活動'][i]['Campaign CN']
        except:
            google_df['Campaign CN'][i] = ''
        try:
            google_df['Campaign OB'][i] = google_df['廣告活動'][i]['Campaign OB']
        except:
            google_df['Campaign OB'][i] = ''

    return google_df

def revised_output(google_revised, google_df, file_name):
    google_revised['Advertiser Currency'] = google_df['貨幣代碼']

    google_revised['Account name'] = google_df['Account name']
    google_revised['Campaign Type'] = google_df['廣告活動類型']
    google_revised['Campaign name'] = google_df['Campaign CN']
    google_revised['Campaign Objective'] = google_df['Campaign OB']

    google_revised['Item (Summary of filter)'] = \
        google_revised['Account name'].astype(str) + "_" + google_revised['Campaign Type'].astype(str) + "_" \
        + google_revised['Campaign name'].astype(str) + "_" + google_revised['Campaign Objective'].astype(str)

    google_revised['Impressions'] = google_df['曝光']
    google_revised['Clicks (all)'] = google_df['點擊']
    google_revised['Spent (TWD)'] = google_df['費用']
    google_revised['MV>5'] = google_df['MV>5']
    google_revised['Sales Engagement'] = google_df['SE']


    google_revised['Region'] = 'APAC'
    google_revised['Market'] = 'TWN'
    google_revised['BU'] = file_name[0]
    google_revised['Customer'] = file_name[1]
    google_revised['Media'] = file_name[2]
    google_revised['Date'] = google_df['日期']

    google_revised['Spent (含佣未稅)'] = google_revised['Spent (TWD)'] * 1.1325

    google_revised['CTR (All)'] = google_df['點閱率']
    google_revised['CPC (All)'] = google_df['平均單次點擊出價']

    google_revised['CPV (MV>5)'] = google_df['CPV']
    google_revised['CPE (Sales)'] = google_df['CPE']

    try:
        google_revised = google_revised.sort_values(['Campaign Type', 'Campaign name', 'Adset name', 'Audience', 'Adset Free Form'], ignore_index=True)
    except:
        google_revised = google_revised.sort_values(['Campaign Type', 'Campaign name'], ignore_index=True)
    return google_revised