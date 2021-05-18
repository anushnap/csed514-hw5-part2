import pymssql 
from vaccine_reservation_scheduler import VaccineReservationScheduler as VaccScheduler
#from COVID19_vaccine.py import COVID19Vaccine as covidVacc

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

        	#Select Caregiver slot IDs that are on hold
        	openSlotCheck = VaccScheduler.PutHoldOnAppointmentSlot(CaregiverSchedulingID)

        	if (openSlotCheck == -2):
        		print("CAREGIVER SLOT NOT OPEN!")
        	else:

        		#Create an entry in the VaccineAppointmentsTable
        		self.sqltext = "INSERT INTO VaccineAppointments ("
        		self.sqltext += "VaccineAppointmentId, VaccineName) VALUES ("
        		self.sqltext += str(openSlotCheck)
				self.sqltext += getattr(Vaccine,'vaccine_name')

        		#Flag the Patient as “Queued for 1st Dose”
        		#not sure how to get infor about the patient and change their appointment status

        		#Create a second appointment 3-6 weeks after the 1st appointment



        def ScheduleAppointment(VaccineAppointmentID, cursor):

