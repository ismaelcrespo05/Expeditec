def verificar_contraseñas(contraseña1, contraseña2):
    errores = []
    
    # Verificar si las contraseñas son iguales
    if contraseña1 != contraseña2:
        errores.append("Las contraseñas no coinciden")
    
    # Verificar longitud mínima (al menos 8 caracteres)
    if len(contraseña1) < 8:
        errores.append("La contraseña es demasiado corta (mínimo 8 caracteres)")
    
    # Verificar que contiene al menos una letra mayúscula
    if not any(c.isupper() for c in contraseña1):
        errores.append("La contraseña debe contener al menos una letra mayúscula")
    
    # Verificar que contiene al menos una letra minúscula
    if not any(c.islower() for c in contraseña1):
        errores.append("La contraseña debe contener al menos una letra minúscula")
    
    # Verificar que contiene al menos un dígito
    if not any(c.isdigit() for c in contraseña1):
        errores.append("La contraseña debe contener al menos un número")
    
    # Verificar que contiene al menos un carácter especial
    caracteres_especiales = "!@#$%^&*()-_=+[]{}|;:'\",.<>/?"
    if not any(c in caracteres_especiales for c in contraseña1):
        errores.append("La contraseña debe contener al menos un carácter especial")
    
    # Si no hay errores, devuelve "OK", de lo contrario, devuelve los errores separados por coma
    return "OK" if not errores else ", ".join(errores)
