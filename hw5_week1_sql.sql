-- Additional helper code for your use if needed

-- --- Drop commands to restructure the DB
-- Drop Table IF EXISTS 
-- 	CareGiverSchedule, 
-- 	VaccineAppointments,
-- 	AppointmentStatusCodes, 
-- 	Patients, 
-- 	Caregivers,
-- 	Vaccines	
-- ;	

-- DROP PROCEDURE IF EXISTS InitDataModel;

-- Go

-- --- Commands to clear the active database Tables for unit testing
-- Truncate Table CareGiverSchedule
-- DBCC CHECKIDENT ('CareGiverSchedule', RESEED, 0)
-- Delete From Caregivers
-- DBCC CHECKIDENT ('Caregivers', RESEED, 0)
-- GO

-- Truncate Table Vaccines
-- DBCC CHECKIDENT ('Vaccines', RESEED, 0)
-- Delete From Vaccines
-- DBCC CHECKIDENT ('Vaccines', RESEED, 0)
-- GO


--Data model as stored procedure
CREATE PROCEDURE InitDataModel
AS
	--Caregivers table
	Create Table Caregivers(
		CaregiverId int IDENTITY PRIMARY KEY,
		CaregiverName varchar(50),
		PhoneNumber int,
		UserPassword varchar(20)
	)

	--AppointmentStatusCodes table
	Create Table AppointmentStatusCodes(
	StatusCodeId int PRIMARY KEY,
	StatusCode   varchar(30)
	)

	INSERT INTO AppointmentStatusCodes (statusCodeId, StatusCode)
		VALUES (0, 'Open')
	INSERT INTO AppointmentStatusCodes (statusCodeId, StatusCode)
		VALUES (1, 'OnHold')
	INSERT INTO AppointmentStatusCodes (statusCodeId, StatusCode)
		VALUES (2, 'Scheduled')
	INSERT INTO AppointmentStatusCodes (statusCodeId, StatusCode)
		VALUES (3, 'Completed')
	INSERT INTO AppointmentStatusCodes (statusCodeId, StatusCode)
		VALUES (4, 'Missed')

	--Patients table
	Create Table Patients(
	PatientId int IDENTITY PRIMARY KEY,
	PatientName varchar(50),
	PhoneNumber int,
	UserPassword varchar(20),
	DosesGiven int DEFAULT 0
	)

	--Vaccines table
	Create Table Vaccines(
	VaccineId int IDENTITY PRIMARY KEY,
	ManufactererName varchar(50),
	DosesNeeded int,
	DosesInStock int DEFAULT 0,
	DosesReserved int DEFAULT 0,
	DaysBetweenDoses int
	)

	--CareGiverSchedule table
	Create Table CareGiverSchedule(
	CaregiverSlotSchedulingId int Identity PRIMARY KEY, 
	CaregiverId int DEFAULT 0 NOT NULL,
	WorkDay date,
	SlotHour int DEFAULT 0 NOT NULL,
	SlotMinute int DEFAULT 0 NOT NULL,
	SlotStatus int  DEFAULT 0 NOT NULL,
	PatientId int,
	VaccineId int,
	FOREIGN KEY (caregiverId) REFERENCES Caregivers(CaregiverId),
	FOREIGN KEY (SlotStatus) REFERENCES AppointmentStatusCodes(StatusCodeId),
	FOREIGN KEY (PatientId) REFERENCES Patients(PatientId),
	FOREIGN KEY (VaccineId) REFERENCES Vaccines(VaccineId)
	)

GO

EXEC InitDataModel;