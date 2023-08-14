# Front End Program - To be Run by the User

import sqlite3
import numpy as np
import CalculatingEmissions, ScoringEmissions, GraphEmissions

class Common_Components:

    # Constructor
    def __init__(self):

        self._vehicle_name = None
        self._distance = None
        self._emissions_total = None
        self._refrigerant_name = None

    # Exceptions

    def _vehicle_name_exception(self,max_id):
        print('ERROR: Please enter an integer from 1 to '+str(max_id)+' to give the vehicle used.')

    def _num_postcodes_exception(self,max_postcodes):
        print('ERROR: Please enter an integer from 2 to '+str(max_postcodes)+' to give the no. of junctions in the transportation journey.')

    def _calculate_distance_exception(self):
        print('ERROR: One of these postcodes does not exist. Please enter existent postcodes.')

    # Setters
    def _set_vehicle_name(self,db):

        c = db.cursor()
        print()
        print('Available Vehicles for Scoring: ') # Presents all vehicles to the user
        print()
        vehicles_object = c.execute('SELECT vehicle_name FROM vehicles')
        vehicles = c.fetchall()

        for vehicle in vehicles:
            vehicle_id_object = c.execute('SELECT vehicle_id FROM Vehicles WHERE vehicle_name=?',(vehicle[0],))
            vehicle_id = str(c.fetchone()[0])
            print(vehicle_id + '. ',vehicle[0])

        max_id_object = c.execute('SELECT MAX(vehicle_id) FROM Vehicles') 
        max_id = c.fetchone()[0]
        
        valid = False
        while valid is False:
            print()
            try:
                vehicle_id = int(input('Enter the vehicle (1-'+str(max_id)+') used in Transportation: ')) 
                if 0 < vehicle_id <= max_id:
                    vehicle_name_object = c.execute('SELECT vehicle_name FROM Vehicles WHERE vehicle_id=?',(vehicle_id,))
                    vehicle_name = c.fetchone()[0]
                    self._vehicle_name = vehicle_name
                    valid = True
                else:
                    self._vehicle_name_exception(max_id)
            except ValueError:
                self._vehicle_name_exception(max_id)

    def _set_distance(self):

        max_postcodes = 6
        print()
        print('The maximum number of postcodes that can be entered is '+ str(max_postcodes))
        valid  = False # Validates number of postcodes passed in journey
        while valid is False:
            print()
            try:
                num_postcodes = int(input('How many junctions are there in the transportation journey? '))
                if 1< num_postcodes <= max_postcodes:
                    valid = True
                else:
                    self._num_postcodes_exception(max_postcodes)
            except ValueError:
                self._num_postcodes_exception(max_postcodes)

        distance_successful = False # Calculates distance travelled
        while distance_successful is False:

            print()
            print('Please enter the postcodes of these junctions below: ')
            print('NB: Please ensure that the spaces in the address are in the right places.')
            postcodes = []
            for i in range(num_postcodes): # Validates each address entered in by calculating the distance between those 2 postcodes.
                print()
                address = input('Postcode ' + str(i+1) + ': ')
                postcodes.append(address)
            try:
                self._distance = CalculatingEmissions.CalculateDistance(postcodes)
                distance_successful = True
            except:
                self._calculate_distance_exception()

    def _set_refrigerant_name(self,db):
        c = db.cursor()
        sql = '''SELECT Refrigerant.refrigerant_name FROM Vehicles
                 INNER JOIN Refrigerant ON Vehicles.refrigerant_id=Refrigerant.refrigerant_id
                 WHERE Vehicles.vehicle_name=?'''
        refrigerant_name_object = c.execute(sql,(self._vehicle_name,))
        self._refrigerant_name = c.fetchone()[0]
        
    def _set_emissions_total(self,calculation_method,attributes):
        
        self._emissions_total = CalculatingEmissions.CalculateEmissions(calculation_method,attributes)
            
    def _set_all_month_data(self):
        pass
    # Output method
    def _print_all_month_data(self):
        pass

class Fuel_based(Common_Components): # Inherits from Common_Components

    def __init__(self):
        super().__init__()
        self._quantity_refrigerant_leaked = None

    # Exceptions
    def __quantity_refrigerant_exception(self):
        print('ERROR: Please enter a positive number. ')

    # Setters

    def __set_quantity_refrigerant_leaked(self):

        print()
        print('Please enter the quantity of refrigerant leaked by your vehicle.')
        print('The refrigerant used by your vehicle is ',self._refrigerant_name)
        valid = False
        while valid is False:
            print()
            try:
                quantity_refrigerant_leaked = float(input('Quantity of '+str(self._refrigerant_name)+' leaked: '))
                if quantity_refrigerant_leaked >= 0:
                    self._quantity_refrigerant_leaked = quantity_refrigerant_leaked
                    valid = True
                else:
                    self.__quantity_refrigerant_exception()
            except ValueError:
                self.__quantity_refrigerant_exception()

    def _set_all_month_data(self,db,month,calculation_method):
        print()
        print('Month '+str(month))
        print('-------')
        self._set_distance()
        self._set_vehicle_name(db)
        self._set_refrigerant_name(db)
        self.__set_quantity_refrigerant_leaked()
        self._set_emissions_total(calculation_method,[db,self._vehicle_name,self._distance,self._refrigerant_name,self._quantity_refrigerant_leaked])

    # Output Method

    def _print_all_month_data(self): # Overrides the method print_all_month_data in parent class

        print('Vehicle used: ',self._vehicle_name)
        print('Distance travelled in 1 journey: ',self._distance)
        print('Quantity Refrigerant Leaked in 1 journey: ',self._quantity_refrigerant_leaked)
        print('Total emissions emitted in 1 journey: ',str(round(self._emissions_total,2)),'CO2e')
            
