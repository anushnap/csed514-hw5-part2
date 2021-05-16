import datetime
from enum import IntEnum
import os
import pymssql
import traceback

from sql_connection_manager import SqlConnectionManager
from vaccine_caregiver import VaccineCaregiver
from enums import *
from utils import *
from COVID19_vaccine import COVID19Vaccine as covid
# from vaccine_patient import VaccinePatient as patient


class VaccineReservationScheduler:

    def __init__(self):
        return None

    def PutHoldOnAppointmentSlot(self,cursor):
        ''' Method that reserves a CareGiver appointment slot &
        returns the unique scheduling slotid
        Should return 0 if no slot is available  or -1 if there is a database error'''
        # Note to students: this is a stub that needs to replaced with your code
        self.slotSchedulingId = 0
        self.getAppointmentSQL = "SELECT CaregiverSlotSchedulingId FROM CareGiverSchedule WHERE SlotStatus = 0"
        try:
            cursor.execute(self.getAppointmentSQL)
            rows = cursor.fetchall()
            self.slotSchedulingId = rows[0] # first open slot in db
            return self.slotSchedulingId['CaregiverSlotSchedulingId']
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])           
            print("SQL text that resulted in an Error: " + self.getAppointmentSQL)
            cursor.connection.rollback()
            return -1
        except IndexError as idx_err:
            print("There are no available appointments at this time.")
            return 0

    def ScheduleAppointmentSlot(self, slotid, cursor):
        '''method that marks a slot on Hold with a definite reservation  
        slotid is the slot that is currently on Hold and whose status will be updated 
        returns the same slotid when the database update succeeds 
        returns 0 is there if the database update fails 
        returns -1 the same slotid when the database command fails
        returns 21 if the slotid parm is invalid '''
        # Note to students: this is a stub that needs to replaced with your code
        if slotid < 1:
            return -2
        self.slotSchedulingId = slotid
        self.getAppointmentSQL = "SELECT * FROM CareGiverSchedule"
        try:
            cursor.execute(self.getAppointmentSQL)
            return self.slotSchedulingId
        except pymssql.Error as db_err:    
            print("Database Programming Error in SQL Query processing! ")
            print("Exception code: " + db_err.args[0])
            if len(db_err.args) > 1:
                print("Exception message: " + str(db_err.args[1]))  
            print("SQL text that resulted in an Error: " + self.getAppointmentSQL)
            return -1

if __name__ == '__main__':
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            clear_tables(sqlClient)
            vrs = VaccineReservationScheduler()

            # get a cursor from the SQL connection
            dbcursor = sqlClient.cursor(as_dict=True)

            # Iniialize the caregivers, patients & vaccine supply
            caregiversList = []
            caregiversList.append(VaccineCaregiver('Carrie Nation', dbcursor))
            caregiversList.append(VaccineCaregiver('Clare Barton', dbcursor))
            caregivers = {}
            for cg in caregiversList:
                cgid = cg.caregiverId
                caregivers[cgid] = cg

            # Add a vaccine and Add doses to inventory of the vaccine
            vaccines_list = []
            vaccines_list.append(covid('Moderna', 'Moderna', 0, 0, 28, 2, dbcursor))
            vaccines_list.append(covid('Pfizer', 'Pfizer-BioNTech', 0, 0, 21, 2, dbcursor))
            vaccines_list.append(covid('J&J', 'Johnson & Johnson/Janssen', 0, 0, 0, 1, dbcursor))
            covid.add_doses('Moderna', 100, dbcursor)
            covid.add_doses('Pfizer', 150, dbcursor)
            covid.add_doses('J&J', 50, dbcursor)

            # Add patients
            # Schedule the patients
            
            # Test cases done!
            clear_tables(sqlClient)
