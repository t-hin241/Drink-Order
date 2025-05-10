from django.db import models
from users.models import CustomUser
from django.db.models import Sum
from transformers import pipeline
import logging

logger = logging.getLogger('django')
# Singleton for sentiment analysis model
class SentimentClassifier:
    _instance = None
    _classifier = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SentimentClassifier, cls).__new__(cls)
            try:
                cls._classifier = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')
            except Exception as e:
                logger.error(f"Failed to load sentiment classifier: {str(e)}")
                cls._classifier = None
        return cls._instance

    def classify(self, text):
        if self._classifier is None:
            return 'neutral'  # Fallback if model fails to load
        try:
            result = self._classifier(text)[0]
            label = result['label'].lower()
            score = result['score']
            # Map model output to sentiment (adjust thresholds as needed)
            if label == 'positive' and score > 0.7:
                return 'positive'
            elif label == 'negative' and score > 0.7:
                return 'negative'
            else:
                return 'neutral'
        except Exception as e:
            logger.error(f"Sentiment classification error: {str(e)}")
            return 'neutral'

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Drink (models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    image = models.ImageField(upload_to='drinks/', blank=True, null=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    @classmethod
    def get_top_drinks(cls, limit=5):
        """
        Returns the top most ordered drinks, ranked by total quantity ordered.
        Returns a list of dicts with 'drink', 'total_quantity', and 'rank'.
        """
        try:
            top_drinks = cls.objects.filter(is_available=True).annotate(
                total_quantity=Sum('orderitem__quantity')
            ).exclude(total_quantity__isnull=True).order_by('-total_quantity')[:limit]
            
            # Assign ranks (1 to limit)
            ranked_drinks = [
                {'drink': drink, 'total_quantity': drink.total_quantity, 'rank': index + 1}
                for index, drink in enumerate(top_drinks)
            ]
            logger.info(f"Retrieved top ordered drinks: {[d['drink'].name for d in ranked_drinks]}")
            return ranked_drinks
        except Exception as e:
            logger.error(f"Error retrieving top ordered drinks: {str(e)}")
            return []
class Review(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'Positive'),
        ('negative', 'Negative'),
        ('neutral', 'Neutral'),
    ]    
    drink = models.ForeignKey(Drink, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    text = models.TextField(max_length=500, blank=True)
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES, default='neutral')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('drink', 'customer')
        ordering = ['-created_on']

    def save(self, *args, **kwargs):
        # Check if text has changed or this is a new review
        original_text = None
        if self.pk:  # Existing review
            try:
                original_text = Review.objects.get(pk=self.pk).text
            except Review.DoesNotExist:
                pass
        # Classify sentiment if new review or text has changed
        if original_text is None or original_text != self.text:
            classifier = SentimentClassifier()
            new_sentiment = classifier.classify(self.text)
            if self.sentiment != new_sentiment:
                self.sentiment = new_sentiment
                logger.info(f"Sentiment updated for review {self.pk or 'new'} to {self.sentiment}")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.username}'s review of {self.drink.name} ({self.rating} stars)"