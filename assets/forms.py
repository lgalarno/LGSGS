from django import forms

from .backend import ticker_name
from .models import Asset, Ticker


class TickerForm(forms.ModelForm):
    class Meta:
        model = Ticker
        fields = ['symbol', 'name']

        labels = {
            "symbol": "Ticker/Symbol",
        }
        widgets = {
            'name': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        symbol = cleaned_data.get('symbol').upper()
        qs = Ticker.objects.filter(symbol=symbol).first()
        if qs:
            self.add_error("symbol", "Symbol already exists")
        else:
            name = ticker_name(symbol)
            if name:
                self.cleaned_data['name'] = name
                self.cleaned_data['symbol'] = symbol
            else:
                self.add_error("symbol", "Symbol does not exist")
        return cleaned_data


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['description', 'quantity', 'price', 'margin', 'monitor']

        labels = {
            # "ticker": "Ticker/Symbol",
            "description": "Description",
            "quantity": "Quantity",
            "price": "Price",
            "margin": "Profit margin",
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class AssetUpdateForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['ticker', 'description', 'quantity', 'price', 'margin']

        labels = {
            "ticker": "Ticker/Symbol",
            "description": "Description",
            "quantity": "Quantity",
            "price": "Price",
            "margin": "Profit margin",
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
