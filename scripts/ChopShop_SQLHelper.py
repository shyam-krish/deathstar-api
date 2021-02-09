import pymysql
from pprint import pprint
import time

write_endpoint= 'chopshop-db.cqltttjataio.us-east-1.rds.amazonaws.com'
# write_endpoint= 'localhost'
# username = 'chopshop_admin'
# password = 'klasikhz814!'
# db_name = 'chopshop-db'

username = 'root'
password = 'chopshop1234'
db_name = 'sys'

def sql_string(value):
    value = "'"+str(value).replace('None','').strip().replace("'","''")+"'"
    if value == "''":
        return 'NULL'
    else: return value
    
def execute_write_sql(sql_statement):
    try: 
        connWrite = pymysql.connect(host='localhost', user=username, passwd=password, db= db_name, connect_timeout=10, port=3306)
    except:
        print("ERROR: Connection failed")
    with connWrite.cursor() as cur:
        cur.execute(sql_statement)
        cur.close()
    connWrite.commit()

def return_ref_id(ref_dict, ref_type, ref_label):
    if ref_label in ref_dict.keys():
        ref_id = ref_dict[ref_label]
    else:
        clean_r_type = sql_string(ref_type).replace("_"," ").upper()
        clean_label = sql_string(ref_label).replace("_"," ").upper()
        
        try: 
            connWrite = pymysql.connect(write_endpoint, user=username, passwd=password, db= db_name, connect_timeout=10)
        except:
            print("ERROR: Connection failed")
        with connWrite.cursor() as cur:
            sp_sql="CALL SP_R_DATA_NORMALIZE(%s, %s, @ref_id);"%(clean_r_type, clean_label)
            cur.execute(sp_sql)
            cur.execute("SELECT @ref_id;")
            ref_id = str(cur.fetchone()[0])
            cur.close()
        connWrite.commit()
        
        ref_dict[ref_label] = ref_id
    
    return ref_id
  
def get_sql_prefix(table_name,column_list):
    print(column_list)
    sql_cols = ",".join(column_list)
    insert = "INSERT INTO %s(%s) VALUES \n"%(table_name, sql_cols)
    return insert

def get_sql_upsert(column_list):
    prefix = "\nON DUPLICATE KEY UPDATE "
    upsert = []
    for col in column_list:
        string = "%s=VALUES(%s)"%(col,col)
        upsert.append(string)
    upsert = ",".join(upsert)
    sql_upsert = prefix+upsert+";"
    return sql_upsert

def create_sql_values(table_name,sql_dict,prim_key,upsert_bool):
    
    """
    Still need to think about how to handle Unique Identifiers for LAFs
    """
    dict_keys = sql_dict.keys()
    value_list = []
    for key in dict_keys:
        value = sql_string(sql_dict[key])
        value_list.append(value)
    
    sql_prefix = get_sql_prefix(table_name, dict_keys)
    sql_val = '('+",".join(value_list)+')'
    final_sql = sql_prefix+sql_val
    if upsert_bool==True:
        sql_upsert= get_sql_upsert(dict_keys)
        final_sql = final_sql+sql_upsert
    #print(final_sql)
    #execute_write_sql(final_sql)
    return final_sql

