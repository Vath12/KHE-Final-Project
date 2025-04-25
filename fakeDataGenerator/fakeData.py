import hashlib,faker,random

outputFile = 'boostrap.sql'


numUsers = 100
numCourses = 40

users = 'INSERT INTO Users (user_id,username,password,first_name,last_name,email,bio) VALUES\n'
fake = faker.Faker()
numbers = 0
for i in range(1,numUsers+1):
    uname = fake.user_name()+str(numbers)
    fname = fake.first_name()
    lname = fake.last_name()
    password = fake.password()
    if (i == 1):
        uname = "hamburger"
        password = "password"
        fname = "hammond"
        lname = "burger"
    numbers += random.randint(1,3)
    email = fake.email()
    bio = fake.text()
    users+=f"#password = {password}\n"
    users+=f"({i},'{uname}',0x{hashlib.sha256(password.encode('utf-8')).hexdigest()},'{fname}','{lname}','{email}','{bio}'),\n"
users = users.rstrip(",\n")+";"


profileLinks = "INSERT INTO UserProfileLinks VALUES\n"
for i in range(numUsers):
    for k in range(random.randint(0,3)):
        profileLinks+=f"({i+1},{k},'{fake.user_name()}'),\n"
profileLinks = profileLinks.rstrip(",\n")+";"


values = list("qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890")
def intToJoinCode(number):
    code = ""
    for i in range(8):
        number,remainder = divmod(number,62)
        code+=values[remainder]
    return code

classes = "INSERT INTO Classes VALUES\n"
codes = []
for i in range(1,numCourses+1):
    unique = False
    code = ""
    while (not unique):
        unique = True
        code = intToJoinCode(random.randint(0,62**8))
        for c in codes:
            if (c == code):
                unique = False
                break
    codes.append(code)
    classes+=f"({i},'{fake.word()}','{(' ').join(fake.sentences(3))}','{fake.sentence()}','{codes[-1]}'),\n"
classes = classes.rstrip(",\n")+";"

memberships = "INSERT INTO Memberships VALUES\n"
members = []
assignments = []
ADMIN = 0b11111111
TA = 0b01000111
DEFAULT = 0b00000000
#professors
for i in range(1,numCourses+1):
    assignments.append([])
    members.append((i,i,ADMIN,1))
#students
for i in range(numCourses+1,numUsers+1):
    enrolled = []
    for k in range(random.randint(3,8)):
        #user_id course_id perms
        id = random.randint(1,numCourses)
        while (id in enrolled):
            id = random.randint(1,numCourses)
        members.append((i,id,TA if (random.randint(0,100)<5) else DEFAULT,1))
        enrolled.append(id)

for m in members:
    memberships+=f"({m[0]},{m[1]},{m[2]},{m[3]}),\n"
memberships = memberships.rstrip(',\n')+';'

work = "INSERT INTO Assignments VALUES\n"
criteria = "INSERT INTO AssignmentCriteria VALUES\n"
grades = "INSERT INTO Grades VALUES"
id = 1
id2 = 1
def randDate():
    return f'2025-{random.randint(1,5):02d}-{random.randint(1,27):02d} {random.randint(0,23):02d}:{random.randint(0,59):02d}:{random.randint(0,59):02d}'
for i in range(1,numCourses+1):
    for k in range(random.randint(10,20)):
        assignments[i-1].append([i,id,
                            fake.sentence(),
                            randDate(),
                            random.randint(5,100)/100.0,[]])
        for z in range(random.randint(1,5)):
            v = random.randint(0,100)
            assignments[i-1][-1][5].append([id2,v])
            criteria += f"({id2},{i},{id},'{fake.sentence()}',{v},{random.randint(10,100)/100.0}),\n"
            id2+=1
        id+=1

for c in assignments:
    for a in c:
        work += f"({a[0]},{a[1]},'{a[2]}','{a[3]}',{a[4]}),\n"
work = work.rstrip(",\n") + ";"
criteria = criteria.rstrip(",\n") + ";"

comments = "INSERT INTO Comments (assignment_id, student_id, author_id, created_on,message) VALUES\n"

for m in members:
    if (m[2] == DEFAULT):
        for a in assignments[m[1]-1]:
            rgrader = random.choice(list(x for x in members if (x[0] == m[1]) and x[2] != DEFAULT))[1]
            comments += f"({a[1]},{m[0]},{rgrader},'{randDate()}','{''.join(fake.sentences(random.randint(1,4)))}'),\n"
            for c in a[5]:
                grades += f"({c[0]},{m[0]},{random.randint(0,c[1])}),\n"
grades = grades.rstrip(",\n")+";"
comments = comments.rstrip(',\n') + ";"



data = f'''
Use gradebook;
{users}
{profileLinks}
{classes}
{memberships}
{work}
{criteria}
{grades}
{comments}
'''

with open(outputFile,"w+") as f:
    f.write(data)

'''
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
(1,1,0b11111111,1),
(2,1,0b00000000,1),
(3,1,0b00000000,1);

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

'''