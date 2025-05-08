from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Drink, Category, Review
from django.db.models import Avg
from .forms import ReviewForm
import logging

logger = logging.getLogger('django')

class DrinkMenuView(View):
    def get(self, request):
        category_id = request.GET.get('category')
        drinks = Drink.objects.all().annotate(avg_rating=Avg('reviews__rating')).order_by('name')
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                drinks = Drink.objects.filter(category=category).annotate(avg_rating=Avg('reviews__rating')).order_by('name')
            except (Category.DoesNotExist, ValueError):
                logger.warning(f"Invalid category_id: {category_id}")
                drinks = Drink.objects.none()  # Show no drinks for invalid category
        else:
            drinks = Drink.objects.all().annotate(avg_rating=Avg('reviews__rating')).order_by('name')
        
        categories = Category.objects.all()
        return render(request, 'drinks/drink_menu.html', {
            'drinks': drinks,
            'categories': categories,
            'selected_category': category_id,
        })

class DrinkDetailView(View):
    def get(self, request, drink_id):
        drink = get_object_or_404(Drink, id=drink_id)
        review_form = ReviewForm() if request.user.is_authenticated and request.user.is_customer else None
        can_review = review_form is not None and not Review.objects.filter(drink=drink, customer=request.user).exists()
        return render(request, 'drinks/drink_detail.html', {
            'drink': drink,
            'review_form': review_form,
            'can_review': can_review,
        })

class ReviewCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_customer

    def post(self, request, drink_id):
        drink = get_object_or_404(Drink, id=drink_id)
        if Review.objects.filter(drink=drink, customer=request.user).exists():
            logger.warning(f"User {request.user.username} attempted to submit multiple reviews for drink {drink_id}")
            return redirect('drinks:drink_detail', drink_id=drink_id)
        
        form = ReviewForm(request.POST)
        if form.is_valid():
            try:
                review = form.save(commit=False)
                review.drink = drink
                review.customer = request.user
                review.save()
                return redirect('drinks:drink_detail', drink_id=drink_id)
            except Exception as e:
                logger.error(f"Error saving review for drink {drink_id}: {str(e)}")
        
        return render(request, 'drinks/drink_detail.html', {
            'drink': drink,
            'review_form': form,
            'can_review': True,
        })
class ReviewEditView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        return self.request.user.is_customer and review.customer == self.request.user

    def get(self, request, drink_id, review_id):
        review = get_object_or_404(Review, id=review_id, drink_id=drink_id)
        form = ReviewForm(instance=review)
        return render(request, 'drinks/drink_detail.html', {
            'drink': review.drink,
            'review_form': form,
            'can_review': False,
            'editing_review': review,
        })

    def post(self, request, drink_id, review_id):
        review = get_object_or_404(Review, id=review_id, drink_id=drink_id)
        logger.debug(f"Processing review edit for review {review_id} by user {request.user.username}")
        form = ReviewForm(request.POST, instance=review)
        logger.debug(f"Edit form data received: {request.POST}")
        if form.is_valid():
            try:
                form.save()
                logger.info(f"Review {review_id} updated successfully by user {request.user.username}")
                #messages.success(request, "Your review has been updated successfully!")
                return redirect('drinks:drink_detail', drink_id=drink_id)
            except Exception as e:
                logger.error(f"Failed to update review {review_id} by user {request.user.username}: {str(e)}")
                #messages.error(request, f"Failed to update review: {str(e)}")
        else:
            logger.warning(f"Invalid edit form for review {review_id} by user {request.user.username}: {form.errors.as_text()}")
            #messages.error(request, "Please correct the errors in the review form.")
        
        return render(request, 'drinks/drink_detail.html', {
            'drink': review.drink,
            'review_form': form,
            'can_review': False,
            'editing_review': review,
        })

class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        review = get_object_or_404(Review, id=self.kwargs['review_id'])
        return self.request.user.is_customer and review.customer == self.request.user

    def post(self, request, drink_id, review_id):
        review = get_object_or_404(Review, id=review_id, drink_id=drink_id)
        logger.debug(f"Processing review deletion for review {review_id} by user {request.user.username}")
        try:
            review.delete()
            logger.info(f"Review {review_id} deleted successfully by user {request.user.username}")
            #messages.success(request, "Your review has been deleted successfully!")
        except Exception as e:
            logger.error(f"Failed to delete review {review_id} by user {request.user.username}: {str(e)}")
            #messages.error(request, f"Failed to delete review: {str(e)}")
        return redirect('drinks:drink_detail', drink_id=drink_id)    