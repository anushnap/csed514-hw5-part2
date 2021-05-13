import pymssql
import traceback

class SqlConnectionManager:
    def __init__(self, Server, DBname, UserId, Password):
        self.Server = Server
        self.DBname = DBname
        self.UserId = UserId
        self.Password = Password
        self.SqlConnection = None

    def __enter__(self):
        try:
            self.SqlConnection = pymssql.connect(server=self.Server, 
                                    database=self.DBname, 
                                    user=self.UserId, 
                                    password=self.Password)
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL connection processing! ")
            sqlrc = str(db_err.args[0])
            print("Exception code: " + str(sqlrc))
            if len(db_err) > 1:
                print("Exception message: " + db_err.args[1]) 
        return self.SqlConnection
    
    def Connect(self):
         try:
             self.SqlConnection = pymssql.connect(server=self.Server, 
                 database=self.DBname, 
                 user=self.UserId, 
                 password=self.Password)
         except pymssql.Error as db_err:
            print("Database Programming Error in SQL connection processing! ")
            sqlrc = str(db_err.args[0])
            print("Exception code: " + str(sqlrc))
            if len(db_err) > 1:
                print("Exception message: " + db_err.args[1]) 

    def __exit__(self, exctype=None, excinst=None, exctb=None):
        self.SqlConnection.close()
        if exctype is None:
            print('Program terminated and MS SQL connection closed')
        else:
            print("Exception captured: " + str(exctype))
            callstack = traceback.extract_tb(exctb)
            print(excinst)
            print("stack trace: " + str(callstack))

#==========================================================================
