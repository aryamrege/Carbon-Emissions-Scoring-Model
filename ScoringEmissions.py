# Scoring the Emissions
import CreateDatabaseEmissions, CalculatingEmissions, sqlite3, random
import numpy as np
import matplotlib.pyplot as plt
import datetime
from scipy.stats import norm

# Fuel-based and distance-based randomised processes

def LCG(divisor): #Implements the Linear Congruential Generator
    def find_coprime(divisor):
        def gcd(a,b): # Stein's Algorithm
            if (a == b):
                return a
            # GCD(0, b) == b; GCD(a, 0) == a,
            # GCD(0, 0) == 0
            if (a == 0):
                return b
            if (b == 0):
                return a
            # look for factors of 2
            # a is even
            if ((~a & 1) == 1):
                # b is odd
                if ((b & 1) == 1):
                    return gcd(a >> 1, b)
                else:
                    # both a and b are even
                    return (gcd(a >> 1, b >> 1)) << 1
            # a is odd, b is even
            if ((~b & 1) == 1):
                return gcd(a, b >> 1)
            # reduce larger number
            if (a > b):
                return gcd((a - b) >> 1, b)
            return gcd((b - a) >> 1, a)
        
        found = False
        i = 2
        while found is False:
            hcf = gcd(i,divisor)
            if hcf == 1: # Stops at the snmallest number coprime to the divisor.
                found = True
            else:
                i += 1
        return i

    def determine_a(divisor): # Determines the smallest value of a for any divisor for my LCG algorithm
        prime_factors = []
        found = False
        factor = 2
        while found is False: # Finds all prime factors of the divisor
            all_one_prime_factor = False
            while all_one_prime_factor is False: # If a prime is a factor, then it checks how many powers of this prime are factors of the divisor. 
                if divisor % factor == 0: 
                    divisor /= factor # it divides the divisor by that prime factor to ensure no prime factors repeat.
                    prime_factors.append(factor) # Adds the prime factor to the prime factor list
                else:
                    all_one_prime_factor = True # Leaves the while loop if there are no more prime factors
            if divisor == 1: # If all the prime factors are found, you leave the loop
                found = True
            else: # If not, you go onto the next number.
                factor += 1 

        num_factors_2 = prime_factors.count(2) # Counts the number of factors of 2
        factors_of_a = list(dict.fromkeys(prime_factors)) # Finds the factors of a by removing repeats from the list. We need a to be divisible by all the prime
        if num_factors_2 >= 2:                              # factors of the divisor.
            a = int(np.prod(factors_of_a) * 2) # Multiplies by an extra factor of 2 if the divisor is a multiple of 4
        else:
            a = int(np.prod(factors_of_a))
        return a
                
    date = datetime.datetime.now().strftime('%M:%S.%f') # Determines the number of times the recurrence relation runs by evaluating the no. of microseconds 
    num_iterations = int(date[9:])                      # Time is at during that minute and taking the last 3 numbers of that microsecond.

    a =  determine_a(divisor) # Determines an a value such that a-1 is divisible by 4
    c = find_coprime(divisor)  # divisor and c must be coprime to get the largest period
    x = int(date[8])  # Randomly determines a starting x value
    for i in range(num_iterations):
        x = (a*x+c)%(divisor+1)   # Computes the Recurrence relation
    if x == 0: # As the random number can never be 0.
        x += 1
    return x

def RandomiseVehicle(db:sqlite3.Connection):

    c = db.cursor()
    # Randomly choosing a vehicle

    max_id_object = c.execute('SELECT MAX(vehicle_id) FROM Vehicles')  # Gets the maximum possible value for the vehicle id.
    max_id = max_id_object.fetchone()[0]
    vehicle_id = LCG(max_id)
    return int(vehicle_id)

def RandomiseDistance():

    #Setting max_value
    max_distance = 1407*5

    #Randomise Process
    distance_travelled = LCG(max_distance*1000) # As floats are also valid, the code will pick a random number and divide by 1000 to get floats.
    distance_travelled /= 1000 # Getting the distance back into range.
    return distance_travelled

# Fuel-based only Randomisation Processes

