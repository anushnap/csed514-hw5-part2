import unittest
import os

from sql_connection_manager import SqlConnectionManager
from enums import *
from utils import *
from vaccine_reservation_scheduler import VaccineReservationScheduler as scheduler
from vaccine_caregiver import VaccineCaregiver
from COVID19_vaccine import COVID19Vaccine as covid

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

                self.assertEqual(scheduler().ScheduleAppointmentSlot(1, 1, cursor), 1)

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

if __name__ == "__main__":
    unittest.main()