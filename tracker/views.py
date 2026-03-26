from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Transaction, Category
from .forms import TransactionForm


@login_required
def dashboard(request):
    # Get only THIS user's transactions, newest first
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    # Calculate totals — if no transactions yet, default to 0
    total_income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expense

    # Send data to the template
    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': balance,
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def add_transaction(request):
    if request.method == 'POST':
        # User submitted the form — validate and save
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)  # don't save to DB yet
            transaction.user = request.user        # attach logged-in user
            transaction.save()                     # now save to DB
            return redirect('dashboard')           # go back to dashboard
    else:
        # User just visited the page — show empty form
        form = TransactionForm()

    return render(request, 'tracker/add_transaction.html', {'form': form})


@login_required
def delete_transaction(request, pk):
    # pk = the ID of the transaction to delete
    # get_object_or_404 makes sure it exists AND belongs to this user
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    transaction.delete()
    return redirect('dashboard')