import sqlite3


class DBHelper:
    def __init__(self, dbname="todo.sqlite"):
        # takes a database name (by default store our data in a file called todo.sqlite) and creates a database connection.
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        # creates a new table called items in our database. This table has one column (called description)
        print("running setup...creating tables...")
        # Adding database indexes
        tblstmt = "CREATE TABLE IF NOT EXISTS items (description text, owner text)"
        itemidx = "CREATE INDEX IF NOT EXISTS itemIndex ON items (description ASC)" 
        ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON items (owner ASC)"
        self.conn.execute(tblstmt)
        self.conn.execute(itemidx)
        self.conn.execute(ownidx)
        self.conn.commit()


    def add_item(self, item_text, owner):
        # takes the text for the item and inserts it into our database table, according to the chat id (owner).
        stmt = "INSERT INTO items (description, owner) VALUES (?, ?)"
        args = (item_text, owner)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_item(self, item_text, owner):
        # deletes items that match and that belong to the indicated owner
        stmt = "DELETE FROM items WHERE description = (?) AND owner = (?)"
        args = (item_text, owner )
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_items(self, owner):
        # return the items that belong to the specified owner. We use a list comprehension to take the first element of each item, 
        # as SQLite will always return data in a tuple format, even when there is only one column, 
        # so in this example each item we retrieve from the database will be similar to ("buy groceries", ) (a tuple) 
        # which the list comprehension converts to "buy groceries" (a simple string).
        stmt = "SELECT description FROM items WHERE owner = (?)"
        args = (owner, )
        return [x[0] for x in self.conn.execute(stmt, args)]