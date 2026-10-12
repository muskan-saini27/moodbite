from django.shortcuts import render


def home(request):
    return render(
        request,
        "home.html",
    )


def food_detail(request, food_id):
    return render(
        request,
        "food_detail.html",
        {
            "food_id": food_id,
        },
    )


def saved_foods(request):
    return render(
        request,
        "saved.html",
    )

def about(request):
    return render(request, "about.html")