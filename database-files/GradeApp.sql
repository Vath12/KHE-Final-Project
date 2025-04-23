DROP SCHEMA IF EXISTS gradebook;
CREATE SCHEMA gradebook;
USE gradebook;

CREATE TABLE Users (
    user_id INTEGER NOT NULL AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password BINARY(32) NOT NULL,
    first_name VARCHAR(64) NOT NULL,
    last_name VARCHAR(64) NOT NULL,
    email VARCHAR(40),
    bio VARCHAR(1024),
    PRIMARY KEY (user_id)
);

CREATE TABLE UserProfileLinks (
    user_id INTEGER NOT NULL,
    platform INTEGER NOT NULL,
    link VARCHAR(255),
    PRIMARY KEY (user_id,platform),
    FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE
);

CREATE TABLE Classes (
    class_id INTEGER NOT NULL AUTO_INCREMENT,
    name VARCHAR(128) NOT NULL,
    description VARCHAR(512) NOT NULL,
    organization VARCHAR(128),
    #use only upper and lowercase letters and numbers 0-9
    join_code VARCHAR(8) UNIQUE,
    PRIMARY KEY (class_id)
);

CREATE TABLE Announcements (
    announcement_id INTEGER NOT NULL AUTO_INCREMENT,
    author_id INTEGER,
    class_id INTEGER NOT NULL,
    title VARCHAR(128) NOT NULL,
    message VARCHAR(1028) NOT NULL,
    date_posted DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (announcement_id),
    FOREIGN KEY (author_id) REFERENCES Users (user_id),
    FOREIGN KEY (class_id) REFERENCES Classes (class_id) ON DELETE CASCADE
);

CREATE TABLE Assignments (
    class_id INTEGER NOT NULL,
    assignment_id INTEGER NOT NULL AUTO_INCREMENT,
    name VARCHAR(128) NOT NULL,
    due_date DATETIME NOT NULL,
    overall_weight DECIMAL NOT NULL,
    PRIMARY KEY (assignment_id),
    FOREIGN KEY (class_id) REFERENCES Classes (class_id) ON DELETE CASCADE
);

CREATE TABLE AssignmentCriteria (
    criterion_id INTEGER NOT NULL AUTO_INCREMENT,
    class_id INTEGER NOT NULL,
    assignment_id INTEGER NOT NULL,
    name VARCHAR(128) NOT NULL,
    value DECIMAL NOT NULL,
    weight DECIMAL NOT NULL,
    PRIMARY KEY (criterion_id),
    FOREIGN KEY (assignment_id) REFERENCES Assignments (assignment_id) ON DELETE CASCADE
);

CREATE TABLE Grades (
    assignment_criterion_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    grade DECIMAL NOT NULL,
    PRIMARY KEY (assignment_criterion_id,student_id),
    FOREIGN KEY (assignment_criterion_id) REFERENCES AssignmentCriteria (criterion_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES Users (user_id) ON DELETE CASCADE
);

CREATE TABLE Comments (
    comment_id INTEGER NOT NULL AUTO_INCREMENT,
    assignment_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    created_on DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    message VARCHAR(1024) NOT NULL,
    PRIMARY KEY (comment_id),
    FOREIGN KEY (assignment_id) REFERENCES Assignments (assignment_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES Users (user_id) ON DELETE CASCADE
);

CREATE TABLE Notifications (
    assignment_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    notification_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (assignment_id,student_id),
    FOREIGN KEY (assignment_id) REFERENCES Assignments (assignment_id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES Users (user_id) ON DELETE CASCADE
);

CREATE TABLE Memberships (
    user_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    permission_level INTEGER NOT NULL DEFAULT 0,
    visibility INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id,class_id),
    FOREIGN KEY (class_id) REFERENCES Classes (class_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE
);

CREATE TABLE LoginSessions (
    session_key INTEGER NOT NULL AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    expiration_time DATETIME NOT NULL,
    PRIMARY KEY (session_key),
    FOREIGN KEY (user_id) REFERENCES Users (user_id) ON DELETE CASCADE
);