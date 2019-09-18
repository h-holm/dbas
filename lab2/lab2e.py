#!/usr/bin/python
import pgdb


params = {'host':'', 'user':'postgres', 'database':'', 'password':''}

connection1 = pgdb.Connection(**params)
connection1.autocommit=False
cursor1 = connection1.cursor()

connection2 = pgdb.Connection(**params)
connection2.autocommit=False
cursor2 = connection2.cursor()


def drop(table):
    # delete the table Sales if it does already exist
    try:
        query = f'DROP TABLE {table}'
        cursor1.execute(query)
        connection1.commit()
        # by default in pgdb, all executed queries for connection 1 up to here form a transaction
        # we can also explicitly start tranaction by executing BEGIN TRANSACTION
    except:
        # Errors in python are caught using try ... except
        print(f'ROLLBACK: {table} table does not exist or other error.')
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

    print('\n-------------------------------------------------------------------')


def scenario2():
    # Default transation isolation level in PostgreSQL is ordinarily READ COMMITTED.
    # 1. SERIALIZABLE (must run either completely before or after other transactions).
    # 2. REPEATABLE-READ (tuples read will reappear if query repeated).
    # 3. READ-COMMITTED (only tuples written by transactions that have already
    #                    committed may be seen by this transaction).
    # 4. "READ-UNCOMMITTED" (no constraint on what the transaction may see).

    # A non-repeatable read is one in which data read twice inside the same
    # transaction cannot be guaranteed to contain the same value.

    # Phantom tuple:
    # a phantom read occurs when, in the course of a transaction, two identical
    # queries are executed, and the collection of rows returned by the second
    # query is different from the first.

    q_crt = "CREATE TABLE ab(a INT PRIMARY KEY, b INT);"

    # tr1 = "BEGIN TRANSACTION;"
    # Uncommenting the row below resolves the non-repeatable read.
    tr1 = "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
    q_sel = "SELECT * FROM ab;"

    tr2 = "BEGIN TRANSACTION;"
    q_ins = "INSERT INTO ab VALUES(5, 5);"
    comm = "COMMIT;"

    print("\nThis scenario demonstrates a non-repeatable read using READ COMMITTED vs. SERIALIZABLE")

    print("\nCreate table:\t", q_crt)
    cursor1.execute(q_crt)
    connection1.commit()

    print("\nU1 (start):\t", tr1)
    cursor1.execute(tr1)
    print("U1 (get all):\t", q_sel)
    cursor1.execute(q_sel)
    user_all = cursor1.fetchone()
    print("\t\t all="+str(user_all))

    print("\nU2 (start):\t", tr2)
    cursor2.execute(tr2)
    print("U2 (ins):\t", q_ins)
    cursor2.execute(q_ins)
    print("U2 (commit):\t", comm)
    cursor2.execute(comm)
    # connection2.commit()

    print("\nU1 (get all):\t", q_sel)
    cursor1.execute(q_sel)
    user_all = cursor1.fetchone()
    print("\t\t all=", str(user_all))

    print("U1 (commit):\t", comm)
    cursor1.execute(comm)
    # connection1.commit()

    print('\n-------------------------------------------------------------------')


