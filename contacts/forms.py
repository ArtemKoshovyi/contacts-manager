from django import forms
from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ["first_name", "last_name", "phone_number", "email", "city", "status"]
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last name"}),
            "phone_number": forms.TextInput(attrs={"placeholder": "+48 ..."}),
            "email": forms.EmailInput(attrs={"placeholder": "name@example.com"}),
            "city": forms.TextInput(attrs={"placeholder": "City"}),
        }

    def clean_phone_number(self):
        phone = (self.cleaned_data.get("phone_number") or "").strip()

        if len(phone) < 9:
            raise forms.ValidationError("Numer telefonu jest za krótki")

        if not phone.replace("+", "").isdigit():
            raise forms.ValidationError("Niepoprawny format numeru telefonu")

        return phone


class ImportCsvForm(forms.Form):
    csv_file = forms.FileField()
