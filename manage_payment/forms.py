from django import forms
from .models import *


class BuyPackageForm(forms.ModelForm):
    number_phone = forms.CharField(max_length=25)
    transaction = forms.CharField(required=False, max_length=25)
    subscription = forms.CharField(required=False, max_length=1000)

    class Meta:
        model = Subscription
        fields = ['package', ]

    # def clean_transaction(self):
    #    transaction = self.data['transaction']
    #    transaction = ''.join(transaction.split(' '))




    def clean_number_phone(self):

        phone = self.data['number_phone']

        phone = ''.join(phone.split(' '))

        if len(phone) == 9:
            pass
        else:
            self.add_error("number_phone", "number phone must contain 9 digits.")

        if phone.startswith('06') or phone.startswith('05'):
            pass

        else:
            # N° de téléphone invalide
            self.add_error("number_phone", "number phone must begin by 05 or 06")

        if phone.isdigit():
            pass
        else:
            self.add_error("number_phone", "number phone must contain only digits.")

        return phone
    
    
    def clean_subscription(self):

        id_subscription = self.data.get('subscription')

        if id_subscription:
            if Subscription.objects.filter(id=id_subscription).exists():
                pass
            else:
                self.add_error('subscription', 'There are errors!')



class CheckTransactionForm(forms.ModelForm):
    subscription = forms.IntegerField()
    
    class Meta:
        model = Transaction
        fields = ['uuid_transaction', ]
    
    def clean_uuid_transaction(self):

        id_transaction = self.data.get('uuid_transaction')

        if id_transaction:

            if Transaction.objects.filter(uuid_transaction=id_transaction).exists():
                pass

            else:
                self.add_error('uuid_transaction', "Cet ID de transaction n'existe pas.")
    

