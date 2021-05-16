import unittest
import os

from sql_connection_manager import SqlConnectionManager
from enums import *
from utils import *
from vaccine_reservation_scheduler import VaccineReservationScheduler as scheduler
from vaccine_caregiver import VaccineCaregiver

class TestReservationScheduler(unittest.TestCase):

    def test_init(self):
        scheduler()
    
    def test_put_on_hold_returns_neg2(self):
        """PutOnHold returns -2"""
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            clear_tables(sqlClient)
            # get a cursor from the SQL connection
            with sqlClient.cursor(as_dict=True) as cursor:
                self.assertEqual(scheduler().PutHoldOnAppointmentSlot(cursor), -2)

                # check no updates made to table
                get_schedule_sql = "SELECT * FROM CareGiverSchedule WHERE SlotStatus = 1"
                cursor.execute(get_schedule_sql)
                rows = cursor.fetchall()
                self.assertTrue(len(rows) < 1)
            
            clear_tables(sqlClient)
            
    def test_put_on_hold(self):
        """PutOnHold returns id"""
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:

            # get a cursor from the SQL connection
            with sqlClient.cursor(as_dict=True) as cursor:
                vc = VaccineCaregiver('Carrie Nation', cursor)
                self.assertEqual(scheduler().PutHoldOnAppointmentSlot(cursor), 0)

                # check 1 update made to table
                get_schedule_sql = "SELECT * FROM CareGiverSchedule WHERE SlotStatus = 1"
                cursor.execute(get_schedule_sql)
                rows = cursor.fetchall()
                self.assertTrue(len(rows) == 1)
            
            clear_tables(sqlClient)

if __name__ == "__main__":
    unittest.main()