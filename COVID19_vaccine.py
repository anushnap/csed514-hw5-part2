import pymssql

class COVID19Vaccine:
    '''Adds the Vaccine to the DB'''
    def __init__(self, manufac_name, days_between_doses, doses_in_stock, doses_reserved, cursor):
        # Determine number of doses needed for each vaccine
        if manufac_name == 'Pfizer-BioNTech' or manufac_name == 'Moderna':
        	self.doses_needed = 2
        else:
        	self.doses_needed = 1
        
        self.sqltext = "INSERT INTO Vaccines (ManufactererName, DosesNeeded, DosesInStock, DosesReserved, DaysBetweenDoses) VALUES ('" 
        self.sqltext += manufac_name + "', "
        self.sqltext += str(self.doses_needed) + ", "
        self.sqltext += str(doses_in_stock) + ", "
        self.sqltext += str(doses_reserved) + ", "
        self.sqltext += str(days_between_doses) + ")"
        
        self.VaccineId = 0
        try: 
            cursor.execute(self.sqltext)
            cursor.connection.commit()
            cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
            _identityRow = cursor.fetchone()
            self.VaccineId = _identityRow['Identity']
            # cursor.connection.commit()
            print('Query executed successfully. Vaccine : ' + manufac_name 
            +  ' added to the database using Vaccine ID = ' + str(self.VaccineId))
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Vaccines! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)         
    
    def add_doses(manufac_name, num_doses_added, cursor):
        '''Add doses to the vaccine inventory for a particular vaccine'''
        sqltext = "UPDATE Vaccines SET DosesInStock = DosesInStock + "
        sqltext += str(num_doses_added)
        sqltext += " WHERE ManufactererName = '"
        sqltext += str(manufac_name) + "'"
        
        try: 
            cursor.execute(sqltext)
            cursor.connection.commit()
            print("Query executed successfully.")
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Vaccines! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqltext)


    def reserve_doses(manufac_name, cursor):
        '''reserve the vaccine doses associated with a specific patient who is being scheduled for vaccine administration'''
        sqltext1 = "SELECT DosesInStock, DosesReserved FROM Vaccines WHERE ManufactererName = '"
        sqltext1 += str(manufac_name) + "'"
        
        #get doses in stock and doses reserved
        try: 
            cursor.execute(sqltext1)
            rows = cursor.fetchall()
            doses_in_stock = 0
            doses_reserved = 0
            
            for row in rows:
                doses_in_stock += row['DosesInStock']
                doses_reserved += row['DosesReserved']
            
            print("Query executed successfully.")
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for ReserveDoses")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqltext)

        if manufac_name == 'Pfizer-BioNTech' or 'Moderna':
            #check if there are enough in stock and reserve
            if doses_in_stock >= 2:
                doses_reserved += 2
                doses_in_stock -= 2
            elif doses_in_stock == 1:
                doses_reserved += 1
                doses_in_stock -= 1
                print("WARNING: STOCK LOW. ONLY ONE DOSE RESERVED")
            else:
                print("WARNING: Not enough vaccines in stock!")
        else:
            #check if there are enough in stock and reserve
            if doses_in_stock >= 1:
                doses_reserved += 1
                doses_in_stock -= 1
            else:
                print("WARNING: Not enough vaccines in stock!")
        
        sqltext2 = "UPDATE VACCINES SET DosesInStock = "
        sqltext2 += str(doses_in_stock) + ", DosesReserved = "
        sqltext2 += str(doses_reserved) + " WHERE ManufactererName = '"
        sqltext2 += manufac_name + "'"

        try: 
            cursor.execute(sqltext2)
            cursor.connection.commit()
            print("Query executed successfully.")
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for ReserveDoses! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqltext)