from django.shortcuts import render, redirect
from django.http import JsonResponse
import json
import datetime
from django.views.decorators.csrf import csrf_exempt
from .models import *
from .registerform import RegisterForm
from django.contrib import auth

# Create your views here.

@csrf_exempt
# 註冊頁面(register)邏輯
def register(request):
    
    # 請求方法為POST
    if request.method == "POST":
        # 以前端表單資料POST過來建立註冊資料
        form = RegisterForm(request.POST)
        # 表單有效
        if form.is_valid():
            # 建立使用者
            form.save()
            # 透過form的資料取得username(使用者帳號)
            username = form.cleaned_data.get('username')
            # 建立User物件(Django內部物件)
            userObj = User.objects.get(username=username)
            # 建立使用者時，也一同建立會員資料(Customer)
            Customer.objects.create(
                user=userObj,
                name=userObj.first_name,
                email=userObj.email,
            )
            # 如果完成註冊即重新導向到購物頁面
            return redirect('/')
        else:
            # 如果是無效表單就傳遞空註冊表單物件，並且重新導向註冊頁面(目前尚未提醒註冊失敗訊息)
            form = RegisterForm()
    else:
        # 如果是GET就傳遞空註冊表單物件
        form = RegisterForm()
    # Reload註冊頁面
    return render(request, 'store/register.html', {'form': form})
    
@csrf_exempt
# 登入頁面(login)邏輯
def login(request):

    # 取得POST過來的帳號及密碼，沒有值的話，預設為空值
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    
    # Django提供帳號驗證，參數為帳號、密碼
    user = auth.authenticate(username=username, password=password)

    # user變數不是null及帳戶有效的話
    if user is not None and user.is_active:
        auth.login(request, user)
        return redirect('/')
    else:
        return render(request, 'store/login.html') 

@csrf_exempt
# 登出頁面(logout)邏輯
def logout(request):

    auth.logout(request)
    
    return redirect('/') #重新導向到登入畫面

# 商店頁面(store)邏輯
def store(request):
    # 當使用者是被認證的(非AnonymousUsrr)
    if request.user.is_authenticated:
        # 取得請求內的user物件的customer物件
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, completed=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'store/store.html', context)

def view(request, id):
    # 當使用者是被認證的(非AnonymousUsrr)
    if request.user.is_authenticated:
        # 取得請求內的user物件的customer物件
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, completed=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    product = Product.objects.get(id=id)
    context = {'product': product, 'cartItems': cartItems}
    return render(request, 'store/view.html', context)

def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, completed=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order': order, 'cartItems': cartItems, 'shipping': False}
    return render(request, 'store/cart.html', context)

def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, completed=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0}
        cartItems = order['get_cart_items']

    context = {'items': items, 'order': order, 'cartItems': cartItems, 'shipping': False}
    return render(request, 'store/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('productId:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, completed=False)

    orderitem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderitem.quantity = (orderitem.quantity + 1)
    elif action == 'remove':
        orderitem.quantity = (orderitem.quantity - 1)
    elif action == 'removeAll':
        orderitem.quantity = 0

    orderitem.save()

    if orderitem.quantity <= 0:
        orderitem.delete()

    return JsonResponse('商品已被加入', safe=False)

@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, completed=False)
        total = data['form']['total']
        order.transaction_id = transaction_id

        if total == format(order.get_cart_total, ','):
            order.completed = True
        order.save()

        if order.shipping == True:
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                address=data['shipping']['address'],
                city=data['shipping']['city'],
                state=data['shipping']['state'],
                zipcode=data['shipping']['zipcode'],
            )

    else:
        print('使用者未登入!')

    return JsonResponse('付款完成', safe=False)