import stripe
from django.shortcuts import render, redirect
from .models import Game, Category, Cart
from django.core.paginator import Paginator
from .forms import RegistrationForm
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

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
    if not request.user.is_authenticated:
        return redirect("/login")

    cart_items = Cart.objects.filter(user=request.user).select_related("game")
    if not cart_items:
        return redirect("/cart")

    line_items = []
    for item in cart_items:
        if item.game.price > 0:
            line_items.append({
                "price_data": {
                    "currency": "cad",
                    "product_data": {"name": item.game.name},
                    "unit_amount": int(item.game.price * 100),
                },
                "quantity": 1,
            })
            
    if not line_items:
        cart_items.delete()
        return redirect("/")

    session = stripe.checkout.Session.create(
        line_items=line_items,
        payment_method_types=["card"],
        mode="payment",
        client_reference_id=str(request.user.id),
        metadata={"game_ids": ",".join(str(item.game.id) for item in cart_items)},
        success_url=request.build_absolute_uri("/success") + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri("/cart"),
    )
    return redirect(session.url)


def success(request):
    if not request.user.is_authenticated:
        return redirect("/login")

    session_id = request.GET.get("session_id")
    if not session_id:
        return redirect("/cart")

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.StripeError:
        return redirect("/cart")

    if session.payment_status == "paid" and session.client_reference_id == str(request.user.id):
        game_ids = session.metadata["game_ids"].split(",")
        Cart.objects.filter(user=request.user, game_id__in=game_ids).delete()

    return redirect("/")