# Creating the Database for the Fuel-based Method

import sqlite3

# Intialise database.

def init_db(db:sqlite3.Connection):

    create_fuel_table(db)
    create_refrigerant_table(db)
    create_vehicles_table(db)
    create_scores_emissions_fuel_table(db)
    create_score_emissions_distance_table(db)
    
def create_fuel_table(db:sqlite3.Connection):

    try:
        # Get Database cursor object
        c = db.cursor()

        # Remove existing Fuel table (if there is one) Doing this to make it easier to re-run the program when de-bugging

        c.execute("DROP TABLE IF EXISTS Fuel")

        # Create Fuel table

        sql = '''CREATE TABLE IF NOT EXISTS Fuel (
                                      fuel_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                      fuel_name VARCHAR NOT NULL,
                                      emission_factor REAL NOT NULL)
                                 '''
        c.execute(sql)
        db.commit()
        print('Fuel Table has been initialised')

    # If there is an error in creating user table, it explains the error in the form of an exception
    except sqlite3.Error as e:  

        db.rollback()
        print('Error. Cannot create Fuel Table. Reason:',e)
        raise e

def create_refrigerant_table(db:sqlite3.Connection):

    try:
        # Get Database Cursor Object
        c = db.cursor()
        # Remove existing Refrigerant Table (if there is one)
        c.execute("DROP TABLE IF EXISTS Refrigerant")

        # Create Refrigerant Table
        sql = '''CREATE TABLE IF NOT EXISTS Refrigerant (
                                      refrigerant_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                      refrigerant_name VARCHAR NOT NULL,
                                      gwp REAL NOT NULL)
                                 '''
        c.execute(sql)
        db.commit()
        print('Refrigerant Table has been initlialised')

    # If there is an error in creating user table, it explains the error in the form of an exception
    except sqlite3.Error as e:
        db.rollback()
        print('Error. Cannot create Refrigerant table. Reason:',e)
        raise e

def create_vehicles_table(db:sqlite3.Connection):

    try:
        # Get Database Cursor Object
        c = db.cursor()

        # Remove any Vehicles Table (if there is one)
        c.execute("DROP TABLE IF EXISTS Vehicles")

        # Create Vehicles Table
        sql = '''CREATE TABLE IF NOT EXISTS Vehicles (
                                      vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                      vehicle_name VARCHAR NOT NULL,
                                      fuel_efficiency REAL NOT NULL,
                                      fuel_id INTEGER NOT NULL,
                                      refrigerant_id INTEGER NOT NULL,
                                      FOREIGN KEY (fuel_id)
                                          REFERENCES Fuel(fuel_id)
                                              ON UPDATE CASCADE
                                              ON DELETE CASCADE
                                      FOREIGN KEY (refrigerant_id)
                                          REFERENCES Refrigerant(refrigerant_id)
                                              ON UPDATE CASCADE
                                              ON DELETE CASCADE)
                                '''
        c.execute(sql)
        db.commit()
        print('Vehicles table has been initialised')
        
    # Handles any errors using an exception.
    except sqlite3.Error as e:
        db.rollback()
        print('Error. Cannot create Vehicles table. Reason:',e)
        raise e

def create_scores_emissions_fuel_table(db:sqlite3.Connection):

    try:
        # Get database cursor object
        c = db.cursor()
        
        #Remove any Score Emissions Fuel tables (if there is one)
        c.execute("DROP TABLE IF EXISTS ScoresEmissionsFuel")

        #Create Emissions Fuel table
        sql = '''CREATE TABLE IF NOT EXISTS  ScoresEmissionsFuel(
                                       round INTEGER PRIMARY KEY AUTOINCREMENT,
                                       total_emissions REAL NOT NULL,
                                       vehicle_id INTEGER NOT NULL,
                                       quantity_refrigerant_leaked REAL NOT NULL,
                                       distance REAL NOT NULL,
                                       FOREIGN KEY (vehicle_id)
                                           REFERENCES Vehicles(vehicles_id)
                                               ON UPDATE CASCADE
                                               ON DELETE CASCADE  )                                                    
                                '''
        c.execute(sql)
        db.commit()
        print('Scores Emissions Fuel Table has been initialised')
        
    except sqlite3.Error as e:
        db.rollback()
        print('Error. Cannot create Scores Emissions Fuel Table. Reason:',e)
        raise e

def create_score_emissions_distance_table(db:sqlite3.Connection):

    try:
        # Get database cursor object
        c = db.cursor()
        #Remove any Emissions Distance tables (if there is one)
        c.execute("DROP TABLE IF EXISTS ScoresEmissionsDistance")

        # Create Emissions Distance table
        sql = '''CREATE TABLE IF NOT EXISTS ScoresEmissionsDistance (
                                        round INTEGER PRIMARY KEY AUTOINCREMENT,
                                        total_emissions REAL NOT NULL,
                                        vehicle_id INTEGER NOT NULL,
                                        mass_goods_purchased REAL NOT NULL,
                                        distance REAL NOT NULL,
                                        FOREIGN KEY (vehicle_id)
                                            REFERENCES Vehicles(vehicles_id)
                                                ON UPDATE CASCADE
                                                ON DELETE CASCADE)
                                    '''
        c.execute(sql)
        db.commit()
        print('Scores Emissions Distance Table has been initialised')

    except sqlite3.Error as e:
        db.rollback()
        print('Error. Cannot create Scores Emissions Distance Table. Reason:',e)
        raise e
                                          
if __name__ == '__main__':

    # Setting up DB Connection

    DB_path = 'CalculateEmissions_db.db'
    db = sqlite3.connect(DB_path, detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row

    init_db(db)


                                        
                                          
                                      
