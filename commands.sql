create database playWithCSV;
use playWithCSV;
create table users(
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	name VARCHAR(255) NOT NULL,
	email VARCHAR(255) NOT NULL,
	password VARCHAR(255) NOT NULL,
	phone_no VARCHAR(255) NOT NULL
);

create table csv_data(
	id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
	email VARCHAR(255),
	name VARCHAR(255),
	phone_no VARCHAR(255),
	location VARCHAR(255)
);
