import os
from mysql.connector import Error
from datetime import datetime
from tkinter import messagebox
import mysql.connector as MySql
import time
import tkinter as TK, re

# --- COLORES EN HEXADECIMALES ---
rosado_claro = "#FEE"
verde = "#00FF00"
amarillo_claro = "#FBFFBF"

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
  for widget in [  txBox_NombreAlumno, label_NombreAlumno, txBox_FechaNacimiento, label_FechaNacimiento, txBox_IDAlumno, label_IDAlumno, 
                   txBox_NombreCarrera, label_NombreCarrera, txBox_Duración, label_Duración, txBox_IDCarrera, label_IDCarrera,
                   txBox_NombreMateria, label_NombreMateria, txBox_HorarioCorrespondiente, label_HorarioCorrespondiente, txBox_IDMateria, label_IDMateria,
                   txBox_NombreProfesor, label_NombreProfesor, txBox_HorasTrabajadas, label_HorasTrabajadas, txBox_IDProfesor, label_IDProfesor,
                   txBox_NotaCalificada, label_NotaCalificada, txBox_CantidadNotas, txBox_Promedio, label_Promedio, txBox_IDNota, label_IDNota ]:
      widget.place_forget()

  botón_seleccionado = opción.get()
  
  if botón_seleccionado in (1, 2, 3, 4, 5):
    botón_agregar.place(x=60,y= 100)
    botón_modificar.place(x=60,y= 160)
    botón_eliminar.place(x=60,y= 220)
    label_Obligatoriedad.pack(padx= 10, pady= 10)
    
    match botón_seleccionado:
      case 1:
        txBox_NombreAlumno.place(x=150, y= 100)
        label_NombreAlumno.place(relx=0.25, rely=0.155)
        txBox_FechaNacimiento.place(x=150, y= 150)
        label_FechaNacimiento.place(relx=0.25, rely=0.25)
        txBox_IDAlumno.place(x=150, y= 200)
        label_IDAlumno.place(relx=0.25, rely=0.345)
      case 2:
        txBox_NombreCarrera.place(x=150, y= 100)
        label_NombreCarrera.place(relx=0.25, rely=0.155)
        txBox_Duración.place(x=150, y= 150)
        label_Duración.place(relx=0.25, rely=0.25)
        txBox_IDCarrera.place(x=150, y= 200)
        label_IDCarrera.place(relx=0.25, rely=0.345)
      case 3:
        txBox_NombreMateria.place(x=150, y= 100)
        label_NombreMateria.place(relx=0.25, rely=0.155)
        txBox_HorarioCorrespondiente.place(x=150, y= 150)
        label_HorarioCorrespondiente.place(relx=0.25, rely=0.25)
        txBox_IDMateria.place(x=150, y= 200)
        label_IDMateria.place(relx=0.25, rely=0.345)
      case 4:
        txBox_NombreProfesor.place(x=150, y= 100)
        label_NombreProfesor.place(relx=0.25, rely=0.155)
        txBox_HorasTrabajadas.place(x=150, y= 150)
        label_HorasTrabajadas.place(relx=0.25, rely=0.25)
        txBox_IDProfesor.place(x=150, y= 200)
        label_IDProfesor.place(relx=0.25, rely=0.345)
      case 5:
        txBox_CantidadNotas.place(x=150, y= 150)
        label_CantidadNotas.place(relx=0.25, rely=0.25)
        txBox_Promedio.place(x=150, y= 200)
        label_Promedio.place(relx=0.25, rely=0.345)
        txBox_IDNota.place(x=150, y= 250)
        label_IDNota.place(relx=0.25, rely=0.420)
      case _:
          print("ES NECESARIO SELECCIONAR")

#Este obtiene la tabla a seleccionar cuando voy a seleccionar RadioButton
def obtener_tabla_seleccionada():
  tabla = {1: 'alumno', 2: 'carrera', 3: 'materia', 4: 'profesor', 5: 'nota'}
  nombre = tabla.get(opción.get(), None)
  return nombre

