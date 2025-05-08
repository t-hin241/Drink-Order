from django import forms
from .models import Review
import logging

logger = logging.getLogger('django')

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.Select(choices=[(i, f"{i} Star{'s' if i != 1 else ''}") for i in range(1, 6)], attrs={'required': True}),
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Write your review here (max 500 characters, optional)...'}),
        }
        labels = {
            'rating': 'Star Rating',
            'text': 'Review',
        }

    def clean(self):
        cleaned_data = super().clean()
        logger.debug(f"ReviewForm cleaned data: {cleaned_data}")
        return cleaned_data

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if not rating:
            logger.warning("Rating field is missing or empty")
            raise forms.ValidationError("Please select a star rating.")
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            logger.warning(f"Invalid rating value: {rating}")
            raise forms.ValidationError("Rating must be between 1 and 5 stars.")
        return rating

    def clean_text(self):
        text = self.cleaned_data.get('text', '')
        if len(text) > 500:
            logger.warning(f"Text exceeds 500 characters: {len(text)}")
            raise forms.ValidationError("Review must be 500 characters or less.")
        return text