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


class VaccinePatient:

    def __init__(self):
        return None