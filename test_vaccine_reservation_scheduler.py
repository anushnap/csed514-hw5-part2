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
    
    def test_put_on_hold_returns_zero(self):
        """PutOnHold returns 0"""
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            # get a cursor from the SQL connection
            with sqlClient.cursor(as_dict=True) as cursor:
                self.assertEqual(scheduler().PutHoldOnAppointmentSlot(cursor), 0)
            
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
            
            clear_tables(sqlClient)

if __name__ == "__main__":
    unittest.main()