def RandomiseQuantityRefrigerantLeaked():

    # Setting max_value
    max_refrigerant = 0.3580366
    place_value = len(str(max_refrigerant)) # Determining the number of digits
    # Randomise Process
    quantity_refrigerant_leaked = LCG(int(max_refrigerant *(10**place_value))) # Have accounted for floats like above by multiplying to make it an integer.
    quantity_refrigerant_leaked /= (10**place_value) # Getting the value back in range.
    return quantity_refrigerant_leaked

# Randomise Distance-based methods

def RandomiseMassGoods():

    #Setting max_value
    max_goods_transported = 500
    place_value = len(str(max_goods_transported))

    #Randomise Process
    goods_transported = LCG(500*int(10**place_value)) # Accounting for floats
    goods_transported /= (10**place_value)
    return goods_transported

# Randomised Calculation Process

def CalculateEmissions(db:sqlite3.Connection,calculation_method): # Calculates Emissions for each round of randomisation

    c = db.cursor()
    vehicle_id = RandomiseVehicle(db) # Calculates a random vehicle id
    vehicle_name_object = c.execute('SELECT vehicle_name FROM Vehicles WHERE vehicle_id=?',(vehicle_id,))
    vehicle_name = c.fetchone()[0] # Gets the vehicle name from the database using the randomly selected vehicle id
    
    distance = RandomiseDistance() # Calculates a random distance

    sql = '''SELECT Refrigerant.refrigerant_name FROM Vehicles
                 INNER JOIN Refrigerant ON Vehicles.refrigerant_id=Refrigerant.refrigerant_id
                 WHERE Vehicles.vehicle_name=?'''
    refrigerant_name_object = c.execute(sql,(vehicle_name,))
    refrigerant_name = c.fetchone()[0] # Gets the name of the refrigerant
    
    if calculation_method == 0:

        quantity_refrigerant_leaked = RandomiseQuantityRefrigerantLeaked() # generates a random value for the quantity refrigerant leaked
        total_emissions = CalculatingEmissions.fuel_based(db,vehicle_name,distance,refrigerant_name,quantity_refrigerant_leaked) # Calculates total emissions based on
        return [total_emissions,vehicle_id,quantity_refrigerant_leaked,distance]                                                 # these random parameters

    if calculation_method == 1:

        mass_goods_purchased = RandomiseMassGoods() # generates a random value for the mass of goods purchased
        total_emissions = CalculatingEmissions.distance_based(db,vehicle_name,distance,refrigerant_name,mass_goods_purchased)#Calculates total emissions using
        return [total_emissions,vehicle_id,mass_goods_purchased,distance]                                                    # these random parameters.

# Creates the array of emissions for each method, sorts it and puts it all in another table for testing later      
def GenerateEmissionsData(db:sqlite3.Connection,calculation_method,rounds): 

    c = db.cursor()
    if calculation_method == 0:
        CreateDatabaseEmissions.create_scores_emissions_fuel_table(db)
    if calculation_method == 1:
        CreateDatabaseEmissions.create_score_emissions_distance_table(db)

    # Carry out each randomisation process and adds the data to the appropriate table
    
    for i in range(rounds):
        
        if calculation_method == 0:
            emissions_data = CalculateEmissions(db,calculation_method) # Generates all the emissions data required for that method
            c.execute("INSERT INTO ScoresEmissionsFuel VALUES (NULL,?,?,?,?)",emissions_data) # Adds all of the data to the correct table
            db.commit()

        else:
            emissions_data = CalculateEmissions(db,calculation_method) # generates all the emissions data required for that method
            c.execute("INSERT INTO ScoresEmissionsDistance VALUES (NULL,?,?,?,?)",emissions_data) # Adds all of the data to the correct table.
            db.commit()

