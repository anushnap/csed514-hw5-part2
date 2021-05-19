import pymssql

class COVID19Vaccine:
    '''Adds the Vaccine to the DB'''
    def __init__(self,
                 vaccine_name,
                 manufac_name,
                 doses_in_stock,
                 doses_reserved,
                 days_between_doses,
                 doses_per_patient,
                 cursor):
        # Determine number of doses needed for each vaccine
        self.sqltext = "INSERT INTO Vaccines ("
        self.sqltext += "VaccineName, VaccineSupplier, AvailableDoses, "
        self.sqltext += "ReservedDoses, TotalDoses, DosesPerPatient, "
        self.sqltext += "DaysBetweenDoses) VALUES ("
        self.sqltext += "'" + vaccine_name + "', "
        self.sqltext += "'" + manufac_name + "', "
        self.sqltext += str(doses_in_stock) + ", "
        self.sqltext += str(doses_reserved) + ", "
        self.sqltext += str(doses_in_stock + doses_reserved) + ", "
        self.sqltext += str(doses_per_patient) + ", "
        self.sqltext += str(days_between_doses) + ")"
        
        try: 
            cursor.execute(self.sqltext)
            cursor.connection.commit()
            # cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
            # _identityRow = cursor.fetchone()
            # self.VaccineId = _identityRow['Identity']
            # # cursor.connection.commit()
            print('Query executed successfully. Vaccine : ' + vaccine_name +  ' added to the database')
        
        except pymssql.Error as db_err:
            cursor.connection.rollback()
            print("Database Programming Error in SQL Query processing for Vaccines!")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)         
    
    def add_doses(vaccine_name, num_doses_added, cursor):
        '''Add doses to the vaccine inventory for a particular vaccine'''
        sqltext = "UPDATE Vaccines SET AvailableDoses = AvailableDoses + "
        sqltext += str(num_doses_added)
        sqltext += " WHERE VaccineName = '"
        sqltext += str(vaccine_name) + "'"
        
        try: 
            cursor.execute(sqltext)
            cursor.connection.commit()
            print("Query executed successfully.")
        
        except pymssql.Error as db_err:
            cursor.connection.rollback()
            print("Database Programming Error in SQL Query processing for Vaccines!")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqltext)

    def reserve_doses(vaccine_name, cursor):
        '''reserve the vaccine doses associated with a specific patient who is being scheduled for vaccine administration'''
        sqltext1 = "SELECT AvailableDoses, ReservedDoses, DosesPerPatient FROM Vaccines WHERE VaccineName = '"
        sqltext1 += str(vaccine_name) + "'"
        
        #get doses in stock and doses reserved
        try: 
            cursor.execute(sqltext1)
            rows = cursor.fetchall()
            doses_in_stock = 0
            doses_reserved = 0
            doses_needed = 0
            
            for row in rows:
                doses_in_stock += row['AvailableDoses']
                doses_reserved += row['ReservedDoses']
                doses_needed += row['DosesPerPatient']
            
            print("Query executed successfully.")
        
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for ReserveDoses")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqltext)

        if doses_needed == 2:
            #check if there are enough in stock and reserve
            if doses_in_stock >= 2:
                doses_reserved += 2
                doses_in_stock -= 2
            else:
                print("WARNING: Not enough vaccines in stock! CANNOT RESERVE")
        else:
            #check if there are enough in stock and reserve
            if doses_in_stock >= 1:
                doses_reserved += 1
                doses_in_stock -= 1
            else:
                print("WARNING: Not enough vaccines in stock! CANNOT RESERVE")
        
        sqltext2 = "UPDATE VACCINES SET AvailableDoses = "
        sqltext2 += str(doses_in_stock) + ", ReservedDoses = "
        sqltext2 += str(doses_reserved) + ", TotalDoses = "
        sqltext2 += str(doses_in_stock + doses_reserved) + " WHERE VaccineName = '"
        sqltext2 += vaccine_name + "'"

        try: 
            cursor.execute(sqltext2)
            cursor.connection.commit()
            print("Query executed successfully.")
        
        except pymssql.Error as db_err:
            cursor.connection.rollback()
            print("Database Programming Error in SQL Query processing for ReserveDoses!")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqltext)

    def deplete_reserve(vaccine_name, cursor):
        """ Remove 1 vaccine from reserved amount after successful appointment """
        '''reserve the vaccine doses associated with a specific patient who is being scheduled for vaccine administration'''
        sqltext = "UPDATE Vaccines SET ReservedDoses = ReservedDoses - 1 "
        sqltext += "WHERE VaccineName = '" + vaccine_name + "'"
        
        try: 
            cursor.execute(sqltext)
            cursor.connection.commit()
            print("Query executed successfully.")
        
        except pymssql.Error as db_err:
            cursor.connection.rollback()
            print("Database Programming Error in SQL Query processing for ReserveDoses")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqltext)