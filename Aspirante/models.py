from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from Administrador import models as Admin_models


ESTADOS = ['Pendiente','En revisión','Aprobada','Rechazada']
class SolicitudCambioCategoria(models.Model):
    aspirante = models.ForeignKey(
        Admin_models.Aspirante,
        on_delete=models.CASCADE,
        related_name='solicitudes'
    )

    categoria_solicitada = models.TextField(null=False)
    area = models.TextField(null=True)
    cargo_actual = models.TextField(null=False)
    especialidad_solicitada = models.TextField(null=False)

    observaciones = models.TextField(null=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.TextField(null=False,default='Pendiente')
    fecha_resolucion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.aspirante} → {self.categoria_solicitada}"



TIPOS_DOCUMENTOS = [
    "Acreditación de cultura general acorde al perfil profesional del educador",
    "Certificación de cumplimiento de objetivos de superación profesional y especializada",
    "Certificación de experiencia en orientación a profesores de menor categoría",
    "Certificado de conducta ejemplar y adhesión a valores de la educación superior cubana",
    "Certificado de dominio o conocimiento de idioma extranjero técnico o profesional",
    "Certificado de participación o liderazgo en proyectos de investigación, innovación o extensión",
    "Constancia de cumplimiento de funciones de la categoría docente precedente",
    "Constancia de experiencia laboral relevante en la disciplina docente",
    "Documentación de conocimientos sobre los Problemas Sociales de la Ciencia y la Tecnología",
    "Documentación de impacto social o aplicación práctica de resultados científicos",
    "Evaluación integral satisfactoria como estudiante de pregrado",
    "Evidencias que acrediten la calidad profesional de docentes externos",
    "Expediente académico satisfactorio con índice igual o superior al exigido",
    "Publicaciones científicas en revistas especializadas o de prestigio internacional",
    "Reconocimiento de prestigio o relevancia en la labor docente, educativa o metodológica",
    "Reconocimiento por trabajo destacado en roles académicos, educativos o científicos institucionales",
    "Registro de patentes como resultado de la actividad científica",
    "Resultados de ejercicios o pruebas para la categoría docente",
    "Resultados de evaluaciones docentes recientes con calificación de Excelente o Bien",
    "Título académico de nivel medio, superior o grado científico",
]



