from django import forms
from .models import Car

class RecommendForm(forms.Form):
    purposeOptions = (("1", "Four wheel Driving"), ("2", "Family trip"), ("3", "Road Trip"))
    purpose = forms.ChoiceField(choices=purposeOptions)
    seatsOptions = (("1", "1 or 2"), ("2", "3 - 5"), ("3", "more than 5"))
    seats = forms.ChoiceField(choices=seatsOptions)
    transmissionOptions = (("1", "Automatic"), ("2", "Manual"))
    transmission = forms.ChoiceField(choices=transmissionOptions)
    monthOptions = (("1", "January"), ("2", "February"), ("3", "March"), ("4", "April"), ("5", "May"),
                    ("6", "June"), ("7", "July"), ("8", "August"), ("9", "September"), ("10", "October"),
                    ("11", "November"), ("12", "December"))
    month = forms.ChoiceField(choices=monthOptions)
    def clean(self):
        purpose = forms.cleaned_data['purpose']
        seats = forms.cleaned_data['seats']
        transmission = forms.cleaned_data['transmission']
        month = forms.cleaned_data['month']
        if purpose or seats or transmission or month:
            return super(RecommendForm, self).clean()

class CarFilterForm(forms.Form):
    # declare list variables
    seriesYearOptions = []
    bodyTypeOptions = []
    transmissionOptions = []
    seatingCapacityOptions = []
    makeOptions = []
    engineOptions = []
    fuelOptions = []
    tankCapacity = []
    powerOptions = []

    # add data from database to lists
    cars = Car.objects.all()
    for car in cars:
        if car.car_series_year not in seriesYearOptions:
            seriesYearOptions.append(car.car_series_year)
        if car.car_bodytype not in bodyTypeOptions:
            bodyTypeOptions.append(car.car_bodytype)
        if car.car_standard_transmission not in transmissionOptions:
            transmissionOptions.append(car.car_standard_transmission)
        if car.car_seating_capacity not in seatingCapacityOptions:
            seatingCapacityOptions.append(car.car_seating_capacity)
        if car.car_makename not in makeOptions:
            makeOptions.append(car.car_makename)
        if car.car_engine_size not in engineOptions:
            engineOptions.append(car.car_engine_size)
        if car.car_fuel_system not in fuelOptions:
            fuelOptions.append(car.car_fuel_system)
        if car.car_tank_capacity not in tankCapacity:
            tankCapacity.append(car.car_tank_capacity)
        if car.car_power not in powerOptions:
            powerOptions.append(car.car_power)

    # sort lists
    seriesYearOptions.sort()
    bodyTypeOptions.sort()
    transmissionOptions.sort()
    seatingCapacityOptions.sort()
    makeOptions.sort()
    engineOptions.sort()
    fuelOptions.sort()
    tankCapacity.sort()
    powerOptions.sort()

    # set years up as list of list and set up field
    year_options = [["Null", "Please Select"]]
    for year in seriesYearOptions:
        year_options.append([year, year])
    minimum_series_year = forms.ChoiceField(choices=year_options)

    # set body type up as list of list and set up field
    bodyType_options = [["Null", "Please Select"]]
    for type in bodyTypeOptions:
        bodyType_options.append([type, type])
    body_type = forms.ChoiceField(choices=bodyType_options)

    # set seating capacity up as list of list and set up field
    seating_options = [["Null", "Please Select"]]
    for seats in seatingCapacityOptions:
        seating_options.append([seats, seats])
    minimum_seating_capacity = forms.ChoiceField(choices=seating_options)

    # set make name up as list of list and set up field
    make_options = [["Null", "Please Select"]]
    for make in makeOptions:
        make_options.append([make, make])
    make_name = forms.ChoiceField(choices=make_options)

    # set engine size up as list of list and set up field
    engine_options = [["Null", "Please Select"]]
    for engine in engineOptions:
        engine_options.append([engine, engine])
    engine_size = forms.ChoiceField(choices=engine_options)

    fuel_options = [["Null", "Please Select"]]
    for fuel in fuelOptions:
        fuel_options.append([fuel, fuel])
    fuel_system = forms.ChoiceField(choices=fuel_options)

    tank_options = [["Null", "Please Select"]]
    for tank in tankCapacity:
        tank_options.append([tank, tank])
    tank_capacity = forms.ChoiceField(choices=tank_options)

    power_options = [["Null", "Please Select"]]
    for power in powerOptions:
        power_options.append([power, power])
    power = forms.ChoiceField(choices=power_options)