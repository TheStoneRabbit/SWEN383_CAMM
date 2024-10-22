/*
OK, so I am going to have to add another column to user called groupID.  This column will dictate what group(s) the users are in
*/


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
    /* Assumed courseLoc and courseTimes format is "Teusday 5:30pm - 6:45pm, Thursday 2:00pm - 4:15pm" */
    courseLoc   varchar(100) NOT NULL,
    courseTimes   varchar(100) NOT NULL,  
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
    lessonNum   int,
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
    lessonNum   int,
    multimediaFile  varchar(50),
    /* course and lesson must exist before multimedia can be added to it */
    CONSTRAINT multimedia_fk FOREIGN KEY (courseID, lessonNum) REFERENCES lesson(courseID, lessonNum),
    CONSTRAINT multimedia_pk PRIMARY KEY (courseID, lessonNum, multimediaFile)
);



/* 
    Needed for public groups as anyone can enter and leave at any time 
    Private Groups already handled during enrollment automatically
*/
CREATE TABLE user_group (
    groupID     int,
    title       varchar(30),
    group_description   varchar(200),
     /* group must exist before a user can be added to it */
    -- CONSTRAINT discussionArea_fk FOREIGN KEY (groupID) REFERENCES discussionArea(groupID),
    /* user must exist before it can be added to a group */
    CONSTRAINT group_pk PRIMARY KEY (groupID)
);


CREATE TABLE studentGroups (
    userID      int,
    groupID     int,
    post        varchar(500),
    postTime    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT group_pk PRIMARY KEY (userID, groupID, post, postTime),
    CONSTRAINT group_fk_user FOREIGN KEY (userID) REFERENCES user(userID),
    CONSTRAINT group_fk_ID FOREIGN KEY (groupID) REFERENCES user_group(groupID)
);


CREATE TABLE groupRequestQueue (
    userID      int,
    groupID     int,
    /* "Add" or "Remove" to indicate which functionality */
    addOrRemove     varchar(10),
    CONSTRAINT queue_pk PRIMARY KEY (userID, groupID),
    CONSTRAINT queue_fk_user FOREIGN KEY (userID) REFERENCES user(userID),
    CONSTRAINT queue_fk_group FOREIGN KEY (groupID) REFERENCES user_group(groupID)
);


CREATE TABLE quiz (
    courseID varchar(7),
    quizID  int,
    quizTitle varchar(50),
    CONSTRAINT quiz_fk FOREIGN KEY (courseID) REFERENCES course (courseID),
    CONSTRAINT quiz_pk PRIMARY KEY (quizID)
);


CREATE TABLE quizQuestion (
    quizID int,
    questionNum int,
    questionDesc varchar(100),
    option1 varchar(20),
    option2 varchar(20),
    option3 varchar(20),
    correct varchar(20),
    CONSTRAINT quizQuestion_fk FOREIGN KEY (quizID) REFERENCES quiz (quizID),
    CONSTRAINT quizQuestion_pk PRIMARY KEY (quizID, questionNum)
);

/* Starter Users */
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Mason", "Lapine", 4263, "mwl4263@rit.edu", "d64dfa6e3c81910d0267c38b158690cf50722b8c4b259f1bc8ea77ea180d6451", 0);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Alexis", "Gordon", 7593, "aag7593@rit.edu", "713bfda78870bf9d1b261f565286f85e97ee614efe5f0faf7c34e7ca4f65baca", 0);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Conor", "Keegan", 5876, "cfk5876@rit.edu", "713bfda78870bf9d1b261f565286f85e97ee614efe5f0faf7c34e7ca4f65baca", 0);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Max", "Gerber", 4789, "mlg4789@rit.edu", "713bfda78870bf9d1b261f565286f85e97ee614efe5f0faf7c34e7ca4f65baca", 0);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Admin", "Admin", 1, "admin@rit.edu", "713bfda78870bf9d1b261f565286f85e97ee614efe5f0faf7c34e7ca4f65baca", 0);

INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Michael", "McQuaid", 4239, "mjmics@rit.edu", "34550715062af006ac4fab288de67ecb44793c3a05c475227241535f6ef7a81b", 1);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Stephen", "Cady", 5237, "sgcics@rit.edu", "267eed33dc459584a996e2cb0613d1d5cfa3c64ad6d97558f477ff74a2e5f71e", 1);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("AbdulMutalib", "Wahaishi", 2015, "tawvse@rit.edu", "26a6b71abb93734b2f2e3f3b6722dc620cd111ababc4e2cdddecbc2499c04ac8", 1);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Jim", "Habermas", 8045, "jim.habermas@rit.edu", "484ae24edd22ea09a58edc2b6c58ee2b5f3879e3b267838a8726366f255fd4b9", 1);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Eleanor", "Chand-Matzke", 0829, "aecgsh@rit.edu", "cd0299854a830cfdbcfb7d6887ddb636c09496099c873f6ce5496aec9c3f044a", 1);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Paul", "Goldman", 2130, "plgics@rit.edu", "0357513deb903a056e74a7e475247fc1ffe31d8be4c1d4a31f58dd47ae484100", 1);

INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Johnny", "Appleseed", 1001, "js1001@rit.edu", "f5903f51e341a783e69ffc2d9b335048716f5f040a782a2764cd4e728b0f74d9", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Robert", "Smalls", 6969, "rws6969@rit.edu", "9f280e9535116563c84ba9135f7b44ef95fd13e68d8d6e8488af0d79445a7f45", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Jameela", "Jamil", 1234, "jjj1234@rit.edu", "24428ae0bbaacc798de0022478eb2cf76c5d5e2f6f1e56d34181aed2b7c302fc", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Michael", "Goodman", 3717, "mog3717@rit.edu", "34550715062af006ac4fab288de67ecb44793c3a05c475227241535f6ef7a81b", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Janet", "Denunzio", 4321, "jdd4321@rit.edu", "0c081477c9bcc99ed2f0b1449dcb034db402ab44c5a73faf01e75303a31f3a64", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Malcom", "Thomas", 6430, "mtt6430@rit.edu", "8298f0dc5d2aa6ce680676c9b6d2ee7ca579c3c337fffde395c7adc12b2f7983", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Eleanor", "Shellstrop", 6669, "ees6669@rit.edu", "cd0299854a830cfdbcfb7d6887ddb636c09496099c873f6ce5496aec9c3f044a", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Anna", "Michaels", 6749, "amm6749@rit.edu", "55579b557896d0ce1764c47fed644f9b35f58bad620674af23f356d80ed0c503", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Shawn", "Evil", 6960, "sse6960@rit.edu", "a30a997579a6d8733555003b7cc698864186fb708731dfdcd14c5e0a22a945e9", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Jason", "Mendoza", 7835, "jbm7835@rit.edu", "06b9a6eacd7a77b9361123fd19776455eb16b9c83426a1abbf514a414792b73f", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Chidi", "Anagonye", 7890, "caa7890@rit.edu", "f41cbe44b294a49ff2ea8557e0039ebb6a0758b7c72f1ebe9d473c13c0c7a0f0", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Benjamin", "Tarentino", 9854, "but9854@rit.edu", "f3c7769dd45d51cbd33a2105124274b75dfb43ecc028d899c2313a4f2f0f95ce", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Ashley", "Saperstein", 3424, "axs3424@rit.edu", "c64975ba3cf3f9cd58459710b0a42369f34b0759c9967fb5a47eea488e8bea79", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Axes", "Smith", 0493, "abs0493@rit.edu", "56f4655f8022518d8ec47843d889343bffacdb529abc1182181578ddc1cb181a", 2);
INSERT INTO user (firstname, lastname, userID, email, hashpassword, typeU) values ("Bethany", "Mota", 2847, "bam2847@rit.edu", "af7c752bf81f575efe5ac39f7ab8c61a3668ff0cf7e950114194fa5267cc830a", 2);



