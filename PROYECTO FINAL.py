import os
from mysql.connector import Error
from datetime import datetime
import mysql.connector as MySql
import time
import tkinter as TK

# --- COLORES EN HEXADECIMALES ---
rosado_claro = "#FFDEDE"
verde = "#00FF00"
amarillo_claro = "#FFFF99"

# --- CONEXIÓN CON LA BASE DE DATOS MySQL WORKBENCH
# --- Y UN ÍCONO PARA LA IMPLEMENTACIÓN---
ícono = os.path.join(os.path.dirname(__file__),"escuela.ico")
def conectar_base_de_datos():
  try:
    cadena_de_conexión = MySql.connect(
        host = 'localhost',
        user = 'root',
        password = 'aHQfu3.4JW8rX/cd!K',
        database = 'escuela',
    )
    conexión_exitosa = cadena_de_conexión.is_connected()
    if conexión_exitosa:
      return cadena_de_conexión
  except Error as e:
    print(f"Error inesperado al conectar MySql {e}")
    return None

def desconectar_base_de_datos(conexión):
  desconectando_db = conexión.is_connected()
  if desconectando_db:
    conexión.close()

#--- FUNCIONES DEL ABM (ALTA, BAJA Y MODIFICACIÓN) ---
def consultar_tabla(nombre_de_la_tabla):
  conexión = conectar_base_de_datos()
  if conexión:
    cursor = conexión.cursor()
    cursor.execute(f"SELECT * FROM {nombre_de_la_tabla};")
    resultado = cursor.fetchall()
    Lista_de_datos.delete(0, TK.END)
    
    #Este for muestra toda la tabla completa en la Lista_de_datos de MySQL
    for fila in resultado:
      filas_formateadas = " | \t".join(map(str, fila))
      Lista_de_datos.insert(TK.END, filas_formateadas)
    
    desconectar_base_de_datos(conexión)

def seleccionar_y_consultar():
  
  botón_seleccionado = opción.get()
  try:
    match botón_seleccionado:
      case 1:
        consultar_tabla('alumno')
      case 2:
        consultar_tabla('carrera')
      case 3:
        consultar_tabla('materia')
      case 4:
        consultar_tabla('profesor')
      case 5:
        consultar_tabla('nota')
      case _:
        print("LA OPCIÓN NO ES VÁLIDA")
  except Error as e:
    print(f"Error al consultar toda la tabla: {e}")

def insertar_todos_los_datos():
  botón_seleccionado = opción.get()
  try:
    match botón_seleccionado:
      case 1:
        insertar_datos('alumno')
      case 2:
        insertar_datos('carrera')
      case 3:
        insertar_datos('materia')
      case 4:
        insertar_datos('profesor')
      case 5:
        insertar_datos('nota')
  except Exception as e:
    print(f"Error al insertar datos necesarios: {e}")


