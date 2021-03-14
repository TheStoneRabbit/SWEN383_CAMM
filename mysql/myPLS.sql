


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



/* 
A course needs to be created by an admin before: 
    a professor can add and edit via the lesson table
    an admin can add professors and learners to said course via enrollment
*/
CREATE TABLE course (
    courseID    varchar(7),
    courseName  varchar(50) NOT NULL,   
    capacity    tinyint,
    CONSTRAINT course_pk PRIMARY KEY (courseID)
);



/* 
    Holds all groups 
    Public groups are populated in the publicGroup table
    Private groups are populated during enrollment since membership is dependent on course
*/
CREATE TABLE discussionArea (
    groupID     int,
    /* groupType where public = 0 and private = 1 */
    groupType   tinyint NOT NULL,
    /* PUBLIC GROUP will have attached discussionUsers list to keep track of users */
    /* PRIVATE GROUP only so can be null */
    hashPassword    varchar(200),
    /* course must exist before a private group can be created for it */
    CONSTRAINT discussionArea_pk PRIMARY KEY (groupID)
);



/* Only admins have access to edit the enrollment table */
CREATE TABLE enrollment (
    courseID    varchar(7),
    /* Either a learner or a professor */
    userID      int,
    /* Automatic enrollment in private group for the course */
    groupID     int,

    /* Grade, professorRatiing, and courseRating can be null since they are only applicable to a learner user type */
    grade       char(2), 
    /* Learner can rate the associated course and professor teaching the course */
    professorRating     tinyint,
    courseRating        tinyint,
    /* course must be added before lessons can be added to it */
    CONSTRAINT enrollment_course_fk FOREIGN KEY (courseID) REFERENCES course(courseID),
    /* user must exist to be added to a course */
    CONSTRAINT enrollment_user_fk FOREIGN KEY (userID) REFERENCES user(userID),
    CONSTRAINT enrollment_pk PRIMARY KEY (courseID, userID)
);



/* Only professors have access to edit and add lessons to a course */
CREATE TABLE lesson (
    courseID    varchar(7),
    lessonNum   tinyint,
    /* quiz will hold multiple choice questions, not varchar */
    quiz    varchar(100) NOT NULL,
    /* course must exist before a lesson can be added to it */
    CONSTRAINT courseMaterial_fk FOREIGN KEY (courseID) REFERENCES course(courseID),
    CONSTRAINT courseMaterial_pk PRIMARY KEY (courseID, lessonNum)
);



/* Only professors have access to edit and add multimedia to lessons */
/* Adds multimedia files (names) to a lesson for a given course */
CREATE TABLE multimedia (
    courseID    varchar(7),
    lessonNum   tinyint,
    multimediaFile  varchar(50),
    /* fileType where document/written = 0, video = 1, and audio = 2 */
    fileType    tinyint    NOT NULL,
    /* course and lesson must exist before multimedia can be added to it */
    CONSTRAINT multimedia_fk FOREIGN KEY (courseID, lessonNum) REFERENCES lesson(courseID, lessonNum),
    CONSTRAINT multimedia_pk PRIMARY KEY (courseID, lessonNum, multimediaFile)
);



/* 
    Needed for public groups as anyone can enter and leave at any time 
    Private Groups already handled during enrollment automatically
*/
CREATE TABLE publicGroup (
    groupID     int,
    userID      int,
     /* group must exist before a user can be added to it */
    CONSTRAINT discussionArea_fk FOREIGN KEY (groupID) REFERENCES discussionArea(groupID),
    /* user must exist before it can be added to a group */
    CONSTRAINT enrollment_user_fk FOREIGN KEY (userID) REFERENCES user(userID),
    CONSTRAINT discussionArea_pk PRIMARY KEY (groupID, userID)
);



/* User test cases */
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Mason", "Lapine", 4263, "mwl4263@rit.edu", "d64dfa6e3c81910d0267c38b158690cf50722b8c4b259f1bc8ea77ea180d6451", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Johnny", "Appleseed", 1001, "js1001@rit.edu", "f5903f51e341a783e69ffc2d9b335048716f5f040a782a2764cd4e728b0f74d9", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Robert", "Smalls", 6969, "rws6969@rit.edu", "9f280e9535116563c84ba9135f7b44ef95fd13e68d8d6e8488af0d79445a7f45", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Admin", "Admin", 1111, "admin@rit.edu", "713bfda78870bf9d1b261f565286f85e97ee614efe5f0faf7c34e7ca4f65baca", 0);
