from django.shortcuts import render, redirect
from django.contrib import auth
from .models import Users as User
from .models import Upss, Address, Category, Products, Packages, Warehouse, Emails, Subscriber
from django.contrib.auth.decorators import login_required
from . import models
from mini_amazon.utils import *
from django.core.mail import send_mail


# homepage:
def index(request):
    # get site-visitor username using session
    username = request.session.get('username')
    categories = list(Category.objects.all())
    # locals() pass local variables to the template, which
    # returns a dictionary holding local variables names (key) and current values (value).
    return render(request, 'index.html', locals())

# Create your views here.
# user register:
def user_reg(request):
    categories = list(Category.objects.all())
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        # if user does not input email or username or password:
        if not username:
            return render(request, 'register.html', {'categories':categories, 'error_reg': 'Please enter a valid username!!!'})
        if not email:
            return render(request, 'register.html', {'categories':categories, 'error_reg': 'Please enter a valid email address!!!'})
        if not password:
            return render(request, 'register.html', {'categories':categories, 'error_reg': 'Please enter a valid password!!!'})
        # username already exists:
        if User.objects.filter(username=username):
            return render(request, 'register.html', {'categories':categories, 'error_reg': 'Username already exists!!!'})
        else:
            if password == confirm_password:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                useremail = Emails(user_id=user.pk, email_address=user.email)
                useremail.save()
                return redirect('/accounts/login/')
            else:
                return render(request, 'register.html', {'categories':categories, 'error_reg': 'The passwords entered twice do not match!!!'})
    else:
        return render(request, 'register.html', {'categories':categories})


# user login:
def login(request):
    categories = list(Category.objects.all())
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if User.objects.filter(username=username):
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                auth.login(request, user)
                # redirect to homepage
                return redirect('/', {'user', user})
            else:
                return render(request, 'login.html', {'categories':categories,'login_password_error' : 'Password is incorrect!!!'})
        else:
            return render(request, 'login.html', {'categories':categories,'login_username_error' : 'This user does not exist!!!'})
    else:
        return render(request, 'login.html', {'categories':categories})


# user logout:
@login_required
def logout(request):
    categories = list(Category.objects.all())
    auth.logout(request)
    return redirect('/accounts/login/')

# User should be able to view their info:
@login_required
def get_user_info(request):
    categories = list(Category.objects.all())
    user = User.objects.get(pk = request.user.pk)
    # commonly used ups account for user
    ups_name = ''
    for ups_account in Upss.objects.filter(user = request.user.pk):
        ups_name = ups_account.ups_name
    # commonly used dest addresses for user
    address_set = Address.objects.filter(user = request.user.pk)
    context = {
        'categories':categories,
        'username': user.username,
        'email': user.email,
        'ups_name': ups_name,
        # commonly used dest addresses query set
        'address_set': address_set,
    }
    return render(request, 'get_user_info.html', context)

# edit user info (email, commonly used address, commonly used ups account)
@login_required
def edit_user_info(request):
    categories = list(Category.objects.all())
    print(request)
    if request.method == 'POST':
        if User.objects.filter(username=request.POST['username']) and request.POST['username'] != request.user.username:
            return render(request, 'edit_user.html', {'categories':categories,'error_reg': 'This username has been registered!'})
        
        request.user.username=request.POST['username']
        request.user.email=request.POST['email']
        request.user.save()
        emails = Emails.objects.filter(user_id=request.user.pk).first()
        emails.email_address = request.POST['email']
        emails.save()
        return redirect('/accounts/get_user_info/')
    context = {
        'categories':categories,
        'username':request.user.username,
        'email':request.user.email
    }
    return render(request, 'edit_user.html', context) # because user is built-in, we don't need to pass in user object

@login_required
def edit_user_ups(request):
    categories = list(Category.objects.all())
    upsname=' '
    if request.method == 'POST':
        UPSacts = Upss.objects.filter(user = request.user.pk)
        if UPSacts.exists():
            ups_account = Upss.objects.get(user = request.user.pk)

            if Upss.objects.filter(ups_name=request.POST['ups_name']) and request.POST['ups_name'] != upsname:
                return render(request, 'edit_user.html', {'categories':categories,'upsname':upsname, 'error_msg': 'This UPS Account has been bound!'})

            if request.POST['ups_name'] != ' ':
                upsname = ups_account.ups_name
                ups_account.ups_name = request.POST['ups_name']
                ups_account.save()
                return redirect('/accounts/get_user_info/')
            else:
                context = {
                    'categories':categories,
                    'upsname':upsname,
                    'error_msg': 'Please type in your UPS Account Name!'
                }
                return render(request, 'edit_user.html', context)
        else:
            ups_account = Upss()
            ups_account.ups_name = request.POST['ups_name']
            ups_account.user = User.objects.get(pk = request.user.pk)
            ups_account.save()
            return redirect('/accounts/get_user_info/')

    context = {
        'categories':categories,
        'upsname':upsname
    }
    return render(request, 'edit_user.html', context) 

