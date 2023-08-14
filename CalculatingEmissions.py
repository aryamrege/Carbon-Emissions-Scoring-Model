# Calculates the Emissions - Both Calculation Methods

from geopy.geocoders import Nominatim
from geopy import distance
import sqlite3

# Retrieves Database from files

DB_PATH = 'TestCalculateEmissions_db.db'

def get_db(DB_PATH): # Gets the database containing all the vehicles for the fuel-based and distance-based method

    db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row
    return db

# Functions used in both calculation methods

def CalculateDistance(postcodes): # Calculates the distance between each consecutive pair of postcodes.

    geolocator = Nominatim(user_agent="CalculateEmissions")

    total_distance = 0

    for i in range(len(postcodes)-1):

        postcode1 = postcodes[i]
        postcode2 = postcodes[i+1]
        
        postcode1 = geolocator.geocode(postcode1) # Finds coordinates for both postcodes
        postcode2 = geolocator.geocode(postcode2)
        
        postcode1_lat = (postcode1.latitude) # Gets latiutude and longitude of both postcodes
        postcode1_lon = (postcode1.longitude)
        postcode2_lat = (postcode2.latitude)
        postcode2_lon = (postcode2.longitude)
        
        location1 = (postcode1_lat, postcode1_lon) # Summarises location of 2 postcodes 
        location2 = (postcode2_lat, postcode2_lon)

        distance_between_2_locations = distance.distance(location1, location2).km # Finds distance between 2 locations in km
        total_distance += distance_between_2_locations # Adds it to the total distance travelled.

    total_distance = round(total_distance,4)
    
    return total_distance

def GetEmissionFactorForFuel(db:sqlite3.Connection, vehicle_name): # Gets the emission factor for the fuel vehicle uses

    c = db.cursor()
    sql = '''SELECT Fuel.emission_factor FROM Vehicles
             INNER JOIN Fuel ON Vehicles.fuel_id = Fuel.fuel_id
             WHERE vehicle_name=?'''
    
    emission_factor_object = c.execute(sql,(vehicle_name,))
    emission_factor = c.fetchone()[0]
    return emission_factor

def GetGWP(db:sqlite3.Connection, refrigerant_name): # Gets global warming potential of refrigerant used.

    c = db.cursor()
    gwp_object = c.execute("SELECT gwp FROM Refrigerant WHERE refrigerant_name=?", (refrigerant_name,)) 
    gwp = c.fetchone()[0]
    return gwp

# Fuel-Based Method Calculations

def GetFuelEfficiency(db:sqlite3.Connection, vehicle_name): # Fetches fuel efficiency of vehicle

    c = db.cursor()
    fuel_efficiency_object = c.execute("SELECT fuel_efficiency FROM Vehicles WHERE vehicle_name=?",(vehicle_name,)) 
    fuel_efficiency = c.fetchone()[0]
    return fuel_efficiency

def CalculateTotalEmissions_fuel(distance,fuel_efficiency,Emission_factor_fuel,quantity_refrigerant_leaked,gwp):

    QuantityFuelConsumed = distance * fuel_efficiency
    Emissions_Fuel = QuantityFuelConsumed * Emission_factor_fuel
    Emissions_Refrigerant = quantity_refrigerant_leaked * gwp
    total_emissions = Emissions_Fuel + Emissions_Refrigerant
    return total_emissions

# Distance-based method calculations

def CalculateTotalEmissions_distance(vehicle_name,distance,mass_goods_purchased,emission_factor_fuel,gwp):

    emission_factor_vehicle = emission_factor_fuel + gwp
    total_emissions = mass_goods_purchased*distance*emission_factor_vehicle
    return total_emissions

# Overall Functions
                            
def fuel_based(db,vehicle_name,distance,refrigerant_name,quantity_refrigerant_leaked): 
    emission_factor = GetEmissionFactorForFuel(db,vehicle_name)
    gwp = GetGWP(db,refrigerant_name)
    fuel_efficiency = GetFuelEfficiency(db,vehicle_name)
    total_emissions = CalculateTotalEmissions_fuel(distance,fuel_efficiency,emission_factor,quantity_refrigerant_leaked,gwp)
    return total_emissions

def distance_based(db,vehicle_name,distance,refrigerant_name,mass_goods_purchased):

    emission_factor_fuel = GetEmissionFactorForFuel(db,vehicle_name)
    gwp = GetGWP(db,refrigerant_name)
    total_emissions = CalculateTotalEmissions_distance(vehicle_name,distance,mass_goods_purchased,emission_factor_fuel,gwp)
    return total_emissions
# Interface

def CalculateEmissions(calculation_method,attributes):
    if calculation_method == 0:
        total_emissions = fuel_based(attributes[0],attributes[1],attributes[2],attributes[3],attributes[4])
        return total_emissions
    else:
        total_emissions = distance_based(attributes[0],attributes[1],attributes[2],attributes[3],attributes[4])
        return total_emissions
                   
if __name__ == '__main__':

    postcodes = ['SW1A 1AA','RG41 2EX']
    vehicle_name = 'Iveco S-way'
    quantity_refrigerant_leaked = 100
    refrigerant_name = 'R134a'
    mass_goods_purchased = 100

    db = get_db(DB_PATH)
    print(CalculateEmissions(0,[db,'Western Star 4700 Series',9,'R134a',0.11]))