#Definí una función para poder mostrar 
#cuando uno de los radioButtons esté seleccionado
def habilitar_botones_e_inputs():
  #Este for me permite gestionar los texBox con sus respectivos labels
  #para que a la hora de seleccionar un radioButton me muestre lo necesario
  for widget in [  txBox_NombreAlumno, label_NombreAlumno, txBox_FechaNacimiento, label_FechaNacimiento,
                   txBox_NombreCarrera, label_NombreCarrera, txBox_Duración, label_Duración,
                   txBox_NombreMateria, label_NombreMateria, txBox_HorarioCorrespondiente, label_HorarioCorrespondiente,
                   txBox_NombreProfesor, label_NombreProfesor, txBox_HorasTrabajadas, label_HorasTrabajadas,
                   txBox_NotaCalificada, label_NotaCalificada, txBox_CantidadNotas, label_CantidadNotas,
                   txBox_Promedio, label_Promedio]:
      widget.place_forget()
    
  
  botón_seleccionado = opción.get()
  
  if botón_seleccionado in (1, 2, 3, 4, 5):
    botón_agregar.place(x=60,y= 100)
    botón_modificar.place(x=60,y= 160)
    botón_eliminar.place(x=60,y= 220)
    
    match botón_seleccionado:
      case 1:
        txBox_NombreAlumno.place(x=150, y= 100)
        label_NombreAlumno.place(relx=0.25, rely=0.155)
        txBox_FechaNacimiento.place(x=150, y= 150)
        label_FechaNacimiento.place(relx=0.25, rely=0.25)
      case 2:
        txBox_NombreCarrera.place(x=150, y= 100)
        label_NombreCarrera.place(relx=0.25, rely=0.155)
        txBox_Duración.place(x=150, y= 150)
        label_Duración.place(relx=0.25, rely=0.25)
      case 3:
        txBox_NombreMateria.place(x=150, y= 100)
        label_NombreMateria.place(relx=0.25, rely=0.155)
        txBox_HorarioCorrespondiente.place(x=150, y= 150)
        label_HorarioCorrespondiente.place(relx=0.25, rely=0.25)
      case 4:
        txBox_NombreProfesor.place(x=150, y= 100)
        label_NombreProfesor.place(relx=0.25, rely=0.155)
        txBox_HorasTrabajadas.place(x=150, y= 150)
        label_HorasTrabajadas.place(relx=0.25, rely=0.25)
      case 5:
        txBox_NotaCalificada.place(x=150, y= 100)
        label_NotaCalificada.place(relx=0.25, rely=0.155)
        txBox_CantidadNotas.place(x=150, y= 150)
        label_CantidadNotas.place(relx=0.25, rely=0.25)
        txBox_Promedio.place(x=150, y= 200)
        label_Promedio.place(relx=0.25, rely=0.325)
      case _:
          print("ES NECESARIO SELECCIONAR")

def obtener_tabla_seleccionada():
  tabla = {1: 'alumno', 2: 'carrera', 3: 'materia', 4: 'profesor', 5: 'nota'}
  nombre = tabla.get(opción.get(), None)
  return nombre

def doble_acción():
  habilitar_botones_e_inputs()
  
  seleccionar_y_consultar()

#Esta función sirve para actualizar la hora
def actualizar_la_hora():
  label_Hora.config(text=time.strftime("%H:%M:%S"))
  mi_ventana.after(1000, actualizar_la_hora)

def deseleccionar_RadioButton():
  botón_seleccionado = opción.get()


# --- CONDIFGURACIÓN DE INTERFAZ Y ELEMENTOS IMPORTANTES DE TKINTER PARA LAS INSTRUCCIONES---
mi_ventana = TK.Tk()
mi_ventana.title("ABM de Alumnos")
mi_ventana.geometry("1200x600")
mi_ventana.minsize(1200, 600)
mi_ventana.maxsize(1200, 600)
mi_ventana.configure(bg=rosado_claro)
mi_ventana.iconbitmap(ícono)
mi_ventana.attributes("-alpha", 1)

# --- BOTONES NECESARIOS ---
#Agregar
botón_agregar = TK.Button(text="Agregar Dato", command=insertar_todos_los_datos, width= 10,height= 1)
botón_agregar.config(fg="black", bg=verde, font=("Arial", 8))

#Modificar
botón_modificar = TK.Button(text="Modificar Dato", command=lambda:modificar_datos(obtener_tabla_seleccionada()), width= 10,height= 1)
botón_modificar.config(fg="black", bg="red", font=("Arial", 8))

#Eliminar
botón_eliminar = TK.Button(text="Eliminar Dato", command=lambda:eliminar_datos(obtener_tabla_seleccionada()), width= 10,height= 1)
botón_eliminar.config(fg="black", bg="blue", font=("Arial", 8))


# --- ETIQUETAS ---

#Etiquetas para la tabla de alumno
label_NombreAlumno = TK.Label(mi_ventana, text="Nombre")
label_NombreAlumno.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

label_FechaNacimiento = TK.Label(mi_ventana, text="Fecha que nació: Formato YYYY-MM-DD")
label_FechaNacimiento.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

