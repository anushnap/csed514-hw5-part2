import unittest
import os

from sql_connection_manager import SqlConnectionManager
from enums import *
from utils import *
from vaccine_reservation_scheduler import VaccineReservationScheduler as scheduler
from vaccine_caregiver import VaccineCaregiver
from COVID19_vaccine import COVID19Vaccine as covid
from VaccinePatient import VaccinePatient as patient

class TestVaccinePatient(unittest.TestCase:

    def test_init(self):
        pass
    
    def test_reserve_appointment(self):
        pass