from django.shortcuts import render
from django.http import HttpRequest
from Login import views as Login_views
from Administrador import models as Admin_models
from django.utils.html import escape
from django.views import View
from django.db.models import Q
from Configuracion import views as Config_views
# Create your views here.

class Busqueda_Personal(View):
    def get(self,request:HttpRequest):
        return Login_views.redirigir_usuario(request=request)
    

    def post(self, request:HttpRequest):
        rrhh = None
        try:
            rrhh = Admin_models.RRHH.objects.get(userid=request.user)
        except Exception as e:
            pass

        if not request.user.is_staff and not rrhh:
            return Login_views.redirigir_usuario(request=request)
        
        else:
            buscar_old = escape(request.POST.get('buscar').strip())
            buscar = buscar_old.lower()
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
                    'aspirantes':aspirantes,'termino_busqueda':buscar_old,
                    'total_resultados': aspirantes.count(),
                    'rrhh':rrhh,
                    'base':Config_views.get_base(request=request)
                })
            else:
                # Si no hay término de búsqueda, mostrar todos ordenados
                return render(request, 'Busqueda_Personal/lista_personal.html', {
                    'aspirantes': Admin_models.Aspirante.objects.all().order_by('nombres', 'primer_apellido'),
                    'termino_busqueda': '',
                    'total_resultados': Admin_models.Aspirante.objects.count(),
                    'rrhh':rrhh,
                    'base':Config_views.get_base(request=request),
                })
        
    
