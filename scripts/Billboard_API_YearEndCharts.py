import billboard
from ChopShop_SQLHelper import create_sql_values_links
from datetime import datetime

"""
For now, this script grabs data for and from ALL year-end charts between 2010-2020. If we want, 
we can add  an additional filter on line 30 to include only the following genres: 
    
GENRES = ['dance-electronic','r-and-b','hip-hop','world','rap','jazz']
"""

#--------------Grab all chart categories, and initialize the script to 
today = datetime.today()

if today.month ==12:
    final_year = today.year + 1
else: 
    final_year = today.year


TYPES = ['artist','producer','songs', 'album']

ALL_YEAREND_CHART_CATEGORIES = billboard.charts(year_end=True)
years = list(range(2010,final_year))

#--------------Loops through all the different chart types
for YEC_Cat in ALL_YEAREND_CHART_CATEGORIES:
    for ty in TYPES:
        #--------------Filters down to only releavant charts (Artists, Producers, Albums, Songs)
        if ty in YEC_Cat and 'imprints' not in YEC_Cat and 'label' not in YEC_Cat:
           
            YEC_SQL_Dict ={}
            #--------------For each year, grabs that chart's attributes and corresponding entries and enters them into the database
            for year in years:
                print(year)
                # try:
                chart = billboard.ChartData(YEC_Cat, year=str(year),fetch=True, timeout=None)
                
                YEC_SQL_Dict['name']=chart.name
                YEC_SQL_Dict['date']=chart.date
                YEC_SQL_Dict['year']=chart.year
                YEC_SQL_Dict['is_year_end']=1
                
                #--------------Artists & Producers
                
                if ('artist' in ty) or ('producer' in ty):
                    ARTIST_PRODUCER_Cols = ['image','artist','peakPos','lastPos','weeks','rank']
                    if 'artist' in ty: 
                        print('--------------Artist')
                        
                        
                    else:
                        print('--------------Producer')
                       
                                                
                    BILLBOARD_ARTIST_PRODUCER_List = []
                    for artist_producer in chart:
                                                    
                        BILLBOARD_ARTIST_PRODUCER_Dict = {}
                        BILLBOARD_ARTIST_PRODUCER_Dict['image'] =artist_producer.image
                        BILLBOARD_ARTIST_PRODUCER_Dict['artist'] =artist_producer.artist
                        BILLBOARD_ARTIST_PRODUCER_Dict['chart_rank'] =artist_producer.rank
                        BILLBOARD_ARTIST_PRODUCER_List.append(BILLBOARD_ARTIST_PRODUCER_Dict)
                    
                    YEC_SQL_Dict['Entries'] = BILLBOARD_ARTIST_PRODUCER_List
                
                    create_sql_values_links(
                                        table_name = 'Billboard_Charts',
                                        sql_dict = YEC_SQL_Dict,
                                        prim_key = 'id',
                                        upsert_bool=True,
                                        linkDictionaryCol = 'Entries',
                                        linkTableName = 'Billboard_Chart_Artists_Producer',
                                        linkTablePK='id',
                                        linkUpsertBoolean = True,
                                        mainTablePKLinkCol = 'chart_id')
                #--------------Songs
                elif 'song' in ty:
                    #CHOPSHOP_SONGS_Dict['occupation'] = 'Artist'
                    print('--------------Song')
                    BILLBOARD_ENTRY_SONG_List = []
                    for song_entry in chart:
                       #--------------Song Id from CHOPSHOP_SONGS_V_SPOTIFY_TRACKS MySQL view
                        CHOPSHOP_SONG_ID = 'NULL'
                        
                        BILLBOARD_ENTRY_SONG_Dict = {}
                        #BILLBOARD_ENTRY_SONG_Dict['song_id'] = CHOPSHOP_SONG_ID
                        BILLBOARD_ENTRY_SONG_Dict['song_album'] =song_entry.title
                        BILLBOARD_ENTRY_SONG_Dict['image'] =song_entry.image
                        BILLBOARD_ENTRY_SONG_Dict['artist'] =song_entry.artist
                        BILLBOARD_ENTRY_SONG_Dict['chart_rank'] =song_entry.rank
                        
                        BILLBOARD_ENTRY_SONG_List.append(BILLBOARD_ENTRY_SONG_Dict)
                         
                    YEC_SQL_Dict['Entries'] = BILLBOARD_ENTRY_SONG_List
                    
                    create_sql_values_links(
                                        table_name = 'Billboard_Charts',
                                        sql_dict = YEC_SQL_Dict,
                                        prim_key = 'id',
                                        upsert_bool=True,
                                        linkDictionaryCol = 'Entries',
                                        linkTableName = 'Billboard_Chart_Song_Album',
                                        linkTablePK='id',
                                        linkUpsertBoolean = True,
                                        mainTablePKLinkCol = 'chart_id')
                #--------------Albums
                elif 'album' in ty:
                    #CHOPSHOP_SONGS_Dict['occupation'] = 'Artist'
                    print('--------------Album')
                    BILLBOARD_ENTRY_ALBUM_List = []
                    for album_entry in chart:
                         #--------------Album Id from CHOPSHOP_ALBUMS_V_SPOTIFY_ALBUMS MySQL view
                        CHOPSHOP_ALBUM_ID = 'NULL'
                        
                        BILLBOARD_ENTRY_ALBUM_Dict = {}
                        #BILLBOARD_ENTRY_ALBUM_Dict['song_id'] = CHOPSHOP_ALBUM_ID
                        BILLBOARD_ENTRY_ALBUM_Dict['song_album'] =album_entry.title
                        BILLBOARD_ENTRY_ALBUM_Dict['image'] =album_entry.image
                        BILLBOARD_ENTRY_ALBUM_Dict['artist'] =album_entry.artist
                        BILLBOARD_ENTRY_ALBUM_Dict['chart_rank'] =album_entry.rank
                        
                        BILLBOARD_ENTRY_ALBUM_List.append(BILLBOARD_ENTRY_ALBUM_Dict)
                 
                    YEC_SQL_Dict['Entries'] = BILLBOARD_ENTRY_ALBUM_List
                    
                    create_sql_values_links(
                                        table_name = 'Billboard_Charts',
                                        sql_dict = YEC_SQL_Dict,
                                        prim_key = 'id',
                                        upsert_bool=True,
                                        linkDictionaryCol = 'Entries',
                                        linkTableName = 'Billboard_Chart_Song_Album',
                                        linkTablePK='id',
                                        linkUpsertBoolean = True,
                                        mainTablePKLinkCol = 'chart_id')
                       
                # except: pass