# Graph Emissions

import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import CalculatingEmissions
  
def Least_Squares(x,y):
    # Sample Size
    n = np.size(x)

    # Calculating Gradient and y intercept of line
    m_x = np.mean(x) # Calculates Mean
    m_y = np.mean(y) # Calculates Standard Deviation
  
    SS_xy = np.sum(y*x) - n*m_y*m_x # Calculates SSxy
    SS_xx = np.sum(x*x) - n*m_x*m_x # Calculates SSxx
  
    gradient = SS_xy / SS_xx # Determines gradient
    intercept = m_y - gradient*m_x # Determines y intercept
  
    return [intercept, gradient]

def Gradient_Descent(x,y):
    def OptimiseCoefs(x,y,c,m,L): # x is independent variable, y is dependent variable, c is y intercept and m is gradient of trend line, L is learning rate
        epochs = 1000 # nunber of iterations
        for i in range(epochs):
            y_pred = m*x + c 
            D_m = (-2/len(x))*np.sum(x*(y-y_pred)) # Partial Derivative with respect to m
            D_c = (-2/len(x))*np.sum(y-y_pred) # Partial Derivative with respect to c
            m -= (L*D_m) # Updates m
            c -= (L*D_c) # Updates c
        return [c,m]

    m = (y[len(y)-1]-y[0])/(x[len(x)-1]-x[0]) # Determines starting m and c values.
    c = y[0] - m*x[0]
    return OptimiseCoefs(x,y,c,m,0.0001)

def calculate_r_squared(x,y,coefficients): # Calculate R Squared value. 

    y_pred = x*coefficients[1] + coefficients[0] # Determines the predicted y.
    mean_y = np.mean(y) # Finds the mean of y
    SSE = np.sum((y-y_pred)**2)
    SSyy = np.sum((y-mean_y)**2)
    r_squared = 1 - (SSE/SSyy) # Calculates the R-Squared score using the formula.
    return r_squared
    
def plot_regression_line(x,y,coefficients): # Plots the trend line and the actual points from emission calculations onto 1 graph.
    plt.ion()
    plt.figure()
    plt.scatter(x, y, color = "m",
               marker = "o", s = 30)
    y_pred = coefficients[0] + coefficients[1]*x
    plt.plot(x, y_pred, color = "g") # Plots the trend line in green colour
    plt.xlabel('Months') # X axis label
    plt.ylabel('Total CO2e Emissions') # Y axis label
    plt.title('Trend of CO2e Emissions') # Title of the graph
    plt.show()
            