#Etiquetas para la tabla de carrera
label_NombreCarrera = TK.Label(mi_ventana, text="Nombre")
label_NombreCarrera.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

label_Duración = TK.Label(mi_ventana, text="Duración")
label_Duración.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

#Etiquetas para la tabla de materia
label_NombreMateria = TK.Label(mi_ventana, text="Nombre")
label_NombreMateria.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

label_HorarioCorrespondiente = TK.Label(mi_ventana, text="Horario correspondiente")
label_HorarioCorrespondiente.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

#Etiquetas para la tabla de profesor
label_NombreProfesor = TK.Label(mi_ventana, text="Nombre")
label_NombreProfesor.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

label_HorasTrabajadas = TK.Label(mi_ventana, text="Horas trabajadas")
label_HorasTrabajadas.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

#Etiquetas para la tabla de nota

label_NotaCalificada = TK.Label(mi_ventana, text="Calificación")
label_NotaCalificada.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

label_CantidadNotas = TK.Label(mi_ventana, text="Cantidad")
label_CantidadNotas.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

label_Promedio = TK.Label(mi_ventana, text="Promedio")
label_Promedio.config(fg="Black",bg=rosado_claro, font=("Arial", 12))



label_Hora = TK.Label(mi_ventana, text=time.strftime("%H:%M:%S"))
label_Hora.config(fg="Black",bg=rosado_claro, font=("Arial", 12))
label_Hora.pack()

#--- ENTRIES ---

#Tabla alumno
txBox_NombreAlumno = TK.Entry(mi_ventana)
txBox_FechaNacimiento = TK.Entry(mi_ventana)

#Tabla carrera
txBox_NombreCarrera = TK.Entry(mi_ventana)
txBox_Duración = TK.Entry(mi_ventana)

#Tabla materia
txBox_NombreMateria = TK.Entry(mi_ventana)
txBox_HorarioCorrespondiente = TK.Entry(mi_ventana)

#Tabla profesor
txBox_NombreProfesor = TK.Entry(mi_ventana)
txBox_HorasTrabajadas = TK.Entry(mi_ventana)

#Tabla nota
txBox_NotaCalificada = TK.Entry(mi_ventana)
txBox_CantidadNotas = TK.Entry(mi_ventana)
txBox_Promedio = TK.Entry(mi_ventana)


# --- RADIOBUTTONS ---
opción = TK.IntVar()

Botón_Tabla_de_Alumno = TK.Radiobutton(mi_ventana, text="Alumno", variable=opción, value= 1, command=doble_acción)
Botón_Tabla_de_Alumno.config(bg=rosado_claro, font=("Arial", 12))

Botón_Tabla_de_Carrera = TK.Radiobutton(mi_ventana, text="Carrera", variable=opción, value= 2, command=doble_acción)
Botón_Tabla_de_Carrera.config(bg=rosado_claro, font=("Arial", 12))

Botón_Tabla_de_Materia = TK.Radiobutton(mi_ventana, text="Materia", variable=opción, value= 3, command=doble_acción)
Botón_Tabla_de_Materia.config(bg=rosado_claro, font=("Arial", 12))

Botón_Tabla_de_Profesor = TK.Radiobutton(mi_ventana, text="Profesor", variable=opción, value= 4, command=doble_acción)
Botón_Tabla_de_Profesor.config(bg=rosado_claro, font=("Arial", 12))

Botón_Tabla_de_Notas = TK.Radiobutton(mi_ventana, text="Nota", variable=opción, value= 5, command=doble_acción)
Botón_Tabla_de_Notas.config(bg=rosado_claro, font=("Arial", 12))

Botón_Tabla_de_Alumno.place(x= 60, y = 500)
Botón_Tabla_de_Carrera.place(x = 180, y = 500)
Botón_Tabla_de_Materia.place(x = 300, y = 500)
Botón_Tabla_de_Profesor.place(x = 420, y = 500)
Botón_Tabla_de_Notas.place(x = 540, y = 500)

