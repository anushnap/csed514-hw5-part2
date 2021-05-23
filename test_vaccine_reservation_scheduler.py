import unittest
import os

from sql_connection_manager import SqlConnectionManager
from enums import *
from utils import *
from vaccine_reservation_scheduler import VaccineReservationScheduler as scheduler
from vaccine_caregiver import VaccineCaregiver
from COVID19_vaccine import COVID19Vaccine as covid
from VaccinePatient import VaccinePatient as patient

class TestReservationScheduler(unittest.TestCase):

    def test_init(self):
        scheduler()
    
    def test_put_on_hold1_returns_neg2(self):
        """PutOnHold returns -2"""
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            clear_tables(sqlClient)
            # get a cursor from the SQL connection
            with sqlClient.cursor(as_dict=True) as cursor:
                self.assertEqual(scheduler().PutHoldOnAppointment1(cursor), -2)

                # check no updates made to table
                get_schedule_sql = "SELECT * FROM CareGiverSchedule WHERE SlotStatus = 1"
                cursor.execute(get_schedule_sql)
                rows = cursor.fetchall()
                self.assertTrue(len(rows) < 1)
            
            clear_tables(sqlClient)
            
    def test_put_on_hold1(self):
        """PutOnHold returns id"""
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            clear_tables(sqlClient)
            # get a cursor from the SQL connection
            with sqlClient.cursor(as_dict=True) as cursor:
                vc = VaccineCaregiver('Carrie Nation', cursor)
                self.assertEqual(scheduler().PutHoldOnAppointment1(cursor), 0)

                # check 1 update made to table
                get_schedule_sql = "SELECT * FROM CareGiverSchedule WHERE SlotStatus = 1"
                cursor.execute(get_schedule_sql)
                rows = cursor.fetchall()
                self.assertTrue(len(rows) == 1)
            
            clear_tables(sqlClient)

    def test_put_on_hold2(self):
        """PutOnHold2 returns id"""
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            clear_tables(sqlClient)
            # get a cursor from the SQL connection
            with sqlClient.cursor(as_dict=True) as cursor:
                vc = VaccineCaregiver('Carrie Nation', cursor)
                scheduler().PutHoldOnAppointment2(1, 21, cursor)
                
                # check 1 update made to table
                get_schedule_sql = "SELECT * FROM CareGiverSchedule WHERE SlotStatus = 1"
                cursor.execute(get_schedule_sql)
                rows = cursor.fetchall()
                self.assertTrue(len(rows) == 1)

            clear_tables(sqlClient)
    
    def test_put_on_hold2_returns_neg2(self):
        """PutOnHold2 returns -2"""
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            clear_tables(sqlClient)
            # get a cursor from the SQL connection
            with sqlClient.cursor(as_dict=True) as cursor:
                vc = VaccineCaregiver('Carrie Nation', cursor)
                self.assertEqual(scheduler().PutHoldOnAppointment2(1, 100, cursor), -2)
                
                # check no updates made to table
                get_schedule_sql = "SELECT * FROM CareGiverSchedule WHERE SlotStatus = 1"
                cursor.execute(get_schedule_sql)
                rows = cursor.fetchall()
                self.assertTrue(len(rows) < 1)
            
            clear_tables(sqlClient)
    
    def test_schedule_appointment_returns_neg2(self):
        """ScheduleAppointmentSlot returns -2"""
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            clear_tables(sqlClient)
            
            with sqlClient.cursor(as_dict=True) as cursor:
                vc = VaccineCaregiver('Carrie Nation', cursor)
                self.assertEqual(scheduler().ScheduleAppointmentSlot(-1, 1, cursor), -2)
                self.assertEqual(scheduler().ScheduleAppointmentSlot("Not a valid id", 1, cursor), -2)
                get_schedule_sql = "SELECT * FROM CareGiverSchedule WHERE SlotStatus = 2"
                cursor.execute(get_schedule_sql)
                rows = cursor.fetchall()
                self.assertTrue(len(rows) < 1)
            
            clear_tables(sqlClient)
    
    def test_schedule_appointment(self):
        """ScheduleAppointmentSlot returns id"""
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            clear_tables(sqlClient)
            
            with sqlClient.cursor(as_dict=True) as cursor:
                vc = VaccineCaregiver('Carrie Nation', cursor)
                vaccine = covid('Moderna', 'Moderna', 10, 10, 28, 2, cursor)
                
                sqlCreatePatient = "INSERT INTO Patients (PatientName, VaccineStatus) VALUES ("
                sqlCreatePatient += "'Patrick Render', 0)"
                cursor.execute(sqlCreatePatient)

                sqlCreateAppt = "INSERT INTO VaccineAppointments ("
                sqlCreateAppt += "VaccineName, PatientId, CaregiverId, SlotStatus) VALUES ("
                sqlCreateAppt += "'Moderna', "
                sqlCreateAppt += "1, "
                sqlCreateAppt += str(vc.caregiverId) + ", "
                sqlCreateAppt += "1)"
                cursor.execute(sqlCreateAppt)

                self.assertEqual(scheduler().ScheduleAppointmentSlot(1, 0, cursor), 1)

                # Caregiverschedule is updated once
                get_schedule_sql = "SELECT * FROM CareGiverSchedule WHERE SlotStatus = 2"
                cursor.execute(get_schedule_sql)
                rows = cursor.fetchall()
                self.assertTrue(len(rows) == 1)

                # VaccineAppointments table is updated once
                get_appointments_sql = "SELECT * FROM VaccineAppointments WHERE SlotStatus = 2"
                cursor.execute(get_appointments_sql)
                rows = cursor.fetchall()
                self.assertTrue(len(rows) == 1)

            clear_tables(sqlClient)

