import pandas as pd

def report(revised_data, revised_file_name):
    # 'Campaign Objective', 'Adset name', 'Audience', 'Adset Free Form'
    result_df = pd.DataFrame()

    result_df['Delivered Impression'] = \
        revised_data.groupby(['Media', 'Media Budget', 'W/AC', 'Budget Progress', \
                              'Item (Summary of filter)'], dropna=False)['Impressions'].sum()

    result_df['Delivered Clicks'] = \
        revised_data.groupby(['Media', 'Media Budget', 'W/AC', 'Budget Progress', \
                              'Item (Summary of filter)'], dropna=False)['Clicks (all)'].sum()

    result_df['Spent'] = \
        revised_data.groupby(['Media', 'Media Budget', 'W/AC', 'Budget Progress', \
                              'Item (Summary of filter)'], dropna=False)['Spent (TWD)'].sum()

    result_df['Spent (含佣未稅)'] = result_df['Spent']*1.1325

    result_df['Web Clicks'] = \
        revised_data.groupby(['Media', 'Media Budget', 'W/AC', 'Budget Progress', \
                              'Item (Summary of filter)'], dropna=False)['Link clicks (Web Clicks)'].sum()

    def divide_func_CPC(row):
        if row['Delivered Clicks'] > 0:
            return row['Spent'] / row['Delivered Clicks']
        return
    result_df['CPC'] = result_df.apply(divide_func_CPC, axis = 1)

    def divide_func_CPM(row):
        if row['Delivered Impression'] > 0:
            return row['Spent'] / row['Delivered Impression']*1000
        return
    result_df['CPM'] = result_df.apply(divide_func_CPM, axis = 1)

    def divide_func_CTR(row):
        if row['Delivered Impression'] > 0:
            return row['Delivered Clicks'] / row['Delivered Impression']
        return
    result_df['CTR'] = result_df.apply(divide_func_CTR, axis = 1)

    result_df = result_df.reset_index()

    revised_data['Date'] = pd.to_datetime(revised_data['Date'])
    result_df['Start'] = \
        revised_data.groupby(['Media', 'Media Budget', 'W/AC', 'Budget Progress', \
                              'Item (Summary of filter)'], dropna=False)['Date'].min().values
    result_df['End'] = \
        revised_data.groupby(['Media', 'Media Budget', 'W/AC', 'Budget Progress', \
                              'Item (Summary of filter)'], dropna=False)['Date'].max().values
    result_df['Start'] = result_df['Start'].dt.strftime("%Y/%m/%d")
    result_df['End'] = result_df['End'].dt.strftime("%Y/%m/%d")
    result_df.insert(0, 'Duration', result_df['Start'].astype(str) + "~" + result_df['End'].astype(str))
    return result_df.iloc[:, :-2]