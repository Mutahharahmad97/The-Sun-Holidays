from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
import requests, json
import datetime
from random import seed
from random import randint
from thesunholidays.models import Destinations

def index(request):
    try:
        location_lat = request.GET.get('Lat')
        location_lon = request.GET.get('Lon')
        location_lat = 51.507351
        location_lon = -0.127758
        seed(0)

    
        # GET NEAREST AIRPORT ON THE BASIS OF COORDINATES
        cityData = requests.get('https://ourairportapi.com/nearest/' +
                                str(location_lat) + ',' + str(location_lon) + '?max=1')
        cityData = cityData.json()
        cityData = cityData['results'][0]
        region = cityData['region']
        #iata = cityData['iata']
        currentCity = cityData['municipality']
        #Useful data: Airport name, City, Country (PK), region (PK-PB), iata (LYP)
        

        #GET LOCAL CURRENCY AND CITY INFO
        countryCode = cityData['country']
        url = "https://restcountries-v1.p.rapidapi.com/alpha/" + countryCode
        headers = {
            'x-rapidapi-host': "restcountries-v1.p.rapidapi.com",
            'x-rapidapi-key': "a8daabe097msh223ac2b437313bep1a98f2jsn31f14dc64939"
        }

        countryInfo = requests.request("GET", url, headers=headers)
        countryInfo = countryInfo.json()
        cityCurrency = countryInfo['currencies'][0]
        #Useful data: Selected City Local Currency(PKR)

        #LIST OF CURRENCIES
        url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/reference/v1.0/currencies"
        headers = {
            'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
            'x-rapidapi-key': "a8daabe097msh223ac2b437313bep1a98f2jsn31f14dc64939"
        }
        currencies = requests.request("GET", url, headers=headers)
        currencies = json.loads(currencies.text)
        currencies = currencies['Currencies']
        #List of all currencies

        #FLIGHTS OF NEXT 14 DAYS
        headers = {
            'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
            'x-rapidapi-key': "adf1ffebddmshc9c49989e763158p1035d7jsn540af4b3a496"
        }
        
        currencies_codes_symbols = {}
        
        currencySymbol = ""
        for currency in currencies:
            if(currency['Code'] == cityCurrency):
                currencySymbol = currency['Symbol']
                
            currencies_codes_symbols[currency['Code']] = currency['Symbol']
        
        data_db = Destinations.objects.all()
        destinations_and_codes = {}
        for i in data_db:
            destinations_and_codes[i.airport] = i.city
        
        destinations = [i for i in destinations_and_codes.keys()]
        cities_names = [i for i in destinations_and_codes.values()]
        cities_names.insert(0, currentCity)
        Cities_Data = {i: [] for i in destinations}
        

        #Loop for 14 Days
        for j in destinations:
            Score = 0

            for i in range(0, 14):
                try:
                    date = datetime.datetime.now() + datetime.timedelta(days=i)
                    url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browseroutes/v1.0/" + \
                        str(countryCode) + "/" + str(cityCurrency) + "/" + str(region) + "/" + \
                        "LCY" + "-sky/" + j + "-sky/" + str(date.strftime("%Y-%m-%d"))

                    response = requests.request("GET", url, headers=headers , params={"inboundpartialdate": date.strftime("%Y-%m-%d")})

                    response = response.json()
                    if(len(response["Quotes"]) > 0):
                        priceOfFlight = response["Quotes"][0]["MinPrice"]
                        rainyDays = GetRandomWeather("rainy")
                        avgTemp = GetRandomWeather("temp")
                        Score += CalculateScore(priceOfFlight, rainyDays, avgTemp)
                        Cities_Data[j].append(
                            {"price": str(currencySymbol) + "" + str(priceOfFlight), "Date": date.strftime("%Y-%m-%d")})
                        
                    
                except Exception as e:
                    print(e)
                    continue

            Cities_Data[j].append({"Score": Score, "city": destinations_and_codes[j], 'current_date': datetime.datetime.now(
            ).strftime("%d %b"), 'end_date': (datetime.datetime.now() + datetime.timedelta(days=13)).strftime("%d %b")})


        Cities_Data['Currencies'] = [currencies_codes_symbols]
        Cities_Data['Cities'] = cities_names
        response = JsonResponse({"data" : Cities_Data})
        
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
        return response
    
    except Exception as e:
        raise Http404('There was a problem Overall')


