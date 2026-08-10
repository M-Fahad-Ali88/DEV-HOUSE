from django.http import JsonResponse
import json


def hello(request):
    return JsonResponse({
        "message": "Hello World",
        "framework": "Django"
    })


def get_users(request):
    return JsonResponse([
        {"id": 1, "name": "Ali"},
        {"id": 2, "name": "Ahmed"}
    ], safe=False)


def create_user(request):
    if request.method != "POST":
        return JsonResponse(
            {"error": "POST request required"},
            status=405
        )

    data = json.loads(request.body)

    return JsonResponse({
        "message": "User created successfully",
        "user": data
    }, status=201)