Use gradebook;

INSERT INTO Users (username,password,first_name,last_name,email,bio) VALUES
#password is hashed with SHA-256 the first one is "password"
('hamburger',0x5E884898DA28047151D0E56F8DC6292773603D0D6AABBDD62A11EF721D1542D8,'Alice','Johnson',NULL,'Professor @ Northeastern'),
#password is "password123"
('hotdog',0xEF92B778BAFE771E89245B89ECBC08A44A4E166C06659911881F383D4473E94F,'Bob','Kentucky',NULL,NULL),
#password is silk150
('textile',0x1B9EE937A8C27DD8C62A711DA8833C2B0DA96442215F58A59F02561AFA52B4DD,'Cilly','String','verySilly@aol.com',NULL);

INSERT INTO UserProfileLinks VALUES
(1,0,'aj1111'),
(1,1,'alicej11'),
(2,3,'b0bBK');

INSERT INTO Classes VALUES
(1,'CS3200','Introduction to Databases','Northeastern University','ABX0101C');

INSERT INTO Memberships VALUES
(1,1,0b1111,1),
(2,1,0b0000,1),
(3,1,0b0000,1);

INSERT INTO Announcements VALUES
(1,1,1,'Welcome','hello everyone!','2025-04-12 08:34:33');

INSERT INTO Assignments VALUES
(1,1,'Syllabus Quiz','2025-01-18 00:00:00',0.1);

INSERT INTO AssignmentCriteria VALUES
(1,1,1,'Completion',10,1);

INSERT INTO Grades VALUES
(1,2,10),
(1,3,0);


INSERT INTO Comments VALUES
(1,1,2,1,'2025-01-20 13:24:05','Good Job!'),
(2,1,3,1,'2025-01-20 13:30:50','You just had to submit this.');


INSERT INTO Notifications VALUES
(1,2,'2025-01-20 13:24:05'),
(1,3,'2025-01-20 13:30:50');

INSERT INTO LoginSessions VALUES
(1,0,'2025-04-19 00:00:00'),
(2,1051,'2025-04-17 00:00:00'),
(3,49228,'2025-04-11 00:00:00');