def GetRandomWeather(random):
    if(random == "temp"):
        return randint(15,40)
    else:
        return randint(0,14)

def CalculateScore(priceofFlight, rainyDays, avgTemp):
    rankOfTemp = avgTemp - (10 * (rainyDays/14) * 100)
    if(avgTemp > 26):
        return rankOfTemp + priceofFlight
    else:
        return (rankOfTemp + priceofFlight) * 2

def DetailApi(request):
    try:
        destination_city = request.GET.get('city')
        # location_lat = request.GET.get('lat')
        # location_lon = request.GET.get('lon')
        location_lat = 51.507351
        location_lon = -0.127758
        destination_query = Destinations.objects.filter(city = destination_city)
        description = destination_query[0].description
        Airport = destination_query[0].airport
                
        cityData = requests.get('https://ourairportapi.com/nearest/' + str(location_lat) + ',' + str(location_lon) + '?max=1')
        
        cityData = cityData.json()
        cityData = cityData['results'][0]
        region = cityData['region']
        #iata = cityData['iata']
        currentCity = cityData['municipality']
        #Useful data: Airport name, City, Country (PK), region (PK-PB), iata (LYP)

        #GET LOCAL CURRENCY AND CITY INFO
        countryCode = cityData['country']
        url = "https://restcountries-v1.p.rapidapi.com/alpha/" + countryCode
        headers = {
            'x-rapidapi-host': "restcountries-v1.p.rapidapi.com",
            'x-rapidapi-key': "a8daabe097msh223ac2b437313bep1a98f2jsn31f14dc64939"
        }

        countryInfo = requests.request("GET", url, headers=headers)
        countryInfo = countryInfo.json()
        cityCurrency = countryInfo['currencies'][0]
        #Useful data: Selected City Local Currency(PKR)

        #LIST OF CURRENCIES
        url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/reference/v1.0/currencies"
        headers = {
            'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
            'x-rapidapi-key': "a8daabe097msh223ac2b437313bep1a98f2jsn31f14dc64939"
        }
        currencies = requests.request("GET", url, headers=headers)
        currencies = json.loads(currencies.text)
        currencies = currencies['Currencies']
        #List of all currencies

        #FLIGHTS OF NEXT 14 DAYS
        headers = {
            'x-rapidapi-host': "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com",
            'x-rapidapi-key': "adf1ffebddmshc9c49989e763158p1035d7jsn540af4b3a496"
        }

        viatorLink = Destinations.objects.filter(city= destination_city)
        viatorLink = viatorLink[0].viator_link

        currencySymbol = ""
        for currency in currencies:
            if(currency['Code'] == cityCurrency):
                currencySymbol = currency['Symbol']
                
        Final_Response = {"CityName": destination_city, "Description" : description, "Viator_Link" : viatorLink}
        
        TempList = list(Destinations.objects.values_list('city', flat=True))
        TempList.insert(0, currentCity)
        Final_Response['Cities'] = TempList
        Dates = {}
        
        for i in range(0,4):
            outboundDate = datetime.datetime.now() + datetime.timedelta(days=i)
            Prices_OutBounds = []
            for j in range(0,4):
                inboundDate = datetime.datetime.now() + datetime.timedelta(days=j)
                url = "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/apiservices/browseroutes/v1.0/" + \
                    str(countryCode) + "/" + str(cityCurrency) + "/" + str(region) + "/" + \
                    "LCY" + "-sky/" + Airport + "-sky/" + str(outboundDate.strftime("%Y-%m-%d"))


                response = requests.request("GET", url, headers=headers, params={"inboundpartialdate": inboundDate.strftime("%Y-%m-%d")})

                response = response.json()
                
                if(len(response["Quotes"]) > 0):
                    priceOfFlight = str(response["Quotes"][0]["MinPrice"]) + str(currencySymbol)
                    
                else:
                    priceOfFlight = " "
                    
                Prices_OutBounds.append(priceOfFlight)
                
            Dates[outboundDate.strftime("%d %b")] =  Prices_OutBounds
                
    except Exception as e:
        print(e)
        raise Http404("There's been a problem with the city you provided")

    Final_Response['Dates'] = Dates
    response = JsonResponse({'data' : Final_Response})

    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response