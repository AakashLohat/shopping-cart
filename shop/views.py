from django.shortcuts import render
from django.http import HttpResponse
from .models import producty, Contact,Order,orderupdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from paytm import checksum
MERCHANT_KEY = 'KgIMFQyovG8n%uxw'


# Create your views here.
def index(request):

    allprods = []
    catprods = producty.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = producty.objects.filter(category=cat)
        n = len(prod)
        nslides = n // 4 + ceil((n / 4) - (n // 4))
        allprods.append([prod, range(1, nslides), nslides])

    pagee = {'allprods':allprods}
    return render(request, 'shop/index.html', pagee)
def searchmatch(query,item):
    if query in item.product_name.lower():
        return True
    else:
        return False
def search(request):
    query = request.GET.get('search')
    allprods = []
    catprods = producty.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = producty.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchmatch(query, item)]
        n = len(prod)
        nslides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod)!= 0:
           allprods.append([prod, range(1, nslides), nslides])

    pagee = {'allprods': allprods,'msg':''}
    if len(allprods) == 0:
        pagee = {'msg':'please make sure that search items is relevent'}
    return render(request, 'shop/search.html', pagee)



def about(request):
    return render(request,'shop/about.html')
def  contact(request):
    if request.method=="POST":
        name=request.POST.get('name','default')
        email=request.POST.get('email','default')
        phone=request.POST.get('phone','default')
        desc=request.POST.get('desc','default')
        cont = Contact(name=name, email=email, phone=phone, desc=desc)
        cont.save()
        thanks = True
        return render(request, 'shop/contact.html',{'thanks':thanks})


    return render(request,'shop/contact.html')
def tracker(request):
    if request.method == "POST":
        order_id = request.POST.get('order_id', 'default')
        email = request.POST.get('email', 'default')

        print(order_id,email)
        try:
            order = Order.objects.filter(order_id=order_id,email=email)
            if len(order)>0:
                update = orderupdate.objects.filter(order_id=order_id)
                updates = []
                for item in update:
                    updates.append({'text':item.update_desc,'time':item.timestamp})
                    response = json.dumps({'status':'success','update':updates,'itemjason':order[0].items_json},default=str)
                return HttpResponse(response)
            else:
                return HttpResponse({'status':'no items'})
        except Exception as e:
                return HttpResponse({'status':'error'})

    return render(request,'shop/tracker.html')



def prodview(request,myid):
    prod = producty.objects.filter(id=myid)
    print(prod)
    return render(request,'shop/prodview.html',{'product':prod[0]})
def checkout(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsjson','default')
        name = request.POST.get('name', 'default')
        amount = request.POST.get('amount', 'default')
        email = request.POST.get('email', 'default')
        phone = request.POST.get('phone', 'default')
        address = request.POST.get('address1', 'default') + " " + request.POST.get('address2', 'default')
        city = request.POST.get('city', 'default')
        state = request.POST.get('state', 'default')
        zip_code = request.POST.get('zip_code', 'default')
        ord = Order(items_json=items_json,name=name,amount=amount, email=email, phone=phone, address=address,city=city,state=state,zip_code=zip_code)
        ord.save()
        update = orderupdate(order_id=ord.order_id,update_desc='thank you for shoping with us your order has been placed')
        update.save()
        thank = True
        id = ord.order_id
        #return render(request,'shop/checkout.html',{'thank':thank,'id':id})
        param_dict = {

            'MID': 'iJQNLu50006240261290',
            'ORDER_ID': str(ord.order_id),
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:8000/shop/handlerequest/'


        }
        param_dict['CHECKSUMHASH'] = checksum.generate_checksum(param_dict, MERCHANT_KEY)
        return render(request,'shop/paytm.html',{'param_dict':param_dict})
    return render(request,'shop/checkout.html')
@csrf_exempt
def handlerequest(request):
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = checksum
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request,'shop/paymentstatus.html', {'response': response_dict})