#!/usr/bin/env python3
import argparse
import gzip
import mysql.connector
import urllib.request
import shutil
import sys
import time

argp = argparse.ArgumentParser(description="Upload CSV to MySQL")
argp.add_argument("-v", action='store_true', help="enable verbosity")
argp.add_argument("--database", type=str, help="database to use")
argp.add_argument("--file", type=str, help="local file to use")
argp.add_argument("--url", type=str, help="url to download file from ")

verbose = False

tmp_file = '/tmp/archive.gz'
tmp_file_uncompressed = '/tmp/archive.txt'

db_config = {
    'host': 'localhost',
    'user': 'test',
    'password': '12345',
    'database': 'csv_mysql'
}
db_structure = {
    'table': 'domains_csv',
    'fields': {
        'domain':'text not null',
        'first_seen':'int(11) unsigned not null',     
        'last_seen':'int(11) unsigned not null',
        'etld':'text not null',
        'id':'int(11) unsigned not null',
        'time_date_imported':'datetime not null',
    },
    'primary_key': 'id',
}

# Check if table exists
def tableExists(db, name):
    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM `information_schema`.tables '\
                   'WHERE `table_name` = "%s"' % name)
    if cursor.fetchone()[0] == 1:
        cursor.close()
        return True
    cursor.close()
    return False

# Create table based on table structure dict
def createTable(db, structure):    
    cursor = db.cursor()
    fields = ', '.join('`%s` %s' % (col_name, col_attrs) 
                  for col_name, col_attrs in structure['fields'].items())
    cursor.execute('CREATE TABLE `%s` ( %s , PRIMARY KEY(`%s`))'\
                   'DEFAULT CHARSET=utf8' % 
                   (structure['table'], fields, structure['primary_key']))
    cursor.close()

# Import data from a preformatted CSV file
def importData(db, table, infile):
    cursor = db.cursor()
    cursor.execute('LOAD DATA LOCAL INFILE "%s" REPLACE INTO TABLE `%s`'\
                   'FIELDS TERMINATED BY "," IGNORE 1 LINES'\
                   '(`domain`, `first_seen`, `last_seen`, `etld`, `id`)'\
                   'SET `time_date_imported` = CURRENT_TIMESTAMP' % 
                   (infile, table))
    cursor.close()
    db.commit()

def debug(msg):
    if verbose is True:
        print(formatMsg('DEBUG', msg))

def err(msg):
    print(formatMsg('ERROR', msg))
    
def crit(msg):
    print(formatMsg('CRIT', msg))
    exit(255)

def warn(msg):
    print(formatMsg('WARN',msg))
    
def formatMsg(level, msg):
    return "\r[%s] [%s] %s" % (time.strftime("%Y-%m-%d %H:%M:%S"),level, msg)
    
if __name__ == '__main__':
    args = argp.parse_args()
    if args.v is True:
        verbose = True
    
    if args.file is not None:
        debug("Using local file: %s" % args.file)
        tmp_file = args.file
    elif args.url is not None:
        debug("Retrieving file by network: %s" % args.url)
        urllib.request.urlretrieve(args.url, tmp_file)
    else:
        argp.print_help()
        exit(0)
    if args.database is not None:
        db_config['database'] = args.database
        
    debug("Run start.")
    
    try:
        db = mysql.connector.connect(**db_config)
    except Exception as e:
        crit("Error connecting to db: %s" % str(e))
    
    debug("Checking if table %s exists." % db_structure['table'])
    
    if not tableExists(db, db_structure['table']):
        debug("Creating table.")
        try:
            createTable(db, db_structure)
        except Exception as e:
            crit("Error while creating table: %s" % str(e))
    else:
        debug("Table exists. Proceeding.")
    
    
    debug("Uncompressing %s" % tmp_file)
    try:
        with gzip.open(tmp_file, 'rb') as f_in:
            with open(tmp_file_uncompressed, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)      
    except KeyboardInterrupt:
        warn("Operation cancelled manually.")
        exit(0)
    except Exception as e:
        crit("Failed to uncompress %s with error: %s" % (tmp_file, str(e)))
    
    debug("Loading %s into %s" % (tmp_file_uncompressed, db_structure['table']))
    try:
        importData(db, db_structure['table'], tmp_file_uncompressed)
        debug("Loaded data successfully.")
    except KeyboardInterrupt:
        warn("Operation cancelled manually.")
        exit(0)
    except Exception as e:
        crit("Error while loading data: %s" % str(e))
    debug("Run finish")