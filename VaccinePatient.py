import pymssql 
from vaccine_reservation_scheduler import VaccineReservationScheduler as VaccScheduler
#from COVID19_vaccine.py import COVID19Vaccine as covidVacc
from datetime import datetime

class VaccinePatient:
	'''Adds patient to Database'''
	def __init__(self,
                 patient_name,
                 vaccine_status,
                 cursor):

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

    def ReserveAppointment(CaregiverSchedulingID, Vaccine, cursor): 
    	'''Validate caregiver slot ID and put on "Hold" status and create an entry 
    	in the VaccineAppointment Table flagged as "Queued for first dose"'''

    	#Select first available CaregiverSlotID that is on hold
    	openSlotCheck = VaccScheduler.PutHoldOnAppointmentSlot(CaregiverSchedulingID, cursor)

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
            #VaccineAppointmentId = row['VaccineAppointmentId']

            print("Query executed successfully.")
        except pymssql.Error as db_err:
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

        sqlCreateAppt = "INSERT INTO VaccineAppointments ("
        sqlCreateAppt += "VaccineName, PatientId, CaregiverId, ReservationDate, ReservationStartHour, "
        sqlCreateAppt += "ReservationStartMinute, AppointmentDuration, SlotStatus, DateAdministered, "
        sqlCreateAppt += "DoseNumber) VALUES ("
        sqlCreateAppt += getattr(Vaccine,'vaccine_name') + ", "
        #sqlCreateAppt += patientID
        sqlCreateAppt += CaregiverId  + ", "
        sqlCreateAppt += str(ReservationDate) + ", "
        sqlCreateAppt += str(ReservationStartHour) + ", "
        sqlCreateAppt += str(ReservationStartMinute) + ", "
        sqlCreateAppt += str(AppointmentDuration) + ", "
        sqlCreateAppt += str(DateAdministered) + ", "
        sqlCreateAppt += str(DoseNumber) + ")"

        appointmentId = 0 #primary key

        try:
            cursor.execute(sqlCreateAppt)
            cursor.connection.commit()
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
            #need patient name param

        sqlUpdatePatientStatus = "UPDATE Patients SET VaccineStatus = 1 "
        sqlUpdatePatientStatus += "WHERE PatientName = '"
        #sqlUpdatePatientStatus += str(patientName) + "'"


        #======================================================================
		#Create a second appointment 3-6 weeks after the 1st appointment

        #Check for first available slot in 3-6 weeks time
            #Query CaregiverSchedule table
        CaregiverId2 = ...

        #Insert second appointment to VaccineAppointments table
        sqlCreateAppt2 = "INSERT INTO VaccineAppointments ("
        sqlCreateAppt2 += "VaccineName, PatientId, CaregiverId, ReservationDate, ReservationStartHour, "
        sqlCreateAppt2 += "ReservationStartMinute, AppointmentDuration, SlotStatus, DateAdministered, "
        sqlCreateAppt2 += "DoseNumber) VALUES ("
        sqlCreateAppt2 += getattr(Vaccine,'vaccine_name') + ", "
        #sqlCreateAppt2 += patientID
        sqlCreateAppt2 += CaregiverId2  + ", "
        sqlCreateAppt2 += str(ReservationDate) + ", "
        sqlCreateAppt2 += str(ReservationStartHour) + ", "
        sqlCreateAppt2 += str(ReservationStartMinute) + ", "
        sqlCreateAppt2 += str(AppointmentDuration) + ", "
        sqlCreateAppt2 += str(DateAdministered) + ", "
        sqlCreateAppt2 += str(DoseNumber) + ")"

        appointmentId2 = 0 #primary key

        try:
            cursor.execute(sqlCreateAppt2)
            cursor.connection.commit()
            cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
            _identityRow = cursor.fetchone()
            appointmentId = _identityRow['Identity']
            print('Query executed successfully. Appointment added to the database using AppointmentID = ' 
                + str(appointmentId2))
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Appointments! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqlCreateAppt2)


    def ScheduleAppointment(VaccineAppointmentID, cursor):

