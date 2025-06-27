import secrets
import string

def generar_contraseña(longitud=24):
    if longitud < 4:
        raise ValueError("La longitud de la contraseña debe ser al menos 4 para incluir todos los tipos de caracteres.")
    
    # Crear un generador seguro de números aleatorios
    rand = secrets.SystemRandom()
    
    # Definir los caracteres permitidos
    mayusculas = string.ascii_uppercase
    minusculas = string.ascii_lowercase
    numeros = string.digits
    caracteres_especiales = string.punctuation

    # Asegurar que haya al menos un carácter de cada tipo
    num_mayusculas = rand.randint(1, longitud - 3)
    num_minusculas = rand.randint(1, longitud - num_mayusculas - 2)
    num_numeros = rand.randint(1, longitud - num_mayusculas - num_minusculas - 1)
    

    # Generar los caracteres aleatorios
    contraseña = [
        secrets.choice(mayusculas) for _ in range(num_mayusculas)
    ] + [
        secrets.choice(minusculas) for _ in range(num_minusculas)
    ] + [
        secrets.choice(numeros) for _ in range(num_numeros)
    ]
    
    # Mezclar la contraseña para que los caracteres no estén en un patrón fijo
    rand.shuffle(contraseña)
    
    # Convertir la lista de caracteres en una cadena
    return ''.join(contraseña)



from django.db.models import Count
from . import models as Admin_models

def contar_por_categoria_docente():
    # Contar la cantidad de aspirantes por cada categoría docente
    categoria_counts = Admin_models.Aspirante.objects.filter(userid__is_active=True).values('categoria_docente').annotate(count=Count('categoria_docente'))

    # Crear un diccionario con el nombre de la categoría y su respectivo conteo
    categoria_dict_raw = {categoria['categoria_docente']: categoria['count'] for categoria in categoria_counts}

    # Lista ordenada según las categorías definidas en el sistema
    categorias_totales = Admin_models.CATEGORIA_DOCENTE_CHOICES

    # Contar los aspirantes sin categoría asignada (None o cadena vacía)
    sin_categoria = Admin_models.Aspirante.objects.filter(
        categoria_docente__isnull=True
    ).count() + Admin_models.Aspirante.objects.filter(
        categoria_docente=''
    ).count()

    # Crear el diccionario final comenzando con 'Sin categoría'
    categoria_dict_ordenado = {'Sin categoría': sin_categoria}

    # Agregar el resto en orden
    categoria_dict_ordenado.update({
        categoria: categoria_dict_raw.get(categoria, 0)
        for categoria in categorias_totales
    })

    return categoria_dict_ordenado
