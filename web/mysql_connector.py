from sqlite3 import InterfaceError
import mysql.connector
from mysql.connector import Error
import unittest
from dotenv import load_dotenv
import os
from mysql.connector import errorcode
load_dotenv()

db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

class MySqlConnector(object):

    def __init__(self, *args, **kwargs):
        try:
            conn = mysql.connector.connect(**db_config)
        except mysql.connector.Error as e:
            if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password: {}, E: {}".format((db_config, e)))
            elif e.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist with given config: {}, E: {}".format((db_config, e)))
            else:
                print(e)
        if not conn.is_connected():
            raise Error(f"could not establish connection with config: {db_config}")
        self.conn = conn

    def execute_test_query(self) -> list[tuple]:
        """
        This query here is just for testing purposes.
        It should return an empty list since there won't be a record with ID 0.
        """
        result = self.query("SELECT * FROM test WHERE ID = 0")

        return result

    def query(self, query: str, params: tuple = (), commit=True) -> list[tuple]:
        """
        Executes the given query with the params.
        If there are records to be returned, returns them as a list of tuples.
        """
        conn = self.conn
        if not conn.is_connected():
            raise Error(f"could not re-establish connection with given config: {db_config}")
        cursor = conn.cursor(prepared=True)
        cursor.execute(query, params)

        try:
            result = cursor.fetchall()
        except InterfaceError as e:
            # unfortunately, the cursor.fetchall() method throws an InterfaceError if there are no records to be returned
            result = []
        
        if commit:
            conn.commit()
        
        cursor.close()

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
                   (ID,))
        result = conn.query("SELECT ID FROM test WHERE ID = %s", (ID,))

        self.assertEqual(result, [(99,)])

        conn.query("DELETE FROM test WHERE ID = %s", (ID,))
        result = conn.query("SELECT ID FROM test WHERE ID = %s", (ID,))
        self.assertEqual(result, [])


if __name__ == '__main__':
    unittest.main()