class TestScenarios(unittest.TestCase):   
    
    def test_main_two_patients(self):
        '''
        Add 2 caregivers, 2 patients, and one vaccine
        Try to schedule patients in order added to db
        Successfully schedule first appointment
        Successfuly hold second appointment
        Successfully reduce vaccine reserve by 4
        '''
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            clear_tables(sqlClient)
            
            with sqlClient.cursor(as_dict=True) as dbcursor:
                vrs = scheduler()

                caregiversList = []
                caregiversList.append(VaccineCaregiver('Carrie Nation', dbcursor))
                caregiversList.append(VaccineCaregiver('Clare Barton', dbcursor))

                vaccine = covid('Moderna', 'Moderna', 0, 0, 28, 2, dbcursor)
                covid.add_doses('Moderna', 5, dbcursor)

                # Add patients
                patientList = []
                patientList.append(patient('Spongebob Squarepants', 0, dbcursor))
                patientList.append(patient('Sandy Cheeks', 0, dbcursor))

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
                        self.fail()

                # Check that transactions went through
                check_patients = "SELECT * FROM Patients"
                check_vaccines = "SELECT * FROM Vaccines"
                check_cgs = "SELECT CaregiverSlotSchedulingId, CaregiverId, WorkDay, SlotStatus, VaccineAppointmentId "
                check_cgs += "FROM CaregiverSchedule where SlotStatus IN (1, 2)"
                check_appts = "SELECT * FROM VaccineAppointments"
                
                # exactly 2 patients
                dbcursor.execute(check_patients)
                rows = dbcursor.fetchall()
                self.assertEqual(len(rows), 2)
                for row in rows:
                    self.assertEqual(row['VaccineStatus'], 2)

                # exactly 1 vaccine, 4 reserved doses, 2 per patient
                dbcursor.execute(check_vaccines)
                rows = dbcursor.fetchall()
                self.assertEqual(len(rows), 1) # exactly 1 vaccine
                self.assertEqual(rows[0]['ReservedDoses'], 4)

                # 4 caregiver slots with slotstatus 1 or 2
                dbcursor.execute(check_cgs)
                rows = dbcursor.fetchall()
                self.assertEqual(len(rows), 4)

                # 4 vaccine appointments
                dbcursor.execute(check_appts)
                rows = dbcursor.fetchall()
                self.assertEqual(len(rows), 4)
        
            clear_tables(sqlClient)
        
    def test_main_five_patients(self):
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            clear_tables(sqlClient)
            
            with sqlClient.cursor(as_dict=True) as dbcursor:
                vrs = scheduler()

                caregiversList = []
                caregiversList.append(VaccineCaregiver('Carrie Nation', dbcursor))
                caregiversList.append(VaccineCaregiver('Clare Barton', dbcursor))

                vaccine = covid('Moderna', 'Moderna', 0, 0, 28, 2, dbcursor)
                covid.add_doses('Moderna', 5, dbcursor)

                # Add patients
                patientList = []
                patientList.append(patient('Spongebob Squarepants', 0, dbcursor))
                patientList.append(patient('Sandy Cheeks', 0, dbcursor))
                patientList.append(patient('Squidward', 0, dbcursor))
                patientList.append(patient('Patrick Star', 0, dbcursor))
                patientList.append(patient('Mr. Krabs', 0, dbcursor))
                
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

                # Check that transactions went through
                check_patients = "SELECT * FROM Patients"
                check_vaccines = "SELECT * FROM Vaccines"
                check_cgs = "SELECT CaregiverSlotSchedulingId, CaregiverId, WorkDay, SlotStatus, VaccineAppointmentId "
                check_cgs += "FROM CaregiverSchedule where SlotStatus IN (1, 2)"
                check_appts = "SELECT * FROM VaccineAppointments"
                
                # exactly 5 patients
                dbcursor.execute(check_patients)
                rows = dbcursor.fetchall()
                self.assertEqual(len(rows), 5)

                # exactly 1 vaccine, 4 reserved doses, 2 per successful patient
                dbcursor.execute(check_vaccines)
                rows = dbcursor.fetchall()
                self.assertEqual(len(rows), 1) # exactly 1 vaccine
                self.assertEqual(rows[0]['ReservedDoses'], 4)

                # 4 caregiver slots with slotstatus 1 or 2
                dbcursor.execute(check_cgs)
                rows = dbcursor.fetchall()
                self.assertEqual(len(rows), 4)

                # 4 vaccine appointments
                dbcursor.execute(check_appts)
                rows = dbcursor.fetchall()
                self.assertEqual(len(rows), 4)
        
            clear_tables(sqlClient)
                
if __name__ == "__main__":
    unittest.main()