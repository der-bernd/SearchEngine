import mysql.connector
from mysql.connector import Error
import unittest
from dotenv import load_dotenv
import os
load_dotenv()


class MySqlConnector:

    def __init__(self, *args, **kwargs):
        host = os.getenv("DB_HOST")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASS")
        db = os.getenv("DB_NAME")

        try:
            self.conn = mysql.connector.connect(
                host=host, user=user, password=password, db=db)
        except Error as e:
            print("CANNOT CONNECT TO DB: {}".format(e))
            return

    def execute_test_query(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM test WHERE ID = 0")
        cursor.fetchone()

        result = cursor.fetchall()
        cursor.close()
        return result

    def query(self, query: str, params: tuple = ()) -> list[tuple]:
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        self.conn.commit()
        cursor.close()

        return result


class SimpleTest(unittest.TestCase):

    # Returns True or False.
    def test(self, *args, **kwargs):
        self.assertTrue(True)

    # returns True if queries can be executed
    def test_conn(self, *args, **kwargs):
        conn = MySqlConnector()
        result = conn.execute_test_query()
        self.assertEqual(result, [])

    def test_query_with_args(self, *args, **kwargs):
        conn = MySqlConnector()
        result = conn.query(
            "SELECT * FROM test WHERE ID = %s", (1,))
        self.assertEqual(result, [(1,)])

    def test_query_select_all(self, *args, **kwargs):
        conn = MySqlConnector()
        result = conn.query("SELECT * FROM test WHERE ID < 10")
        self.assertEqual(result, [(1,), (2,)])

    def test_insert_and_delete(self, *args, **kwargs):
        """
        Just to test if the insert and delete works.
        Insert a new row and delete it.
        """
        conn = MySqlConnector()
        id = 99
        conn.query("INSERT INTO test (ID) VALUES (%s)", (id,))
        result = conn.query("SELECT ID FROM test WHERE ID = %s", (id,))

        self.assertEqual(result, [(99,)])

        conn.query("DELETE FROM test WHERE ID = %s", (id,))
        result = conn.query("SELECT ID FROM test WHERE ID = %s", (id,))
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