@login_required
def add_user_address(request):
    categories = list(Category.objects.all())
    address = Address()
    if request.method == 'POST':
        # if request.user.is_authenticated:
        duplicates = Address.objects.filter(user = request.user.pk)
        duplicates = duplicates.filter(address_x=request.POST['address_x'])
        duplicates = duplicates.filter(address_y=request.POST['address_y'])

        if duplicates.exists():
            context = {
                'categories':categories,
                'add_address': ' ',
                'error_msg': 'This address has been added!'
            }
            return render(request, 'edit_user.html', context)
        else:
            address.address_x = request.POST['address_x']
            address.address_y = request.POST['address_y']
            address.user = User.objects.get(id = request.user.pk)
            address.save()
            return redirect('/accounts/get_user_info/')
        
    context = {
        'categories':categories,
        'address_id':address.id,
        'address_x':address.address_x,
        'address_y':address.address_y,
        'add_address': ' '
        }
    return render(request, 'edit_user.html', context)


@login_required
def edit_user_address(request, address_id):
    categories = list(Category.objects.all())
    address = Address.objects.get(id=address_id)
    if request.method == 'POST':
        # if request.user.is_authenticated:
        duplicates = Address.objects.filter(user = request.user.pk)
        duplicates = duplicates.filter(address_x=request.POST['address_x'])
        duplicates = duplicates.filter(address_y=request.POST['address_y'])
        if duplicates.exists():
            context = {
                'categories':categories,
                'edit_address': ' ',
                'error_msg': 'This address has been added!'
            }
            return render(request, 'edit_user.html', context)
        else:
            address.address_x = request.POST['address_x']
            address.address_y = request.POST['address_y']
            address.save()
            return redirect('/accounts/get_user_info/')         

    context = {
        'categories':categories,
        'edit_address': ' ',
        'address_id':address_id,
    }
    return render(request, 'edit_user.html', context) 


@login_required
def delete_user_address(request, address_id):
    categories = list(Category.objects.all())
    Address.objects.filter(user=request.user.pk, id=address_id).delete()
    return redirect('/accounts/get_user_info/')


