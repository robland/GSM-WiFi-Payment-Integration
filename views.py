from django.shortcuts import redirect, render, HttpResponse
from django.http import JsonResponse

from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from .models import *

from .forms import *
from django.contrib.auth.decorators import login_required

import os
from gsm.aio_gsm import *



def return_response(subscription, package):
    return JsonResponse(
                        data = {
                                "success": False,
                                "message": {
                                    'id_subscription': subscription.pk,
                                    'id_package': package.pk,
                                     'id_transaction': "Transaction incorrecte!"
                                },
                                "errors": ['ID de transaction invalide!',]
                                }, encoder=DjangoJSONEncoder, safe=False)

def new_subscription(request):
    form = BuyPackageForm()
    if request.POST:
        form = BuyPackageForm(request.POST)

        if form.is_valid():
    
            cd = form.cleaned_data
            number_phone = cd['number_phone']
            # id_subscription = cd['subscription']
            # transaction = cd["transaction"]
            package = cd["package"]
            profile, created = Profile.objects.get_or_create(phone_number=number_phone)
            
            if Package.objects.filter(pk=package.pk).exists():
                subscription = Subscription.objects.create(package=package, profile=profile)
                request.session.set('subscription', subscription)
                return render(request, 'manage_payment/confirmation_step.html', locals())
            
            else:
                return render(request, 'manage_payment/buy_forfait.html')

                """
                return JsonResponse(
                    data = {
                            "success": False,
                            "message": {
                                'id_subscription': "",
                                    'id_package': "Ce package n'existe pas!"
                            },
                            'errors': [[k, v] for k, v in form.errors.items()]
                            }, encoder=DjangoJSONEncoder, safe=False)
                """
        else:
            return render(request, 'manage_payment/buy_forfait.html', locals())
                    
    else:
        return render(request, 'manage_payment/buy_forfait.html', locals())

def new_func(request):
    return render(request, 'manage_payment/buy_forfait.html', context=locals())


def check_transaction(request):
    
    form = CheckTransactionForm(request.POST)
    subscription = Subscription.objects.get(pk=form.data['subscription'])
    if request.POST:
        
        if form.is_valid():
            
            cd = form.cleaned_data
            uuid_transaction = cd['uuid_transaction']
            id_subscription = cd['subscription']

            transaction = Transaction.objects.get(uuid_transaction=uuid_transaction)

             
            subs = Subscription.objects.get(pk=id_subscription)

            if subs.in_processing:
                form.add_error('uuid_transaction', 'La transaction est en cours de traitement.')
                return render(request, 'manage_payment/confirmation_step.html', locals())
            else:
                subs.in_processing = True
                subs.save()
            try:
                subs.transaction = transaction
                # creer le compte ici ou laisser les futures identifiants du compte
                message_to_send = f"username:{subs.profile.phone_number}\npassword:{transaction.uuid_transaction}"
                message_to_send = TokenMessage.objects.create(message=message_to_send)
                subs.save()
            except:
                form.add_error('uuid_transaction', 'ID de transaction invalide.')
                return render(request, 'manage_payment/confirmation_step.html', locals())
            else:
                subs.is_terminated = True
                subs.in_processing = False
                subs.save()
                return redirect('login')
        else:
            return render(request, 'manage_payment/confirmation_step.html', locals())
    else:
        return render(request, 'manage_payment/confirmation_step.html', locals())


def sim800l_get_transactions(request, prefix):
    # all_objects = [*Subscription.objects.all(), *Profile.objects.all()]
    obj = Subscription.objects.filter(in_processing=False, profile__phone_number__startswith=prefix, is_traited=False).first()
    list_data = []
    if obj:
        obj.in_processing = True
        obj.save()
        list_data.append(obj)

    return JsonResponse(data=serialize('json', list_data, cls=DjangoJSONEncoder, fields=["profile", "package"], use_natural_foreign_keys=True, use_natural_primary_keys=True), safe=False)


def sim800l_update_transactions(request, pk):
    if Subscription.objects.filter(pk=pk, in_processing=True).exists():
        obj = Subscription.objects.get(pk=pk)
        obj.is_traited = True
        obj.in_processing = False
        obj.save()
        return HttpResponse("OK")
    else:
        return HttpResponse('ERROR')

@login_required
def sim800l_get_messages(requet):
    messages = TokenMessage.objects.get(is_sent=False)
    return JsonResponse(data=serialize('json', messages, cls=DjangoJSONEncoder, use_natural_foreign_keys=True, use_natural_primary_keys=True), safe=False)

def sim800l_update_message(request, pk):
    message = TokenMessage.objects.get(pk=pk)
    message.is_sent = True
    message.save()
    return HttpResponse('OK')

def get_subscription_state(request):
    
    pk = request.GET.get("id_subscription")
    obj = Subscription.objects.get(pk=pk)

    if obj.is_traited == True:
        return JsonResponse(
            data={'state':True},
            encoder=DjangoJSONEncoder, 
            safe=False 
            )

    else:
        return JsonResponse(
            data={'state':False}, 
            encoder=DjangoJSONEncoder, 
            safe=False
            )


def update_subscription_state(request):
    pass


def add_transaction(request, date, id_trans, op, amount):
    
    if Transaction.objects.filter(uuid_transaction=id_trans).exists():
        return HttpResponse('ERROR')
    else:    
        transaction = Transaction.objects.create(amount=float(amount), date=date, uuid_transaction=int(id_trans))
        return HttpResponse("OK")


def get_first_validated_transaction(request):
    list_data = []
    transaction = Subscription.objects.filter(is_confirmed=True).first()

    # print(transaction)
    if not transaction:
        list_data = []
    
    else:
        transaction.in_processing = True
        transaction.save()
        list_data.append(transaction)
    return JsonResponse(data=serialize('json', list_data, cls=DjangoJSONEncoder, fields=["profile", "package"], use_natural_foreign_keys=True, use_natural_primary_keys=True), safe=False)


def change_state_of_transaction(request, pk):
    transaction = Subscription.objects.get(pk=pk)

    if transaction.in_processing == True:

        if request.GET.get('state') == 'terminated':
            transaction.is_terminated = True
        
        if request.GET.get('state') == 'traited':
            transaction.is_terminated = True

        if request.GET.get('state') == 'confirmed':
            transaction.is_terminated = True
        
        transaction.in_processing = False

        transaction.save()

        return HttpResponse('OK')
    else:
        return HttpResponse('ERROR')


def captive_portal_login(request):
    return render(request, 'registration/index.html', {})