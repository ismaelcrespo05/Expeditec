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
    num_caracteres_especiales = longitud - num_mayusculas - num_minusculas - num_numeros

    # Generar los caracteres aleatorios
    contraseña = [
        secrets.choice(mayusculas) for _ in range(num_mayusculas)
    ] + [
        secrets.choice(minusculas) for _ in range(num_minusculas)
    ] + [
        secrets.choice(numeros) for _ in range(num_numeros)
    ] + [
        secrets.choice(caracteres_especiales) for _ in range(num_caracteres_especiales)
    ]
    
    # Mezclar la contraseña para que los caracteres no estén en un patrón fijo
    rand.shuffle(contraseña)
    
    # Convertir la lista de caracteres en una cadena
    return ''.join(contraseña)



from django.db.models import Count
from . import models as Admin_models
def contar_por_categoria_docente():
    # Contar la cantidad de aspirantes por cada categoría docente
    categoria_counts = Admin_models.Aspirante.objects.values('categoria_docente').annotate(count=Count('categoria_docente'))
    
    # Crear un diccionario con el nombre de la categoría y su respectivo conteo
    categoria_dict = {categoria['categoria_docente']: categoria['count'] for categoria in categoria_counts}
    
    # Asegurarnos de que todas las categorías estén presentes, incluso si tienen 0 aspirantes
    categorias_totales = ['Ninguna','ATD Medio Superior','ATD Superior','Instructor','Asistente','Auxiliar','Titular']
    
    # Agregar las categorías que no están en el resultado
    for categoria in categorias_totales:
        if categoria not in categoria_dict:
            categoria_dict[categoria] = 0
    
    return categoria_dict


