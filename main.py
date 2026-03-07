import time
import json

try:
    archivo = open("tareas.json", "r")
    historial = json.load(archivo)
    archivo.close()
except:
    historial = []

while True:
    print("\n MENU ")
    print("1. Iniciar Pomodoro")
    print("2. Ver historial")
    print("3. Salir")
    
    opcion = input("Elige una opcion: ")

    if opcion == "1":
        tarea = input("Que estas practicando?: ")
        
        print("Empezando...")
        
        for i in range(60, 0, -1):
            print("Quedan:", i)
            time.sleep(1)
        
        print("Terminaste!")
        
        
        historial.append(tarea + " - 60 segundos")
        
        archivo = open("tareas.json", "w")
        json.dump(historial, archivo)
        archivo.close()
        
        print(" Guardado con exito ")

    elif opcion == "2":
        print("\n TAREAS HECHAS ")
        for t in historial:
            print("-", t)
        
    elif opcion == "3":
        print("Saliendo...")
        break