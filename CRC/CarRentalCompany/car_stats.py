from .models import *

# function to pull the placing of car_id in terms of popularity
def popularity_place(car_id):
    # pull all cars ordered by popularity
    cars_by_popularity = Car.top_cars()

    popularity_place = 1
    # go through each car in above list, incrementing placing each iteration until the desired car is found
    for car in cars_by_popularity:
        if car.id == car_id:
            break
        else:
            popularity_place += 1

    # return the placing
    return popularity_place


# function to find which age group a car is most popular in
def popular_age_group(car_id):
    # set up an array the lower bound in each age group
    age_groups = [30, 40, 50, 60, 70, 80]
    count_orders = []
    cursor = connection.cursor()
    # for each age group set up a query to pull number of times this car was rented by a customer in the age group
    for age_group in age_groups:
        query = ('''SELECT count(carrentalcompany_order.car_id_id)
                FROM carrentalcompany_order
                LEFT JOIN carrentalcompany_car
                ON carrentalcompany_car.id = carrentalcompany_order.car_id_id
                LEFT JOIN carrentalcompany_user
                ON carrentalcompany_order.customer_id_id = carrentalcompany_user.id
                WHERE carrentalcompany_car.id = %d and (FLOOR(DATEDIFF(curdate(), carrentalcompany_user.user_birthday) / 365.25)) BETWEEN %d AND %d''' % (car_id, age_group, age_group + 9))
        cursor.execute(query)
        results = cursor.fetchall()
        for result in results:
            count_orders.append(result[0])
    index = 0
    current_max = 0
    max_index = 0
    # find the max number of rentals in an age group
    for count in count_orders:
        if count > current_max:
            current_max = count
            max_index = index
        index += 1
    # return the age group with max rentals
    return age_groups[max_index]


# find what type of driving is best suited to a car
def best_suited_for(car_id):
    # get details for car
    car = Car.objects.get(pk=car_id)
    tank_capacity = int(car.car_tank_capacity.replace("L", ""))
    # if the tank capacity is greater than 70, the car is suited to long driving
    if tank_capacity > 70:
        suited_for = "Long Distance Driving (tank capacity is %d)" % tank_capacity
    # if the seating capacity is 5 or more, the car is suited for family trips
    elif car.car_seating_capacity > 4:
        suited_for = "Family trips (seating capacity is %d)" % car.car_seating_capacity
    #if the car is a 4WD, it is suited for four wheel driving
    elif car.car_drive == "4WD":
        suited_for = "Four wheel driving (drive type is 4WD)"
    else:
        #otherwise it is suited for just general driving
        suited_for = "General driving"

    return suited_for