/* Starter Courses */
INSERT INTO course (courseID, courseName, capacity, courseLoc, courseTimes) values ('ISTE330', 'Database and Connectivity', 30, 'GOL 2620', 'Monday 12:20pm - 1:10pm, Wednesday 12:20pm - 1:10pm, Friday 12:20pm - 1:10pm');
INSERT INTO course (courseID, courseName, capacity, courseLoc, courseTimes) values ('ISTE252', 'Foundations of Mobile Computing', 28, 'GOL 3510', 'Tuesday 2pm - 3:15pm, Thursday 2pm - 3:15pm');
INSERT INTO course (courseID, courseName, capacity, courseLoc, courseTimes) values ('ISTE264', 'Prototyping and Usability Testing', 34, 'GOL 3510', 'Monday 11:15am - 12:05pm, Wednesday 11:15am - 12:05pm, Friday 11:15am - 12:05pm');
INSERT INTO course (courseID, courseName, capacity, courseLoc, courseTimes) values ('SWEN383', 'Software Design Principles & Patterns', 24, 'Tuesday GOL 1550, Thursday ONLINE', 'Tuesday 8:00am - 9:15am, Thursday 8:00am - 9:15am');
INSERT INTO course (courseID, courseName, capacity, courseLoc, courseTimes) values ('ISTE340', 'Client Programming', 24, 'ONLINE', 'Tuesday 9:30am - 10:45am, Thursday 9:30am - 10:45am');
INSERT INTO course (courseID, courseName, capacity, courseLoc, courseTimes) values ('PSYC251', 'Research Methods II', 28, 'Tuesday ONLINE, Thursday LBR 3244', 'Tuesday 12:30pm - 1:45pm, Thursday 12:30pm - 1:45pm');


/* Starter Enrollment */
/* Professors */
INSERT INTO enrollment (courseID, userID) values ('ISTE252', 5237);
INSERT INTO enrollment (courseID, userID) values ('SWEN383', 2015);
INSERT INTO enrollment (courseID, userID) values ('ISTE264', 4239);
INSERT INTO enrollment (courseID, userID) values ('ISTE330', 8045);
INSERT INTO enrollment (courseID, userID) values ('ISTE340', 2130);


/* Learners */
INSERT INTO enrollment (courseID, userID) values ('ISTE252', 7890);
INSERT INTO enrollment (courseID, userID) values ('ISTE252', 7835);
INSERT INTO enrollment (courseID, userID) values ('ISTE252', 6669);
INSERT INTO enrollment (courseID, userID) values ('ISTE252', 4321);
INSERT INTO enrollment (courseID, userID) values ('ISTE252', 3717);
INSERT INTO enrollment (courseID, userID) values ('ISTE252', 1234);

INSERT INTO enrollment (courseID, userID) values ('SWEN383', 1001);
INSERT INTO enrollment (courseID, userID) values ('SWEN383', 6969);
INSERT INTO enrollment (courseID, userID) values ('SWEN383', 6430);
INSERT INTO enrollment (courseID, userID) values ('SWEN383', 6749);
INSERT INTO enrollment (courseID, userID) values ('SWEN383', 6960);

INSERT INTO enrollment (courseID, userID) values ('ISTE264', 9854);
INSERT INTO enrollment (courseID, userID) values ('ISTE264', 3424);
INSERT INTO enrollment (courseID, userID) values ('ISTE264', 0493);

INSERT INTO enrollment (courseID, userID) values ('PSYC251', 0829);
INSERT INTO enrollment (courseID, userID) values ('PSYC251', 9854);
INSERT INTO enrollment (courseID, userID) values ('PSYC251', 3424);
INSERT INTO enrollment (courseID, userID) values ('PSYC251', 0493);

INSERT INTO enrollment (courseID, userID, grade, professorRating, courseRating) values ('ISTE340', 9854, 95, 2, 3);
INSERT INTO enrollment (courseID, userID, grade, professorRating, courseRating) values ('ISTE340', 3424, 88, 1, 3);
INSERT INTO enrollment (courseID, userID, grade, professorRating, courseRating) values ('ISTE340', 0493, 90, 3, 4);

INSERT INTO enrollment (courseID, userID) values ('ISTE330', 9854);
INSERT INTO enrollment (courseID, userID) values ('ISTE330', 3424);
INSERT INTO enrollment (courseID, userID) values ('ISTE330', 0493);