def improve_emissions(db,coefficients,x,y,calculation_method,attributes): # Algorithm determining more efficient vehicles.
    def determine_efficient_vehicles():
        def sort_emissions(efficient_vehicles,emission_totals): # Sorts the arrays in ascending order of total emissions
            if len(emission_totals) > 1:
                mid = len(emission_totals) // 2
                left_array_vehicles = efficient_vehicles[:mid] # slices the efficient_vehicles array into the first half 
                right_array_vehicles = efficient_vehicles[mid:] # slices the efficient_vehicles array into the second half
                left_array_emissions = emission_totals[:mid] # slices the emission_totals array into the first half 
                right_array_emissions = emission_totals[mid:] # slices the emission_totals array into the second half
                
                sort_emissions(left_array_vehicles,left_array_emissions) # Recursively calls the function on the first half arrays
                sort_emissions(right_array_vehicles,right_array_emissions) # Recursively calls the function on the second half arrays

                i = 0
                j = 0
                k = 0
                # Sorts the elements in each half.
                while i<len(left_array_emissions) and j<len(right_array_emissions): # Moves through each array,incrementing the index if the number in the list is 
                    if left_array_emissions[i] < right_array_emissions[j]: #bigger
                        emission_totals[k] = left_array_emissions[i] # If left array element is bigger, this is placed in that kth position of emission_totals
                        efficient_vehicles[k] = left_array_vehicles[i] # Does the same thing with vehicles as the vehicles need to be sorted based on its 
                        i += 1                                         # emission totals
                    else:
                        emission_totals[k] = right_array_emissions[j] # If right array element is >= to left array element,the right array element  
                                                                      # is placed in kth position of emission_totals
                        efficient_vehicles[k] = right_array_vehicles[j] # Does the same thing with vehicles as the vehicles need to be sorted based on its 
                        j += 1                                          #emission_totals
                    k += 1

                # Adding the terms that are left on.
                while i<len(left_array_emissions):
                    emission_totals[k] = left_array_emissions[i] # Adds on any large terms left in the left array 
                    efficient_vehicles[k] = left_array_vehicles[i] # Adds the vehicles based on this.
                    i += 1 # increments i and k to add each one
                    k += 1

                while j<len(right_array_emissions):
                    emission_totals[k] = right_array_emissions[j] # Adds on any large terms left in the right array
                    efficient_vehicles[k] = right_array_vehicles[j] # Adds on the vehicles accordingly
                    j += 1 # Increments j and k to add each one
                    k += 1
        c = db.cursor()
        max_id_object = c.execute('SELECT MAX(vehicle_id) FROM Vehicles')
        max_id = c.fetchone()[0]
        efficient_vehicles = []
        emission_totals = []

        for i in range(max_id): # Goes through each vehicle calculating the total emissions with each one. Vehicle is added to the list if total emissions < most
            vehicle_name_object = c.execute('SELECT vehicle_name FROM Vehicles WHERE vehicle_id=?',(i+1,)) # recent data.
            vehicle_name = c.fetchone()[0]
            
            if calculation_method == 0:
                emissions_total = CalculatingEmissions.fuel_based(db,vehicle_name,attributes[0],attributes[1],attributes[2])#Calculates emissions with each vehicle
                if emissions_total < y[len(x)-1]: # If total emissions < most recent emissions total calculated, then it is added to the efficient vehicles list.
                    efficient_vehicles.append(vehicle_name) # The emissions total using that vehicle is added to the emission totals list.
                    emission_totals.append(emissions_total)

            if calculation_method == 1: # Same as the previous bit with with the distance-based method instead of fuel-based method.
                emissions_total = CalculatingEmissions.distance_based(db,vehicle_name,attributes[0],attributes[1],attributes[2])
                if emissions_total < y[len(x)-1]:
                    efficient_vehicles.append(vehicle_name)
                    emission_totals.append(emissions_total)
                    
        if len(efficient_vehicles) == 0: # Outputs more efficient vehicles to user. If none exist, user is told to minimise distance travelled.
            print('Currently, there are no vehicles in the database that are more efficient in emissions. Try to reduce the distance travelled in your journey.')
        else:
            sort_emissions(efficient_vehicles,emission_totals) # Sorts the vehicles and emisison totals is ascending order of emission totals.
            print('Here are a list of more efficient vehicles (in ascending order) with the total emissions given if this vehicle was to be used.')
            for i in range(len(efficient_vehicles)):
                print()
                print(efficient_vehicles[i],': ',round(emission_totals[i],2), ' CO2e')

    if coefficients[1] >= 0: # Determines which is the appropriate message to give to the user.
        print('Over time, your emissions have not been falling. Improvement is required.')
        print()
        
    else:  
        print('Your emissions are falling over time. However, you can still improve.')
        print()
    determine_efficient_vehicles()
              
def Graph_and_Improve(db,x,y,calculation_method,attributes): # Interface
  
    coefficients = Gradient_Descent(x,y) # Determines coefficients from gradient descent
    coefficients1 = Least_Squares(x,y) # Determines coefficients from least squares.
    r_squared = calculate_r_squared(x,y,coefficients)
    r_squared_1 = calculate_r_squared(x,y,coefficients1)

    if abs(r_squared-1)<abs(r_squared_1-1): # Determines which set of coefficients are more accurate and plots the more accurate trend line.
        plot_regression_line(x,y,coefficients) # Plots Gradient Descent Trend Line
        improve_emissions(db,coefficients,x,y,calculation_method,attributes)
    else:
        plot_regression_line(x,y,coefficients1) # Plots Least Squares Trend line
        improve_emissions(db,coefficients1,x,y,calculation_method,attributes)
  
if __name__ == "__main__":
    x = np.array([1,2,3,4,5,6])
    y = np.array([32,37,41,49,58,63])

    DB_PATH = 'TestCalculateEmissions_db.db'
    db = sqlite3.connect(DB_PATH,detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row
    c = db.cursor()
    Graph_and_Improve(db,x,y,1,[3,'R134a',15])




