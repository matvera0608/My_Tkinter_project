import os
from mysql.connector import Error
from datetime import datetime
import mysql.connector as MySql
import time
import tkinter as TK

##Colores en hexadecimales
rosado_claro = "#FFDEDE"
verde = "#00FF00"
amarillo_claro = "#FFFF99"

ícono = os.path.join(os.path.dirname(__file__),"escuela.ico")

#Esta función se trata de la cadena de conexión con mi base de datos
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

#En esta región tendré las funciones de base de datos MySQL como Consultar
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


#Definí una función para hacer aparecer las opciones de agregar,
#modificar y eliminar ciertos datos
def habilitar_botones_e_inputs():
  botón_seleccionado = opción.get()
  if botón_seleccionado == 1 or botón_seleccionado == 2 or botón_seleccionado == 3:
    print()
  else:
    print()
    
def doble_acción():
  habilitar_botones_e_inputs()
  
  seleccionar_y_consultar()

#Esta función sirve para actualizar la hora
def actualizar_la_hora():
  label_Hora.config(text=time.strftime("%H:%M:%S"))
  mi_ventana.after(1000, actualizar_la_hora)

#Esta ventana es el comienzo de mi proyecto Tkinter
mi_ventana = TK.Tk()
mi_ventana.title("ABM de Alumnos")
mi_ventana.geometry("1200x600")
mi_ventana.minsize(1200, 600)
mi_ventana.maxsize(1200, 600)
mi_ventana.configure(bg=rosado_claro)
mi_ventana.iconbitmap(ícono)
mi_ventana.attributes("-alpha", 1)

#Creo los botones necesarios para el ABM de alumnos
botón_agregar = TK.Button(text="Agregar Dato", command=insertar_todos_los_datos, width= 10,height= 1)
botón_agregar.config(fg="black", bg=verde, font=("Arial", 8))

botón_modificar = TK.Button(text="Modificar Dato", command=insertar_todos_los_datos, width= 10,height= 1)
botón_modificar.config(fg="black", bg="red", font=("Arial", 8))

botón_eliminar = TK.Button(text="Eliminar Dato", command=insertar_todos_los_datos, width= 10,height= 1)
botón_eliminar.config(fg="black", bg="blue", font=("Arial", 8))


#Aquí van las etiquetas necesarias como los datos necesarios según la tabla que se seleccione a consultar
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

label_Hora = TK.Label(mi_ventana, text=time.strftime("%H:%M:%S"))
label_Hora.config(fg="Black",bg=rosado_claro, font=("Arial", 12))
label_Hora.pack()

#En esta región crearé un textBox a prueba
txBox_Nombre = TK.Entry(mi_ventana)

txBox_FechaNacimiento = TK.Entry(mi_ventana)

txBox_Nota = TK.Entry(mi_ventana)


#En esta región tendrá RadioButtons
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

#En esta región habrá una listBox
Lista_de_datos = TK.Listbox(mi_ventana, width= 60, height= 40)
Lista_de_datos.config(fg="blue", font=("Arial", 10))
Lista_de_datos.place(x= 750, y= 0)

#Hice un pequeño desorden dentro de mi proyecto, porque creé la función insertar y modificar datos después de declarar
#las variables entry, es decir, textbox ya que en caso contrario la función me dirá que el txBox no se encuentra
def insertar_datos(nombre_de_la_tabla):
  Nombre = txBox_Nombre.get()
  Fecha_de_Nacimiento = txBox_FechaNacimiento.get()
  Cantidad_de_notas = txBox_Nota.get()
  
  Datos_necesarios = Nombre and Cantidad_de_notas and Fecha_de_Nacimiento
  
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
        values = (Nombre, Cantidad_de_notas, Fecha_de_Nacimiento)
        query = f"INSERT INTO {nombre_de_la_tabla} (Nombre, Fecha_de_Nacimiento) VALUES (%s, %s, %s)"
        cursor.execute(query, values)
        conexión.commit()
        
        print("SE AGREGÓ LOS DATOS NECESARIOS")
        
        txBox_Nombre.delete(0, TK.END)
        txBox_FechaNacimiento.delete(0, TK.END)
        txBox_Nota.delete(0, TK.END)
        
        consultar_tabla(nombre_de_la_tabla)
    except Error as e:
      print(f"ERROR INESPERADO AL INSERTAR: {e}")
  else:
    print("No tiene todos los datos")

def modificar_datos(nombre_de_la_tabla):
  columna_seleccionada = Lista_de_datos.curselection()

  if columna_seleccionada:
    ID_Seleccionado = Lista_de_datos.get(columna_seleccionada).split('|')[3].strip()

    Nombre = txBox_Nombre.get()
    Fecha_de_Nacimiento = txBox_FechaNacimiento.get()
    Cantidad_de_Notas = txBox_Nota.get()
  
    Datos_necesarios = Nombre and Fecha_de_Nacimiento and Cantidad_de_Notas
  
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
          values = (Nombre, Fecha_de_Nacimiento, Cantidad_de_Notas, ID_Seleccionado,)
          query = f"UPDATE {nombre_de_la_tabla} SET Nombre = %s, Fecha_de_Nacimiento = %s, WHERE ID_Alumno = %s"
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
        query = f"DELETE FROM {nombre_de_la_tabla} where ID = %s"
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