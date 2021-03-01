


DROP DATABASE IF EXISTS myPLS;

CREATE DATABASE myPLS;

USE myPLS;

/* Creation of the superclass table with basics for login and identification */
CREATE TABLE user (
    firstName   varchar(30) NOT NULL,
    lastName    varchar(30) NOT NULL,
    userID      int,
    email       varchar(50) NOT NULL,
    hashPassword    varchar(200) NOT NULL,
    /* typeU where adminU = 0, professorU = 1, and learnerU = 2*/
    typeU       tinyint NOT NULL,
    CONSTRAINT user_pk PRIMARY KEY (userID)
);


/* subclass of user*/
CREATE TABLE adminU ();


/* subclass of user*/
CREATE TABLE professorU ();


/* subclass of user*/
CREATE TABLE learnerU ();


/* 
A course needs to be created by an admin before: 
    a professor can add course material via courseMaterial
    an admin can add professors and learners to said course via enrollment
*/
CREATE TABLE course (
    courseID    varchar(7),
    courseName  varchar(50) NOT NULL,
    capacity    tinyint,
    CONSTRAINT course_pk PRIMARY KEY (courseID)
);


/* Only professors have access to edit the courseMaterial table */
CREATE TABLE courseMaterial (
    courseID    varchar(7),
    /* content will hold some type of file, not varchar */
    content     varchar(100),
    /* course must exist before material can be added to it */
    CONSTRAINT courseMaterial_fk FOREIGN KEY (courseID) REFERENCES course(courseID),
    CONSTRAINT courseMaterial_pk PRIMARY KEY (courseID, content)
);


/* Only admins have access to edit the enrollment table */
CREATE TABLE enrollment (
    courseID    varchar(7),
    userID      int,
    /* Grade can be null since a user can be a professor */
    grade       char(2), 
    /* A given course has a learner rating */
    rating      tinyint, 
    /* course must be added before material can be added to it */
    CONSTRAINT enrollment_course_fk FOREIGN KEY (courseID) REFERENCES course(courseID),
    /* user must exist to be added to a course */
    CONSTRAINT enrollment_user_fk FOREIGN KEY (userID) REFERENCES user(userID),
    CONSTRAINT enrollment_pk PRIMARY KEY (courseID, userID)
);

/* User test cases */
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Mason", "Lapine", 4263, "mwl4263@rit.edu", "d64dfa6e3c81910d0267c38b158690cf50722b8c4b259f1bc8ea77ea180d6451", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Johnny", "Appleseed", 1001, "js1001@rit.edu", "f5903f51e341a783e69ffc2d9b335048716f5f040a782a2764cd4e728b0f74d9", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Robert", "Smalls", 6969, "rws6969@rit.edu", "9f280e9535116563c84ba9135f7b44ef95fd13e68d8d6e8488af0d79445a7f45", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Admin", "Admin", 1111, "admin@rit.edu", "713bfda78870bf9d1b261f565286f85e97ee614efe5f0faf7c34e7ca4f65baca", 0);