#Esta función validar_datos valida los datos para evitar redundancias
def validar_datos(nombre_de_la_tabla, datos):
  #El patron_nombre contiene una expresión regular para permitir
  #letras con acentos y otros caracteres especiales
  patron_nombre = re.compile(r"^[\w\sáéíóúÁÉÍÓÚñÑüÜ]+$")
  patrón_númerosDecimales = re.compile([r'^\d+(,\d+)?$'])
  
  try:
    match nombre_de_la_tabla:
      case 'alumno':
        if not patron_nombre.match(datos["Nombre"]):
          messagebox.showerror("Error", "El nombre del alumno necesita contener letras")
          return False
        datetime.strptime(datos["FechaDeNacimiento"], '%Y-%m-%d')
    
      case 'carrera':
        if not patron_nombre.match(datos["Nombre"]):
          messagebox.showerror("Error", "El nombre de la carrera necesita contener letras")
          return False
    
      case 'materia':
        if not patron_nombre.match(datos["Nombre"]):
          messagebox.showerror("Error", "El nombre de la materia necesita contener letras")
          return False
        datetime.strptime(datos["HorarioMateria"], '%H:%M')
    
      case 'profesor':
        if not patron_nombre.match(datos["Nombre"]):
          messagebox.showerror("Error", "El nombre del profesor necesita contener letras")
          return False
    
      case 'nota':
        if not patrón_númerosDecimales.match(["NúmeroDeNota"]):
          messagebox.showerror("Error", "La nota calificada permite sólo números")
          return False
      
        if not datos["CantidadDeNotas"].isdigit():
          messagebox.showerror("Error", "La cantidad de notas permite sólo números")
          return False
      case _:
        messagebox.showerror("Error", "No existe la tabla o la misma es desconocida")
        return False
    #Se retorna verdadero cuando las validaciones son correctas
    return True
  except ValueError:
    messagebox.showerror("Error", "El formato de uno de los campos es incorrecto")
    return False

def obtener_datos_de_Formulario(nombre_de_la_tabla):
  
  campos_de_la_base_de_datos = {'alumno': ["Nombre", "FechaDeNacimiento"],
                                'carrera': ["Nombre", "Duración"],
                                'materia': ["Nombre", "HorarioMateria"],
                                'profesor': ["Nombre", "HorasTrabajadas"],
                                'nota': ["NúmeroDeNota", "CantidadNotas"]
                                }
  
  datos = {}
  
  cajasDeTexto = {'alumno': (txBox_NombreAlumno, txBox_FechaNacimiento),
                  'carrera': (txBox_NombreCarrera, txBox_Duración),
                  'materia': (txBox_NombreMateria, txBox_HorarioCorrespondiente),
                  'profesor': (txBox_NombreProfesor, txBox_HorasTrabajadas),
                  'nota': (txBox_NotaCalificada, txBox_CantidadNotas), 
                  }
  
  for campo in campos_de_la_base_de_datos[nombre_de_la_tabla]:
    if campo == "Nombre":
      datos[campo] = cajasDeTexto[nombre_de_la_tabla][0].get()
    elif campo in ["FechaDeNacimiento", "Duración", "HorarioMateria","HorasTrabajadas","NúmeroDeNota", "CantidadNotas"]:
      datos[campo] = cajasDeTexto[nombre_de_la_tabla][1].get()

  print(datos)
  
  if validar_datos(nombre_de_la_tabla, datos):
    return datos
  else:
    return None

#Esta función llamada extraerIDs sirve
#para que pueda modificar y eliminar datos de una tabla dinámicamente
def extraerIDs(selección):
  partes = selección.split('|')
  for parte in partes:
    parte = parte.strip()
    dígito = parte.isdigit()
    if dígito:
      return int(parte)
  return None

#Esta función me permite obtener el ID 
#de cualquier tabla que se encuentre en mi base de datos
def conseguir_campo_ID(nombre_de_la_tabla):
  nombre_de_la_tabla = nombre_de_la_tabla.strip().lower() 
  match nombre_de_la_tabla:
    case 'alumno':
      return "ID_Alumno"
    case 'carrera':
      return "ID_Carrera"
    case 'materia':
      return "ID_Materia"
    case 'profesor':
      return "ID_Profesor"
    case 'nota':
      return "ID_Nota"

def doble_acción():
  habilitar_botones_e_inputs()
  
  seleccionar_y_consultar()

def deseleccionar_RadioButton(Event):
  opción.set(0)
  Lista_de_datos.delete(0, TK.END)
  habilitar_botones_e_inputs()

#Esta función sirve para actualizar la hora
def actualizar_la_hora():
  label_Hora.config(text=time.strftime("%H:%M:%S"))
  mi_ventana.after(1000, actualizar_la_hora)
  
