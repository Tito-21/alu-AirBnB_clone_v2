# AirBnB Clone - MySQL

## Project Description
This is the second version of the AirBnB clone project, implementing MySQL database storage alongside the existing file storage system. The project demonstrates the use of Object-Relational Mapping (ORM) with SQLAlchemy to manage database operations.

## Team Members
- Patrick Tuyizere
- Elvis Shimwa

## Environment Variables
The application uses the following environment variables:

- `HBNB_ENV`: Running environment (`dev`, `test`, or `production`)
- `HBNB_MYSQL_USER`: MySQL username
- `HBNB_MYSQL_PWD`: MySQL password
- `HBNB_MYSQL_HOST`: MySQL hostname (default: localhost)
- `HBNB_MYSQL_DB`: MySQL database name
- `HBNB_TYPE_STORAGE`: Storage type (`file` for FileStorage or `db` for DBStorage)

## Installation

### Prerequisites
- Python 3.8.5+
- MySQL 8.0+
- SQLAlchemy 1.4.x

### Setup
1. Clone the repository:
```bash
git clone https://github.com/your-username/alu-AirBnB_clone_v2.git
cd alu-AirBnB_clone_v2
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup MySQL databases:
```bash
# Development database
cat setup_mysql_dev.sql | mysql -hlocalhost -uroot -p

# Test database
cat setup_mysql_test.sql | mysql -hlocalhost -uroot -p
```

## Usage

### Console Commands
The console supports creating objects with parameters:

```bash
# Using FileStorage
./console.py

# Using DBStorage
HBNB_MYSQL_USER=hbnb_dev HBNB_MYSQL_PWD=hbnb_dev_pwd HBNB_MYSQL_HOST=localhost HBNB_MYSQL_DB=hbnb_dev_db HBNB_TYPE_STORAGE=db ./console.py
```

### Creating Objects with Parameters
```
create State name="California"
create City state_id="<state_id>" name="San_Francisco"
create Place city_id="<city_id>" user_id="<user_id>" name="My_little_house" number_rooms=4 number_bathrooms=2 max_guest=10 price_by_night=300 latitude=37.773972 longitude=-122.431297
```

## Testing
Run all tests:
```bash
python3 -m unittest discover tests
```

Run specific test file:
```bash
python3 -m unittest tests/test_models/test_base_model.py
```

Test with DBStorage:
```bash
HBNB_ENV=test HBNB_MYSQL_USER=hbnb_test HBNB_MYSQL_PWD=hbnb_test_pwd HBNB_MYSQL_HOST=localhost HBNB_MYSQL_DB=hbnb_test_db HBNB_TYPE_STORAGE=db python3 -m unittest discover tests
```

## Project Structure
```
alu-AirBnB_clone_v2/
├── models/
│   ├── __init__.py
│   ├── base_model.py
│   ├── user.py
│   ├── state.py
│   ├── city.py
│   ├── amenity.py
│   ├── place.py
│   ├── review.py
│   └── engine/
│       ├── __init__.py
│       ├── file_storage.py
│       └── db_storage.py
├── tests/
│   └── test_models/
├── console.py
├── setup_mysql_dev.sql
├── setup_mysql_test.sql
├── requirements.txt
└── README.md
```

## Features
- Dual storage system (File and Database)
- SQLAlchemy ORM integration
- MySQL database support
- Command-line interface with parameter parsing
- Comprehensive unit tests
- Environment-based configuration

## Learning Objectives
- Unit testing in large projects
- Using *args and **kwargs
- Handling named arguments
- Creating MySQL databases and users
- Understanding ORM (Object-Relational Mapping)
- Mapping Python classes to MySQL tables
- Managing multiple storage engines
- Using environment variables

## Authors
- Patrick Tuyizere
- Elvis Shimwa

## License
This project is part of the ALU Software Engineering program.
