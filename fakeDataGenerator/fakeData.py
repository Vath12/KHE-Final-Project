import hashlib,faker,random

outputFile = 'boostrap.sql'


numUsers = 500
numCourses = 40

users = 'INSERT INTO Users (username,password,first_name,last_name,email,bio) VALUES\n'
fake = faker.Faker()
for i in range(numUsers):
    uname = fake.user_name()
    fname = fake.first_name()
    lname = fake.last_name()
    password = fake.password()
    email = fake.email()
    bio = fake.text()
    users+=f"#password = {password}\n"
    users+=f"('{uname}','{fname}',{lname},0x{hashlib.sha256(password.encode('utf-8')).hexdigest()},'{email}','{bio}'),\n"
users = users.rstrip(",")+";"


profileLinks = "INSERT INTO UserProfileLinks VALUES\n"
for i in range(numUsers):
    for k in range(random.randint(0,3)):
        profileLinks+=f"({i+1},{k},'{fake.user_name()}'),\n"
profileLinks = profileLinks.rstrip(",")+";"


values = list("qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890")
def intToJoinCode(number):
    code = ""
    for i in range(8):
        number,remainder = divmod(number,62)
        code+=values[remainder]
    return code

classes = "INSERT INTO Classes VALUES\n"
codes = []
for i in range(40):
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
    classes+=f"({i},'{fake.word()}','{fake.sentence()}','{codes[-1]}')\n"
classes = classes.rstrip(",")+";"

memberships = "INSERT INTO Memberships VALUES\n"
members = []
assignments = []
ADMIN = 0b11111111
TA = 0b01000111
DEFAULT = 0b00000000
#professors
for i in range(numCourses):
    assignments.append([])
    members.append((i,i,ADMIN,1))
#students
for i in range(numCourses,numUsers):
    enrolled = []
    for k in range(random.randint(3,8)):
        #user_id course_id perms
        id = random.randint(0,numCourses)
        while (id in enrolled):
            id = random.randint(0,numCourses)
        members.append((i,id,TA if (random.randint(0,100)<5) else DEFAULT,1))
        enrolled.append(id)

for m in members:
    memberships+=f"({m[0]},{m[1]},{m[2]},{m[3]}),\n"
memberships = memberships.rstrip(',')+';'

id = 0
for i in range(numCourses):
    assignments[i].append([i,id,
                           fake.sentence(),
                           fake.date(),random.randint(5,100)/100.0])
    id+=1

data = f'''
Use gradebook;
{users}
{profileLinks}
{classes}
{memberships}
'''

with open(outputFile,"w+") as f:
    f.write(data)

'''
Use gradebook;

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