import unittest
import os

from sql_connection_manager import SqlConnectionManager
from enums import *
from utils import *
from vaccine_reservation_scheduler import VaccineReservationScheduler as scheduler
from vaccine_caregiver import VaccineCaregiver as caregiver
from COVID19_vaccine import COVID19Vaccine as covid
from VaccinePatient import VaccinePatient as patient

class TestVaccinePatient(unittest.TestCase):

    def test_init(self):
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            clear_tables(sqlClient)
            with sqlClient.cursor(as_dict=True) as cursor:
                vp = patient('Dwight Sablan', 0 , cursor)

                get_patient_sql = "SELECT * FROM Patients"
                cursor.execute(get_patient_sql)
                rows = cursor.fetchall()
                self.assertTrue(len(rows) == 1)
            
            clear_tables(sqlClient)
    
    def test_reserve_appointment(self):
        '''
        reserve_appointment changes patient status from new to queued
        adds row to VaccineAppointments table with slot status 'hold'
        returns appointmentid
        '''
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            clear_tables(sqlClient)
            with sqlClient.cursor(as_dict=True) as cursor:
                # initalize objects
                vp = patient('Dwight Sablan', 0 , cursor)
                vc = caregiver('Carrie Nation', cursor)
                vaccine = covid('Pfizer', 'Pfizer-BioNTech', 10, 10, 21, 2, cursor)
                hold_first_cgslot_sql = "UPDATE CaregiverSchedule "
                hold_first_cgslot_sql += "SET SlotStatus = 1 "
                hold_first_cgslot_sql += "WHERE CaregiverSlotSchedulingId = 1"
                cursor.execute(hold_first_cgslot_sql)

                appt = vp.ReserveAppointment(1, vaccine, cursor)
                self.assertEqual(appt, 0)
                
                # check VaccineAppointments has exactly 2 rows
                check_appointments_sql = "SELECT * FROM VaccineAppointments"
                cursor.execute(check_appointments_sql)
                rows = cursor.fetchall()
                self.assertTrue(len(rows) == 2)
                
                # check each row
                for row in rows:
                    self.assertTrue(row['VaccineName'] == 'Pfizer')
                    self.assertTrue(row['PatientId'] == 1)
                    self.assertTrue(row['CaregiverId'] == 1)
                    self.assertTrue(row['SlotStatus'] == 1)
                    
                # check caregiverschedule has vaccineappointmentid = 1
                check_caregivers_sql = "SELECT SlotStatus, VaccineAppointmentId FROM CareGiverSchedule "
                check_caregivers_sql += "WHERE SlotStatus = 1"
                cursor.execute(check_caregivers_sql)
                rows = cursor.fetchall()
                self.assertTrue(len(rows) == 2)

                # check patient status is updated
                check_patient_sql = "SELECT * FROM Patients"
                cursor.execute(check_patient_sql)
                row = cursor.fetchone()
                self.assertTrue(row['VaccineStatus'] == 1)
            
            clear_tables(sqlClient)

    def test_schedule_appointment(self):
        '''
        schedule_appointment maintains vaccine inventory, update slot status in 
        caregiverschedule and appointments table, update patient appointment status
        '''
        with SqlConnectionManager(Server=os.getenv("Server"),
                                  DBname=os.getenv("DBName"),
                                  UserId=os.getenv("UserID"),
                                  Password=os.getenv("Password")) as sqlClient:
            clear_tables(sqlClient)
            with sqlClient.cursor(as_dict=True) as cursor:
                # initalize objects
                vp = patient('Anushna Prakash', 1 , cursor)
                vc = caregiver('Carrie Nation', cursor)
                vaccine = covid('Pfizer', 'Pfizer-BioNTech', 10, 10, 21, 2, cursor)

                #Insert appointment in appointments table
                vacc_appt_insert_sql = "INSERT INTO VaccineAppointments("
                vacc_appt_insert_sql += "VaccineName, PatientId, CaregiverId, ReservationDate, "
                vacc_appt_insert_sql += "ReservationStartHour, ReservationStartMinute, AppointmentDuration, "            
                vacc_appt_insert_sql += "SlotStatus, DateAdministered, DoseNumber) VALUES "
                vacc_appt_insert_sql += "('Pfizer', 1, 1, NULL, 10, 15, 15, 1, NULL, 1)"
                cursor.execute(vacc_appt_insert_sql)

                #Schedule the appointment
                vp.ScheduleAppointment(1, 0, vaccine, cursor)

                #check VaccineAppointments has exactly 1 rows
                check_appointments_sql = "SELECT * FROM VaccineAppointments"
                cursor.execute(check_appointments_sql)
                rows = cursor.fetchall()
                self.assertTrue(len(rows) == 1)
                self.assertTrue(rows[0]['SlotStatus'] == 2)

                #check vaccines inventory updated
                check_inventory_sql = "SELECT * FROM Vaccines"
                cursor.execute(check_inventory_sql)
                row = cursor.fetchone()
                self.assertTrue(row['AvailableDoses'] == 8)
                self.assertTrue(row['ReservedDoses'] == 12)

                #check slot statuses in caregiver schedule updated
                check_slot_stat2_sql = "SELECT * FROM CaregiverSchedule "
                check_slot_stat2_sql += "WHERE CaregiverSlotSchedulingId = 1"
                cursor.execute(check_slot_stat2_sql)
                row = cursor.fetchone()
                self.assertTrue(row['SlotStatus'] == 2)

                #check patient vaccine status updated
                check_patient_sql = "SELECT * FROM Patients"
                cursor.execute(check_patient_sql)
                row = cursor.fetchone()
                self.assertTrue(row['VaccineStatus'] == 2)

            clear_tables(sqlClient)


if __name__ == '__main__':
    unittest.main()