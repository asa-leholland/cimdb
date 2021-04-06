# import MySQLdb
import os

# facilitates migration to postgres
# import urllib.parse as up
import psycopg2

from psycopg2.extras import RealDictCursor


from dotenv import load_dotenv, find_dotenv

# Load our environment variables from the .env file in the root of our project.
load_dotenv(find_dotenv())


DB_NAME = 'czidautk'
DB_USER = 'czidautk'
DB_PASS = 'FrehVqDTs6WkKc5RdB72xC5b78v5Q_iG'
DB_HOST = 'kashin.db.elephantsql.com'
DB_PORT = '5432'



# os.environ['DATABASE_URL'] = 'postgres://czidautk:FrehVqDTs6WkKc5RdB72xC5b78v5Q_iG@kashin.db.elephantsql.com:5432/czidautk'
# os.environ['DBUSER'] = 'czidautk'
# os.environ['DBPASS'] = 'FrehVqDTs6WkKc5RdB72xC5b78v5Q_iG'
# os.environ['DBHOST'] = 'kashin.db.elephantsql.com'
# os.environ['DBNAME'] = 'CIMDB'

# database_uri = 'postgresql+psycopg2://{dbuser}:{dbpass}@{dbhost}/{dbname}'.format(
#   dbuser=os.environ['DBUSER'],
#   dbpass=os.environ['DBPASS'],
#   dbhost=os.environ['DBHOST'],
#   dbname=os.environ['DBNAME']
# )


# up.uses_netloc.append("postgres")
# url = up.urlparse(os.environ["DATABASE_URL"])





def connect_to_database():
    '''
    connects to a database and returns a database objects
    '''

    try: 
        conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        print('Connected to CIMDB on PostGres')
        return conn

    except:
        print('Could not connect to database')
        connect_to_database()

    # db_connection = psycopg2.connect(database=url.path[1:],
    #     user=url.username,
    #     password=url.password,
    #     host=url.hostname,
    #     port=url.port
    #     )


# # These variables connect to Asa's database on PHPMyAdmin. 
# # They can be currently accessed using localhost.
# host = 'classmysql.engr.oregonstate.edu'      # MUST BE THIS
# user = 'cs340_hollaasa'       # don't forget the CS_340 prefix
# passwd = '9908'               # should only be 4 digits if default
# db = 'cs340_hollaasa' 

# # # Ali
# host = 'localhost'
# user = 'user'                                   # can be different if you set up another username in your MySQL installation
# passwd = '1qaz2wsx!QAZ@WSX'                        # set accordingly
# db = 'cimdb'


# def connect_to_database(host = host, user = user, passwd = passwd, db = db):
#     '''
#     connects to a database and returns a database objects
#     '''
#     db_connection = MySQLdb.connect(host,user,passwd,db)
#     return db_connection

def execute_query(db_connection = None, query = None, query_params = ()):
    '''
    executes a given SQL query on the given db connection and returns a Cursor object
    db_connection: a MySQLdb connection object created by connect_to_database()
    query: string containing SQL query
    returns: A Cursor object as specified at https://www.python.org/dev/peps/pep-0249/#cursor-objects.
    You need to run .fetchall() or .fetchone() on that object to actually acccess the results.
    '''
    print('executing:', query, query_params)

    if db_connection is None:
        print("No connection to the database found! Have you called connect_to_database() first?")
        return None

    if query is None or len(query.strip()) == 0:
        print("query is empty! Please pass a SQL query in query")
        return None

    print("Executing %s with %s" % (query, query_params));
    # Create a cursor to execute query. Why? Because apparently they optimize execution by retaining a reference according to PEP0249
    cursor = db_connection.cursor(cursor_factory=RealDictCursor)

    '''
    params = tuple()
    #create a tuple of paramters to send with the query
    for q in query_params:
        params = params + (q)
    '''
    #TODO: Sanitize the query before executing it!!!
    cursor.execute(query, query_params)
    # this will actually commit any changes to the database. without this no
    # changes will be committed!
    db_connection.commit();
    return cursor

if __name__ == '__main__':
    print('testing db connection')
    db = connect_to_database()
    query = "SELECT * from Sites;"
    results = execute_query(db, query);
    print("Printing results of %s" % query)

    for r in results.fetchall():
        print(r)