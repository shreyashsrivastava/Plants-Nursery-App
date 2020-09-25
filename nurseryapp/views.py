from django.shortcuts import render, reverse, redirect
from .models import CustomUser, UserForm, Plants, PlantsForm, Order, OrderItem, ShippingAddress
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
import datetime 
import re
# from django.contrib import messages

def home(request):
    if not request.user.is_staff:
        plants = Plants.objects.all()
        return render(request, 'nurseryapp/index.html', {'plants':plants})

    return HttpResponseRedirect(reverse("nurseryapp:dashboard"))
    
def signup_index(request):
    return render(request, "user/index.html")

def signup_form(request, user):
    form = UserForm()
    if user == 1:
        return render(request, "user/customer_signup.html", {'form':form})
    elif user == 2:
        return render(request, "user/manager_signup.html", {'form':form})
    else:
        return redirect('nurseryapp:signup')

def signup(request, user):
    if request.method == 'POST':
        customuser = CustomUser.objects.all()
        email = request.POST['username']
        phone = request.POST['phone']
        password = request.POST['password']
        for users in customuser:
            if email == users.username:
                return HttpResponse("Your'e already signed In.")
            if phone == users.phone:
                return HttpResponse("Phone number already registered.")
        if not re.match("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", email):
            return HttpResponse('Enter a valid email')
        if not len(phone) == 10 or not phone.isnumeric():
            return HttpResponse("Enter a valid phone number, should be 10 digits and numbers only.")
        if not len(password) > 5:
            return HttpResponse("Password should not be less than 5 characters")
        if user == 1: # user is a customer
            customer = UserForm(request.POST)
            if customer.is_valid():
                user = customer.save(commit=False)
                user.set_password(request.POST['password'])
                user.save()
                return HttpResponseRedirect(reverse('nurseryapp:login_page'))
            
        elif user == 2: #user is a manager
            manager = UserForm(request.POST)
            if manager.is_valid():
                user = manager.save(commit=False)
                user.set_password(request.POST['password'])
                user.save()
            
            nursery = request.POST['nursery']
            mgr = CustomUser.objects.get(username=email)
            mgr.is_staff=True
            mgr.nursery = nursery
            mgr.save()
            return HttpResponseRedirect(reverse('nurseryapp:login_page'))


        else:
            return HttpResponse("back to home")


def dashboard(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            myplants = Plants.objects.filter(manager=request.user)
            order_items = OrderItem.objects.filter(product__id__in=myplants.all()) #life saver line
           
            for_front = {
                'myplants':myplants,
                'orders':order_items,
            }

            return render(request, 'dashboard/manager.html', for_front)
        else:
            order = Order.objects.filter(customer=request.user, complete=True)
            order_items = OrderItem.objects.filter(order__id__in=order.all()) 
            print(order_items)
            for_front = {
                'order_items':order_items
            }
            return render(request, 'dashboard/customer.html', for_front)
    else:
        return HttpResponseRedirect(reverse('nurseryapp:login_page'))
              
def user_login(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user_model = get_user_model()
            print(user_model)
            print(password)
        try:
            user = user_model.objects.get(username=username)
            print(user)
            if user.check_password(password):
                login(request, user)
                if user.is_staff:
                    return HttpResponseRedirect(reverse("nurseryapp:dashboard"))
                else:
                    return HttpResponseRedirect(reverse("nurseryapp:home"))
            else:
                return HttpResponse("Invalid password")
        except user_model.DoesNotExist:
            return HttpResponse("Invalid email")
        else:
            return HttpResponse("Not a POST request")
    else:
        return HttpResponse("You're already logged in")

def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse("nurseryapp:home"))

@login_required 
def addplant_form(request):
    if request.user.is_staff:
        form = PlantsForm()
        return render(request, 'dashboard/addplant_form.html', {'form':form})

@login_required
def addplant(request):
    if request.user.is_staff and request.method == 'POST':
        plant = PlantsForm(request.POST, request.FILES)
        if plant.is_valid:
            p = plant.save(commit=False)
            p.manager = request.user 
            plant.save()
            return HttpResponseRedirect(reverse("nurseryapp:dashboard"))
    else:
        return HttpResponse("Waait a min, Who Are You ?")

@login_required(login_url='nurseryapp:login_page')
def cart_action(request, p_id, action):
    user = request.user
    product = Plants.objects.get(id=p_id)
    order, created = Order.objects.get_or_create(customer=user, complete=False)
    orderitem, created = OrderItem.objects.get_or_create(order=order, product=product)   
    if action == 1: # for add item
        orderitem.quantity += 1
    elif action == 0: # For Remove Item
        orderitem.quantity -= 1

    orderitem.save()

    if orderitem.quantity <= 0:
        orderitem.delete()
    
    return HttpResponseRedirect(reverse('nurseryapp:cart'))

@login_required(login_url='nurseryapp:login_page')
def cart(request):
    customer = request.user
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitem_set.all()
    return render(request, 'nurseryapp/cart.html', {'items':items, 'order':order})


@login_required(login_url='nurseryapp:login_page')
def checkout(request):
    customer = request.user
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitem_set.all()
    return render(request, 'nurseryapp/checkout.html', {'items':items, 'order':order})

@login_required(login_url='nurseryapp:login_page')
def process_order(request):
    transaction_id = datetime.datetime.now().timestamp()

    customer = request.user

    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    total = order.get_cart_total
    order.transaction_id = transaction_id

    order.complete = True
    order.save()    


    ShippingAddress.objects.create(
        customer = customer,
        order = order,
        address = request.POST['address'],
        city = request.POST['city'],
        state = request.POST['state'],
        pincode = request.POST['pincode'],
    )

    return HttpResponseRedirect(reverse('nurseryapp:dashboard'))