class Distance_based(Common_Components): # Inherits from Common_Components
    
    def __init__(self):
        super().__init__()
        self._mass_purchased = None

    # Exceptions

    def __mass_exception(self):
        print("ERROR: Please enter a mass between 0 and 500kg.")

    # Setters
    def __set_mass_purchased(self):
        max_mass = 500
        print('Please enter the Mass of goods purchased below. NB: Maximum mass is 500 kg')
        valid = False
        while valid is False:
            print()
            try:
                mass_purchased = float(input('Mass of Goods purchased: '))
                if 0 < mass_purchased <= 500:
                    self._mass_purchased = mass_purchased
                    valid = True
                else:
                    self.__mass_exception()
            except ValueError:
                self.__mass_exception()

    def _set_all_month_data(self,db,month,calculation_method):
        print()
        print('Month '+str(month))
        print('-------')
        self._set_distance()
        self._set_vehicle_name(db)
        self._set_refrigerant_name(db)
        self.__set_mass_purchased()
        self._set_emissions_total(calculation_method,[db,self._vehicle_name,self._distance,self._refrigerant_name,self._mass_purchased])
        
    # Output method
    def _print_all_month_data(self): # Overrides print_all_month_data in parent class
        print('Vehicle used: '+self._vehicle_name)
        print('Distance travelled across 1 journey:'+str(self._distance))
        print('Mass of goods purchased:', str(self._mass_purchased))
        print('Total Emissions emitted:',str(round(self._emissions_total,2)),' CO2e')
        
class Months_of_Data: # Contains objects of one of the child classes. Composition

    def __init__(self):
        self.__calculation_method = None
        self.__num_months = None
        self.__objects = []
        self.__list_of_emissions = []

    # Exceptions

    def _method_exception(self):
        print('ERROR: Please enter 1 or 2.')
    
    def _num_months_exception(self):
        print('ERROR: Please enter an integer between 2 and 6 inclusive.')

    # Setters

    def __set_method_used(self):

        print('Possible Calculation Methods:')
        print()
        print('1. Fuel-based Method')
        print('2. Distance-based Method')

        valid = False # Validates user input for calculation method
        while valid is False:
            print()
            try:
                calculation_method = int(input('Enter the calculation method (1 or 2) you wish to use for scoring: '))
                if calculation_method == 1 or calculation_method == 2:
                    self.__calculation_method = calculation_method - 1
                    valid = True
                else:
                    self._method_exception()
            except ValueError:
                self._method_exception()

    def __set_num_months(self):

        print()
        print('Please enter how many months you want to enter data for: ')
        print('NB: The maximum no. of months is 6.')

        max_months = 6
        valid = False
        while valid is False:
            print()
            try:
                num_months = int(input('No. of Months: '))
                if 1 < num_months <= max_months:
                    self.__num_months = num_months
                    valid = True
                else:
                    self._num_months_exception()
            except ValueError:
                self._num_months_exception()

    def __set_month_data(self,db):

        if self.__calculation_method == 0: # Creating fuel-based method objects
            for i in range(self.__num_months):
                Month = Fuel_based()
                Month._set_all_month_data(db,i+1,self.__calculation_method)
                self.__list_of_emissions.append(Month._emissions_total)
                self.__objects.append(Month)
        else:
            for i in range(self.__num_months): # Creating distance-based method objects
                Month = Distance_based()
                Month._set_all_month_data(db,i+1,self.__calculation_method)
                self.__list_of_emissions.append(Month._emissions_total)
                self.__objects.append(Month)

    # Methods acting on data entered in by user

    def __score_emissions(self,db): # Calls the scoring program to score all the emission totals
        ScoringEmissions.DetermineEmissionsScore(db,self.__calculation_method,self.__list_of_emissions)

    def __graph_emissions(self,db): # Calls the graphing model
        x_values = np.array([i for i in range(1,len(self.__list_of_emissions)+1)])
        recent_month = self.__objects[len(self.__objects)-1] # Obtains the data from the most recent month.
        if self.__calculation_method == 0:
            attributes = [recent_month._distance,recent_month._refrigerant_name,recent_month._quantity_refrigerant_leaked]
            #Takes all needed fuel-based attributes to calculate total emissions in determining more efficient vehicles.
        else:                                                                                                               
            attributes = [recent_month._distance,recent_month._refrigerant_name,recent_month._mass_purchased]              
            # Takes all the needed distance-based attributes to calculate total emissions in determinin more efficient vehicles.
        GraphEmissions.Graph_and_Improve(db,x_values,np.array(self.__list_of_emissions),self.__calculation_method,attributes)
                                        
    # Output Method

    def __print_all(self):

        print()
        print('Summary of Data for each Month')
        print('------------------------------')
        for i in range(len(self.__objects)): # Iterates through each month, printing all data
            print()
            print('Month ' + str(i+1)+' data')
            print('------------')
            print()
            self.__objects[i]._print_all_month_data()

    # Start Method

    def start(self,db):
        self.__set_method_used()
        self.__set_num_months()
        self.__set_month_data(db)
        self.__print_all()
        self.__score_emissions(db)
        self.__graph_emissions(db)

    
if __name__ == '__main__':

    DB_PATH = 'TestCalculateEmissions_db.db'
    db = sqlite3.connect(DB_PATH,detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row
    c = db.cursor()

    test = Months_of_Data()
    test.start(db)
    