REQUISITOS_CATEGORIA_CAMPOS = {
    "Profesor Titular": [
        "Título académico de nivel medio, superior o grado científico",
        "Reconocimiento de prestigio o relevancia en la labor docente, educativa o metodológica",
        "Reconocimiento por trabajo destacado en roles académicos, educativos o científicos institucionales",
        "Constancia de cumplimiento de funciones de la categoría docente precedente",
        "Certificación de experiencia en orientación a profesores de menor categoría",
        "Documentación de impacto social o aplicación práctica de resultados científicos",
        "Publicaciones científicas en revistas especializadas o de prestigio internacional",
        "Registro de patentes como resultado de la actividad científica",
        "Resultados de evaluaciones docentes recientes con calificación de Excelente o Bien",
        "Certificado de conducta ejemplar y adhesión a valores de la educación superior cubana",
        "Acreditación de cultura general acorde al perfil profesional del educador",
        "Resultados de ejercicios o pruebas para la categoría docente",
        "Evidencias que acrediten la calidad profesional de docentes externos",
    ],
    "Profesor Auxiliar": [
        "Título académico de nivel medio, superior o grado científico",
        "Reconocimiento de prestigio o relevancia en la labor docente, educativa o metodológica",
        "Reconocimiento por trabajo destacado en roles académicos, educativos o científicos institucionales",
        "Constancia de cumplimiento de funciones de la categoría docente precedente",
        "Certificación de experiencia en orientación a profesores de menor categoría",
        "Certificado de participación o liderazgo en proyectos de investigación, innovación o extensión",
        "Publicaciones científicas en revistas especializadas o de prestigio internacional",
        "Documentación de impacto social o aplicación práctica de resultados científicos",
        "Documentación de conocimientos sobre los Problemas Sociales de la Ciencia y la Tecnología",
        "Certificado de dominio o conocimiento de idioma extranjero técnico o profesional",
        "Resultados de evaluaciones docentes recientes con calificación de Excelente o Bien",
        "Certificado de conducta ejemplar y adhesión a valores de la educación superior cubana",
        "Acreditación de cultura general acorde al perfil profesional del educador",
        "Resultados de ejercicios o pruebas para la categoría docente",
        "Evidencias que acrediten la calidad profesional de docentes externos"
    ],
    "Profesor Asistente": [
        "Reconocimiento de prestigio o relevancia en la labor docente, educativa o metodológica",
        "Reconocimiento por trabajo destacado en roles académicos, educativos o científicos institucionales",
        "Certificación de cumplimiento de objetivos de superación profesional y especializada",
        "Certificado de participación o liderazgo en proyectos de investigación, innovación o extensión",
        "Constancia de cumplimiento de funciones de la categoría docente precedente",
        "Publicaciones científicas en revistas especializadas o de prestigio internacional",
        "Documentación de conocimientos sobre los Problemas Sociales de la Ciencia y la Tecnología",
        "Certificado de dominio o conocimiento de idioma extranjero técnico o profesional",
        "Resultados de evaluaciones docentes recientes con calificación de Excelente o Bien",
        "Certificado de conducta ejemplar y adhesión a valores de la educación superior cubana",
        "Acreditación de cultura general acorde al perfil profesional del educador",
        "Resultados de ejercicios o pruebas para la categoría docente",
        "Evidencias que acrediten la calidad profesional de docentes externos"
    ],
    "Instructor": [
        "Título académico de nivel medio, superior o grado científico",
        "Evaluación integral satisfactoria como estudiante de pregrado",
        "Expediente académico satisfactorio con índice igual o superior al exigido",
        "Certificado de conducta ejemplar y adhesión a valores de la educación superior cubana",
        "Acreditación de cultura general acorde al perfil profesional del educador",
        "Resultados de ejercicios o pruebas para la categoría docente",
        "Evidencias que acrediten la calidad profesional de docentes externos",
        "Constancia de cumplimiento de funciones de la categoría docente precedente"
    ],
    "ATD Superior": [
        "Título académico de nivel medio, superior o grado científico",
        "Expediente académico satisfactorio con índice igual o superior al exigido",
        "Certificado de conducta ejemplar y adhesión a valores de la educación superior cubana",
        "Acreditación de cultura general acorde al perfil profesional del educador",
        "Resultados de ejercicios o pruebas para la categoría docente",
        "Evidencias que acrediten la calidad profesional de docentes externos",
        "Constancia de cumplimiento de funciones de la categoría docente precedente"
    ],
    "ATD Medio Superior": [
        "Título académico de nivel medio, superior o grado científico",
        "Constancia de experiencia laboral relevante en la disciplina docente",
        "Expediente académico satisfactorio con índice igual o superior al exigido",
        "Certificado de conducta ejemplar y adhesión a valores de la educación superior cubana",
        "Acreditación de cultura general acorde al perfil profesional del educador",
        "Resultados de ejercicios o pruebas para la categoría docente",
        "Evidencias que acrediten la calidad profesional de docentes externos",
        "Constancia de cumplimiento de funciones de la categoría docente precedente"
    ]
}



