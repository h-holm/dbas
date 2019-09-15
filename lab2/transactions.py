#!/usr/bin/python
import pgdb
# This example python script illustrates how we can run multiple connections to study
# concurrency issues between two transactions running in separate connections.

# see documentation of pgdb: http://www.pygresql.org/contents/pgdb/index.html
# see http://www.pygresql.org/contents/tutorial.html#first-steps-with-the-db-api-2-0-interface

#If you are using a local postgres server as user postgres with default database 'postgres'
#params = {'host':'', 'user':'postgres', 'database':'', 'password':''}
#If you are using nestor2, copy this python file to u-shell and then execute there 
params = {'host':'nestor2.csc.kth.se', 'user': 'your_kthusername', 'database':'', 'password':'your_postgres_password'}

# We work with two connections to the database, simulating concurrent users. These
# connections could be remote, in separate programs etc, but we run them in the same file
# here to test out concurrency issues. Connection1/cursor1 are for "user 1",
# Connection2/cursor2 for "user 2"
connection1 = pgdb.Connection(**params)
connection1.autocommit=False
cursor1 = connection1.cursor()

connection2 = pgdb.Connection(**params)
connection2.autocommit=False
cursor2 = connection2.cursor()

def drop():
    # delete the table Sales if it does already exist
    try:
        query = "DROP TABLE Sales";
        cursor1.execute(query)
        connection1.commit()  
        # by default in pgdb, all executed queries for connection 1 up to here form a transaction
        # we can also explicitly start tranaction by executing BEGIN TRANSACTION
    except:
        # Errors in python are caught using try ... except
        print "ROLLBACK: Sales table does not exists or other error."
        connection1.rollback()
        pass

def init():
    # Create table sales and add two initial tuples
    query = "CREATE TABLE Sales(name VARCHAR(30), price float)";
    cursor1.execute(query)
    query = """INSERT INTO Sales VALUES('Toothbrush', 100)""";
    cursor1.execute(query)
    query = """INSERT INTO Sales VALUES('Pen', 10)""";
    cursor1.execute(query)

    # this commits all executed queries forming a transaction up to this point
    connection1.commit()

def scenario1():
    # Here we test some concurrency issues.

    tr1 = "BEGIN TRANSACTION"
    q_max = "select MAX(price) from Sales";
    q_min = "select MIN(price) from Sales";
    tr2 = "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE"
    q_del = "delete from sales";
    q_ins = "insert into sales values('Chair', 2000)";

    print("U1: (start) "+ tr1)
    cursor1.execute(tr1)
    print("U1: (max)   "+ q_max)
    cursor1.execute(q_max)
    # result of fetchone is a tuple with 1 attribute, we access first component value with [0]
    user_max = cursor1.fetchone()[0]
    print("... max="+str(user_max))

    print("U2: (start) "+ tr2)
    cursor2.execute(tr1)
    print("U2: (del)   "+ q_del)
    cursor2.execute(q_del)
    print("U2: (ins)   "+ q_ins)
    cursor2.execute(q_ins)
    connection2.commit()

    print("U1: (min)   "+ q_min)
    cursor1.execute(q_min)
    # result of fetchone is a tuple with 1 attribute, we access first component value with [0]
    user_min = cursor1.fetchone()[0]
    print("... min="+str(user_min))
    print("... min > max as highlighted in lecture notes")
    connection1.commit()
def showall():
    cursor1.execute("SELECT * FROM Sales;");
    connection1.commit()
    print cursor1.rowcount
    for i in range(cursor1.rowcount):
        print cursor1.fetchone()
    #results = cursor1.fetchall()
    #print "Sales relation contents:"
    #for r in results:
    #print r;
def close():
    connection1.close()
    connection2.close()


# when calling python filename.py the following functions will be executed:
drop()
init()
showall()
scenario1()
showall()
close()

