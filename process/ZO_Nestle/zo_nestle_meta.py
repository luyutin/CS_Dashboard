import pandas as pd
import streamlit as st
from process.utils import ask_wrong, meta_cn2en

def split2(df):
    if 'Reporting starts' not in df.columns:
        df = meta_cn2en(df)

    adname = df['Ad name'].str.split('_', expand=True)
    df['Campaign Type'] = adname[1]
    df['Ad Free Form'] = adname[5]
    df['Message Type'] = adname.iloc[:, 9:].fillna('').apply("_".join, axis=1)

    adsetname = df['Ad Set Name'].str.split('_', expand=True)
    df['Audience'] = adsetname[[1, 2]].apply("_".join, axis=1)
    #df['Audience'] = adsetname[1] + adsetname[2]
    df['Buying Type'] = adsetname[[3, 4]].apply("_".join, axis=1)
    df['Adset name'] = adsetname.iloc[:, 5:].fillna('').apply("_".join, axis=1)

    campaign = df['Campaign name'].str.split('_', expand=True)
    df['Product name'] = campaign[[4, 5, 6]].fillna('').apply("_".join, axis=1)
    df['Campaign Objective'] = campaign[[7, 8]].fillna('').apply("_".join, axis=1)
    df['Campaign Free Form'] = campaign.iloc[:, 9:].fillna('').apply("_".join, axis=1)
    df['Campaign name'] = campaign[0]
    return df

def split(df):
    if 'Reporting starts' not in df.columns:
        df = meta_cn2en(df)
    # ------------------------------------------------------------------
    # 2️⃣ 依索引逐欄指定（可照自己需求增刪）── Campaign 層
    #    索引位置對應：                0                1   2    3    4    5     6    7      8        9
    #    SBUX-CPG-NC003865 | TW | CFEE | STBK | STB | ABEY | NA | CON |  FND | 20250506-0511抹茶白雪Purchase
    # ------------------------------------------------------------------
    campaign = df["Campaign name"].str.split('_', expand=True)
    df["Campaign name"]      = campaign[0]   # 含 Brand-BU-ID；要再細分可再 .str.split('-')
    df["Market"]             = campaign[1]   # TW
    df["Category"]           = campaign[2]   # CFEE
    df["Master Brand"]       = campaign[3]   # STBK
    df["Product name"]       = campaign[4]   # STB
    df["Audience123"]        = campaign[5]   # ABEY
    df["Placement"]          = campaign[6]   # NA
    df["Campaign Objective"] = campaign[7]   # CON / COV / TRAF ...
    df["Funnel Stage"]       = campaign[8]   # FND / CON / RET ...
    df["Campaign Free Form"] = campaign[9]   # 20250506-0511抹茶白雪Purchase

    # ------------------------------------------------------------------
    # 3️⃣ Ad Set 層（範例：索引 0~6）-----------------------------------
    #    SBUX-CPG-NC003865 | 3RD | NA | OA | CPC | Multi | 25-54-SBX
    # ------------------------------------------------------------------
    adset = df["Ad Set Name"].str.split('_', expand=True)
    df["AS_CampaignID"]      = adset[0]   # Trace back to Campaign
    df["AS_Source"]          = adset[1]   # 1ST / 3RD / RTR ...（資料來源標籤）
    df["AS_Placement"]       = adset[2]   # NA / FB / IG / Audience Network...
    df["AS_Optimization"]    = adset[3]   # OA / LV / ATC ...
    df["Buying Type"]        = adset[4]   # CPC / CPM / oCPM ...
    df["AS_Format"]          = adset[5]   # Single / Multi / DPA ...
    df["Audience"]           = adset[6]   # 25-54-SBX (年齡＋品牌興趣)

    # ------------------------------------------------------------------
    # 4️⃣ Ad 層（範例：索引 0~12，可依實際長度調整）--------------------
    #    0SBUX-CPG-NC003865 | 1Image | 2LCL | 3N | 4na | 51:1 | 6EP | 7ZH | 8NA | 9NA | 10[NA] | 110505-0511 | 12星巴克經典風味...
    # ------------------------------------------------------------------
    ad = df["Ad name"].str.split('_', expand=True)
    df["AD_CampaignID"]        = ad[0]
    df["Campaign Type"]        = ad[1]
    df["Placement Tag"]        = ad[2]
    df["Dynamic Flag"]         = ad[3]
    df["Language Placeholder"] = ad[4]
    df["Creative Size"]        = ad[5]
    df["Copy Variant"]         = ad[6]
    df["Language"]             = ad[7]
    df["CTA"]                  = ad[8]
    df["Extra Slot"]           = ad[9]
    df["Personalization"]      = ad[10]
    df["Message Type"]         = ad.iloc[:, 11:].fillna('').apply("_".join, axis=1)
    return df

def revised_output(revised, df, file_name):
    selected_col = ['Reporting starts', 'Impressions', 'Clicks (all)', 'Reach', 'Link clicks', '3-second video', 'ThruPlays',
                    'Amount spent (TWD)', 'Post reactions', 'Post comments', 'Post shares', 'Post engagements',
                    'Adds to cart', 'Purchases', 'Purchases conversion value', 'Purchase ROAS (return on ad spend)',
                    "Campaign name", "Product name", "Placement","Campaign Objective","Campaign Free Form",
                    "Buying Type", "Audience", "Campaign Type", "Creative Size", "Message Type"]

    filled_col = ['Date', 'Impressions', 'Clicks (all)', 'Reach', 'Link clicks (Web Clicks)', '3" Video Views', '15" Video Views (ThruPlays)',
                  'Spent (TWD)', 'Post reactions', 'Post comments', 'Post shares', 'Post engagements',
                  'Adds to cart', 'Purchases', 'Purchases conversion value', 'Purchase ROAS',
                  "Campaign name", "Product", "Placement","Campaign Objective", "Campaign Free Form",
                  "Buying Type", "Audience", "Campaign Type", "Ad Free Form", "Message Type"]
    ask_wrong(selected_col, filled_col, revised, df)

    revised['Item (Summary of filter)'] = \
        revised[['Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form',
                 'Adset name',  'Audience', 'Adset Free Form', 'Message Type', 'Campaign Type', 'Buying Type',
                 'Placement', 'SEM Status', 'Working session']].astype(str).apply("_".join, axis=1)

    revised['Region'] = 'APAC'
    revised['Market'] = 'TWN'
    revised['BU'] = file_name[0]
    revised['Customer'] = file_name[2]
    revised['Media'] = file_name[3]

    revised['Date'] = pd.to_datetime(revised['Date'])
    revised = revised.sort_values(['Media', 'Campaign Type', 'Campaign name', 'Audience', 'Date'], ignore_index=True)
    return revised