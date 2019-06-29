import sqlite3

# Credit: https://github.com/swip3798/SqliteDictionaryWrapper
# Modified to handle single quotes and unicode

class colors:
    green = '\033[1;32;40m'
    red = '\033[1;31;40m'
    reset = '\033[0m'
    grey = '\033[1;30;40m'
    white = '\033[1;39;40m'

def dict_factory(cursor, row):

    # Internal Method for the row factor
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class DataBase:



    def __init__(self, filename):

        self.filename = filename
        conn = sqlite3.connect(filename)
        conn.text_factory = bytes
        conn.commit()
        conn.close()

    def makeTable(self,tablename, dictionary, id_col):
        statement = "CREATE TABLE "
        statement += tablename + " ("
        conn = sqlite3.connect(self.filename)
        conn.text_factory = bytes
        c = conn.cursor()
        for i in dictionary:
            if type(dictionary[i]) is str:
                statement += str(i) + " text,"
            elif type(dictionary[i]) is int:
                statement += str(i) + " int,"
            elif type(dictionary[i]) is float:
                statement += str(i) + " real,"
        statement += "UNIQUE(" + id_col + ")"
        statement += ")"
        try:
            c.execute(statement)
        except Exception as e:
            print(e)
        conn.commit()
        conn.close()


    def insert(self, tablename, row, update = False):
        # print('### FILE NAME: ' + str(self.filename))
        conn = sqlite3.connect(self.filename)
        conn.text_factory = bytes
        c = conn.cursor()
        if update:
            statement = "INSERT OR REPLACE INTO "
        else:
            #statement = "INSERT OR IGNORE INTO "
            statement = "INSERT INTO "

        if type(row) is list or type(row) is tuple:
            if any((isinstance(el, list) or isinstance(el, tuple)) for el in row):
                statement += tablename + " VALUES ("
                for i in row[0]:
                    statement += "?,"
                statement = statement[:-1] + ")"
                c.executemany(statement, row)
            elif any((isinstance(el, dict)) for el in row):
                statement += tablename + " VALUES ("
                for i in row[0]:
                    statement += "?,"
                statement = statement[:-1] + ")"

                for i in row:
                    c.execute(statement, list(i.values()))
            else:
                statement += tablename + " VALUES ("
                for i in row:
                    statement += "?,"
                statement = statement[:-1] + ")"

                c.executemany(statement, row)
        else:

            statement += tablename + "("
            values = "("
            n = 1
            for i in row:
                if n + 1 <= len(row):
                    #print('TYPE: ' + str(type(row[i])))
                    statement += i + ", "
                    if type is unicode or type is str:
                        values += '"' + unicode(row[i]).encode('utf-8').strip().replace("'", "\'") + '", '
                    else:
                        #print('TYPE: ' + str(type(row[i])))

                        values += '"' + unicode(row[i]).encode('utf-8') + '", '
                else:
                    #print('TYPE: ' + str(type(row[i])))
                    statement += i + ") "
                    if type is unicode or type is str:
                        values += '"' + unicode(row[i]).encode('utf-8').strip().replace("'", "\'") + '")'
                    else:
                        values += '"' + unicode(row[i]).encode('utf-8') + '")'
                n += 1

            statement += " VALUES " + values

            try:
                c.execute(statement)
            except sqlite3.IntegrityError as e:
                if 'UNIQUE' in str(e):
                    return {'result': False, 'reason': 'dupe', 'sql': statement, 'error': str(e)}

                elif 'NOT NULL' in str(e):
                    print(colors.red + '## STATEMENT ERROR ## ' + colors.reset + statement + ' ' +  str(e))
                    return {'result': False, 'reason': 'statement', 'sql': statement, 'error': str(e)}

                else:
                    print(colors.red + '## FATAL ERROR ## ' + colors.reset + statement + ' ' +  str(e))
                    return {'result': False, 'reason': 'fatal_error', 'sql': statement, 'error': str(e)}

            except sqlite3.OperationalError as e:
                print(colors.red + '## FATAL ERROR ## ' + colors.reset + statement + ' ' +  str(e))
                print("#SQL# STATEMENT: " + statement)
                return {'result': False, 'reason': 'op_error', 'sql': statement, 'error': str(e)}

            """
            statement += tablename + " VALUES ("

            for i in row:
                statement += i+","  # "?,"
            statement = statement[:-1] + ")"

            print(statement + '\n' + str(list(row.values())))

            c.execute(statement, list(row.values()))
            """

        conn.commit()
        conn.close()
        return True

    def execute(self, statement, params=(), mode=dict):
        conn = sqlite3.connect(self.filename)
        conn.text_factory = bytes
        if mode == dict:
            conn.row_factory = dict_factory
        c = conn.cursor()
        results = c.execute(statement, params)
        table = c.fetchall()
        conn.commit()
        conn.close()
        return table