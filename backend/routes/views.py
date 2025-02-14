from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Destination

@csrf_exempt
def add_destination(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            full_place_name = data.get("name")
            time = data.get("time")

            if not full_place_name or not time:
                return JsonResponse({"error": "Missing fields"}, status=400)

            # Extract city name (first part before the first comma)
            place_name = full_place_name.split(",")[0].strip()

            # Insert into MySQL table
            Destination.objects.create(name=place_name, time=int(time))

            return JsonResponse({"message": f"{place_name} added successfully!"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)
