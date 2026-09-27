import stripe
from django.shortcuts import render, redirect
from .models import Game, Category, Cart
from django.core.paginator import Paginator
from .forms import RegistrationForm
from django.conf import settings

def home_page(request):
    games = Game.objects.all()[:6]
    return render(request, "home.html", {"games" : games, })

def registration_page(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/login")
    else: 
        form = RegistrationForm()
    return render(request, "registration.html", {"form" : form})

def gamesearch_page(request):
    categories = Category.objects.all()
    games = Game.objects.all()
    category = request.GET.get("category")
    game = request.GET.get("search", "")
    current_page = request.GET.get("page", 1)

    if category:
        games = games.filter(categories__id=category)
        category = int(category)
    if game:
        games = games.filter(name__icontains=game)

    paginator = Paginator(games, 5)
    games = paginator.get_page(current_page)
    return render(request, "gamesearch.html", {"games" : games, "categories" : categories, "category" : category, "game" : game})

def login_page(request):
    return render(request, "login.html")

def game_page(request, key):
    if not request.user.is_authenticated:
        return redirect("/login")
    game = Game.objects.filter(id=key)
    if game:
        return render(request, "gamepage.html", {"game" : game[0]})
    else:
        return render(request, "404.html")
    
def categories_page(request):
    categories = Category.objects.all()
    
    return render(request, 'categories.html', {'categories': categories})

def cart_page(request):
    if not request.user.is_authenticated:
        return redirect("/login")
    games = Cart.objects.filter(user=request.user)
    final_price = 0
    amount = 0 
    for saved in games:
        final_price += saved.game.price
        amount += 1
    return render(request, "cart.html", {"games" : games, "price" : final_price, "amount" : amount})
    
def toggle_cart(request, key):
    if not request.user.is_authenticated:
        return redirect("/login")
    
    if Cart.objects.filter(user=request.user, game_id = key):
        Cart.objects.get(user=request.user, game_id = key).delete()
    else:
        Cart.objects.create(user=request.user, game_id = key)

    return redirect(request.META["HTTP_REFERER"])

def payment(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    payment = stripe.checkout.Session.create(
        line_items=[{
            "price_data":{
                "currency": "cad",
                "product_data": {"name": "Game"},
                "unit_amount": 200,
            },
        "quantity": 1,
        }],
        payment_method_types = ["card"],
        success_url = "http://127.0.0.1:8000/success",
        cancel_url = "http://127.0.0.1:8000/cart",
        mode = "payment",
    )
    print(payment.url)
    return redirect(payment.url)

def success(request):
    Cart.objects.filter(user=request.user).delete()
    return redirect("/")