def scenario3():
    # Default transation isolation level in PostgreSQL is ordinarily READ COMMITTED.
    # 1. SERIALIZABLE (must run either completely before or after other transactions).
    # 2. REPEATABLE-READ (tuples read will reappear if query repeated).
    # 3. READ-COMMITTED (only tuples written by transactions that have already
    #                    committed may be seen by this transaction).
    # 4. "READ-UNCOMMITTED" (no constraint on what the transaction may see).

    # A non-repeatable read is one in which data read twice inside the same
    # transaction cannot be guaranteed to contain the same value.

    q_crt = "CREATE TABLE ab(a INT, b INT);"
    q_ins = "INSERT INTO ab Values(1, 2);"

    # tr1 = "BEGIN TRANSACTION;"
    # tr1 = "BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;"
    tr1 = "BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;"
    q_sel = "SELECT * FROM ab;"

    tr2 = "BEGIN TRANSACTION;"
    q_ins2 = "UPDATE ab SET a = 7 WHERE a = 1;"
    comm = "COMMIT;"

    print("\nThis scenario demonstrates a non-repeatable read using READ COMMITTED vs. REPEATABLE READ")

    print("\nCreate table:\t", q_crt)
    cursor1.execute(q_crt)
    connection1.commit()
    print("\nAdd first tuple to relation\t", q_ins)
    cursor1.execute(q_ins)
    connection1.commit()

    print("\nU1 (start):\t", tr1)
    cursor1.execute(tr1)
    print("U1 (get all):\t", q_sel)
    cursor1.execute(q_sel)
    user_all = cursor1.fetchone()
    print("\t\t all="+str(user_all))

    print("\nU2 (start):\t", tr2)
    cursor2.execute(tr2)
    print("U2 (upd):\t", q_ins2)
    cursor2.execute(q_ins2)
    print("U2 (commit):\t", comm)
    cursor2.execute(comm)
    print("U2 (get all):\t", q_sel)
    cursor2.execute(q_sel)
    user_all = cursor2.fetchone()
    print("\t\t all=", str(user_all))

    # connection2.commit()

    print("\nU1 (get all):\t", q_sel)
    cursor1.execute(q_sel)
    user_all = cursor1.fetchone()
    print("\t\t all=", str(user_all))

    print("U1 (commit):\t", comm)
    cursor1.execute(comm)
    # connection1.commit()

    print('\n-------------------------------------------------------------------')


def scenario4():
    # Default transation isolation level in PostgreSQL is ordinarily READ COMMITTED.
    # 1. SERIALIZABLE (must run either completely before or after other transactions).
    # 2. REPEATABLE-READ (tuples read will reappear if query repeated).
    # 3. READ-COMMITTED (only tuples written by transactions that have already
    #                    committed may be seen by this transaction).
    # 4. "READ-UNCOMMITTED" (no constraint on what the transaction may see).

    # A non-repeatable read is one in which data read twice inside the same
    # transaction cannot be guaranteed to contain the same value.

    q_crt = "CREATE TABLE ab(a INT PRIMARY KEY, b INT);"

    tr1 = "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
    q_ins1 = "INSERT INTO ab VALUES(1, 2);"
    q_sel = "SELECT * FROM ab;"

    tr2 = "BEGIN TRANSACTION;"
    q_ins2 = "INSERT INTO ab VALUES(3, 4);"
    # q_ins3 = "INSERT INTO ab VALUES('hello', 'world');"
    q_ins3 = "INSERT INTO ab VALUES(NULL, 6);"
    # q_ins3 = "INSERT INTO ab VALUES(5, 6, 7);"
    comm = "COMMIT;"

    print("\nThis scenario demonstrates how a transaction with two insert elements")
    print("of which the second fails can be rolled back without affecting another")
    print("user's queries.")

    print("\nCreate table:\t", q_crt)
    cursor1.execute(q_crt)
    connection1.commit()

    print("\nU1 (start):\t", tr1)
    cursor1.execute(tr1)
    print("U1 (ins):\t", q_ins1)
    cursor1.execute(q_ins1)
    print("U1 (get all):\t", q_sel)
    cursor1.execute(q_sel)
    user_all = cursor1.fetchone()
    print("\t\t all="+str(user_all))

    try:
        print("\nU2 (start):\t", tr2)
        cursor2.execute(tr2)
        print("U2 (ins):\t", q_ins2)
        cursor2.execute(q_ins2)
        print("U2 (ins):\t", q_ins3)
        print("At this point, U2's insertion fails")
        cursor2.execute(q_ins3)
        print("U2 (commit):\t", comm)
        cursor2.execute(comm)
        # connection2.commit()
    except:
        print("Rolling back")
        connection2.rollback()

    print("\nU1 (get all):\t", q_sel)
    cursor1.execute(q_sel)
    user_all = cursor1.fetchone()
    print("\t\t all=", str(user_all))

    print("U1 (commit):\t", comm)
    cursor1.execute(comm)
    connection1.commit()

    print('\n-------------------------------------------------------------------')


