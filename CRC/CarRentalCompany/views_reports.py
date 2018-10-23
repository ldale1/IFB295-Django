from django.db import connection
from django.http import JsonResponse
from django.template import loader
from django.shortcuts import HttpResponse, render, redirect, reverse
from django.contrib.auth import (authenticate, login, get_user_model, logout)
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

from .forms_custom_report import *
from .graphs import *
from .models import Car, Store, Order, User, UserProfile
from .custom_sql import *
from .recommendation import handle_recommendation

from datetime import *
from calendar import monthrange, isleap

# ------- REPORTS ------ #

default_start = datetime(2007, 1, 1)
default_end = datetime(2007, 1, 30)

## Supporting
# Authentication
def is_management(request):
    if request.user.is_authenticated:
        user_profile = request.user.userprofile
        customer = user_profile.is_customer
        floor_staff = user_profile.is_floorStaff
        if not customer and not floor_staff:
           return True
    return False

# Add a certain amount of years, months and days to a date
def new_date(current, skip, forwards):
    # Get datetime obj
    edited_date = datetime.strptime(current, '%Y-%m-%d')
    # Days to jump
    month_days = monthrange(edited_date.year, edited_date.month)[1]
    year_days = 365
    if isleap(edited_date.year):
        year_days = 364
    # duration to skip
    increment = 1
    if not (forwards == 'true'): # This has to have = 'true'
        increment = -1
    # calculate increment 
    if (skip == 'year'):
        increment = increment * year_days;
    elif (skip == 'month'):
        increment = increment * month_days;
    # Add the days
    edited_date = edited_date + timedelta(days = increment)
    return edited_date.strftime("%Y-%m-%d")


# Graphs
def cars_seasonal_graph(data):
    graphdata = []
    for car in data:
        graphdata.append([car.car_makename, car.number_of_orders])
    return drawGraph('bar', 'cars_seasonal', graphdata)
def cars_inactive_graph(data = 0):
    graphdata = []
    for car in data:
        graphdata.append([car.car_makename, (date.today() - car.Return_Date).days])
    return drawGraph('horizBar', 'cars_inactive', graphdata)
def store_parking_graph(data = 0):
    graphdata = []
    for store in data:
        graphdata.append([store.store_city.replace(" ", ""), store.picked_up])
    return drawGraph('horizBar', 'store_parking', graphdata)
def store_activity_graph(data):
    graphdata = []
    for store in data:
        graphdata.append([store.store_city, store.total_activity])
    return drawGraph('pie', 'store_activity', graphdata)
def customer_demographics_graph(data=0):
    graphdata = []
    for demographic in data:
        graphdata.append([demographic[2], demographic[0]])
    return drawGraph('pie', 'customer_demographics', graphdata)


'''
' SPRINT 1
' The following are sprint 1:
'''
##### Reports Dashboard #####
def dashboard_context(limit = 5, 
                      start_date = default_start.strftime("%Y-%m-%d"), 
                      end_date = default_end.strftime("%Y-%m-%d")):
    seasonal_cars = Car.top_cars(limit)
    car_inactive = Car.inactive_cars(limit)
    store_activity = Store.store_activity(limit)
    store_parks = Store.store_parking(limit)
    customer_demographics = User.user_demographics(limit)
    context =  {'seasonal_cars': seasonal_cars,
                'store_activity': store_activity,
                'cars_seasonal_graph': cars_seasonal_graph(seasonal_cars),
                'cars_inactive_graph': cars_inactive_graph(car_inactive),
                'store_parking_graph': store_parking_graph(store_parks),
                'store_activity_graph': store_activity_graph(store_activity),
                'customer_demographics_graph': customer_demographics_graph(customer_demographics)}
    return context
def json_dashboard_context(request):
    dates = (request.GET.get('start_date', None), request.GET.get('end_date', None))
    data_rendered = {
        'html_response': render_to_string("CarRentalCompany/Includes/reports_dashboard_content.html", dashboard_context(dates=dates, limit=10))
    }
    return JsonResponse(data_rendered)
def dashboard(request):
    if is_management(request):
        return render(request,
                      'CarRentalCompany/reports_dashboard.html',
                      dashboard_context())
    return redirect('index')

##### Seasonal Cars Report #####
def cars_seasonal_context(limit = 10, 
                          start_date = default_start.strftime("%Y-%m-%d"), 
                          end_date = default_end.strftime("%Y-%m-%d")):
    seasonal_cars_results = Car.top_cars(limit, start_date, end_date)
    context =  {'cars_list': Car.objects.all(),
                'seasonal_cars':  seasonal_cars_results,
                'cars_seasonal_graph': cars_seasonal_graph(seasonal_cars_results),
                'start_date': start_date,
                'end_date': end_date}
    return context
def json_cars_seasonal_context(request):
    # Get update variables
    skip = request.GET.get('skip', None)
    forwards = request.GET.get('forwards', None) 
    no_change = request.GET.get('no_change', None)
    # Get dates
    to_date = request.GET.get('end_date', None)
    from_date = new_date(to_date, skip, 'false')
    # If the dates are being shifted
    if (no_change == 'false'): # == 'true' is necessary
        from_date = new_date(from_date, skip, forwards)
        to_date = new_date(to_date, skip, forwards)
    # send it
    data_rendered = {
        'html_response': render_to_string("CarRentalCompany/Includes/reports_cars_seasonal_content.html", 
                                          cars_seasonal_context(start_date = from_date, 
                                                                end_date = to_date))
    }
    return JsonResponse(data_rendered)
def cars_seasonal(request):
    if is_management(request):
        return render(request,
                      'CarRentalCompany/reports_cars_seasonal.html',
                      cars_seasonal_context())
    return redirect('index')


