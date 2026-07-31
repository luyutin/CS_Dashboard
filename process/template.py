import pandas as pd
from process.SC_Abbot import sc_abbot_sem, sc_abbot_ga
from process.SC_PG import sc_pg_meta, sc_pg_line, sc_pg_DV3_iMedia, sc_pg_DV3_YTVideo, sc_pg_DV3_OEVideo, sc_pg_TTD_iMedia, sc_pg_TTD_OEVideo, sc_pg_kol
from process.SC_Samsung import sc_samsung_pmax , sc_samsung_meta, sc_samsung_google, sc_samsung_line, sc_samsung_ttd, sc_samsung_GA
from process.ZO_MAC import zo_mac_meta
from process.ZO_Grapeking import zo_grapeking_meta
from process.ZO_Goldencar import zo_goldencar_meta
from process.ZO_Nestle import zo_nestle_ga, zo_nestle_ga4, zo_nestle_meta, zo_nestle_DV3_dsp, zo_nestle_DV3_YT, zo_nestle_sem, zo_nestle_lm, zo_nestle_line, zo_nestle_youtube
from process.SC_Lipton import sc_lipton_meta, sc_lipton_YT
from process.ZO_Quaker import zo_quaker_lm, zo_quaker_YT, zo_quaker_meta, zo_quaker_tv
from process.ZO_Nespresso import zo_nespresso_TTD, zo_nespresso_meta, zo_nespresso_YT, zo_nespresso_sem, zo_nespresso_lm, zo_nespresso_line, zo_nespresso_ga


def template():
    columns = ['Region', 'Market', 'BU', 'Customer', 'Date', 'Duration',
               'Media', 'Platform', 'Advertiser Currency', 'Final URL', 'Item (Summary of filter)',
               'Account name', 'Campaign name', 'Campaign Objective', 'Campaign Free Form', 'Adset name',  'Audience', 'Adset Free Form',
               'Message Type', 'Ad Free Form', 'Adset MD', 'Product',
               'Channel', 'InName Site', 'Campaign Type', 'Buying Type','Placement', 'SEM Status',
               'Reach', 'Impressions', 'Clicks (all)', 'Frequency', 'Link clicks (Web Clicks)', 'Spent (TWD)',
               'Purchases conversion value', 'Conversions', 'Conversion Value', 'MV>5',
               'Views', '3" Video Views', '15" Video Views (ThruPlays)', 'TrueView: Views',
               'Video played to 25%', 'Video played to 50%', 'Video played to 75%', 'Video played to 100%',
               'Fan page like', 'Page Likes or followers',
               'Post comments', 'Post engagements', 'Post reactions', 'Post shares', 'Photo Views', 'Post Saves',
               'Adds to cart', 'Purchases', 'Revenue', 'Sales Engagement', 'Purchase ROAS', 'Quality Score',
               'Leads', 'Actions', 'View-through conversion', 'Clicks conversion', 'View conversion',
               'User number', 'Total PPL', 'New user', 'Working session', 'Bounce Rate',
               'Avg engagement time per session', 'Avg Working session time', 'GA Session name', 'GA Session Type', 'GA Session Qty',
               'TVR', '10 Second TVR', 'Reach 000s']
    return pd.DataFrame(columns=columns)

def process_map():
    relation_map = {
        'SC': {
            'Samsung':{
                'Google' : sc_samsung_google,
                'PMAX' : sc_samsung_pmax,
                'Meta' : sc_samsung_meta,
                'Line' : sc_samsung_line,
                'TTD' : sc_samsung_ttd,
                'GA' : sc_samsung_GA,
                'banner' : sc_samsung_meta,
                'ivideo' : sc_samsung_meta,
                'RD' : sc_samsung_meta,
                'TV' : sc_samsung_meta
            },
            'coke':{
                'banner' : sc_samsung_meta,
                'ivideo' : sc_samsung_meta,
                'RD' : sc_samsung_meta,
                'TV' : sc_samsung_meta
            },
            'PG':{
                'Social' : sc_pg_meta,
                'Line': sc_pg_line,
                'DV3-iMedia': sc_pg_DV3_iMedia,
                'DV3-YTVideo':sc_pg_DV3_YTVideo,
                'DV3-OEVideo':sc_pg_DV3_OEVideo,
                'TTD-iMedia': sc_pg_TTD_iMedia,
                'TTD-OEVideo':sc_pg_TTD_OEVideo,
                'KOL-Boosting' : sc_pg_kol
            },
            'ABBOT':{
                'SEM': sc_abbot_sem,
                'GA': sc_abbot_ga
            },
            'Lipton':{
                'Meta': sc_lipton_meta,
                'YT': sc_lipton_YT
            }
        },
        'ZO': {
            'MAC':{'Meta' : zo_mac_meta},
            'Nestle':{
                'Meta' : zo_nestle_meta,
                'DV3-display' : zo_nestle_DV3_dsp,
                'DV3-YT' : zo_nestle_DV3_YT,
                'SEM' : zo_nestle_sem,
                'LM' : zo_nestle_lm,
                'YT' : zo_nestle_DV3_YT,
                'LINE' : zo_nestle_line,
                'GA4' : zo_nestle_ga4,
                'GA' : zo_nestle_ga
            },
            'Nespresso':{
                'Meta' : zo_nespresso_meta,
                'TTD' : zo_nespresso_TTD,
                'SEM' : zo_nespresso_sem,
                'LM' : zo_nespresso_lm,
                'YT' : zo_nespresso_YT,
                'LINE' : zo_nespresso_line,
                'GA' : zo_nespresso_ga
            },
            'Wonka':{
                'Meta' : zo_nestle_meta,
                'LINE' : zo_nestle_line,
                'YT' : zo_nestle_youtube
                #'DSP' : zo_nestle_dsp,
                #'DV360' : zo_nestle_DV360
            },
            '葡萄王':{
                'Meta' : zo_grapeking_meta
            },
            '金車':{
                'Meta' : zo_goldencar_meta
            },
            '佳格':{
                'Meta' : zo_quaker_meta,
                'LM' : zo_quaker_lm,
                'YT' : zo_quaker_YT,
                'TV' : zo_quaker_tv
            }
        }
    }
    return relation_map

def general_process(bu_module, df, file_name):
    df_revised = getattr(bu_module, 'split')(df) if hasattr(bu_module, 'split') else df
    df_revised = getattr(bu_module, 'insert_col')(df_revised) if hasattr(bu_module, 'insert_col') else df_revised
    template_processed = template()
    template_processed = getattr(bu_module, 'revised_output')(template_processed, df_revised, file_name)
    return template_processed
