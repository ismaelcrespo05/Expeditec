from django.shortcuts import render
from django.views import View
from Login import views as Login_views
from Administrador import models as Admin_models
# Create your views here.



class RRHH_Dashboard(View):
    def get(self,request):
        try:
            rrhh = Admin_models.RRHH.objects.get(userid=request.user)
            return render(request,'RRHH/rrhh_base.html',{
                'rrhh':rrhh
            })
        
        except Exception as e:
            return Login_views.redirigir_usuario(request=request)

    def post(self,request):
        pass