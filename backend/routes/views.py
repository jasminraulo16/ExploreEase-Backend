import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Destination
import random
import numpy as np


@csrf_exempt
def add_destination(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            full_place_name = data.get("name")
            time = data.get("time")
            latitude = data.get("latitude")
            longitude = data.get("longitude")

            if not all([full_place_name, time, latitude, longitude]):
                return JsonResponse({"error": "Missing fields"}, status=400)

            # Extract city name (first part before the first comma)
            place_name = full_place_name.split(",")[0].strip()

            # Insert into MySQL table
            Destination.objects.create(
                name=place_name,
                latitude=float(latitude),
                longitude=float(longitude),
                time=int(time)
            )

            return JsonResponse({"message": f"{place_name} added successfully!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


def get_destinations(request):
    destinations = list(Destination.objects.values())
    return JsonResponse({"destinations": destinations})

@csrf_exempt
def delete_destination(request, id):
    try:
        destination = Destination.objects.get(id=id)
        destination.delete()
        return JsonResponse({"success": True})
    except Destination.DoesNotExist:
        return JsonResponse({"success": False, "error": "Destination not found"}, status=404)
    

def get_time_matrix():
    """Fetch travel time matrix from OSRM"""
    destinations = Destination.objects.all()
    if len(destinations) < 2:
        return None, "At least two destinations required"
    
    coordinates = ";".join([f"{d.longitude},{d.latitude}" for d in destinations])
    osrm_url = f"http://router.project-osrm.org/table/v1/driving/{coordinates}?annotations=duration"

    response = requests.get(osrm_url)
    osrm_data = response.json()

    if "durations" not in osrm_data:
        return None, "Failed to fetch time matrix from OSRM"
    
    return np.array(osrm_data["durations"]), destinations

def genetic_algorithm(time_matrix, places, total_time):
    """Optimize route using Genetic Algorithm"""
    num_places = len(places)
    population_size = 50
    generations = 100
    mutation_rate = 0.1

    def fitness(route):
        time_spent = sum(places[i].time for i in route)
        travel_time = sum(time_matrix[route[i]][route[i+1]] for i in range(len(route)-1))
        total_time_used = time_spent + travel_time
        return total_time - total_time_used if total_time_used <= total_time else -1e6

    def mutate(route):
        idx1, idx2 = random.sample(range(len(route)), 2)
        route[idx1], route[idx2] = route[idx2], route[idx1]
        return route

    population = [random.sample(range(num_places), num_places) for _ in range(population_size)]
    
    for _ in range(generations):
        population.sort(key=fitness, reverse=True)
        new_population = population[:10]
        for _ in range(population_size - 10):
            parent = random.choice(population[:20])
            child = mutate(parent[:])
            new_population.append(child)
        population = new_population

    best_route = population[0]
    return best_route

def optimize_route(request):
    """API to return optimized route"""
    try:
        total_time = int(request.GET.get("time", 240))  # Default 4 hours
        time_matrix, places = get_time_matrix()

        if time_matrix is None:
            return JsonResponse({"error": places}, status=400)

        optimized_order = genetic_algorithm(time_matrix, places, total_time)
        optimized_places = [places[i] for i in optimized_order]

        result = [
            {"id": place.id, "name": place.name, "lat": place.latitude, "lon": place.longitude}
            for place in optimized_places
        ]

        return JsonResponse({"route": result})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
