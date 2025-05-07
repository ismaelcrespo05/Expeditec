from django.shortcuts import render
from django.views import View
from Login import views as Login_views
from Administrador import models as Admin_models,utils as Admin_utils
# Create your views here.



class RRHH_Dashboard(View):
    def get(self,request):
        try:
            rrhh = Admin_models.RRHH.objects.get(userid=request.user)
            cant_profesores = Admin_models.Aspirante.objects.filter(tipo='Profesor').count()
            cant_estudiantes = Admin_models.Aspirante.objects.filter(tipo='Estudiante').count()
            cantidad_x_categoria = Admin_utils.contar_por_categoria_docente()
            total_usuarios = cant_estudiantes + cant_profesores
            distribucion_x_categoria = {}
            for categoria, cantidad in cantidad_x_categoria.items():
                distribucion_x_categoria[categoria] = round((cantidad / total_usuarios) * 100, 2) if total_usuarios != 0 else 0
            print(distribucion_x_categoria)
            return render(request,'RRHH/dashboard.html',{
                'rrhh':rrhh,
                'Dashboard':True,'cant_profesores':cant_profesores,'cant_estudiantes':cant_estudiantes,
                'total_personal':total_usuarios,'cantidad_x_categoria':cantidad_x_categoria,
                'distribucion_x_categoria':distribucion_x_categoria
            })
        
        except Exception as e:
            return Login_views.redirigir_usuario(request=request)

    def post(self,request):
        pass

from Aspirante import models as Aspirante_models
class Solicitudes(View):
    def get(self, request):
        try:
            rrhh = Admin_models.RRHH.objects.get(userid=request.user)
            
            
            # Obtenemos todas las solicitudes ordenadas por fecha descendente
            solicitudes = Aspirante_models.SolicitudCambioCategoria.objects.all().order_by('-fecha_solicitud')
            
            # Definimos los estados posibles
            ESTADOS = ['Pendiente', 'En revisión', 'Aprobada', 'Rechazada']
            
            # Pre-filtramos las solicitudes por estado
            solicitudes_por_estado = {
                estado: solicitudes.filter(estado=estado) 
                for estado in ESTADOS
            }
            
            # Calculamos el total de solicitudes
            total_solicitudes = solicitudes.count()
            
            # Verificamos si puede solicitar (no tiene solicitudes pendientes o en revisión)
            tiene_solicitudes_activas = solicitudes.filter(
                estado__in=['Pendiente', 'En revisión']
            ).exists()

            return render(request, 'RRHH/solicitudes.html', {
                "Cambio_categoria": True,
                "solicitudes_por_estado": solicitudes_por_estado,
                "ESTADOS": ESTADOS,
                "puede_solicitar": not tiene_solicitudes_activas,
                "total_solicitudes": total_solicitudes,  # Nuevo campo añadido
                'rrhh':rrhh,'Solicitudes':True
            })
        
        except Exception as e:
            return Login_views.redirigir_usuario(request=request)