def CalculateStats(db:sqlite3.Connection,calculation_method):
    def CalculateMean(c): # Calculates Mean
        if calculation_method == 0:
            Mean_object = c.execute('SELECT AVG(total_emissions) FROM ScoresEmissionsFuel')
            Mean = c.fetchone()[0]
        if calculation_method == 1:
            Mean_object = c.execute('SELECT AVG(total_emissions) FROM ScoresEmissionsDistance')
            Mean = c.fetchone()[0]
        return Mean

    def CalculateSD(c,Mean): # Calculates Standard Deviation
        if calculation_method == 0:
            rounds_object = c.execute('SELECT MAX(round) FROM ScoresEmissionsFuel') # Gets the number of records in the table
            rounds = c.fetchone()[0]
            Squared_Mean_Deviation = 0
            
            for i in range(rounds): # Calculates sum of squared deviations from the mean
                total_emissions_object = c.execute('SELECT total_emissions FROM ScoresEmissionsFuel WHERE round=?',((i+1),))
                total_emissions = c.fetchone()[0]
                squared_mean_deviation = (total_emissions-Mean)**2
                Squared_Mean_Deviation += squared_mean_deviation

            Variance = Squared_Mean_Deviation/(rounds-1) # Calculates variance
            Standard_Deviation = Variance ** 0.5 # Calculates standard deviation

        if calculation_method == 1:
            rounds_object = c.execute('SELECT MAX(round) FROM ScoresEmissionsDistance') # Gets the number of records in the table
            rounds = c.fetchone()[0]
            Squared_Mean_Deviation = 0

            for i in range(rounds): # Calculates sum of squared deviations from the mean
                total_emissions_object = c.execute('SELECT total_emissions FROM ScoresEmissionsDistance WHERE round=?',((i+1),))
                total_emissions = c.fetchone()[0]
                squared_mean_deviation = (total_emissions-Mean)**2
                Squared_Mean_Deviation += squared_mean_deviation

            Variance = Squared_Mean_Deviation/(rounds-1) # Calculates Variance
            Standard_Deviation = Variance ** 0.5 # Calculates Standard Deviation.
        return Standard_Deviation

    c = db.cursor()
    Mean = CalculateMean(c)
    SD = CalculateSD(c,Mean)
    return Mean,SD

# Will be called in Front End. Functions and Procedures above won't be called in Front End
 
