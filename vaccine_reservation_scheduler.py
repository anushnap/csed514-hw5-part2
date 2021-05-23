from datetime import datetime
from datetime import timedelta
from enum import IntEnum
import os
import pymssql
import traceback

from sql_connection_manager import SqlConnectionManager
from vaccine_caregiver import VaccineCaregiver
from enums import *
from utils import *
from COVID19_vaccine import COVID19Vaccine as covid
from VaccinePatient import VaccinePatient as patient


class VaccineReservationScheduler:

    def __init__(self):
        return None

    def PutHoldOnAppointment1(self, cursor):
        ''' Method that reserves a CareGiver appointment slot &
        returns the unique scheduling slotid for first dose shot
        Returns -2 if no slot is available
        Returns -1 if there is a database error'''

        # Get first available caregiver appointment slot
        self.slotSchedulingId = 0
        self.getAppointmentSQL = "SELECT TOP 1 CaregiverSlotSchedulingId FROM CareGiverSchedule WHERE SlotStatus = 0 " 
        self.getAppointmentSQL += "ORDER BY WorkDay ASC, SlotHour ASC, SlotMinute ASC"

        try:
            cursor.execute(self.getAppointmentSQL)
            rows = cursor.fetchall()
            self.slotSchedulingId = rows[0]['CaregiverSlotSchedulingId'] # first open slot in db

            # Put appointment on hold 
            self.put_on_hold_sql = "UPDATE CareGiverSchedule "
            self.put_on_hold_sql += "SET SlotStatus = 1 "
            self.put_on_hold_sql += "WHERE CaregiverSlotSchedulingId = " + str(self.slotSchedulingId)
            cursor.execute(self.put_on_hold_sql)

            return self.slotSchedulingId

        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])           
            print("SQL text that resulted in an Error: " + self.getAppointmentSQL)
            return -1
        
        # No appointments available
        except IndexError as idx_err:
            print("There are no available appointments at this time.")
            return -2

    def PutHoldOnAppointment2(self, caregiver_slotid_first_dose, days_between_doses, cursor):
        ''' Method that reserves a CareGiver appointment slot &
        returns the unique scheduling slotid for second dose shot
        Returns -2 if no slot is available
        Returns -1 if there is a database error'''

        # Get datetime from first dose
        getDateSQL = "SELECT WorkDay from CareGiverSchedule WHERE "
        getDateSQL += "CaregiverSlotSchedulingId = " + str(caregiver_slotid_first_dose)

        try:
            cursor.execute(getDateSQL)
            row = cursor.fetchone()
            first_dose_date = row['WorkDay']
            
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])           
            print("SQL text that resulted in an Error: " + getAppointmentSQL)
            
        # Calculate minimum date of next appointment
        date_next_dose = datetime.fromisoformat(first_dose_date) + timedelta(days = days_between_doses)
        date_next_dose_fmt = date_next_dose.strftime('%Y-%m-%d')
        self.slotSchedulingId = 0
        self.getAppointmentSQL = "SELECT TOP 1 CaregiverSlotSchedulingId FROM CareGiverSchedule WHERE SlotStatus = 0 " 
        self.getAppointmentSQL += "AND WorkDay >= '" + date_next_dose_fmt + "' " 
        self.getAppointmentSQL += "ORDER BY WorkDay ASC, SlotHour ASC, SlotMinute ASC"
        
        try:
            # Get first available slotschedulingid
            cursor.execute(self.getAppointmentSQL)
            row = cursor.fetchone()
            
            # Return -2 if no available slotschedulingid, else return slotschedulingid.
            if row is None:
                print("There are no available appointments at this time.")
                return -2
            else: 
                # Put appointment slot on hold 
                self.slotSchedulingId = row['CaregiverSlotSchedulingId']
                self.put_on_hold_sql = "UPDATE CareGiverSchedule "
                self.put_on_hold_sql += "SET SlotStatus = 1 "
                self.put_on_hold_sql += "WHERE CaregiverSlotSchedulingId = " + str(self.slotSchedulingId)
                cursor.execute(self.put_on_hold_sql)

                return self.slotSchedulingId
        
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])           
            print("SQL text that resulted in an Error: " + getAppointmentSQL)
            return -1

    def ScheduleAppointmentSlot(self, 
                                caregiver_slotid,
                                appointment_id,
                                cursor):
        '''Marks a slot on Hold with a definite reservation in CaregiverSchedule and VaccineAppointments.  
        slotid is the caregiver slot id that is currently on Hold and whose status will be updated 
        returns the same slotid when the database update succeeds
        returns -1 is there if the database update fails 
        returns -2 if the slotid parm is invalid '''

        if isinstance(caregiver_slotid, int) is False:
            return -2
        elif caregiver_slotid < 0:
            return -2

        self.slotSchedulingId = caregiver_slotid
        self.appointment_id = appointment_id

        # Update the CaregiverSchedule table from Hold to Scheduled
        self.updateCaregiverSql = "UPDATE CaregiverSchedule "
        self.updateCaregiverSql += "SET SlotStatus = 2 "
        self.updateCaregiverSql += "WHERE CaregiverSlotSchedulingId = "
        self.updateCaregiverSql += str(caregiver_slotid)
        
        try:
            cursor.execute(self.updateCaregiverSql)
        
        except pymssql.Error as db_err:    
            print("Database Programming Error in SQL Query processing! ")
            print("Exception code: " + db_err.args[0])
            if len(db_err.args) > 1:
                print("Exception message: " + str(db_err.args[1]))  
            print("SQL text that resulted in an Error: " + self.updateCaregiverSql)
            return -1
        
        # Update VaccineAppointments table from Hold to Scheduled
        self.updateAppointmentSql = "UPDATE VaccineAppointments "
        self.updateAppointmentSql += "SET SlotStatus = 2 "
        self.updateAppointmentSql += "WHERE VaccineAppointmentId = " + str(appointment_id)

        try:
            cursor.execute(self.updateAppointmentSql)
            print("Slot statuses updated from hold to scheduled.")
        
        except pymssql.Error as db_err:    
            print("Database Programming Error in SQL Query processing! ")
            print("Exception code: " + db_err.args[0])
            if len(db_err.args) > 1:
                print("Exception message: " + str(db_err.args[1]))  
            print("SQL text that resulted in an Error: " + self.updateAppointmentSql)
            return -1
        
        return self.slotSchedulingId

