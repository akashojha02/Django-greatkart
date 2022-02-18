
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from carts.models import Cart, CartItem
from store.models import Product, Variation
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required



def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart    

def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) #get the product
    # if user is autehnticated
    if current_user.is_authenticated:
        product_varition = []
        if request.method == "POST":
            for item in request.POST:
                key = item            
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_varition.append(variation)
                except:
                    pass    

        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user)
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            ex_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_variation_list.append(list(existing_variation))
                id.append(item.id)
                # print(ex_variation_list)

            if product_varition in ex_variation_list:
                index = ex_variation_list.index(product_varition)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product=product, quantity=1, user=current_user)
                if len(product_varition) >0:
                    item.variations.clear()
                    item.variations.add(*product_varition)
                    item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity = 1,
                user=current_user,
            )
            if len(product_varition) >0:
                cart_item.variations.clear()
                for item in product_varition:
                    cart_item.variations.add(item)
                cart_item.save()      
        return redirect('cart')

    # if user is not authenticated    
    else:    
        product_varition = []
        if request.method == "POST":
            for item in request.POST:
                key = item            
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                    product_varition.append(variation)
                except:
                    pass    

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request)) # get the cart using the cart_id present in the session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart)
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            # existing variation -> database
            # current varition -> product_variation
            # item_id ->database
            ex_variation_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_variation_list.append(list(existing_variation))
                id.append(item.id)
                # print(ex_variation_list)

            if product_varition in ex_variation_list:
                index = ex_variation_list.index(product_varition)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += 1
                item.save()
            else:
                item = CartItem.objects.create(product=product, quantity=1, cart=cart)
                if len(product_varition) >0:
                    item.variations.clear()
                    item.variations.add(*product_varition)
                    item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity = 1,
                cart=cart,
            )
            if len(product_varition) >0:
                cart_item.variations.clear()
                for item in product_varition:
                    cart_item.variations.add(item)
                cart_item.save()      
        return redirect('cart')

def remove_cart(request, product_id, cart_item_id):    
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass        
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user=request.user, product=product, id=cart_item_id)
    else:    
        cart = Cart.objects.get(cart_id=_cart_id(request))    
        cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')



def cart(request, tax = 0, total=0, quantity=0, grand_total=0, cart_items=None):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user= request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2*total)/100
        grand_total = total+tax    
            
    except ObjectDoesNotExist:
        pass

    context = {
        "total":total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total
    }
    return render(request, 'store/cart.html', context)

    
@login_required(login_url='login')
def checkout(request, tax = 0, total=0, quantity=0, grand_total=0, cart_items=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2*total)/100
        grand_total = total+tax    
            
    except ObjectDoesNotExist:
        pass

    context = {
        "total":total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'grand_total':grand_total
    }
    return render(request, 'store/checkout.html', context)    