def DetermineEmissionsScore(db,calculation_method,User_Total_Emissions):  

    # Assemble Probability Distribution Function (PDF) and create Graph. Also Marks on the emissions from the user-enterded data.
    # Also returns score for each emissions total from User_Total_Emissions

    def PlotGraph(x_values,Mean,SD,User_Total_Emissions):

        def DetermineScoreBoundaries(Grades,Mean,SD): # Determines Score Boundaries

            num_grades = len(Grades)
            cum_zero = norm(loc=Mean,scale=SD).cdf(0) # Determines the probability of the emissions score being < 0
            remaining_p = 1 - cum_zero # Determines probability of the emissions score being >= 0
            gap = remaining_p/num_grades # Splits the probability of emissions score being >= 0 into 5 equal chunks.
            score_boundaries = [cum_zero+gap,cum_zero+(2*gap),cum_zero+(3*gap),cum_zero+(4*gap)] # Sets gap as the proportion of all the possible emission scores
            score_boundaries_x = []                                                              # falling under 1 grade. Sets score boundaries in terms of 
                                                                                                 # probability            
            for i in range(len(score_boundaries)):
                z_x_value = norm.ppf(score_boundaries[i]) # Determines the total emissions value that each score boundary comes from. 
                x_value = (z_x_value*SD)+Mean # Adjusts the above value to fit my normal distribution.
                score_boundaries_x.append(x_value) 
            score_boundaries_x.append(x_values[len(x_values)-1])
            return score_boundaries_x

        def DetermineGrade(Grades,score_boundaries_x,User_Total_Emissions): # Determines Grade for User
            print()
            print('Grades for each month: ')
            print('-----------------------')
            print()
            for Month in range(len(User_Total_Emissions)):
                Grade_found = False
                index = 0
                Grade = ''
                while Grade_found is False: # Indexes through each score boundary to see if each one exceeds the emission total
                    if score_boundaries_x[index] >= User_Total_Emissions[Month]: # Sees which is the first score boundary to be greater than the emission total
                        Grade = Grades[index] # This becomes the grade.
                        print()
                        print('Month ',(Month+1))
                        print('-------')
                        print()
                        print('Total Emissions: ', User_Total_Emissions[Month],' CO2e')
                        print('Grade: ' + Grade)
                        print()
                        Grade_found = True
                    else:
                        index += 1  # Moves onto the next score boundary
        
        plt.ion()
        y_values = norm.pdf(x_values,Mean,SD)
        image,axes = plt.subplots(figsize=(10,8))
        plt.style.use('fivethirtyeight')
        axes.plot(x_values,y_values,'b',linewidth=2)

        axes.fill_between(x_values,y_values,0, alpha=0.1, color='b') # Plots on x labels, y labels, x range,y range and title of graph.
        axes.set_xlabel('Emission Values')
        axes.set_ylabel('Normally rationalised score')
        axes.set_xticks(np.arange(0,x_values[len(x_values)-1],x_values[len(x_values)-1]/10))
        axes.set_yticks(np.arange(0,max(y_values),max(y_values)/10))
        axes.set_title('How emissions fare on Distribution curve')

        # Labels on emissions based on user-entered data
        for i in range(len(User_Total_Emissions)):

            x_user_emissions = User_Total_Emissions[i]
            y_user_emissions = float((norm.pdf(x_user_emissions,Mean,SD)))
            Month = 'Month ' + str(i+1)
            plt.scatter(x_user_emissions,y_user_emissions,marker = 'x',alpha=1)

            plt.annotate(Month,(x_user_emissions,y_user_emissions))

        # Determine Score Boundaries
        Grades = ['A','B','C','D','E']
        score_boundaries_x = DetermineScoreBoundaries(Grades,Mean,SD)
        # Determines Grade
        DetermineGrade(Grades,score_boundaries_x,User_Total_Emissions)
            
        # Shows Graph to user
        for i in range(len(score_boundaries_x)):
            plt.axvline(x=score_boundaries_x[i],color='r',linewidth=0.9)
            if i == 0:
                plt.annotate(Grades[i],(score_boundaries_x[i]/2,0)) # Plots on labels denoting grade regions. Label is placed in the middle bottom of each region
            else:
                plt.annotate(Grades[i],(score_boundaries_x[i]-(score_boundaries_x[i]-score_boundaries_x[i-1])/2,0)) 
        plt.show()

    def DetermineMaxEmissions(db,calculation_method): # Determines the maximum total emissions from the randomisation processes
            c = db.cursor()
            if calculation_method == 0: # Done to determine the range of emissions values needed to plot the normal distributions.
                max_emissions_object = c.execute('SELECT MAX(total_emissions) FROM ScoresEmissionsFuel')
                max_emissions = c.fetchone()[0]
                return max_emissions
            else:
                max_emissions_object = c.execute('SELECT MAX(total_emissions) FROM ScoresEmissionsDistance')
                max_emissions = c.fetchone()[0]
                return max_emissions

    max_emissions = DetermineMaxEmissions(db,calculation_method) # Determines maximum emissions so the range of x values is plotted properly.
    if calculation_method == 0:

        # Mean: 1401.2978889861004
        # SD: 1578.0315281896908
        Mean = 1401.2978889861004
        SD = 1578.0315281896908
        x_values = np.arange(0,max_emissions,0.5) # Determines x values to be plotted
        PlotGraph(x_values,Mean,SD,User_Total_Emissions) # Plots the Graph

    if calculation_method == 1:

        # Mean: 2740269.4551994572
        # SD: 2735613.7940128436
        Mean = 2740269.4551994572
        SD = 2735613.7940128436
        x_values = np.arange(0,max_emissions,2) # Determines x values to be plotted
        PlotGraph(x_values,Mean,SD,User_Total_Emissions) # Plots the Graph

def ScoreEmissions(db,calculation_method,User_Total_Emissions): # Interface

    DetermineEmissionsScore(db,calculation_method,User_Total_Emissions)

if __name__ == '__main__':
    DB_PATH = 'TestCalculateEmissions_db.db'
    db = sqlite3.connect(DB_PATH,detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    GenerateEmissionsData(db,1,1000)
    #print(CalculateStats(db,0))
    #ScoreEmissions(db,1,[1000000,2000000])
        
    # 0 is fuel-based, 1 is distance-based   
        
    

