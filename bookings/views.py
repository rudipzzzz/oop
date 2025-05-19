from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import Booking, Participant, Payment
from tours.models import Tour, TourDate
from .forms import BookingForm, ParticipantFormSet, PaymentForm


@login_required
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'bookings/booking_list.html', {
        'bookings': bookings,
    })


@login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'bookings/booking_detail.html', {
        'booking': booking,
    })


@login_required
def booking_create(request, tour_date_id):
    tour_date = get_object_or_404(TourDate, id=tour_date_id)
    tour = tour_date.tour
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        participant_formset = ParticipantFormSet(request.POST)
        payment_form = PaymentForm(request.POST)
        
        if form.is_valid() and participant_formset.is_valid() and payment_form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.tour = tour
            booking.tour_date = tour_date
            booking.total_price = tour_date.price * booking.number_of_people
            booking.save()
            
            participants = participant_formset.save(commit=False)
            for participant in participants:
                participant.booking = booking
                participant.save()
            
            payment = payment_form.save(commit=False)
            payment.booking = booking
            payment.amount = booking.total_price
            # In a real system, we would process payment here
            import uuid
            payment.transaction_id = str(uuid.uuid4())
            payment.save()
            
            # Update available spots
            tour_date.available_spots -= booking.number_of_people
            tour_date.save()
            
            messages.success(request, 'Booking created successfully!')
            return redirect('booking_detail', booking_id=booking.id)
    else:
        form = BookingForm(initial={'tour': tour, 'tour_date': tour_date})
        participant_formset = ParticipantFormSet()
        payment_form = PaymentForm()
    
    return render(request, 'bookings/booking_form.html', {
        'form': form,
        'participant_formset': participant_formset,
        'payment_form': payment_form,
        'tour': tour,
        'tour_date': tour_date,
    })


@login_required
def manage_bookings(request):
    if request.user.is_staff:
        bookings = Booking.objects.all()
    else:
        bookings = Booking.objects.filter(user=request.user)
    
    return render(request, 'bookings/manage_bookings.html', {
        'bookings': bookings,
    })


@login_required
def booking_edit(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user is allowed to edit this booking
    if not request.user.is_staff and request.user != booking.user:
        messages.error(request, 'You do not have permission to edit this booking.')
        return redirect('booking_list')
    
    if booking.status != 'pending':
        messages.error(request, 'This booking cannot be edited.')
        return redirect('booking_detail', booking_id=booking.id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        participant_formset = ParticipantFormSet(request.POST, instance=booking)
        
        if form.is_valid() and participant_formset.is_valid():
            booking = form.save()
            participant_formset.save()
            messages.success(request, 'Booking updated successfully!')
            return redirect('booking_detail', booking_id=booking.id)
    else:
        form = BookingForm(instance=booking)
        participant_formset = ParticipantFormSet(instance=booking)
    
    return render(request, 'bookings/booking_edit.html', {
        'form': form,
        'participant_formset': participant_formset,
        'booking': booking,
    })


@login_required
def booking_cancel(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user is allowed to cancel this booking
    if not request.user.is_staff and request.user != booking.user:
        messages.error(request, 'You do not have permission to cancel this booking.')
        return redirect('booking_list')
    
    if booking.status == 'completed':
        messages.error(request, 'This booking cannot be cancelled as it is already completed.')
        return redirect('booking_detail', booking_id=booking.id)
    
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        
        # Return spots to tour date
        tour_date = booking.tour_date
        tour_date.available_spots += booking.number_of_people
        tour_date.save()
        
        messages.success(request, 'Booking cancelled successfully.')
        return redirect('booking_list')
    
    return render(request, 'bookings/booking_cancel.html', {
        'booking': booking,
    })


@login_required
def booking_receipt(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user is allowed to view this receipt
    if not request.user.is_staff and request.user != booking.user:
        messages.error(request, 'You do not have permission to view this receipt.')
        return redirect('booking_list')
    
    return render(request, 'bookings/booking_receipt.html', {
        'booking': booking,
    })