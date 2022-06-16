import mysql.connector
from mysql.connector import Error
import unittest
from dotenv import load_dotenv
import os
load_dotenv()


class MySqlConnector(object):

    def __init__(self, *args, **kwargs):
        host = os.getenv("DB_HOST")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        db = os.getenv("DB_NAME")

        try:
            self.db = mysql.connector.connect(
                host=host, user=user, password=password, db=db)
            self.cursor = self.db.cursor(buffered=True)
        except Error as e:
            print("CANNOT CONNECT TO DB: {}".format(e))
            return

    def execute_test_query(self) -> list[tuple]:
        cursor = self.cursor
        cursor.execute("SELECT * FROM test WHERE ID = 0")
        self.db.commit()

        result = [row for row in cursor.fetchall()]
        return result

    def query(self, query: str, params: tuple = (), commit=False, no_fetchall=False) -> list[tuple]:
        """
        Executes the given query with the params.
        If that is a SELECT query, it returns the result as a list of tuples.
        If that is a INSERT query, it returns the last inserted id as an int.
        You can switch between INSERT and SELECT by setting no_fetchall.
        """
        cursor = self.cursor
        cursor.execute(query, params)
        self.db.commit()

        if no_fetchall:
            return cursor.lastrowid
        else:
            result = [row for row in cursor.fetchall()]
            return result


class SimpleTest(unittest.TestCase):

    def setUp(self) -> None:
        self.conn = MySqlConnector()

    # Returns True or False.
    def test(self, *args, **kwargs):
        self.assertTrue(True)

    # returns True if queries can be executed
    def test_conn(self, *args, **kwargs):
        conn = self.conn
        result = conn.execute_test_query()
        self.assertEqual(result, [])

    def test_query_with_args(self, *args, **kwargs):
        conn = self.conn
        result = conn.query(
            "SELECT * FROM test WHERE ID = %s", (1,))
        self.assertEqual(result, [(1,)])

    def test_query_select_all(self, *args, **kwargs):
        conn = self.conn
        result = conn.query("SELECT * FROM test WHERE ID < 10")
        self.assertEqual(result, [(1,), (2,)])

    def test_insert_and_delete(self, *args, **kwargs):
        """
        Just to test if the insert and delete works.
        Insert a new row and delete it.
        """
        conn = self.conn
        ID = 99
        conn.query("INSERT INTO test (ID) VALUES (%s)",
                   (ID,), no_fetchall=True)
        result = conn.query("SELECT ID FROM test WHERE ID = %s", (ID,))

        self.assertEqual(result, [(99,)])

        conn.query("DELETE FROM test WHERE ID = %s", (ID,), no_fetchall=True)
        result = conn.query("SELECT ID FROM test WHERE ID = %s", (ID,))
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
