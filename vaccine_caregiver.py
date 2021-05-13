from datetime import datetime
from datetime import timedelta
import pymssql


class VaccineCaregiver:
    ''' Adds the CareGiver to the DB and adds vaccine scheduling slots '''
    def __init__(self, name, cursor):
        _hoursToSchedlue = [10,11]
        _appointmentDuration = 15
        self.sqltext = "INSERT INTO CareGivers (CaregiverName) VALUES ('" + name + "')"
        self.caregiverId = 0
        try: 
            cursor.execute(self.sqltext)
            cursor.connection.commit()
            cursor.execute("SELECT @@IDENTITY AS 'Identity'; ")
            _identityRow = cursor.fetchone()
            self.caregiverId = _identityRow['Identity']
            # cursor.connection.commit()
            print('Query executed successfully. Caregiver : ' + name 
            +  ' added to the database using Caregiver ID = ' + str(self.caregiverId))
        except pymssql.Error as db_err:
            print("Database Programming Error in SQL Query processing for Caregivers! ")
            print("Exception code: " + str(db_err.args[0]))
            if len(db_err.args) > 1:
                print("Exception message: " + db_err.args[1])
            print("SQL text that resulted in an Error: " + self.sqltext)

        _weeks_to_schedule = []
        _now = datetime.now()
        _weeks_to_schedule.append(_now)
        _one_week_time_delta = timedelta(days=7)
        _weeks_ahead = 4
        _lcv = 0
        while _lcv < _weeks_ahead:
            _now = _now + _one_week_time_delta
            _weeks_to_schedule.append(_now)
            _lcv = _lcv + 1

        _formatstring = "%Y-%m-%d"

        for _day in _weeks_to_schedule:
            _formattedDate = _day.strftime(_formatstring)
            # print (_formattedDate)

            for _hr in _hoursToSchedlue:
                _startTime = 0
                while _startTime < 60:
                    _sqltext2 = ("INSERT INTO CareGiverSchedule (caregiverid, WorkDay, SlotHour, SlotMinute) VALUES (") 
                    _sqltext2 += str(self.caregiverId) + ", '" + _formattedDate + "', " 
                    _sqltext2 += str(_hr) + ", "  
                    _sqltext2 += str(_startTime) + ")" 
                    try:
                        cursor.execute(_sqltext2)
                        _startTime = _startTime + _appointmentDuration
                    except pymssql.Error as db_err:
                        print("Database Programming Error in SQL Query processing for CareGiver scheduling slots! ")
                        print("Exception code: " + str(db_err.args[0]))
                        if len(db_err.args) > 1:
                            print("Exception message: " + db_err.args[1]) 
                        print("SQL text that resulted in an Error: " + _sqltext2)
        cursor.connection.commit()


        #insert code for phone number and password