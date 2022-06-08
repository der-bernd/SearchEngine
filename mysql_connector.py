import unittest

import MySQLdb


class MySqlConnector:
    db = MySQLdb.connect("localhost", "webcrawler_db_user",
                         "jmyGxtBUneh9", "webcrawler")

    def __init__(self):
        pass

    def execute_test_query(self):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM test")
        result = cursor.fetchall()
        return result

    def execute_query(self, query):
        cursor = self.db.cursor()
        cursor.execute(query)
        self.db.commit()
        return cursor.fetchall()


class SimpleTest(unittest.TestCase):

    # Returns True or False.
    def test(self):
        self.assertTrue(True)

    # returns True if queries can be executed
    def test_conn(self):
        conn = MySqlConnector()
        result = conn.execute_test_query()
        print(result)
        self.assertEqual(result, ())


if __name__ == '__main__':
    unittest.main()
