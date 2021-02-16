from PyQt5 import QtWidgets, uic, QtCore
import sys
from config import HOST, USERNAME, PASS
from mysql.connector import connect, Error


def error_message(message):
    error_dialog = QtWidgets.QErrorMessage()

    error_dialog.showMessage(message)
    error_dialog.exec_()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('ui.ui', self)
        self.show()
        self.addButton.clicked.connect(self.add_item)
        self.connect_to_db()
        self.init_table()

    def connect_to_db(self):
        try:
            self.connection = connect(host=HOST, user=USERNAME, password=PASS)
            select_db_query = "SELECT * FROM wishlist.maintable"
            self.cursor = self.connection.cursor()
            self.cursor.execute(select_db_query)
        except Error as e:
            print(e)

    def init_table(self):
        self.table.setHorizontalHeaderLabels(["Id", "Name", "Price", "Link", "Note", "Edit", "Delete"])

        # fill table with elements from DB
        row_number = 0
        for db in self.cursor:
            self.table.insertRow(self.table.rowCount())

            for index in range(0, 5):
                item1 = QtWidgets.QTableWidgetItem(str(db[index]))
                self.table.setItem(row_number, index, item1)

            #delete and edit buttons in each row
            self.btn_edit = QtWidgets.QPushButton('Edit')
            self.btn_edit.clicked.connect(self.edit_item)
            self.table.setCellWidget(row_number, 5, self.btn_edit)

            self.btn_delete = QtWidgets.QPushButton('Delete')
            self.btn_delete.clicked.connect(self.delete_item)
            self.table.setCellWidget(row_number, 6, self.btn_delete)
            row_number += 1

    def delete_item(self):

        button = QtWidgets.qApp.focusWidget()
        index = self.table.indexAt(button.pos())

        delete_db_query = f"DELETE FROM wishlist.maintable WHERE id={self.table.item(index.row(), 0).text()}"

        try:
            self.cursor.execute(delete_db_query)
            self.connection.commit()
        except Error as e:
            print(e)
        self.table.removeRow(index.row())

    def edit_item(self):
        button = QtWidgets.qApp.focusWidget()
        index = self.table.indexAt(button.pos())

        #validation
        name = self.table.item(index.row(), 1).text() if isinstance(self.table.item(index.row(), 1).text(), str)\
            else error_message('name должен быть строкой!')
        try:
            price = float(self.table.item(index.row(), 2).text())
        except Exception:
            error_message('Кажется, price не число')
        link = self.table.item(index.row(), 3).text()
        note = 'NULL' if self.table.item(index.row(), 4).text() == '' else self.table.item(index.row(), 4).text()

        edit_db_query = f"UPDATE wishlist.maintable SET " \
                        f"name = '{name}', " \
                        f"price = '{price}', " \
                        f"link = '{link}', " \
                        f"note = '{note}' " \
                        f"WHERE id = '{self.table.item(index.row(), 0).text()}'"
        try:
            self.cursor.execute(edit_db_query)
            self.connection.commit()
        except Error as e:
            print(e)

    def add_item(self):

        name = self.textEdit.toPlainText() if isinstance(self.textEdit_2.toPlainText(), str) \
            else error_message('name должен быть строкой!')

        try:
            price = float(self.textEdit_2.toPlainText())
        except Exception:
            error_message('Кажется, price не число')

        link = self.textEdit_3.toPlainText()
        note = 'NULL' if self.textEdit_4.toPlainText() == '' else self.textEdit_4.toPlainText()

        add_db_query = f"INSERT INTO wishlist.maintable " \
                       f"(name, price, link, note) VALUES " \
                       f"('{name}', '{price}', '{link}', '{note}')"

        try:
            self.cursor.execute(add_db_query)
            self.connection.commit()
            self.init_table()
        except Error as e:
            print(e)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec_()
