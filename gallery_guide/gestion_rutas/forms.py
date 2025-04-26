from django import forms

class CreateRouteForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        label="Nombre de la ruta"
    )
    description = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Descripción (opcional)"
    )
    time_available = forms.IntegerField(
        min_value=1,
        required=True,
        label="Tiempo disponible (en minutos)"
    )
    preferred_authors = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Autores preferidos"
    )
    preferred_movements = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Movimientos preferidos"
    )
    is_public = forms.BooleanField(
        required=False,
        label="¿Hacer esta ruta pública?"
    )