# buy products (shopping cart)
@login_required
def checkout(request, results):
    categories = list(Category.objects.all())
    user = User.objects.get(pk = request.user.pk)
    # packages list (package id) in this order:
    packages_bought_id = [int(num) for num in results.split(", ")]
    print(request.POST.get('is_add_address'))
    if request.method == "POST":
        ups_objs = Upss.objects.filter(user = request.user.pk)
        if not ups_objs:
            return render(request, 'checkout_result.html', {'categories':categories,'result_mssg': 'What a pity! Your purchase failed!', 'reason': 'Because your account is not yet linked to a UPS account. Please do it before buying.', 'reason_id': 1})
        # 1. get and save dist_x and dist_y and ups name and product price when product is bought
        address = request.POST.get('address')
        if not address and request.POST.get('is_add_address'):
            # No address selected and user add a new address and save it to frequently used address
            dist_x = request.POST.get('x')
            dist_y = request.POST.get('y')
            # address = Address.objects.get(user=request.user.pk, address_x=dist_x, address_y=dist_y)
            address_obj = Address(user=User.objects.get(pk = request.user.pk), address_x=dist_x, address_y=dist_y)
            address_obj.save()
            for package_id in packages_bought_id:
                package = Packages.objects.get(user=User.objects.get(pk = request.user.pk), id=package_id)
                package.dest_address = address_obj
                package.save()
        elif address and not request.POST.get('is_add_address'):
            x_y = [int(num) for num in address.split(", ")]
            address_obj = Address.objects.get(user=request.user.pk, address_x=x_y[0], address_y=x_y[1])
            for package_id in packages_bought_id:
                package = Packages.objects.get(user=User.objects.get(pk = request.user.pk), id=package_id)
                package.dest_address = address_obj
                package.save()
        elif not address and not request.POST.get('is_add_address'):
            return render(request, 'checkout_result.html', {'categories':categories,'result_mssg': 'What a pity! Your purchase failed!', 'reason': 'Because you did not select a common shipping address or input a new shipping address.', 'reason_id': 2})
        ups_obj = Upss.objects.filter(user = request.user.pk).first()
        for package_id in packages_bought_id:
            package = Packages.objects.get(id=package_id)
            package.bought_price = package.product_id.price
            package.ups_name = ups_obj
            # 3. change the package status become bought
            package.status = 1
            # 2. get best warehouse and save it
            # package.warehouse_id = get_best_warehouse(package.dest_address.address_x, package.dest_address.address_y)
            package.save()
        # check payment method:
        pay_mathod = request.POST.get('payment-method')
        if pay_mathod == "bank":
            return render(request, 'checkout_result.html', {'categories':categories,'result_mssg': 'What a pity! Your purchase failed!', 'reason': 'Because we do not support credit card payment at the moment. Please choose another payment method.', 'reason_id': 4})
        if pay_mathod is None:
            return render(request, 'checkout_result.html', {'categories':categories,'result_mssg': 'What a pity! Your purchase failed!', 'reason': 'Please choose a valid payment method.', 'reason_id': 5})
        # 4. send email to user: successful purchase
        subject = "Your purchase was successful!"
        print("Your purchase was successful!")
        email_content = "You have just successfully purchased products on our website. Thank you for your trust in our website."
        #send_email(subject, email_content, str(user.email))
        send_mail(
            subject=subject,
            message=email_content,
            from_email='miniamazon.rui.aoli1@gmail.com',
            recipient_list=[user.email],
            fail_silently=False
        )

    return render(request, 'checkout_result.html', {'categories':categories,'result_mssg': 'Congratulations! Your purchase was successful!', 'reason': 'Next, you just need to wait for your package at home.', 'reason_id': 3})


# show user's shopping cart
@login_required
def get_shopping_cart(request):
    categories = list(Category.objects.all())
    if request.method == 'POST':
        action = request.POST.get('action')
        # delete specific package
        if action == 'delete':
            package_id = request.POST.get('package_id')
            Packages.objects.filter(
                user=request.user.pk, id=package_id).delete()
        # checkout:
        elif action == 'checkout':
            # package objects:
            packages = Packages.objects.filter(user=request.user.pk, status=0).order_by('create_time').all()
            total = 0
            for package in packages:
                total += package.product_id.price * package.purchase_quantity
            # a list of packages' id
            packages_bought = []
            for package in packages:
                packages_bought.append(package.id)
            packages_bought_str = list(map(str, packages_bought))
            results = ', '.join(packages_bought_str)
            ups = Upss.objects.filter(user = request.user.pk)
            addresses = Address.objects.filter(user = request.user.pk)
            if not packages.exists():
                return render(request, 'checkout.html', context={'categories':categories,"results": results, "ups": ups, "addresses": addresses, "packages": packages, "total": total, "no_order": "No Order"})
            return render(request, 'checkout.html', context={'categories':categories,"results": results, "ups": ups, "addresses": addresses, "packages": packages, "total": total})
        # update purchase quantity:
        elif action == 'add':
            package_id = request.POST.get('package_id')
            p = Packages.objects.filter(
                user=request.user.pk, id=package_id).first()
            p.purchase_quantity = p.purchase_quantity + 1
            p.save()
        elif action == 'reduce':
            package_id = request.POST.get('package_id')
            p = Packages.objects.filter(
                user=request.user.pk, id=package_id).first()
            p.purchase_quantity = p.purchase_quantity - 1
            p.save()

    package_results = Packages.objects.filter(
        user=request.user.pk, status=0).order_by('create_time').all()
    results = []
    total_price = 0
    for item in package_results:
        i = {}
        i['item'] = item
        total_price += item.product_id.price * item.purchase_quantity
        i['subtotal'] = item.product_id.price * item.purchase_quantity
        results.append(i)
    return render(request, 'cart.html', {'categories':categories,'package_results': results, 'total_price': total_price})


# delete order/package from shopping cart
@login_required
def delete_package_from_cart(request, package_id):
    categories = list(Category.objects.all())
    Packages.objects.filter(user=request.user.pk, id=package_id).delete()
    return redirect('/get_shopping_cart/')

