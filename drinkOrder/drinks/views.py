from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Drink, Category, Review
from django.db.models import Avg, Q
from .forms import ReviewForm
import logging

logger = logging.getLogger('django')

class DrinkMenuView(View):
    '''
    Common drink menu view for customer
    Content display:
    - List of drinks with avarage rating from reviews
    - Search feature
    - Filter drink category
    '''
    def get(self, request):
        search_query = request.GET.get('search', '').strip()
        category_id = request.GET.get('category')
        top_drinks = [top['drink'] for top in Drink.get_top_drinks(limit=5)]
    
        # search feature
        if search_query:
            drinks = Drink.objects.filter(name__icontains=search_query)
            logger.debug(f"After search query '{search_query}': {drinks.count()} drinks")
            if not drinks.exists():
                logger.info(f"No drinks found for search query: '{search_query}'")
        else:
            drinks = Drink.objects.all()
        # category filter drink
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                drinks = drinks.filter(category=category)
            except (Category.DoesNotExist, ValueError):
                logger.warning(f"Invalid category_id: {category_id}")
                drinks = Drink.objects.none()  # Show no drinks for invalid category
        
        categories = Category.objects.all()
        return render(request, 'drinks/drink_menu.html', {
            'drinks': drinks.annotate(avg_rating=Avg('reviews__rating')).order_by('name'),
            'categories': categories,
            'selected_category': category_id,
            'search_query': search_query,
            'top_drinks': top_drinks,
        })
class TopDrinksView(View):
    def get(self, request):
        top_drinks = Drink.get_top_drinks(limit=5)
        return render(request, 'drinks/top_drinks.html', {
            'top_drinks': top_drinks,
        })    
class BartenderMenuView(LoginRequiredMixin, UserPassesTestMixin, View):
    '''
    Bartender menu view for manage available drink that allow customer to order
    Content display: the same as DrinkMenuView with addittion feature to allow bartender set status for drink available or not
    '''
    def test_func(self):
        return self.request.user.is_bartender

    def get(self, request):
        search_query = request.GET.get('search', '').strip()
        category_id = request.GET.get('category')
        # search feature
        if search_query:
            drinks = Drink.objects.filter(name__icontains=search_query)
            logger.debug(f"After search query '{search_query}': {drinks.count()} drinks")
            if not drinks.exists():
                logger.info(f"No drinks found for search query: '{search_query}'")
        else:
            drinks = Drink.objects.all()

        #category filter drink        
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                drinks = drinks.filter(category=category)
            except (Category.DoesNotExist, ValueError):
                logger.warning(f"Invalid category_id: {category_id}")
                drinks = Drink.objects.none()
        
        for drink in drinks:
            logger.debug(f"Bartender view - Drink {drink.name}: is_available={drink.is_available}, avg_rating={drink.avg_rating}")
        
        categories = Category.objects.all()
        return render(request, 'drinks/bartender_menu.html', {
            'drinks': drinks.annotate(avg_rating=Avg('reviews__rating')).order_by('name'),
            'categories': categories,
            'selected_category': category_id,
            'search_query': search_query,
        })

    def post(self, request):
        drink_id = request.POST.get('drink_id')
        action = request.POST.get('action')
        drink = get_object_or_404(Drink, id=drink_id)
        
        logger.debug(f"Processing availability toggle for drink {drink_id} by user {request.user.username}: action={action}")
        
        try:
            if action == 'make_available':
                drink.is_available = True
                #messages.success(request, f"{drink.name} is now available.")
            elif action == 'make_unavailable':
                drink.is_available = False
                #messages.success(request, f"{drink.name} is now unavailable.")
            else:
                logger.warning(f"Invalid action for drink {drink_id}: {action}")
                #messages.error(request, "Invalid action.")
                return redirect('drinks:bartender_menu')
            
            drink.save()
            logger.info(f"Drink {drink.name} availability set to {drink.is_available} by user {request.user.username}")
        except Exception as e:
            logger.error(f"Failed to update availability for drink {drink_id}: {str(e)}")
            #messages.error(request, f"Failed to update {drink.name}: {str(e)}")
        
        return redirect('drinks:bartender_menu')
    
class DrinkDetailView(View):
    def get(self, request, drink_id):
        drink = get_object_or_404(Drink, id=drink_id)
        reviews = Review.objects.all()
        sentiment = request.GET.get('sentiment')
        if sentiment:
            try:
                reviews = reviews.filter(sentiment=sentiment)
            except (Review.DoesNotExist, ValueError):
                logger.warning(f"Invalid sentiment: {sentiment}")
                reviews = Review.objects.none()                
        review_form = ReviewForm() if request.user.is_authenticated and request.user.is_customer else None
        can_review = review_form is not None and not Review.objects.filter(drink=drink, customer=request.user).exists()
        return render(request, 'drinks/drink_detail.html', {
            'drink': drink,
            'reviews': reviews,
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