# --- CONFIGURACIÓN DE INTERFAZ Y ELEMENTOS IMPORTANTES DE TKINTER PARA LAS INSTRUCCIONES---
mi_ventana = TK.Tk()
mi_ventana.title("Sistema Gestor de Asistencia")
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
label_NombreAlumno = TK.Label(mi_ventana, text="Nombre del Alumno *")
label_NombreAlumno.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

label_FechaNacimiento = TK.Label(mi_ventana, text="Fecha que nació: Formato YYYY-MM-DD *")
label_FechaNacimiento.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

label_IDAlumno = TK.Label(mi_ventana, text="ID *")
label_IDAlumno.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

#Etiquetas para la tabla de carrera
label_NombreCarrera = TK.Label(mi_ventana, text="Nombre de la Carrera *")
label_NombreCarrera.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

label_Duración = TK.Label(mi_ventana, text="Duración *")
label_Duración.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

label_IDCarrera = TK.Label(mi_ventana, text="ID *")
label_IDCarrera.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

#Etiquetas para la tabla de materia
label_NombreMateria = TK.Label(mi_ventana, text="Nombre de la Materia*")
label_NombreMateria.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

label_HorarioCorrespondiente = TK.Label(mi_ventana, text="Horario correspondiente: Formato %H:%M *")
label_HorarioCorrespondiente.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

label_IDMateria = TK.Label(mi_ventana, text="ID *")
label_IDMateria.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

#Etiquetas para la tabla de profesor
label_NombreProfesor = TK.Label(mi_ventana, text="Nombre del Profesor *")
label_NombreProfesor.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

label_HorasTrabajadas = TK.Label(mi_ventana, text="Horas trabajadas *")
label_HorasTrabajadas.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

label_IDProfesor = TK.Label(mi_ventana, text="ID *")
label_IDProfesor.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

#Etiquetas para la tabla de nota
label_NotaCalificada = TK.Label(mi_ventana, text="Calificación *")
label_NotaCalificada.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

label_CantidadNotas = TK.Label(mi_ventana, text="Cantidad *")
label_CantidadNotas.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

label_Promedio = TK.Label(mi_ventana, text="Promedio")
label_Promedio.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

label_IDNota = TK.Label(mi_ventana, text="ID *")
label_IDNota.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

#Etiqueta para mostrar la hora
label_Hora = TK.Label(mi_ventana, text=time.strftime("%H:%M:%S"))
label_Hora.config(fg="Black",bg=rosado_claro, font=("Arial", 12))
label_Hora.pack()

#Etiqueta para indicar que significa el asterisco
label_Obligatoriedad = TK.Label(mi_ventana, text="el * significa que son obligatorio seleccionar los datos")
label_Obligatoriedad.config(fg="Black",bg=rosado_claro, font=("Arial", 8))

#--- ENTRIES ---

#Tabla alumno
txBox_NombreAlumno = TK.Entry(mi_ventana)
txBox_FechaNacimiento = TK.Entry(mi_ventana)
txBox_IDAlumno = TK.Entry(mi_ventana)

#Tabla carrera
txBox_NombreCarrera = TK.Entry(mi_ventana)
txBox_Duración = TK.Entry(mi_ventana)
txBox_IDCarrera = TK.Entry(mi_ventana)

#Tabla materia
txBox_NombreMateria = TK.Entry(mi_ventana)
txBox_HorarioCorrespondiente = TK.Entry(mi_ventana)
txBox_IDMateria = TK.Entry(mi_ventana)

#Tabla profesor
txBox_NombreProfesor = TK.Entry(mi_ventana)
txBox_HorasTrabajadas = TK.Entry(mi_ventana)
txBox_IDProfesor = TK.Entry(mi_ventana)

#Tabla nota
txBox_NotaCalificada = TK.Entry(mi_ventana)
txBox_CantidadNotas = TK.Entry(mi_ventana)
txBox_Promedio = TK.Entry(mi_ventana)
txBox_IDNota = TK.Entry(mi_ventana)

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