def scenario5():
    print("\nScenario: R(a, b and strange behaviour even when using SERIALIZABLE)")

    def instantiate():
        q_crt = "CREATE TABLE R(a INT, b INT);"
        q_ins1 = "INSERT INTO R VALUES(0, 1);"
        q_ins2 = "INSERT INTO R VALUES(0, 2);"
        q_ins3 = "INSERT INTO R VALUES(1, 10);"
        q_ins4 = "INSERT INTO R VALUES(1, 20);"

        print("\nCreate table:\t", q_crt)
        cursor1.execute(q_crt)
        print("Add tuples:\t", q_ins1)
        cursor1.execute(q_ins1)
        print("Add tuples:\t", q_ins2)
        cursor1.execute(q_ins2)
        print("Add tuples:\t", q_ins3)
        cursor1.execute(q_ins3)
        print("Add tuples:\t", q_ins4)
        cursor1.execute(q_ins4)
        connection1.commit()

        q_sel = "SELECT * FROM R;"

        print("Fetch all:\t", q_sel)
        cursor1.execute(q_sel)
        user_all = cursor1.fetchall()
        print("\t\t R(a, b) = ", str(user_all))

        comm = "COMMIT;"
        print("\nCommit:\t\t", comm)
        cursor1.execute(comm)
        connection1.commit()

    # Transaction 1
    def transaction1():
        tr1 = "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
        print("\nU1 (start t1):\t", tr1)
        cursor1.execute(tr1)

        a1 = "SELECT SUM(b) FROM R WHERE a = 0;"
        print("Get xval1:\t", a1)
        cursor1.execute(a1)
        xval1 = cursor1.fetchone()[0]
        print("\t\t xval1 = ", xval1)
        b1 = f"INSERT INTO R Values(1, {xval1});"
        print("Ins xval1:\t", b1)
        cursor1.execute(b1)
        q_sel = "SELECT * FROM R;"
        print("Fetch all:\t", q_sel)
        cursor1.execute(q_sel)
        user_all = cursor1.fetchall()
        print("\t\t R(a, b) = ", str(user_all))
        comm = "COMMIT;"
        print("\nCommit:\t\t", comm)
        cursor1.execute(comm)
        # connection1.commit()

    def transaction2():
        # Transaction 2
        tr2 = "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
        print("\nU2 (start t2):\t", tr2)
        cursor2.execute(tr2)

        a2 = "SELECT SUM(b) FROM R WHERE a = 1;"
        print("Get xval2:\t", a2)
        cursor2.execute(a2)
        xval2 = cursor2.fetchone()[0]
        print("\t\t xval2 = ", xval2)
        b2 = f"INSERT INTO R Values(0, {xval2});"
        print("Ins xval2:\t", b2)
        cursor2.execute(b2)
        q_sel = "SELECT * FROM R;"
        print("Fetch all:\t", q_sel)
        cursor2.execute(q_sel)
        user_all = cursor2.fetchall()
        print("\t\t R(a, b) = ", str(user_all))
        comm = "COMMIT;"
        print("\nCommit:\t\t", comm)
        cursor2.execute(comm)
        # connection2.commit()

    instantiate()
    print("\nTransaction 1 followed by Transaction 2")
    transaction1()
    transaction2()

    print('\n-------------------------------------------------------------------')

    drop("R")
    instantiate()
    print("\nTransaction 1 followed by Transaction 2")
    transaction2()
    transaction1()

    print('\n-------------------------------------------------------------------')


