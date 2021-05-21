import pymssql 
from vaccine_reservation_scheduler import VaccineReservationScheduler as VaccScheduler
from COVID19_vaccine import COVID19Vaccine as CovidVaccine
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
        sqlSelectCaregiverSlot += str(CaregiverSchedulingID)

        try: 
            cursor.execute(sqlSelectCaregiverSlot)
            row = cursor.fetchone()

            CaregiverId = row['CaregiverId']
            ReservationDate = "'" + row['WorkDay'] + "'"
            ReservationStartHour = row['SlotHour']
            ReservationStartMinute = row['SlotMinute']
            AppointmentDuration = 15
            SlotStatus = row['SlotStatus']
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

        #Insert first appointment to VaccineAppointments table
        sqlCreateAppt = "INSERT INTO VaccineAppointments ("
        sqlCreateAppt += "VaccineName, PatientId, CaregiverId, ReservationDate, ReservationStartHour, "
        sqlCreateAppt += "ReservationStartMinute, AppointmentDuration, SlotStatus, DoseNumber) "
        sqlCreateAppt += "VALUES ("
        sqlCreateAppt += "'" + getattr(Vaccine,'vaccine_name') + "', "
        sqlCreateAppt += str(self.patientId) + ", "
        sqlCreateAppt += str(CaregiverId)  + ", "
        sqlCreateAppt += str(ReservationDate) + ", "
        sqlCreateAppt += str(ReservationStartHour) + ", "
        sqlCreateAppt += str(ReservationStartMinute) + ", "
        sqlCreateAppt += str(AppointmentDuration) + ", "
        sqlCreateAppt += str(SlotStatus) + ", "
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
        #update caregiver schedule and set vaccine appiontment id from 0 -> unique value

        sqlUpdateAppointmentID = "UPDATE CaregiverSchedule SET VaccineAppointmentId = "
        sqlUpdateAppointmentID += str(appointmentId) + " "
        sqlUpdateAppointmentID += "WHERE CaregiverSlotSchedulingId = "
        sqlUpdateAppointmentID += str(CaregiverSchedulingID)

        try:
            cursor.execute(sqlUpdateAppointmentID)

        except pymssql.Error as db_err:    
            print("Database Programming Error in SQL Query processing! ")
            print("Exception code: " + db_err.args[0])
            if len(db_err.args) > 1:
                print("Exception message: " + str(db_err.args[1]))  
            print("SQL text that resulted in an Error: " + sqlUpdateAppointmentID)

        #======================================================================
		#Update patient appointment status: New -> Queued for first dose

        sqlUpdatePatientStatus = "UPDATE Patients SET VaccineStatus = 1 "
        sqlUpdatePatientStatus += "WHERE PatientId = "
        sqlUpdatePatientStatus += str(self.patientId)

        try:
            cursor.execute(sqlUpdatePatientStatus)
            print('Query executed successfully. Patient status updated using patientID = ' 
                + str(self.patientId))
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Patients! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqlUpdatePatientStatus)

        #======================================================================
		#Create a second appointment 3-6 weeks after the 1st appointment

        #Check for first available slot in 3-6 weeks time
        openSlotCheck2 = VaccScheduler().PutHoldOnAppointment2(CaregiverSchedulingID, getattr(Vaccine,'days_between_doses'), cursor)

        #Select * for corresponding CaregiverSlotID in caregivers table
        sqlSelectCaregiverSlot2 = "SELECT * FROM CareGiverSchedule WHERE CaregiverSlotSchedulingId = "
        sqlSelectCaregiverSlot2 += str(openSlotCheck2)

        try: 
            cursor.execute(sqlSelectCaregiverSlot2)
            row = cursor.fetchone()

            CaregiverId = row['CaregiverId']
            ReservationDate = "'" + row['WorkDay'] + "'"
            ReservationStartHour = row['SlotHour']
            ReservationStartMinute = row['SlotMinute']
            AppointmentDuration = 15
            SlotStatus = row['SlotStatus']
            DoseNumber = 2

        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Selecting Caregiver Slot 2")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqlSelectCaregiverSlot2)

        #======================================================================
        #Insert second appointment to VaccineAppointments table
        sqlCreateAppt2 = "INSERT INTO VaccineAppointments ("
        sqlCreateAppt2 += "VaccineName, PatientId, CaregiverId, ReservationDate, ReservationStartHour, "
        sqlCreateAppt2 += "ReservationStartMinute, AppointmentDuration, SlotStatus, DoseNumber) "
        sqlCreateAppt2 += "VALUES ("
        sqlCreateAppt2 += "'" + getattr(Vaccine,'vaccine_name') + "', "
        sqlCreateAppt2 += str(self.patientId) + ", "
        sqlCreateAppt2 += str(CaregiverId) + ", "
        sqlCreateAppt2 += str(ReservationDate) + ", "
        sqlCreateAppt2 += str(ReservationStartHour) + ", "
        sqlCreateAppt2 += str(ReservationStartMinute) + ", "
        sqlCreateAppt2 += str(AppointmentDuration) + ", "
        sqlCreateAppt2 += str(SlotStatus) + ", "
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


    def ScheduleAppointment(self, CaregiverSlotID, VaccineAppointmentID, Vaccine, cursor):
        '''update the Patient’s VaccineStatus from "Queued for first dose" to 1st Dose Scheduled
            maintain the Vaccine inventory'''

        #======================================================================
        #Maintain vaccine inventory

        #Reserve 2 doses
        CovidVaccine.reserve_doses(getattr(Vaccine,'vaccine_name'))

        #======================================================================
        #Update caregiver slot status from hold to scheduled
        #Update vaccineappointment slot status from hold to scheduled

        sqlUpdateSlotStatuses = VaccScheduler.ScheduleAppointmentSlot(CaregiverSlotID, VaccineAppointmentID)

        # if (sqlUpdatePatientStatus < 0): 
        #     print("Slot statuses not updated")

        #======================================================================
        #Update patient appointment status: Queued for 1st dose -> Scheduled for first dose

        sqlUpdatePatientStatus = "UPDATE Patients SET VaccineStatus = 2 "
        sqlUpdatePatientStatus += "WHERE PatientId = "
        sqlUpdatePatientStatus += str(self.patientId)

        try:
            cursor.execute(sqlUpdatePatientStatus)
            print('Query executed successfully. Patient status updated using patientID = ' 
                + str(self.patientId))
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Patients! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + sqlUpdatePatientStatus)

        #======================================================================