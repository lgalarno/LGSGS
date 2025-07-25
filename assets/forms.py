from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column

from .backend import ticker_name
from .models import Asset  #, Ticker, Trader

#
# class TraderForm(forms.ModelForm):
#     class Meta:
#         model = Trader
#         fields = ['name', 'logo', 'url', 'fees_buy', 'fees_sell']
#
#         labels = {
#             "fees_buy": "Fees when buying",
#             "fees_sell": "Fees when selling",
#         }
#
#     def clean(self):
#         cleaned_data = super().clean()
#         name = cleaned_data.get('name')
#         qs = Trader.objects.filter(name=name).first()
#         if qs:
#             self.add_error("name", "Trader already exists")
#         return cleaned_data
#
#
# class TickerForm(forms.ModelForm):
#     class Meta:
#         model = Ticker
#         fields = ['symbol', 'name', 'type']
#
#         labels = {
#             "symbol": "Ticker/Symbol",
#         }
#         widgets = {
#             'name': forms.HiddenInput(),
#         }
#
#     def clean(self):
#         cleaned_data = super().clean()
#         symbol = cleaned_data.get('symbol').upper()
#         type = cleaned_data.get('type')
#         qs = Ticker.objects.filter(symbol=symbol).first()
#         if qs:
#             self.add_error("symbol", "Symbol already exists")
#         else:
#             name = ticker_name(symbol, type)
#             if name:
#                 self.cleaned_data['name'] = name
#                 self.cleaned_data['symbol'] = symbol
#             else:
#                 self.add_error("symbol", "Symbol does not exist or please, be more specific")
#         return cleaned_data


class AssetForm(forms.ModelForm):

    class Meta:
        model = Asset
        fields = ['date', 'description', 'quantity', 'price', 'margin', 'monitor']

        labels = {
            "date": "Date d'achat",
            "description": "Description",
            "quantity": "Quantité",
            "price": "Prix",
            "margin": "Marge de profit",
            'monitor': "Suivre"
        }
        widgets = {
            'date': forms.DateInput(attrs={"type": "date"}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(AssetForm, self).__init__(*args, **kwargs)
        # format the form using crispy_forms FormHelper
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            'description',
            Row(
                Column('date', css_class='form-group col-md-3 mb-0'),
                Column('quantity', css_class='form-group col-md-3 mb-0'),
                Column('price', css_class='form-group col-md-3 mb-0'),
                Column('margin', css_class='form-group col-md-3 mb-0')
            ),
            'monitor'
        )


class AssetUpdateForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['date', 'description', 'quantity',
                  'price', 'fees_per_unit', 'margin', 'monitor', 'staking', 'emailed']

        labels = {
            # "ticker": "Ticker/Symbol",
            "quantity": "Quantité",
            'price': 'prix',
            'fees_per_unit': 'frais par unité',
            "date": "Date d'achat",
            "margin": "Marge de profit",
            'monitor': "Suivre",
            'emailed':  'email envoyé'
        }
        widgets = {
            'date': forms.DateInput(attrs={"type": "date"}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        is_crypto = kwargs.pop('is_crypto', None)
        super(AssetUpdateForm, self).__init__(*args, **kwargs)
        # if not is_crypto:
        #     self.fields.pop('staking')
        # format the form using crispy_forms FormHelper
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                # Column('ticker', css_class='form-group col-md-4 mb-0'),
                # Column('trader', css_class='form-group col-md-4 mb-0'),
                Column('date', css_class='form-group col-md-4 mb-0'),
            ),
            'description',
            Row(
                Column('quantity', css_class='form-group col-md-3 mb-0'),
                Column('price', css_class='form-group col-md-3 mb-0'),
                Column('fees_per_unit', css_class='form-group col-md-3 mb-0'),
                Column('margin', css_class='form-group col-md-3 mb-0')
            ),
            Row(
                Column('monitor', css_class='form-group col-md-3 mb-0'),
                Column('staking', css_class='form-group col-md-3 mb-0'),
                Column('emailed', css_class='form-group col-md-3 mb-0')
            ),
        )
        # remove staking filed if is not crypto
        if not is_crypto:
            self.helper.layout.fields[3].pop(1)
