import csv
import io
import requests
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework import generics, serializers
from .forms import ContactForm, ImportCsvForm
from .models import Contact, ContactStatusChoice

class ContactSerializer(serializers.ModelSerializer):
   
    status = serializers.SlugRelatedField(
        slug_field='name', 
        queryset=ContactStatusChoice.objects.all()
    )

    class Meta:
        model = Contact
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'email', 'city', 'status', 'created_at']


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return

def get_weather_for_city(city):
    if not city:
        return None
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url, timeout=5).json()
        
        if not geo_res.get('results'):
            return None
            
        lat = geo_res['results'][0]['latitude']
        lon = geo_res['results'][0]['longitude']
        
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = requests.get(weather_url, timeout=5).json()
        
        return {
            "temperature": w_res['current_weather']['temperature'],
            "wind_speed": w_res['current_weather']['windspeed']
        }
    except Exception as e:
        print(f"Weather error for {city}: {e}")
        return None



def contact_list(request: HttpRequest) -> HttpResponse:
    query = (request.GET.get("q") or "").strip()
    sort = (request.GET.get("sort") or "-created_at").strip()

    contacts = Contact.objects.all()
    if query:
        contacts = contacts.filter(
            Q(first_name__icontains=query) | Q(last_name__icontains=query) |
            Q(phone_number__icontains=query) | Q(email__icontains=query) | Q(city__icontains=query)
        )

    contacts = contacts.order_by(sort)

  
    weather_cache = {}
    for contact in contacts:
        city = contact.city
        if city not in weather_cache:
            weather_cache[city] = get_weather_for_city(city)
        contact.weather = weather_cache[city]

    return render(request, "contacts/contact_list.html", {
        "contacts": contacts,
        "query": query,
        "sort": sort,
    })

def contact_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("contacts:list")
    else:
        form = ContactForm()
    return render(request, "contacts/contact_form.html", {"form": form, "title": "Add contact"})

def contact_update(request: HttpRequest, pk: int) -> HttpResponse:
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect("contacts:list")
    else:
        form = ContactForm(instance=contact)
    return render(request, "contacts/contact_form.html", {"form": form, "title": "Edit contact"})

def contact_delete(request: HttpRequest, pk: int) -> HttpResponse:
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == "POST":
        contact.delete()
        return redirect("contacts:list")
    return render(request, "contacts/contact_confirm_delete.html", {"contact": contact})

def contact_import_csv(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = ImportCsvForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["csv_file"]
            raw = file.read().decode("utf-8", errors="ignore")
            reader = csv.DictReader(io.StringIO(raw))
            created_count = 0
            for row in reader:
                status_name = (row.get("status") or "New").strip()
                status_obj, _ = ContactStatusChoice.objects.get_or_create(name=status_name)
                Contact.objects.create(
                    first_name=(row.get("first_name") or "").strip(),
                    last_name=(row.get("last_name") or "").strip(),
                    phone_number=(row.get("phone_number") or "").strip(),
                    email=(row.get("email") or "").strip(),
                    city=(row.get("city") or "").strip(),
                    status=status_obj,
                )
                created_count += 1
            return render(request, "contacts/import_result.html", {"created_count": created_count})
    else:
        form = ImportCsvForm()
    return render(request, "contacts/import_form.html", {"form": form})

def contact_export_csv(request: HttpRequest) -> HttpResponse:
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="contacts.csv"'

    writer = csv.writer(response)
    writer.writerow(["first_name", "last_name", "phone_number", "email", "city", "status", "created_at"])

    for c in Contact.objects.select_related("status").all().order_by("-created_at"):
        writer.writerow([
            c.first_name,
            c.last_name,
            c.phone_number,
            c.email,
            c.city,
            c.status.name,
            c.created_at.strftime("%Y-%m-%d %H:%M"),
        ])

    return response


class ContactListCreateAPI(generics.ListCreateAPIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [AllowAny]
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer


class ContactDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [AllowAny]
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
