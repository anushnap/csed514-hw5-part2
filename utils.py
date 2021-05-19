def clear_tables(client):
    sqlQuery = '''
            Truncate Table CareGiverSchedule
            DBCC CHECKIDENT ('CareGiverSchedule', RESEED, 0)
            Delete From Caregivers
            DBCC CHECKIDENT ('Caregivers', RESEED, 0)
            Delete from Vaccines
            '''
    client.cursor().execute(sqlQuery)
    client.commit()
