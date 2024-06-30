from django import forms
from django.utils import timezone

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Hidden, Field

from .models import Wallet, Transfer, Transaction


class WalletForm(forms.ModelForm):
    class Meta:
        model = Wallet
        fields = ['name']


class TransferForm(forms.ModelForm):
    class Meta:
        model = Transfer
        fields = ['type', 'amount', 'date', 'wallet']

        labels = {
            "date": "Date transferred",
        }
        widgets = {
            'date': forms.DateInput(attrs={"type": "date"}),
            'wallet': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].initial = timezone.now()
        # self.fields['wallet']. = timezone.now()

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data['amount']
        if cleaned_data.get('type') == 'withdrawal':
            w = cleaned_data['wallet']
            if amount > w.balance:
                self.add_error("amount", "Not enough money in the wallet to withdraw this amount.")
            else:
                cleaned_data['amount'] = -amount
        return cleaned_data


class TransactionForm(forms.ModelForm):

    class Meta:
        model = Transaction
        fields = ['date', 'description', 'quantity', 'price', 'currency', 'change', 'fees', 'wallet']

        labels = {
            "date": "Date",
            "description": "Description",
            "quantity": "Quantity",
            "price": "Price",
            "fees": "Fees (in crypto or $)",
        }
        widgets = {
            'date': forms.DateInput(attrs={"type": "date"}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'wallet': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        max_quantity = kwargs.pop('max_quantity', None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        # self.fields['date'].initial = timezone.now()
        if max_quantity:
            self.fields['quantity'].widget.attrs.update(
                {
                 'max': max_quantity},
            )
            self.fields['quantity'].initial = max_quantity
        # format the form using crispy_forms FormHelper
        self.helper = FormHelper()
        self.helper.add_input(Hidden("hidden", "hide-me"))
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'description',
            Row(
                Column('quantity', css_class='form-group col-md-4 mb-0'),
                Column('price', css_class='form-group col-md-4 mb-0'),
                Column('currency', css_class='form-group col-md-4 mb-0')
            ),
            Row(
                Column('change', css_class='form-group col-md-4 mb-0'),
                Column('fees', css_class='form-group col-md-4 mb-0'),
                Column('date', css_class='form-group col-md-4 mb-0'),
            ),
            Field('wallet', type="hidden"),
        )
