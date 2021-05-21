import pymssql 
from vaccine_reservation_scheduler import VaccineReservationScheduler as VaccScheduler
#from COVID19_vaccine.py import COVID19Vaccine as covidVacc
from datetime import datetime

class VaccinePatient:
    '''Adds patient to Database'''
    def __init__(self, patient_name, vaccine_status, cursor):

        self.sqltext = "INSERT INTO Patients ("
        self.sqltext += "PatientName, VaccineStatus) VALUES ("
        self.sqltext += "'" + patient_name + "', "
        self.sqltext += str(vaccine_status) + ")"

        self.patientId = 0

        try: 
            cursor.execute(self.sqltext)
            cursor.connection.commit()
            cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
            _identityRow = cursor.fetchone()
            self.patientId = _identityRow['Identity']
            # cursor.connection.commit()
            print('Query executed successfully. Patient : ' + patient_name
            +  ' added to the database using Patient ID = ' + str(self.patientId))
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Patients! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)

    def ReserveAppointment(self, CaregiverSchedulingID, Vaccine, cursor):
        '''create an entry in the VaccineAppointments Table,  flag patient as "Queued for first dose", 
        create 2nd entry in VaccineAppointments Table'''

        #Select * for corresponding CaregiverSlotID in caregivers table
        sqlSelectCaregiverSlot = "SELECT * FROM CareGiverSchedule WHERE CaregiverSlotSchedulingId = "
        sqlSelectCaregiverSlot += str(openSlotCheck)

        try: 
            cursor.execute(sqlSelectCaregiverSlot)
            row = cursor.fetchone()

            CaregiverId = row['CaregiverId']
            ReservationDate = row['WorkDay']
            ReservationStartHour = row['SlotHour']
            ReservationStartMinute = row['SlotMinute']
            AppointmentDuration = 15
            SlotStatus = row['SlotStatus']
            DateAdministered = NULL #needs to be changed when vaccine is administered 
            DoseNumber = 1

            #print("Query executed successfully.")
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Selecting Caregiver Slot")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqlSelectCaregiverSlot)

        #======================================================================
		#Create an entry in the VaccineAppointmentsTable 
            #Q: how to get patient ID that corresponds to this appointment?
            #need patientID/name as parameter

        #Insert first appointment to VaccineAppointments table
        sqlCreateAppt = "INSERT INTO VaccineAppointments ("
        sqlCreateAppt += "VaccineName, PatientId, CaregiverId, ReservationDate, ReservationStartHour, "
        sqlCreateAppt += "ReservationStartMinute, AppointmentDuration, SlotStatus, DateAdministered, "
        sqlCreateAppt += "DoseNumber) VALUES ("
        sqlCreateAppt += getattr(Vaccine,'vaccine_name') + ", "
        sqlCreateAppt += str(self.patientId) + ", "
        sqlCreateAppt += str(CaregiverId)  + ", "
        sqlCreateAppt += str(ReservationDate) + ", "
        sqlCreateAppt += str(ReservationStartHour) + ", "
        sqlCreateAppt += str(ReservationStartMinute) + ", "
        sqlCreateAppt += str(AppointmentDuration) + ", "
        sqlCreateAppt += str(SlotStatus) + ", "
        sqlCreateAppt += str(DateAdministered) + ", "
        sqlCreateAppt += str(DoseNumber) + ")"

        appointmentId = 0 #primary key

        try:
            cursor.execute(sqlCreateAppt)
            #cursor.connection.commit()
            cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
            _identityRow = cursor.fetchone()
            appointmentId = _identityRow['Identity']
            print('Query executed successfully. Appointment added to the database using AppointmentID = ' 
                + str(appointmentId))
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Appointments! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqlCreateAppt)

        #======================================================================
		#Update patient appointment status: New -> Queued for first dose

        sqlUpdatePatientStatus = "UPDATE Patients SET VaccineStatus = 1 "
        sqlUpdatePatientStatus += "WHERE PatientId = "
        sqlUpdatePatientStatus += str(self.patientId)

        #======================================================================
		#Create a second appointment 3-6 weeks after the 1st appointment

        #Check for first available slot in 3-6 weeks time
        openSlotCheck2 = VaccScheduler.PutHoldOnAppointment2(CaregiverSchedulingID, getattr(Vaccine,'days_between_doses'))

        #Select * for corresponding CaregiverSlotID in caregivers table
        sqlSelectCaregiverSlot2 = "SELECT * FROM CareGiverSchedule WHERE CaregiverSlotSchedulingId = "
        sqlSelectCaregiverSlot2 += str(openSlotCheck2)

        try: 
            cursor.execute(sqlSelectCaregiverSlot2)
            row = cursor.fetchone()

            CaregiverId = row['CaregiverId']
            ReservationDate = row['WorkDay']
            ReservationStartHour = row['SlotHour']
            ReservationStartMinute = row['SlotMinute']
            AppointmentDuration = 15
            SlotStatus = row['SlotStatus']
            DateAdministered = NULL #needs to be changed when vaccine is administered 
            DoseNumber = 1

            #print("Query executed successfully.")
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Selecting Caregiver Slot 2")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqlSelectCaregiverSlot2)


        #Insert second appointment to VaccineAppointments table
        sqlCreateAppt2 = "INSERT INTO VaccineAppointments (VaccineAppointmentId, "
        sqlCreateAppt2 += "VaccineName, PatientId, CaregiverId, ReservationDate, ReservationStartHour, "
        sqlCreateAppt2 += "ReservationStartMinute, AppointmentDuration, SlotStatus, DateAdministered, "
        sqlCreateAppt2 += "DoseNumber) VALUES ("
        sqlCreateAppt2 += getattr(Vaccine,'vaccine_name') + ", "
        sqlCreateAppt2 += str(self.patientId) + ", "
        sqlCreateAppt2 += str(CaregiverId) + ", "
        sqlCreateAppt2 += str(ReservationDate) + ", "
        sqlCreateAppt2 += str(ReservationStartHour) + ", "
        sqlCreateAppt2 += str(ReservationStartMinute) + ", "
        sqlCreateAppt2 += str(AppointmentDuration) + ", "
        sqlCreateAppt2 += str(SlotStatus) + ", "
        sqlCreateAppt2 += str(DateAdministered) + ", "
        sqlCreateAppt2 += str(DoseNumber) + ")"
        
        appointmentId2 = 0 #primary key

        try:
            cursor.execute(sqlCreateAppt2)
            #cursor.connection.commit()
            cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
            _identityRow = cursor.fetchone()
            appointmentId2 = _identityRow['Identity']
            print('Query executed successfully. Appointment added to the database using AppointmentID = ' 
                + str(appointmentId2))
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Appointments! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqlCreateAppt2)


    def ScheduleAppointment(self, VaccineAppointmentID, cursor):
        pass