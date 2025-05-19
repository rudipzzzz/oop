from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Destination, Region
from .forms import DestinationForm, DestinationImageFormSet


def destination_list(request):
    destinations = Destination.objects.filter(is_active=True)
    featured = Destination.objects.filter(is_featured=True, is_active=True)[:3]
    regions = Region.objects.all()
    
    return render(request, 'destinations/destination_list.html', {
        'destinations': destinations,
        'featured': featured,
        'regions': regions,
    })


def destination_detail(request, slug):
    destination = get_object_or_404(Destination, slug=slug, is_active=True)
    related = Destination.objects.filter(region=destination.region).exclude(id=destination.id)[:3]
    
    return render(request, 'destinations/destination_detail.html', {
        'destination': destination,
        'related': related,
    })


def region_destinations(request, region_id):
    region = get_object_or_404(Region, id=region_id)
    destinations = Destination.objects.filter(region=region, is_active=True)
    
    return render(request, 'destinations/region_destinations.html', {
        'region': region,
        'destinations': destinations,
    })


@login_required
def manage_destinations(request):
    destinations = Destination.objects.all()
    return render(request, 'destinations/manage_destinations.html', {
        'destinations': destinations,
    })


@login_required
def destination_create(request):
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES)
        formset = DestinationImageFormSet(request.POST, request.FILES, instance=Destination())
        
        if form.is_valid() and formset.is_valid():
            destination = form.save()
            formset.instance = destination
            formset.save()
            messages.success(request, 'Destination created successfully!')
            return redirect('manage_destinations')
    else:
        form = DestinationForm()
        formset = DestinationImageFormSet(instance=Destination())
    
    return render(request, 'destinations/destination_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Create Destination'
    })


@login_required
def destination_edit(request, slug):
    destination = get_object_or_404(Destination, slug=slug)
    
    if request.method == 'POST':
        form = DestinationForm(request.POST, request.FILES, instance=destination)
        formset = DestinationImageFormSet(request.POST, request.FILES, instance=destination)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Destination updated successfully!')
            return redirect('manage_destinations')
    else:
        form = DestinationForm(instance=destination)
        formset = DestinationImageFormSet(instance=destination)
    
    return render(request, 'destinations/destination_form.html', {
        'form': form,
        'formset': formset,
        'destination': destination,
        'title': 'Edit Destination'
    })


@login_required
def destination_delete(request, slug):
    destination = get_object_or_404(Destination, slug=slug)
    
    if request.method == 'POST':
        destination.delete()
        messages.success(request, 'Destination deleted successfully!')
        return redirect('manage_destinations')
    
    return render(request, 'destinations/destination_confirm_delete.html', {
        'destination': destination,
    })