import unittest
import os

from sql_connection_manager import SqlConnectionManager
from enums import *
from utils import *
from COVID19_vaccine import COVID19Vaccine as covid

class TestCovid19(unittest.TestCase):
    def test_init(self):
        """Test init of COVID19Vaccine"""
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    # create a new VaccineCaregiver object
                    covid(vaccine_name = 'Pfizer',
                          manufac_name = 'Pfizer-BioNTech',
                          doses_in_stock = 100,
                          doses_reserved = 0,
                          days_between_doses = 21,
                          doses_per_patient = 2,
                          cursor=cursor)
                    # check if the patient is correctly inserted into the database
                    sqlQuery = '''
                               SELECT *
                               FROM Vaccines
                               WHERE VaccineName = 'Pfizer'
                               '''
                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()
                    if len(rows) < 1:
                        self.fail("Creating COVID vaccine failed")
                    # clear the tables after testing, just in-case
                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("Creating COVID vaccine failed")

    def test_add_doses(self):
        """Test COVID19Vaccine.add_doses adds the specified num of doses"""
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    covid(vaccine_name = 'Moderna',
                         manufac_name = 'Moderna',
                         doses_in_stock = 100,
                         doses_reserved = 0,
                         days_between_doses = 28,
                         doses_per_patient = 2,
                         cursor=cursor)
                    # get current doses
                    sqlQuery = '''
                                SELECT *
                                FROM Vaccines
                                WHERE VaccineName = 'Moderna'
                            '''
                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()
                    current_stock = 0
                    for row in rows:
                        current_stock += row["AvailableDoses"]
                    
                    # add new doses and check that count changes
                    add_doses = 10
                    covid.add_doses('Moderna', add_doses, cursor)

                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()
                    for row in rows:
                        check_stock = row["AvailableDoses"]
                        if (add_doses + current_stock) != check_stock:
                            self.fail("Stock failed to add to database: " 
                                      + str(add_doses + current_stock) + "vs. "
                                      + str(check_stock))
                    # clear the tables after testing, just in-case
                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("add_doses method failed")

    def test_reserve_doses(self):
        """Test COVID19Vaccine.reserve_doses reserves the correct num of doses"""
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            with sqlClient.cursor(as_dict=True) as cursor:
                try:
                    # clear the tables before testing
                    clear_tables(sqlClient)
                    covid(vaccine_name = 'Pfizer',
                          manufac_name = 'Pfizer-BioNTech',
                          doses_in_stock = 100,
                          doses_reserved = 0,
                          days_between_doses = 21,
                          doses_per_patient = 2,
                          cursor=cursor)
                    # get current doses
                    sqlQuery = '''
                                SELECT *
                                FROM Vaccines
                                WHERE VaccineName = 'Pfizer'
                            '''
                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()
                    current_stock = 0
                    current_reserved = 0
                    for row in rows:
                        current_stock += row["AvailableDoses"]
                        current_reserved += row["ReservedDoses"]
                    
                    # add new doses and check that count changes
                    to_reserve = 10
                    covid.reserve_doses('Pfizer', cursor)
                    
                    cursor.execute(sqlQuery)
                    rows = cursor.fetchall()
                    for row in rows:
                        check_stock = row["AvailableDoses"]
                        check_reserve = row["ReservedDoses"]
                        if ((current_stock - 2) != check_stock) & ((current_reserved + 2) != check_reserve):
                            self.fail("Stock failed to be reserved in database: " 
                                      + str(current_reserved) + "vs. "
                                      + str(check_reserve))
                    # clear the tables after testing, just in-case
                    clear_tables(sqlClient)
                except Exception:
                    # clear the tables if an exception occurred
                    clear_tables(sqlClient)
                    self.fail("reserve_doses method failed")

if __name__ == '__main__':
    unittest.main()