##### Inactive Cars Report #####
def cars_inactive_context(limit = 5, 
                          start_date = default_start.strftime("%Y-%m-%d"), 
                          end_date = default_end.strftime("%Y-%m-%d")):
    car_inactive = Car.inactive_cars(limit)
    context =  {'cars_list': Car.objects.all(),
                'inactive_cars': car_inactive,
                'cars_inactive_graph': cars_inactive_graph(car_inactive)}
    return context
def json_cars_inactive_context(request):
    dates = (request.GET.get('start_date', None), request.GET.get('end_date', None))
    data_rendered = {
        'html_response': render_to_string("CarRentalCompany/Includes/reports_cars_inactive_content.html", cars_inactive_context(dates))
    }
    return JsonResponse(data_rendered)
def cars_inactive(request):
    if is_management(request):
        return render(request,
                      'CarRentalCompany/reports_cars_inactive.html',
                      cars_inactive_context())
    return redirect('index')


##### Store Activity Report #####
def store_activity_context(limit = 5, 
                          start_date = default_start.strftime("%Y-%m-%d"), 
                          end_date = default_end.strftime("%Y-%m-%d")):
    locations = []
    for store in Store.objects.all():
        locations.append([eval(store.store_latitude), eval(store.store_longitude), store.store_name])
    store_results = Store.store_activity(limit, start_date, end_date)
    context =  {'stores_list': Store.objects.all(),
                'location_maps': locations,
                'store_results': store_results,
                'store_activity_graph': store_activity_graph(store_results),
                'start_date': start_date,
                'end_date': end_date}
    return context
def json_store_activity_context(request):
    # Get update variables
    skip = request.GET.get('skip', None)
    forwards = request.GET.get('forwards', None) 
    no_change = request.GET.get('no_change', None)
    # Get dates
    to_date = request.GET.get('end_date', None)
    from_date = new_date(to_date, skip, 'false')
    # If the dates are being shifted
    if (no_change == 'false'): # == 'true' is necessary
        from_date = new_date(from_date, skip, forwards)
        to_date = new_date(to_date, skip, forwards)
    # send it
    data_rendered = {
        'html_response': render_to_string("CarRentalCompany/Includes/reports_store_activity_content.html", 
                                          store_activity_context(start_date = from_date,
                                                                 end_date = to_date))
    }
    return JsonResponse(data_rendered)
def store_activity(request):
    if is_management(request):
        return render(request,
                      'CarRentalCompany/reports_store_activity.html',
                      store_activity_context())
    return redirect('index')


##### Store Parking Report #####
def store_parking_context(limit = 5, 
                          start_date = default_start.strftime("%Y-%m-%d"), 
                          end_date = default_end.strftime("%Y-%m-%d")):
    results = Store.store_parking(limit, start_date, end_date)
    context =  {'queried_stores': results,
                'stores': Store.objects.all(),
                'store_parking_graph': store_parking_graph(results),
                'start_date': start_date,
                'end_date': end_date}
    return context
def json_store_parking_context(request):
    # Get update variables
    skip = request.GET.get('skip', None)
    forwards = request.GET.get('forwards', None) 
    no_change = request.GET.get('no_change', None)
    # Get dates
    to_date = request.GET.get('end_date', None)
    from_date = new_date(to_date, skip, 'false')
    # If the dates are being shifted
    if (no_change == 'false'): # == 'true' is necessary
        from_date = new_date(from_date, skip, forwards)
        to_date = new_date(to_date, skip, forwards)
    # send it
    data_rendered = {
        'html_response': render_to_string("CarRentalCompany/Includes/reports_store_parking_content.html", 
                                          store_parking_context(start_date = from_date,
                                                                 end_date = to_date))
    }
    return JsonResponse(data_rendered)
def store_parking(request):
    if is_management(request):
        return render(request,
                      'CarRentalCompany/reports_store_parking.html',
                      store_parking_context())
    return redirect('index')


##### Customer Demographics Report #####
def customer_demographics_context(limit = 5, 
                                  start_date = default_start.strftime("%Y-%m-%d"), 
                                  end_date = default_end.strftime("%Y-%m-%d")):
    results = User.user_demographics()
    context =  {'users_list': User.objects.all(),
                'results': results,
                'customer_demographics_graph': customer_demographics_graph(results)}
    return context
def json_customer_demographics_context(request):
    dates = (request.GET.get('start_date', None), request.GET.get('end_date', None))
    data_rendered = {
        'html_response': render_to_string("CarRentalCompany/Includes/reports_customer_demographics_content.html", customer_demographics_context(dates))
    }
    return JsonResponse(data_rendered)
def customer_demographics(request):
    if is_management(request):
        results = customer_demographics_query()
        return render(request,
                      'CarRentalCompany/reports_customer_demographics.html',
                      customer_demographics_context())
    return redirect('index')



'''
' SPRINT 2
' The following are sprint 2:
'''
def custom(request):
    if request.user.is_authenticated:
        form = choose_report_type()
        form_cars = custom_report_cars()
        cars_selected = False
        type_selected = False
        report_actioned = False
        fields = ""
        if request.method == 'POST' and 'report_type' in request.POST:
            report_type = request.POST['report_type']
            type_selected = True
            if report_type == 'Cars':
                cars_selected = True
        if request.method == 'POST' and 'car_filters' in request.POST:
            fields = request.POST
            report_actioned = True
        return render(request,
                      'CarRentalCompany/custom_report.html',
                      {'form': form,
                       'form_cars': form_cars,
                       'cars_selected': cars_selected,
                       'type_selected': type_selected,
                       'fields': fields.items(),
                       'report_actioned': report_actioned})
    else:
        return redirect('index')