def create_sql_values_links(table_name,sql_dict,prim_key,upsert_bool,**kwargs):
   
    """
    For cases like LAFs, sometimes there will be link inserts, sometimes not. When there ARE link inserts, 
    these are the required kwargs:
        
    1. linkDictionaryCol
    2. linkTableName
    3. linkTablePK
    4. linkUpsertBoolean
    5. mainTablePKLinkCol
    """
    
    MAIN_TABLE_DICT = sql_dict
    #pprint(MAIN_TABLE_DICT.keys())
    if kwargs.get('linkDictionaryCol'):
        
        LINK_SQL_LIST = sql_dict[kwargs.get('linkDictionaryCol')]
        # print(MAIN_TABLE_DICT)
        # time.sleep(5)
        # print('---------------------------------------')
        MAIN_TABLE_DICT.pop(kwargs.get('linkDictionaryCol'))
        # print(MAIN_TABLE_DICT)
        #Updates the table with a brand new entry or updates the old one; always returns the Primary Key
        #--------------Creates and preps all parts of the UPSERT_MAIN_TABLE_PK_SQL
        value_list = []
        where_cols = []
        ups_cols=[]
        for key in MAIN_TABLE_DICT.keys():
            ups_cols.append(key)
            value = sql_string(MAIN_TABLE_DICT[key])
            value_list.append(value)
            if value !='NULL':
                string = f'{key}={value}'
            else:
                print(value)
                string = f'{key} IS NULL'
            where_cols.append(string)
       
        
        if_exists_cols = ','.join(MAIN_TABLE_DICT.keys())    
        where_cols = " AND ".join(where_cols)
        
        #--------------Creates Main Table Insert Statement
        ins_sql_prefix = get_sql_prefix(table_name, MAIN_TABLE_DICT.keys())
        ins_sql_val = '('+",".join(value_list)+')'
        ins_sql_new = ins_sql_prefix+ins_sql_val
        
        #--------------Creates Main Table Upsert Statement
        link_table_PK = kwargs.get('linkTablePK')
        ups_cols.insert(0,link_table_PK)
        ups_sql_prefix = get_sql_prefix(table_name, 
                                        ups_cols)
        ups_sql_suffix = get_sql_upsert(ups_cols)
        ups_sql_val = "(prim_key_id,"+",".join(value_list)+')'
        upsert_sql = ups_sql_prefix+ups_sql_val+ups_sql_suffix
        
        print(upsert_sql)

        NESTED_INSERT_SP = f"""
                                CREATE DEFINER=`root`@`localhost` PROCEDURE `SP_TEMP_NESTED_INSERT`(OUT prim_key_id INT)
                                BEGIN
                                IF EXISTS (SELECT {if_exists_cols} FROM {table_name} WHERE {where_cols} ) 
                                    THEN  
                                        SELECT {prim_key} FROM {table_name} WHERE {where_cols} into prim_key_id;
                                        {upsert_sql}
                                    ELSE 
                                        {ins_sql_new}; 
                                        SELECT {prim_key} FROM {table_name} WHERE {where_cols} into prim_key_id;
                                END IF;
                                END """
                            
       #--------------Runs the UPSERT_MAIN_TABLE_PK_SQL and saves the PK
        print(NESTED_INSERT_SP)
        connWrite = pymysql.connect(host='localhost', user=username, passwd=password, db= db_name, port=3306, connect_timeout=10)
        
        #connWrite = pymysql.connect(write_endpoint, user=username, passwd=password, db= db_name,connect_timeout=10)
        print('--------------------------Connected to ChopShop Database')
        with connWrite.cursor() as cur:
            cur.execute(NESTED_INSERT_SP)
            print('--------------------------Running Stored Procedure')
            cur.execute("CALL SP_TEMP_NESTED_INSERT(@prim);")
            #print('--------------------------Obtaining Main Table PK')
            cur.execute("SELECT @prim;")
            MAIN_TABLE_PK = str(cur.fetchone()[0])
            print('--------------------------PK is ' + MAIN_TABLE_PK)
            print('--------------------------Dropping Stored Procedure')
            cur.execute("DROP PROCEDURE SP_TEMP_NESTED_INSERT;")
            print('--------------------------Main Table operations completed')
            cur.close()
        connWrite.commit()

        #--------------Add Main table PK to Link SQL Dictionary and handle link Inserts
        
        for LINK_SQL_DICT in LINK_SQL_LIST:
            print(kwargs.get('mainTablePKLinkCol'))
            print(MAIN_TABLE_PK)
            LINK_SQL_DICT[kwargs.get('mainTablePKLinkCol')] = MAIN_TABLE_PK
            pprint(LINK_SQL_DICT)
            final_sql = create_sql_values(table_name = kwargs.get('linkTableName'),
                                          sql_dict = LINK_SQL_DICT,
                                          prim_key = kwargs.get('linkTablePK'),
                                          upsert_bool = kwargs.get('linkUpsertBoolean'))
            print(final_sql)
            execute_write_sql(final_sql)
            
        
   
    else: create_sql_values(table_name,sql_dict,prim_key,upsert_bool)
        
    