REQUISITOS_CATEGORIA = {
    'Profesor Titular':[
        # Inciso a)
        "Acreditación de Grado Científico",
        # Inciso b)
        "Evidencia de papel relevante en docencia (pregrado, posgrado y profesional)",
        # Inciso c)
        "Evidencia de trabajo educativo destacado en roles académicos y científicos",
        # Inciso d)
        "Acreditación de cumplimiento de funciones de categoría docente anterior",
        "Evidencia de prestigio en formación de profesionales con valores ideológicos",
        "Aval de orientación a profesores de menor categoría",
        # Inciso e)
        "Evidencia de resultados de proyectos de investigación e innovación",
        "Acreditación de 3 artículos en revistas de prestigio internacional",
        "Evidencia de otras publicaciones especializadas",
        "Acreditación de patentes registradas",
        "Evidencia de impacto social demostrado de resultados científicos",
        # Inciso f)
        "Acreditación de evaluaciones recientes: 'Excelente' o 'Bien'",
        # Inciso g)
        "Aval de conducta ejemplar y valores de educación cubana",
        "Evidencia de cultura general como educador",
        # Inciso h)
        "Acreditación de resultados de ejercicios evaluativos",
        # Inciso i)
        "Evidencia para externos: relevancia en actividades profesionales",
    ],
    'Profesor Auxiliar':[
        # Inciso a)
        "Acreditación de título de máster, especialista o grado científico",
        # Inciso b)
        "Evidencia de resultados satisfactorios en actividades docentes",
        # Inciso c)
        "Evidencia de trabajo educativo destacado como profesor guía, principal de año, jefe de disciplina, jefe de colectivo de carreras o miembro del Consejo Científico",
        # Inciso d)
        "Acreditación de cumplimiento de funciones de la categoría docente precedente",
        "Evidencia de prestigio en trabajo metodológico con aspectos ideológicos y formativos de su disciplina",
        "Aval de orientación a profesores de categorías inferiores",        
        # Inciso e)
        "Evidencia de ejecución de proyectos de investigación, desarrollo e innovación o extensión universitaria",
        "Acreditación de 2 artículos científicos publicados en revistas de prestigio internacional",
        "Evidencia de resultados aplicados en la práctica social con impacto demostrado (últimos 5 años o vigencia científica)",
        # Inciso f)
        "Aval de conocimientos sobre Problemas Sociales de la Ciencia y la Tecnología",
        # Inciso g)
        "Acreditación de dominio de idioma extranjero útil para su campo profesional",
        # Inciso h)
        "Acreditación de últimas evaluaciones: 'Excelente' o 'Bien'",
        # Inciso i)
        "Aval de conducta ejemplar y valores de la educación superior cubana",
        "Evidencia de cultura general como educador de nuevas generaciones",
        # Inciso j)
        "Acreditación de resultados satisfactorios en ejercicios establecidos para la categoría",
        # Inciso k)
        "Evidencia para profesionales externos: relevancia en actividades profesionales (sustituye incisos b, c, d)"
    ],
    'Profesor Asistente':[
        # Inciso a)
        "Evidencia de resultados satisfactorios en actividades docentes en general",
        # Inciso b)
        "Evidencia de trabajo educativo destacado como profesor y profesor guía",
        # Inciso c)
        "Acreditación de cumplimiento de objetivos de superación básica y especializada",
        "Evidencia de formación para funciones de categoría precedente",
        # Inciso d)
        "Evidencia de participación en proyectos de investigación, desarrollo e innovación o extensión universitaria",
        "Acreditación de cumplimiento satisfactorio de funciones encomendadas",
        "Evidencia de elaboración de materiales y publicación científica útil",
        "Acreditación de al menos un artículo científico publicado o aprobado en revistas especializadas",
        # Inciso e)
        "Aval de conocimientos sobre los Problemas Sociales de la Ciencia y la Tecnología",
        # Inciso f)
        "Acreditación de conocimiento de idioma extranjero para consulta científico-técnica",
        # Inciso g)
        "Acreditación de últimas evaluaciones obtenidas de Excelente o Bien",
        # Inciso h)
        "Aval de conducta ejemplar y valores compartidos de la educación superior cubana",
        "Evidencia de cultura general acorde a su condición de educador",
        # Inciso i)
        "Acreditación de realización satisfactoria de ejercicios establecidos para la categoría",
        # Inciso j)
        "Evidencia para profesionales externos: relevante papel en actividades profesionales (excepto incisos b, c y d)"
    ],
    'Instructor':[
        # Inciso a)
        "Acreditación de título de nivel superior",
        "Evidencia de buena evaluación integral como estudiante de pregrado",
        # Inciso b)
        "Acreditación de índice académico no menor de 4 puntos o equivalente",
        # Inciso c)
        "Aval de conducta ejemplar y valores compartidos de la educación superior cubana",
        "Evidencia de cultura general acorde a su condición de educador",
        # Inciso d)
        "Acreditación de realización satisfactoria de ejercicios establecidos para la categoría",
        # Inciso e)
        "Evidencia para profesionales externos: resultado satisfactorio avalado por jefe facultado",
        "Acreditación de cumplimiento de requisitos restantes para la categoría"
    ],
    'ATD Superior':[
        # Inciso a)
        "Acreditación de título de nivel superior",        
        # Inciso b)
        "Evidencia de expediente integral satisfactorio con índice académico no menor de 3.5 puntos",
        # Inciso c)
        "Aval de conducta ejemplar y valores compartidos de la educación superior cubana",
        "Evidencia de cultura general acorde a su condición de educador",
        # Inciso d)
        "Acreditación de aprobación del ejercicio establecido para esta categoría",
        # Inciso e)
        "Evidencia para profesionales externos: resultado satisfactorio avalado por jefe facultado",
        "Acreditación de cumplimiento de requisitos restantes para la categoría"
    ],
    'ATD Medio Superior':[
        # Inciso a)
        "Acreditación de título de nivel medio superior en especialidad relacionada con la disciplina",
        "Evidencia de experiencia laboral vinculada con la disciplina docente (en caso de no tener título relacionado)",
        # Inciso b)
        "Acreditación de expediente integral satisfactorio con índice académico no menor de 80 puntos",
        # Inciso c)
        "Aval de conducta ejemplar y valores compartidos de la educación superior cubana",
        "Evidencia de cultura general acorde a su condición de educador",
        # Inciso d)
        "Acreditación de aprobación del ejercicio establecido para esta categoría",
        # Inciso e)
        "Evidencia para profesionales externos: resultado satisfactorio avalado por jefe facultado",
        "Acreditación de cumplimiento de requisitos restantes para la categoría"
    ],
}