# show all user's historical orders/packages and search user's historical orders/packages by product name or by status
@login_required
def get_packages(request):
    categories = list(Category.objects.all())
    # query user's historical orders/packages with uid and not "delete" "buying" status
    package_results = Packages.objects.filter(user = request.user.pk, status__lt = 8, status__gt = 0).order_by('create_time').all()
    # search packages by product name or product status
    if request.method == "POST":
        search_by_name = request.POST.get('search_by_name')
        search_by_status = request.POST.get('search_by_status')
        search_results = []
        if search_by_name:
            search_results = Packages.objects.filter(user=request.user.pk, status__lt=8, status__gt = 0, product_id__pdname__icontains=search_by_name).order_by('create_time').all()
        elif search_by_status:
            # transfer user input become integer
            status_choices = {
                "Bought": 1,
                "Packing": 2,
                "Packed": 3,
                "Loading": 4,
                "Loaded": 5,
                "Delivering": 6,
                "Delivered": 7,
            }
            search_results = Packages.objects.filter(user=request.user.pk, status=status_choices[search_by_status]).order_by('create_time').all()
        package_results = search_results
    return render(request, 'historical_orders.html', {'categories':categories,'package_results': package_results})

# show details for one specific historical orders/packages
@login_required
def get_package_info(request, package_id):
    categories = list(Category.objects.all())
    package_results = Packages.objects.filter(id=package_id)
    for package in package_results:
        total_price = package.product_id.price * package.purchase_quantity
        return render(request, 'get_order_info.html', {'categories':categories,'package': package, 'total_price': total_price})

# delete historical order/package with "delivered" status
@login_required
def delete_package(request, package_id):
    categories = list(Category.objects.all())
    Packages.objects.filter(user=request.user.pk, id=package_id).delete()
    return redirect('/accounts/historical_orders/')

@login_required
def rate(request, package_id):
    categories = list(Category.objects.all())
    package = Packages.objects.get(id=package_id)
    product = package.product_id

    if package.rating != 0:
            context = {
                'categories':categories,
                'product_name':product.pdname,
                'message': 'You have rated this product!',
                'rated':package.rating,
                'product_id':product.id
            }
            return render(request, 'rate.html', context) 
    
    if request.method == 'POST':      
        product.total_rating += float(request.POST['rating'])
        product.num_rating += 1
        product.save()
        product.avg_rating = product.total_rating/product.num_rating
        product.save()
        package.rating = float(request.POST['rating'])
        package.save()
        return redirect('/accounts/historical_orders/')
    
    context = {
        'categories':categories,
        'product_name':product.pdname,
        'package_id': package_id,
        'product_id':product.id
    }
    return render(request, 'rate.html', context) 

def search_pd_by_cat(request, catName):
    categories = list(Category.objects.all())
    cat = models.Category.objects.get(name=catName)
    results = models.Products.objects.filter(category=cat.id).all()

    if request.method == 'POST':
        search = request.POST.get('search_title')
        results = results.filter(description__icontains=search)| results.filter(pdname__icontains=search)

    categories = list(Category.objects.all()) 
    context = {
        'categories':categories,
        "results":results,
        "catName":catName,
        "categories":categories
    }

    return render(request, 'searchResults.html', context)


# search product by product name and product description
def search_product(request):
    categories = list(Category.objects.all())
    results = models.Products.objects.all()
    search = 'All Products'
    if request.method == 'POST':
        search = request.POST.get('search_title')
        # result = models.Category.objects.filter(name__icontains=search_title)
        results = models.Products.objects.filter(description__icontains=search) | models.Products.objects.filter(pdname__icontains=search)
    categories = list(Category.objects.all())
    context = {
        'categories':categories,
        "results":results,
        "search":search,
        "categories":categories
    }
    return render(request, 'searchResults.html', context)