#--- LISTBOX ---
Lista_de_datos = TK.Listbox(mi_ventana, width= 60, height= 40)
Lista_de_datos.config(fg="blue",bg=amarillo_claro, font=("Arial", 10))
Lista_de_datos.place(x= 750, y= 0)

# --- EJECUCIÓN DE LA VENTANA PRINCIPAL ---

def insertar_datos(nombre_de_la_tabla):
  Nombre = txBox_NombreAlumno.get()
  Fecha_de_Nacimiento = txBox_FechaNacimiento.get()
  
  Datos_necesarios = Nombre and Fecha_de_Nacimiento
  
  if Datos_necesarios:
    conexión = conectar_base_de_datos()
    cursor = conexión.cursor()
    try:
      Fecha_de_Nacimiento = datetime.strptime(Fecha_de_Nacimiento, '%Y-%m-%d')
    except ValueError:
      print("El formato no es correcto.Debe ser YYYY-MM-DD")
      return
    try:
      if conexión:
        values = (Nombre, Fecha_de_Nacimiento)
        query = f"INSERT INTO {nombre_de_la_tabla} (Nombre, Fecha_de_Nacimiento) VALUES (%s, %s)"
        cursor.execute(query, values)
        conexión.commit()
        
        print("SE AGREGÓ LOS DATOS NECESARIOS")
        
        txBox_NombreAlumno.delete(0, TK.END)
        txBox_FechaNacimiento.delete(0, TK.END)
        
        consultar_tabla(nombre_de_la_tabla)
    except Error as e:
      print(f"ERROR INESPERADO AL INSERTAR: {e}")
  else:
    print("No tiene todos los datos")

def modificar_datos(nombre_de_la_tabla):
  columna_seleccionada = Lista_de_datos.curselection()

  if columna_seleccionada:
    ID_Seleccionado = Lista_de_datos.get(columna_seleccionada).split('|')[3].strip()

    Nombre = txBox_NombreAlumno.get()
    Fecha_de_Nacimiento = txBox_FechaNacimiento.get()
  
    Datos_necesarios = Nombre and Fecha_de_Nacimiento
  
    if Datos_necesarios:
      conexión = conectar_base_de_datos()
      cursor = conexión.cursor()
      try:
        Fecha_de_Nacimiento = datetime.strptime(Fecha_de_Nacimiento, '%Y-%m-%d')
      except ValueError:
        print("El formato no es correcto.Debe ser YYYY-MM-DD")
        return
      try:
        if conexión:
          values = (Nombre, Fecha_de_Nacimiento, ID_Seleccionado,)
          query = f"UPDATE {nombre_de_la_tabla} SET Nombre = %s, Fecha_de_Nacimiento = %s WHERE ID_Alumno = %s"
          cursor.execute(query, values)
          conexión.commit()
          print("Se ha modificado correctamente los datos")
      except Error as e:
        print(f"ERROR INESPERADO: {e}")
    else:
      print("Faltó completar los campos obligatorios")

  else:
    print("No se seleccionó ninguna columna")

def eliminar_datos(nombre_de_la_tabla):
  columna_seleccionada = Lista_de_datos.curselection()
  
  if columna_seleccionada:
    conexión = conectar_base_de_datos()
    if conexión:
      cursor = conexión.cursor()
      try:
        for _ in columna_seleccionada:
          selección = Lista_de_datos.get(_)
          try:
            ID_Seleccionado = int(selección.split('|')[3].strip())
          except ValueError:
            print(f"El ID {ID_Seleccionado} no vale")
            continue
        values = (ID_Seleccionado,)
        query = f"DELETE FROM {nombre_de_la_tabla} where ID_Alumno = %s"
        cursor.execute(query, values)
        conexión.commit()
        print(f"Una columna ha sido eliminada exitosamente con id {ID_Seleccionado}")
        consultar_tabla(nombre_de_la_tabla)
      except Error as e:
        print(f"ERROR INESPERADO: {e}")
      finally:
        desconectar_base_de_datos(conexión)
  else:
    print("No seleccionaste la columna a eliminar")

actualizar_la_hora()
mi_ventana.mainloop()