#######################################################################################################
#######################################################################################################
#######################################################################################################
#######################################################################################################









EJERCICIOS_CHOICE = [
    "Clase de comprobación sobre un tema de su asignatura",
    "Clase de comprobación sobre una asignatura de su disciplina",
    "Clase metodológica sobre un tema de su disciplina",
    "Clase práctica o de laboratorio sobre la asignatura en la que trabajará",
    "Disertación sobre aspectos del programa de la disciplina",
    "Evaluación sobre el uso de tecnologías de la información y comunicación",
    "Examen sobre normas jurídicas del trabajo docente",
    "Exposición crítica del programa analítico de su asignatura",
    "Exposición crítica sobre el plan de estudios de la carrera o disciplina",
    "Exposición sobre el desarrollo de cursos en línea",
    "Exposición sobre el diseño y desarrollo de cursos en línea",
    "Exposición sobre el montaje de cursos en línea"
]


EJERCICIOS_X_CATEGORIA = {
    "Profesor Titular": [
        "Clase metodológica sobre un tema de su disciplina",
        "Exposición crítica sobre el plan de estudios de la carrera o disciplina",
        "Examen sobre normas jurídicas del trabajo docente",
        "Evaluación sobre el uso de tecnologías de la información y comunicación",
        "Exposición sobre el diseño y desarrollo de cursos en línea"
    ],
    "Profesor Auxiliar": [
        "Clase metodológica sobre un tema de su disciplina",
        "Disertación sobre aspectos del programa de la disciplina",
        "Examen sobre normas jurídicas del trabajo docente",
        "Evaluación sobre el uso de tecnologías de la información y comunicación",
        "Exposición sobre el desarrollo de cursos en línea"
    ],
    "Profesor Asistente": [
        "Clase de comprobación sobre un tema de su asignatura",
        "Examen sobre normas jurídicas del trabajo docente",
        "Exposición crítica del programa analítico de su asignatura",
        "Evaluación sobre el uso de tecnologías de la información y comunicación",
        "Exposición sobre el montaje de cursos en línea"
    ],
    "Instructor": [
        "Clase de comprobación sobre una asignatura de su disciplina",
        "Examen sobre normas jurídicas del trabajo docente",
        "Evaluación sobre el uso de tecnologías de la información y comunicación"
    ],
    "ATD Superior": [
        "Clase práctica o de laboratorio sobre la asignatura en la que trabajará"
    ],
    "ATD Medio Superior": [
        "Clase práctica o de laboratorio sobre la asignatura en la que trabajará"
    ]
}


















def documento_upload_to(instance, filename):
    return f'expedientedocente/{instance.aspirante_id.ci}/{filename}'

class DocumentosExpedienteDocente(models.Model):
    aspirante_id = models.ForeignKey(
        Admin_models.Aspirante,
        on_delete=models.CASCADE,
        related_name='documentos'
    )
    tipo = models.TextField(null=False)
    archivo = models.FileField(upload_to=documento_upload_to)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(null=False, blank=True)
    
    def __str__(self):
        return f"{self.tipo} - {self.fecha_subida.date()}"




# Configuración de autoeliminación de archivos
from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=DocumentosExpedienteDocente)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.archivo:
        instance.archivo.delete(save=False)









def actas_upload_to(instance, filename):
    return f'actas_tribunal/{instance.solicitud_id.id}/{filename}'

from RRHH import models as RRHH_models
class Actas_Tribunal(models.Model):
    solicitud_id = models.ForeignKey(SolicitudCambioCategoria,on_delete=models.CASCADE)
    archivo = models.FileField(upload_to=actas_upload_to)
    miembro = models.ForeignKey(RRHH_models.Miembro_tribunal,on_delete=models.SET_NULL,null=True,related_name='actas_tribunal')
    descripcion = models.TextField(null=False, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)



@receiver(post_delete, sender=Actas_Tribunal)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.archivo:
        instance.archivo.delete(save=False)

