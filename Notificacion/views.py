from django.shortcuts import render
from datetime import datetime
from Aspirante import models as Aspirante_models
from verificacion_email import correo
from django.contrib.auth.models import User
from Administrador import models as Admin_models
from RRHH import models as RRHH_models

def get_mail(solicitud: Aspirante_models.SolicitudCambioCategoria, tipo: str):
    def get_emails_miembros_tribunal(solicitud_id):
        return list(RRHH_models.Miembro_tribunal.objects.filter(
            tribunal_id__solicitud_id=solicitud_id,
            miembro__userid__is_active=True
        ).exclude(miembro__userid__email='').values_list('miembro__userid__email', flat=True))

    def get_email_aspirante(solicitud):
        return [solicitud.aspirante.userid.email] if solicitud.aspirante.userid.email else []

    def get_emails_rrhh():
        return list(Admin_models.RRHH.objects.exclude(
            userid__email__isnull=True
        ).exclude(userid__email='').values_list('userid__email', flat=True))
    
    CORREOS_ESTADO = {
        'NUEVA_SOLICITUD': {
            'destinatarios': get_emails_rrhh(),
            'asunto': f"Nueva solicitud de cambio de categoría recibida - {datetime.now().strftime('%d/%m/%Y')}",
            'mensaje': f"""
            Hola equipo de Recursos Humanos,

            Les informamos que se ha recibido una nueva solicitud de cambio de categoría por parte de un aspirante. A continuación, les compartimos los detalles para su revisión:
            🔹 Fecha de Solicitud: {solicitud.fecha_solicitud.strftime('%d/%m/%Y')}  
            🔹 Nombre del Aspirante: {solicitud.aspirante.nombres}  
            🔹 CI: {solicitud.aspirante.ci}  
            🔹 Categoría Actual: {solicitud.aspirante.categoria_docente if solicitud.aspirante.categoria_docente else "Sin categoria"}
            🔹 Categoría Solicitada: {solicitud.categoria_solicitada}  
            🔹 Área: {solicitud.area}
            🔹 Especialidad: {solicitud.especialidad_solicitada}

            Saludos cordiales,  
            Expeditec
            """
        },
        'EN_REVISION': {
            'destinatarios': list(set(get_emails_miembros_tribunal(solicitud.id) + get_email_aspirante(solicitud))),
            'asunto': f"Solicitud {solicitud} en revisión - Notificación de estado",
            'mensaje': f"""
            Hola,

            Les informamos que la solicitud de cambio de categoría correspondiente al aspirante {solicitud.aspirante} ha sido oficialmente pasada a estado En revisión por el Departamento de Recursos Humanos.

            🗓️ Fecha de cambio de estado: {datetime.now().strftime('%d/%m/%Y %H:%M')}  
            📌 Estado actual: En revisión

            Esta etapa implica el análisis formal de la documentación presentada y la preparación del proceso para evaluación por parte del tribunal.

            Agradecemos su atención a este proceso.  
            Se enviarán nuevas notificaciones conforme la solicitud avance a las siguientes fases.

            Saludos cordiales,  
            Departamento de Recursos Humanos
            """
        },
        'APROBADA_TRIBUNAL': {
            'destinatarios': get_emails_rrhh() + get_email_aspirante(solicitud),
            'asunto': f"Solicitud {solicitud} aprobada por el Tribunal Evaluador",
            'mensaje': f"""
            Hola,

            Nos complace informar que la solicitud de cambio de categoría presentada por {solicitud.aspirante} ha sido aprobada por el Tribunal Evaluador.

            📄 Detalles de la resolución:  
            - Fecha de aprobación: {solicitud.fecha_resolucion.strftime('%d/%m/%Y')}  
            - Nueva categoría asignada: {solicitud.categoria_solicitada}  

            Este resultado marca un paso importante en el desarrollo profesional del aspirante.  
            El Departamento de Recursos Humanos gestionará los pasos siguientes para formalizar el cambio.

            Felicitamos al aspirante por este logro y agradecemos a todas las partes involucradas en el proceso.

            Atentamente,  
            Tribunal Evaluador
            """
        },
        'RECHAZADA_TRIBUNAL': {
            'destinatarios': get_emails_rrhh() + get_email_aspirante(solicitud),
            'asunto': f"Resultado de la solicitud {solicitud} – No aprobada",
            'mensaje': f"""
            Hola,

            Tras el proceso de evaluación, lamentamos informarte que la solicitud de cambio de categoría presentada por {solicitud.aspirante} no ha sido aprobada.

            📄 Detalles de la resolución:  
            - Fecha de resolución: {solicitud.fecha_resolucion.strftime('%d/%m/%Y')}  
            - Observación: {solicitud.observaciones}

            Entendemos que este resultado puede ser desalentador.  

            Agradecemos tu participación en este proceso y te animamos a continuar fortaleciendo tu trayectoria profesional.

            Atentamente,  
            Tribunal Evaluador
            """
        }
    }
    
    mail = CORREOS_ESTADO.get(tipo)
    if not mail:
        raise ValueError(f"Tipo de notificación no válido: {tipo}")
    
    try:
        correo.enviar_correo(
            email=mail['destinatarios'],
            asunto=mail['asunto'],
            mensaje=mail['mensaje']
        )
    except Exception as e:
        print(f"Error al enviar correo: {e}")