#Mejoré mi función de insertar datos para agregarlo
#dinámicamente sin tener que entrar a MySQL
def insertar_datos(nombre_de_la_tabla):
  
  datosNecesarios = obtener_datos_de_Formulario(nombre_de_la_tabla)
  
  if datosNecesarios:
    conexión = conectar_base_de_datos()
    
    try:
      if conexión:
        cursor = conexión.cursor()
        columnas = ', '.join(datosNecesarios.keys())
        marcador_de_posiciones = ', '.join(['%s'] * len(datosNecesarios))
        values = tuple(datosNecesarios.values())
        
        query = f"INSERT INTO {nombre_de_la_tabla} ({columnas}) VALUES ({marcador_de_posiciones})"
        cursor.execute(query, values)
        conexión.commit()
        messagebox.showinfo("CORRECTO", "SE AGREGÓ LOS DATOS NECESARIOS")
        consultar_tabla(nombre_de_la_tabla)
    except Error as e:
      messagebox.showerror("ERROR", f"ERROR INESPERADO AL INSERTAR: {e}")
    finally:
      desconectar_base_de_datos(conexión)
  else:
    messagebox.showwarning("FALTA DE DATOS", "FALTA LOS DATOS NECESARIOS")

#Mejoré mi función de insertar datos para modificarlo
#dinámicamente sin tener que entrar a MySQL y puse una
#función que extrae el ID en todas las palabras ya que
#no siempre tiene un valor fijo
def modificar_datos(nombre_de_la_tabla):
  columna_seleccionada = Lista_de_datos.curselection()
  if not columna_seleccionada:
    messagebox.showwarning("ADVERTENCIA", "FALTA SELECCIONAR UNA COLUMNA")
    return

  selección = Lista_de_datos.get(columna_seleccionada[0])
  ID_Seleccionado = extraerIDs(selección)
  if ID_Seleccionado is None:
      messagebox.showerror("ERROR", "NO SE HA ENCONTRADO EL ID VÁLIDO")
      return
  Datos_necesarios = obtener_datos_de_Formulario(nombre_de_la_tabla)
  CampoID = conseguir_campo_ID(nombre_de_la_tabla)
  if not Datos_necesarios:
    messagebox.showwarning("FALTA DE DATOS", "FALTA LOS DATOS NECESARIOS")
    return
  
  try:
    with conectar_base_de_datos() as conexión:
      cursor = conexión.cursor()
      columnas = ', '.join([f"{k} = %s" for k in Datos_necesarios.keys()])
      values = list(Datos_necesarios.values()) + [ID_Seleccionado]
      query = f"UPDATE {nombre_de_la_tabla} SET {columnas} WHERE {CampoID} = %s"
      print("QUERY:",query)
      print("VALUES",values)
      cursor.execute(query, values)
      conexión.commit()
      consultar_tabla(nombre_de_la_tabla)
      messagebox.showinfo("CORRECTO", "SE MODIFICÓ EXITOSAMENTE")
  except Error as e:
    messagebox.showerror("ERROR", f"ERROR INESPERADO AL MODIFICAR: {e}")
  
#Mejoré mi función de insertar datos para eliminar
#dinámicamente sin tener que entrar a MySQL y puse una
#función que extrae el ID en todas las palabras ya que
#no siempre tiene un valor fijo
def eliminar_datos(nombre_de_la_tabla):
  columna_seleccionada = Lista_de_datos.curselection()
  CampoID = conseguir_campo_ID(nombre_de_la_tabla)
  if columna_seleccionada:
      try:
        with conectar_base_de_datos() as conexión:
          cursor = conexión.cursor()
          for index in columna_seleccionada:
            selección = Lista_de_datos.get(index)
            ID_Seleccionado = extraerIDs(selección)
            ID_Encontrado = ID_Seleccionado is not None
            if ID_Encontrado:
              values = (ID_Seleccionado,)
              query = f"DELETE FROM {nombre_de_la_tabla} where {CampoID} = %s"
              cursor.execute(query, values)
              messagebox.showinfo("ÉXITOS", f"Una columna ha sido eliminada exitosamente con id {ID_Seleccionado}")
            else:
              messagebox.showerror("ERROR", "NO SE HA ENCONTRADO EL ID VÁLIDO")
            conexión.commit()
            consultar_tabla(nombre_de_la_tabla)
      except Error as e:
         messagebox.showerror("ERROR", f"ERROR INESPERADO AL ELIMINAR: {e}")
  else:
    messagebox.showwarning("ADVERTENCIA", "NO SELECCIONASTE NINGUNA COLUMNA")

actualizar_la_hora()
mi_ventana.mainloop()