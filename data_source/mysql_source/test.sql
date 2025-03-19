-- Create the test database 
CREATE DATABASE IF NOT EXISTS testdb;

USE testdb;

-- 2. Create the Departments Table
CREATE TABLE IF NOT EXISTS departments (
    department_id INT AUTO_INCREMENT PRIMARY KEY, -- Primary Key
    department_name VARCHAR(100) NOT NULL, -- Department name
    location VARCHAR(100) NOT NULL -- Location of the department
);

-- 3. Create the Employees Table
CREATE TABLE IF NOT EXISTS employees (
    employee_id INT AUTO_INCREMENT PRIMARY KEY, -- Primary Key
    first_name VARCHAR(100) NOT NULL, -- First name of the employee
    last_name VARCHAR(100) NOT NULL, -- Last name of the employee
    email VARCHAR(100) UNIQUE NOT NULL, -- Email (unique for each employee)
    hire_date DATE NOT NULL, -- Date of hire
    department_id INT, -- Foreign Key
    FOREIGN KEY (department_id) REFERENCES departments(department_id) -- Linking employee to a department
);

-- 4. Create the Salaries Table
CREATE TABLE IF NOT EXISTS salaries (
    salary_id INT AUTO_INCREMENT PRIMARY KEY, -- Primary Key
    employee_id INT, -- Foreign Key
    salary_amount DECIMAL(10, 2) NOT NULL, -- Salary amount
    start_date DATE NOT NULL, -- Start date of the salary period
    end_date DATE NOT NULL, -- End date of the salary period
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) -- Linking salary to an employee
);


-- SHOW tables;

-- Inserting data into departments table
INSERT INTO departments (department_name, location) VALUES
('Human Resources', 'New York'),
('Sales', 'San Francisco'),
('Engineering', 'London');

-- Inserting data into employees table
INSERT INTO employees (first_name, last_name, email, hire_date, department_id) VALUES
('John', 'Doe', 'john.doe@example.com', '2020-01-15', 1),
('Jane', 'Smith', 'jane.smith@example.com', '2019-03-10', 2),
('Mike', 'Johnson', 'mike.johnson@example.com', '2018-07-23', 3);

-- Inserting data into salaries table
INSERT INTO salaries (employee_id, salary_amount, start_date, end_date) VALUES
(1, 55000.00, '2020-01-15', '2021-01-15'),
(2, 75000.00, '2019-03-10', '2020-03-10'),
(3, 100000.00, '2018-07-23', '2019-07-23');



SELECT * FROM employees;
SELECT * FROM salaries;
SELECT * FROM departments;