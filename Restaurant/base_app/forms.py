from django import forms
from .models import BookTable, Feedback

class BookingForm(forms.ModelForm):
    class Meta:
        model = BookTable
        fields = ['Name', 'Phone_number', 'Email', 'Total_person', 'Booking_date', 'Booking_time']
        widgets = {
            'Name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'Phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'Email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'Total_person': forms.Select(choices=[(i, str(i)) for i in range(1, 11)], attrs={'class': 'form-control nice-select wide'}),
            'Booking_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'Booking_time': forms.Select(attrs={'class': 'form-control nice-select wide'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        booking_date = cleaned_data.get('Booking_date')
        booking_time = cleaned_data.get('Booking_time')
        
        if booking_date and booking_time:
            # Check how many bookings exist for this date and time
            existing_bookings = BookTable.objects.filter(
                Booking_date=booking_date,
                Booking_time=booking_time
            ).count()
            
            if existing_bookings >= BookTable.MAX_TABLES_PER_SLOT:
                raise forms.ValidationError(
                    f"Sorry, all tables are booked for {booking_time} on {booking_date}. Please choose a different time slot."
                )
        
        return cleaned_data

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['User_name', 'Description', 'Rating', 'Image']
        widgets = {
            'User_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'Description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Feedback', 'rows': 4}),
            'Rating': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Rating (1-5)', 'min': 1, 'max': 5}),
            'Image': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']
        
    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

from .models import Review
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
