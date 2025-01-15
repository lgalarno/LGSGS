from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column

from .backend import ticker_name
from .models import Asset, Ticker, Trader


class TraderForm(forms.ModelForm):
    class Meta:
        model = Trader
        fields = ['name', 'logo', 'url', 'fees_buy', 'fees_sell']

        labels = {
            "fees_buy": "Fees when buying",
            "fees_sell": "Fees when selling",
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        qs = Trader.objects.filter(name=name).first()
        if qs:
            self.add_error("name", "Trader already exists")
        return cleaned_data


class TickerForm(forms.ModelForm):
    class Meta:
        model = Ticker
        fields = ['symbol', 'name', 'type']

        labels = {
            "symbol": "Ticker/Symbol",
        }
        widgets = {
            'name': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        symbol = cleaned_data.get('symbol').upper()
        type = cleaned_data.get('type')
        qs = Ticker.objects.filter(symbol=symbol).first()
        if qs:
            self.add_error("symbol", "Symbol already exists")
        else:
            name = ticker_name(symbol, type)
            if name:
                self.cleaned_data['name'] = name
                self.cleaned_data['symbol'] = symbol
            else:
                self.add_error("symbol", "Symbol does not exist")
        return cleaned_data


class AssetForm(forms.ModelForm):

    class Meta:
        model = Asset
        fields = ['date', 'description', 'quantity', 'price', 'margin', 'monitor']

        labels = {
            "date": "Date purchased",
            "description": "Description",
            "quantity": "Quantity",
            "price": "Price",
            "margin": "Profit margin",
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
        fields = ['ticker', 'trader', 'date', 'description', 'quantity', 'price', 'margin', 'monitor', 'staking', 'emailed']

        labels = {
            "ticker": "Ticker/Symbol",
            "date": "Date purchased",
            "margin": "Profit margin",
        }
        widgets = {
            'date': forms.DateInput(attrs={"type": "date"}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        is_crypto = kwargs.pop('is_crypto', None)
        print(f'is_crypto  {is_crypto}')
        super(AssetUpdateForm, self).__init__(*args, **kwargs)
        # if not is_crypto:
        #     self.fields.pop('staking')
        # format the form using crispy_forms FormHelper
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Row(
                Column('ticker', css_class='form-group col-md-6 mb-0'),
                Column('trader', css_class='form-group col-md-6 mb-0')
            ),
            'description',
            Row(
                Column('date', css_class='form-group col-md-3 mb-0'),
                Column('quantity', css_class='form-group col-md-3 mb-0'),
                Column('price', css_class='form-group col-md-3 mb-0'),
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
