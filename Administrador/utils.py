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