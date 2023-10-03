from django.shortcuts import render
from departments.models import Department
from django.urls import reverse
from .forms import paymentForm
from .models import Transaction
from django.contrib import messages
import uuid
# Create your views here.

def mainPage(request):
    return render(request, 'main/home.html',{
        'depts': Department.objects.all()
    })


from django.shortcuts import redirect

def payment(request):
    form = paymentForm(request.POST or None)
    print(request.method)
    if request.method == 'POST':
        if form.is_valid():
            txn = form.save()
            uid = str(uuid.uuid4())
            request.session[uid] = txn.txn_id
            return redirect(reverse('Main:success', kwargs={'id': uid}))
        else:
            form.add_error(None, 'Invalid Credentials')
            return render(request, 'transaction/payment.html', {
                'form': form
            })
    return render(request, 'transaction/payment.html', {
        'form': form
    })

def success(request, id):
    try:
        txn_id = request.session.get(id, None)
        txn = Transaction.objects.get(txn_id=txn_id)
        if txn.paid_by == request.user:
            return render(request, 'transaction/success.html', {
                'txn': txn,
                'error': False
            })
        else:
            return render(request, 'transaction/success.html', {
                'error': True,
                'message': 'You are not authorized to view this transaction'
            })
    except Transaction.DoesNotExist:
        messages.error(request, 'Invalid Transaction ID')
        return redirect(reverse('Main:payment'))