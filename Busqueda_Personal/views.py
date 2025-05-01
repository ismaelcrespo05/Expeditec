from django.shortcuts import render
from django.http import HttpRequest
from Login import views as Login_views
from Administrador import models as Admin_models
from django.utils.html import escape
from django.views import View
from django.db.models import Q

# Create your views here.

class Busqueda_Personal(View):
    def get(self,request:HttpRequest):
        return Login_views.redirigir_usuario(request=request)
    

    def post(self, request:HttpRequest):
        if request.user.is_authenticated and request.user.is_staff:
            buscar = escape(request.POST.get('buscar').strip())
        
            if buscar:
                # Campos donde se buscará (solo los requeridos)
                campos_busqueda = [
                    'nombres',
                    'primer_apellido',
                    'segundo_apellido',
                    'ci',
                ]
                
                # Construir consulta OR para buscar en todos los campos
                consulta = Q()
                for campo in campos_busqueda:
                    consulta |= Q(**{f"{campo}__icontains": buscar})  # Búsqueda insensible a mayúsculas/minúsculas
                
                # Filtrar aspirantes que cumplan al menos una condición
                aspirantes = Admin_models.Aspirante.objects.filter(consulta).distinct().order_by('nombres', 'primer_apellido')
            
                return render(request, 'Busqueda_Personal/lista_personal.html', {
                    'aspirantes':aspirantes,'termino_busqueda':buscar,
                    'total_resultados': aspirantes.count(),
                })
            else:
                # Si no hay término de búsqueda, mostrar todos ordenados
                return render(request, 'Busqueda_Personal/lista_personal.html', {
                    'aspirantes': Admin_models.Aspirante.objects.all().order_by('nombres', 'primer_apellido'),
                    'termino_busqueda': '',
                    'total_resultados': Admin_models.Aspirante.objects.count(),
                })
        return Login_views.redirigir_usuario(request=request)
    