def scenario6():
    print("\nScenario: R(a, b and strange behaviour even when using SERIALIZABLE)")

    def instantiate():
        q_crt = "CREATE TABLE R(a INT, b INT);"
        q_ins1 = "INSERT INTO R VALUES(0, 1);"
        q_ins2 = "INSERT INTO R VALUES(0, 2);"
        q_ins3 = "INSERT INTO R VALUES(1, 10);"
        q_ins4 = "INSERT INTO R VALUES(1, 20);"

        print("\nCreate table:\t", q_crt)
        cursor1.execute(q_crt)
        print("Add tuples:\t", q_ins1)
        cursor1.execute(q_ins1)
        print("Add tuples:\t", q_ins2)
        cursor1.execute(q_ins2)
        print("Add tuples:\t", q_ins3)
        cursor1.execute(q_ins3)
        print("Add tuples:\t", q_ins4)
        cursor1.execute(q_ins4)
        connection1.commit()

        q_sel = "SELECT * FROM R;"

        print("Fetch all:\t", q_sel)
        cursor1.execute(q_sel)
        user_all = cursor1.fetchall()
        print("\t\t R(a, b) = ", str(user_all))

        comm = "COMMIT;"
        print("\nCommit:\t\t", comm)
        cursor1.execute(comm)
        connection1.commit()

    instantiate()

    # Transaction 1
    tr1 = "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
    # tr1 = "BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;"
    print("\nU1 (start t1):\t", tr1)
    cursor1.execute(tr1)

    # Transaction 2
    tr2 = "BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
    # tr2 = "BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;"
    print("\nU2 (start t2):\t", tr2)
    cursor2.execute(tr2)

    # a1 a2 b1 b2
    # a1
    a1 = "SELECT SUM(b) FROM R WHERE a = 0;"
    print("Get xval1:\t", a1)
    cursor1.execute(a1)
    xval1 = cursor1.fetchone()[0]
    print("\t\t xval1 = ", xval1)

    # a2
    a2 = "SELECT SUM(b) FROM R WHERE a = 1;"
    print("Get xval2:\t", a2)
    cursor2.execute(a2)
    xval2 = cursor2.fetchone()[0]
    print("\t\t xval2 = ", xval2)

    # b1
    b1 = f"INSERT INTO R Values(1, {xval1});"
    print("Ins xval1:\t", b1)
    cursor1.execute(b1)
    q_sel = "SELECT * FROM R;"
    print("Fetch all:\t", q_sel)
    cursor1.execute(q_sel)
    user_all = cursor1.fetchall()
    print("\t\t R(a, b) = ", str(user_all))
    comm = "COMMIT;"
    print("\nCommit U1:\t\t", comm)
    cursor1.execute(comm)
    # connection1.commit()

    # b2
    b2 = f"INSERT INTO R Values(0, {xval2});"
    print("Ins xval2:\t", b2)
    cursor2.execute(b2)
    q_sel = "SELECT * FROM R;"
    print("Fetch all:\t", q_sel)
    cursor2.execute(q_sel)
    user_all = cursor2.fetchall()
    print("\t\t R(a, b) = ", str(user_all))
    comm = "COMMIT;"
    print("\nCommit U2:\t", comm)
    cursor2.execute(comm)
    # connection2.commit()

    print('\n-------------------------------------------------------------------')



def showall():
    cursor1.execute("SELECT * FROM Sales;");
    connection1.commit()
    print(cursor1.rowcount)
    for i in range(cursor1.rowcount):
        print(cursor1.fetchone())
    #results = cursor1.fetchall()
    #print("Sales relation contents:")
    #for r in results:
    #print(r;)


def close():
    connection1.close()
    connection2.close()


# when calling python filename.py the following functions will be executed:
# drop("Sales")
# init()
# showall()
# scenario1()
# showall()
# close()

drop("ab")
scenario2()
drop("ab")
scenario3()
drop("ab")
scenario4()
drop("ab")
close()

connection1 = pgdb.Connection(**params)
connection1.autocommit=False
cursor1 = connection1.cursor()

connection2 = pgdb.Connection(**params)
connection2.autocommit=False
cursor2 = connection2.cursor()

drop("R")
scenario5()
drop("R")

drop("R")
# a1 a2 b1 b2 is not possible in SERIALIZABLE. Attempts raise an error.
# Were it possible, the end result should be
# a    b
# 0    1
# 0    2
# 1    10
# 1    20
# 1    3
# 0    30
# We can achieve this result setting the isolation mode to READ COMMITTED.
scenario6()
drop("R")

close()
