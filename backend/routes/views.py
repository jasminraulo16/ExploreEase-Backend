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

            place_name = full_place_name.split(",")[0].strip()

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
    destinations = Destination.objects.all()
    if len(destinations) < 2:
        return None, "At least two destinations required"
    
    coordinates = ";".join([f"{d.longitude},{d.latitude}" for d in destinations])
    osrm_url = f"http://router.project-osrm.org/table/v1/driving/{coordinates}?annotations=duration"

    response = requests.get(osrm_url)
    osrm_data = response.json()

    if "durations" not in osrm_data:
        return None, "Failed to fetch time matrix from OSRM"
    
    return np.array(osrm_data["durations"]), list(destinations)

import random

def genetic_algorithm(time_matrix, places, total_time):
    """Optimize route using Genetic Algorithm with fixed source and shortest path selection"""
    num_places = len(places)
    population_size = 50
    generations = 100
    mutation_rate = 0.1

    # Keep the first destination fixed
    def fitness(route):
        route_with_source = [0] + route  # Keep first place fixed
        time_spent = sum(places[i].time for i in route_with_source)
        travel_time = sum(time_matrix[route_with_source[i]][route_with_source[i+1]] for i in range(len(route_with_source)-1))
        total_time_used = time_spent + travel_time

        if total_time_used > total_time:
            return -1 * (total_time_used - total_time)  # Small penalty instead of extreme -1e6

        return -travel_time  # Still prioritize shorter routes


    def mutate(route):
        if len(route) > 1:
            idx1, idx2 = random.sample(range(len(route)), 2)
            route[idx1], route[idx2] = route[idx2], route[idx1]
        return route

    # Generate initial population while keeping the first destination fixed
    initial_routes = [random.sample(range(1, num_places), num_places - 1) for _ in range(population_size)]
    population = [[0] + route for route in initial_routes]  # Keep first place fixed

    for _ in range(generations):
        population.sort(key=fitness, reverse=True)
        new_population = population[:10]

        for _ in range(population_size - 10):
            parent = random.choice(population[:20])
            child = mutate(parent[1:])  # Mutate only the remaining places
            new_population.append([0] + child)  # Keep the first place fixed

        population = new_population

    # Select only the shortest route within the total_time
    # Select only the shortest route within the total_time
    best_route = [0]  # Start with the source
    time_used = places[0].time  # Include time spent at the first place

    for i in population[0][1:]:  # Skip the source (0)
        last_place = best_route[-1]  # Get the last visited place
        travel_time = time_matrix[last_place][i] / 60  # Convert seconds to minutes

        if time_used + places[i].time + travel_time <= total_time:
            best_route.append(i)
            time_used += places[i].time + travel_time
        else:
            break  # Stop adding places if time exceeds limit


    return best_route


def optimize_route(request):
    """API to return optimized route starting from the first added destination"""
    try:
        total_time = int(request.GET.get("time", 240))  # Default 4 hours
        time_matrix, places = get_time_matrix()
        print(time_matrix)

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


