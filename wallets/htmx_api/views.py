from django.shortcuts import render, HttpResponse

from accounts.forms import WalletForm


def wallet_create(request):
    form = WalletForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return HttpResponse(status=204, headers={'HX-Trigger': 'tickerListChanged'})
    context = {
        "title": "new-wallet",
        'form_wallet': form,
    }
    return render(request, 'assets/partials/ticker-form.html', context)