# show the product info of a pecific product and user can "buy now" and 
# "add to cart" for this specific product
def product_details(request, pd_id):
    categories = list(Category.objects.all())
    product = Products.objects.get(id=pd_id)
    if request.method == "POST":
        if request.user.is_authenticated:
            quantity = int(request.POST.get("quantity"))
            if(not quantity or int(quantity) <= 0):
                return render(request, 'product_details.html', {'categories':categories,'quantity_error' : 'Please enter a valid quantity.'})
            # buy this product directly 
            if "buy_now" in request.POST:
                package = Packages(user=User.objects.get(pk = request.user.pk), product_id=product, purchase_quantity=quantity, status=None)
                package.save()
                total = package.purchase_quantity * package.product_id.price
                packages = []
                packages.append(packages)
                packages_bought = []
                packages_bought.append(package.id)
                packages_bought_str = list(map(str, packages_bought))
                results = ', '.join(packages_bought_str)
                ######################TODO: checkout #########################
                ups = Upss.objects.filter(user = request.user.pk)
                addresses = Address.objects.filter(user = request.user.pk)
                return render(request, 'checkout.html', context={'categories':categories,"results": results, "ups": ups, "addresses": addresses, "packages": packages, "total": total})
            # or add this product to shopping cart
            elif "add_to_cart" in request.POST:
                package, created = Packages.objects.get_or_create(
                    user=User.objects.get(pk = request.user.pk),
                    product_id=product,
                    status=0
                )
                package.purchase_quantity += int(quantity)
                package.save()
        else:
            return redirect('/accounts/login/')
    # show related products of this product (they have the same category)
    related_products = Products.objects.filter(category = product.category).order_by('pdname').all()
    return render(request, "product_detail.html", {'categories':categories,"product": product, "related_products": related_products})



########################   footer pages   ########################
def aboutUS(request):
    categories = list(Category.objects.all())
    return render(request, "footer.html", {'categories':categories, 'aboutus':" "})

def contact(request):
    categories = list(Category.objects.all())
    return render(request, "footer.html", {'categories':categories, 'contact':" "})

def guide(request):
    categories = list(Category.objects.all())
    return render(request, "footer.html", {'categories':categories, 'guide':" "})

def exchange(request):
    categories = list(Category.objects.all())
    return render(request, "footer.html", {'categories':categories, 'exchange':" "})

def faq(request):
    categories = list(Category.objects.all())
    return render(request, "footer.html", {'categories':categories, 'faq':" "})


def subscribe(request):
    if request.method == 'POST':
        categories = list(Category.objects.all())
        receiver = request.POST.get('email')
        if not is_valid_email(receiver):
            return render(request, "footer.html", {'invalid_email':"Please enter a valid email address"})
        subscriber_obj = Subscriber(email_address=receiver)
        subscriber_obj.save()
        subject = "Thank You For Subscribing To Our Newsletter"
        email_content = "Welcome to Mini Amazon. Thank you for your subscription! When new products are released, we will send emails to notify you in time! You are one step closer to a seamless shopping experience! We sincerely hope you enjoy your shopping!"
        # send_email(subject, email_content, receiver)
        send_mail(
            subject=subject,
            message=email_content,
            from_email='miniamazon.rui.aoli1@gmail.com',
            recipient_list=[receiver],
            fail_silently=False
        )
        return render(request, "footer.html", {'categories':categories, 'subscribed':" "})

    
# User can send messagesn (questions & suggestions & Reviews) to us:
def msg_recved(request):
    if request.method == 'POST':
        categories = list(Category.objects.all())
        receiver = 'miniamazon.rui.aoli1@gmail.com'
        contact_name = request.POST.get('contact_name')
        subject = "Message from " + contact_name
        email = request.POST.get('email')
        if email == "":
            return render(request, "footer.html", {'contact':" ", "err": "Please enter your email address so that you can receive our reply."})
        if not is_valid_email(email):
            return render(request, "footer.html", {'invalid_email':"Please enter a valid email address"})
        if not request.POST.get('is_robot'):
            return render(request, "footer.html", {'contact':" ", "err": "Please verify you are not a robot."})
        message = request.POST.get('message')
        if message == "":
            return render(request, "footer.html", {'contact':" ", "err": "Please enter the message."})
        email_content = message + "    Email: " + email
        # send_email(subject, email_content, receiver)
        send_mail(
            subject=subject,
            message=email_content,
            from_email='miniamazon.rui.aoli1@gmail.com',
            recipient_list=[receiver],
            fail_silently=False
        )
        msg_received = "Thank you for contacting us and we will be in contact with you shortly!"
        # send_email(subject, msg_received, email)
        send_mail(
            subject=subject,
            message=msg_received,
            from_email='miniamazon.rui.aoli1@gmail.com',
            recipient_list=[email],
            fail_silently=False
        )
        return render(request, "footer.html", {'categories':categories, 'contacted':" "})
    