/* Starter Groups */
INSERT INTO user_group (groupID, title, group_description) VALUES (1, "ISTE340 Discussion", "This is the Client Programming course discussion. Anyone currently taking the course can discuss JavaScript syntax, properties, and more.");
INSERT INTO user_group (groupID, title, group_description) VALUES (2, "SWEN383 Discussion", "This is the Software Design Principles and Patterns course discussion. Anyone currently taking the course can discuss functional requirements, domain models, design patterns, and more.");
INSERT INTO user_group (groupID, title, group_description) VALUES (3, "ISTE264 Group Project", "This is a private group dicussion for members of the App redesign project.");

INSERT INTO studentGroups VALUES (9854, 1, "User 9854 has been added to this group", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (6960, 2, "User 6960 has been added to this group", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (9854, 3, "User 9854 has been added to this group", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (0493, 3, "User 0493 has been added to this group", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (1001, 2, "User 1001 has been added to this group", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (3424, 1, "User 3424 has been added to this group", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (0493, 1, "User 0493 has been added to this group", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (6969, 2, "User 6969 has been added to this group", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (3424, 3, "User 3424 has been added to this group", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (2130, 1, "User 2130 has been added to this group", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (9854, 1, "Hey guys", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (6960, 2, "Hello everyone. I just joined. Do we have any work due soon?", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (9854, 3, "what's up guys", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (0493, 3, "Hello!", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (1001, 2, "I think we have some homework due saturday", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (3424, 1, "I will be right back", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (0493, 1, "how are you guys doing?", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (6969, 2, "i am going to get started on my work right now", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (3424, 3, "this is the best group ever", CURRENT_TIMESTAMP);
INSERT INTO studentGroups VALUES (2130, 1, "i am doing well", CURRENT_TIMESTAMP);

INSERT INTO lesson VALUES ('ISTE340', 1, " ");
INSERT INTO multimedia VALUES ('ISTE340', 1, 'placeholder.txt');
INSERT INTO multimedia VALUES ('ISTE340', 1, 'Lesson1.pptx');
INSERT INTO multimedia VALUES ('ISTE340', 1, 'Lesson1.txt');

INSERT INTO quiz (courseID, quizID, quizTitle) VALUES ("ISTE264", 1, "ISTE-264 Quiz");
INSERT INTO quiz (courseID, quizID, quizTitle) VALUES ("ISTE330", 2, "ISTE-330 Quiz");

INSERT INTO quizQuestion (quizID, questionNum, questionDesc, option1, option2, option3, correct) VALUES (1, 1, "Which is a mobile deivce?", "Laptop", "Desktop", "T.V.", "iPhone");
INSERT INTO quizQuestion (quizID, questionNum, questionDesc, option1, option2, option3, correct) VALUES (1, 2, "What sound does a dog make?", "Meow", "Moo", "Quack", "Woof");
INSERT INTO quizQuestion (quizID, questionNum, questionDesc, option1, option2, option3, correct) VALUES (1, 3, "What is 3 + 3?", "2", "5", "3", "6");
INSERT INTO quizQuestion (quizID, questionNum, questionDesc, option1, option2, option3, correct) VALUES (1, 4, "What color is the sky?", "Green", "Red", "Orange", "Blue");

INSERT INTO quizQuestion (quizID, questionNum, questionDesc, option1, option2, option3, correct) VALUES (2, 1, "Whhich language is used for database queries?", "C++", "Java", "Python", "MySQL");
INSERT INTO quizQuestion (quizID, questionNum, questionDesc, option1, option2, option3, correct) VALUES (2, 2, "What is the name of your local server?", "MyServer", "Server", "personalServer", "localhost");
INSERT INTO quizQuestion (quizID, questionNum, questionDesc, option1, option2, option3, correct) VALUES (2, 3, "Which database statement is used to view information?", "DELETE", "UPDATE", "DROP", "SELECT");
INSERT INTO quizQuestion (quizID, questionNum, questionDesc, option1, option2, option3, correct) VALUES (2, 4, "How do you drop a database?", "SELECT statement", "DELETE statement", "UPDATE statement", "DROP statement");