if __name__ == '__main__':
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            clear_tables(sqlClient)
            vrs = VaccineReservationScheduler()

            # get a cursor from the SQL connection
            with sqlClient.cursor(as_dict=True) as dbcursor:
                # Initalize the caregivers, patients & vaccine supply
                caregiversList = []
                caregiversList.append(VaccineCaregiver('Carrie Nation', dbcursor))
                caregiversList.append(VaccineCaregiver('Clare Barton', dbcursor))
                caregivers = {}
                for cg in caregiversList:
                    cgid = cg.caregiverId
                    caregivers[cgid] = cg

                # Add a vaccine and Add doses to inventory of the vaccine
                vaccine = covid('Moderna', 'Moderna', 0, 0, 28, 2, dbcursor)
                covid.add_doses('Moderna', 5, dbcursor)

                # Add patients
                patientList = []
                patientList.append(patient('Spongebob Squarepants', 0, dbcursor))
                patientList.append(patient('Sandy Cheeks', 0, dbcursor))
                patientList.append(patient('Squidward', 0, dbcursor))
                patientList.append(patient('Patrick Star', 0, dbcursor))
                patientList.append(patient('Mr. Krabs', 0, dbcursor))
                patients = {}
                for pt in patientList:
                    ptid = pt.patientId
                    patients[ptid] = pt

            with sqlClient.cursor(as_dict = True) as dbcursor:
            # Schedule the patients
                for p in patientList:
                    try:
                        # PutHoldOn
                        cg_first_slot = vrs.PutHoldOnAppointment1(dbcursor)
                        # Reserve appointment
                        first_appt = p.ReserveAppointment(cg_first_slot, vaccine, dbcursor)
                        # Schedule appointment
                        p.ScheduleAppointment(cg_first_slot, first_appt, vaccine, dbcursor)
                        # commit
                        dbcursor.connection.commit()
                    except Exception as e:
                        err_str = "Oops! An exception occurred. The transaction for patient "
                        err_str += str(p.patientId) + ": " + str(p.patientName) + " "
                        err_str += "was rolled back."
                        print(err_str)
                        print(e)
                        dbcursor.connection.rollback()

            # Test cases done!
            # clear_tables(sqlClient)