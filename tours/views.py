from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Tour, TourCategory, TourDate
from .forms import TourForm, TourDateForm, TourDateFormSet


def tour_list(request):
    tours = Tour.objects.filter(is_active=True)
    featured = Tour.objects.filter(is_featured=True, is_active=True)[:3]
    categories = TourCategory.objects.all()
    
    return render(request, 'tours/tour_list.html', {
        'tours': tours,
        'featured': featured,
        'categories': categories,
    })


def tour_detail(request, slug):
    tour = get_object_or_404(Tour, slug=slug, is_active=True)
    dates = TourDate.objects.filter(tour=tour, available_spots__gt=0).order_by('start_date')
    related = Tour.objects.filter(category=tour.category).exclude(id=tour.id)[:3]
    
    return render(request, 'tours/tour_detail.html', {
        'tour': tour,
        'dates': dates,
        'related': related,
    })


def category_tours(request, category_id):
    category = get_object_or_404(TourCategory, id=category_id)
    tours = Tour.objects.filter(category=category, is_active=True)
    
    return render(request, 'tours/category_tours.html', {
        'category': category,
        'tours': tours,
    })


@login_required
def manage_tours(request):
    tours = Tour.objects.all()
    return render(request, 'tours/manage_tours.html', {
        'tours': tours,
    })


@login_required
def tour_create(request):
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES)
        if form.is_valid():
            tour = form.save()
            messages.success(request, 'Tour created successfully!')
            return redirect('manage_tours')
    else:
        form = TourForm()
    
    return render(request, 'tours/tour_form.html', {
        'form': form,
        'title': 'Create Tour'
    })


@login_required
def tour_edit(request, slug):
    tour = get_object_or_404(Tour, slug=slug)
    
    if request.method == 'POST':
        form = TourForm(request.POST, request.FILES, instance=tour)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tour updated successfully!')
            return redirect('manage_tours')
    else:
        form = TourForm(instance=tour)
    
    return render(request, 'tours/tour_form.html', {
        'form': form,
        'tour': tour,
        'title': 'Edit Tour'
    })


@login_required
def tour_delete(request, slug):
    tour = get_object_or_404(Tour, slug=slug)
    
    if request.method == 'POST':
        tour.delete()
        messages.success(request, 'Tour deleted successfully!')
        return redirect('manage_tours')
    
    return render(request, 'tours/tour_confirm_delete.html', {
        'tour': tour,
    })


@login_required
def manage_tour_dates(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    
    if request.method == 'POST':
        formset = TourDateFormSet(request.POST, instance=tour)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Tour dates updated successfully!')
            return redirect('manage_tours')
    else:
        formset = TourDateFormSet(instance=tour)
    
    return render(request, 'tours/tour_dates_form.html', {
        'tour': tour,
        'formset': formset,
    })