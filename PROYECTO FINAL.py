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
dorado = "#FFDF00"

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

    for fila in resultado:
      filas_formateadas = " | ".join(map(str, fila))
      Lista_de_datos.insert(TK.END, filas_formateadas)
    
    desconectar_base_de_datos(conexión)

def seleccionar_y_consultar():
  botón_seleccionado = opción.get()
  tabla = {
               1: 'alumno',
               2: 'asistencia',
               3: 'carrera',
               4: 'materia',
               5: 'profesor',
               6: 'nota'
              }
  try:
    nombre_de_la_tabla = tabla.get(botón_seleccionado)
    if nombre_de_la_tabla is None:
      raise ValueError("Selección inválida. Los valores están entre el 1 y 6")
    else:
      consultar_tabla(nombre_de_la_tabla)
  except Exception as e:
    messagebox.showerror(f"Error al consultar la tabla: {e}")
    return None

#Definí una función para poder mostrar 
#cuando uno de los radioButtons esté seleccionado
def habilitar_botones_e_inputs():
  #Este for me permite gestionar los texBox con sus respectivos labels
  #para que a la hora de seleccionar un radioButton me muestre lo necesario
  txBoxes = [
                     txBox_NombreAlumno, label_NombreAlumno, txBox_FechaNacimiento, label_FechaNacimiento, txBox_IDAlumno, label_IDAlumno,
                     txBox_EstadoDeAsistencia, label_EstadoDeAsistencia ,txBox_IDAsistencia, label_IDAsistencia,
                     txBox_NombreCarrera, label_NombreCarrera, txBox_Duración, label_Duración, txBox_IDCarrera, label_IDCarrera,
                     txBox_NombreMateria, label_NombreMateria, txBox_HorarioCorrespondiente, label_HorarioCorrespondiente, txBox_IDMateria, label_IDMateria,
                     txBox_NombreProfesor, label_NombreProfesor, txBox_HorasTrabajadas, label_HorasTrabajadas, txBox_IDProfesor, label_IDProfesor,
                     txBox_NotaCalificadaUNO, label_NotaCalificadaUNO, txBox_NotaCalificadaDOS, label_NotaCalificadaDOS, txBox_IDNota, label_IDNota
                   ]

  for widget in txBoxes:
    widget.place_forget()

  botón_seleccionado = opción.get()
  
  botón_agregar.place(x = 40, y = 100)
  botón_modificar.place(x = 40, y = 160)
  botón_eliminar.place(x = 40, y = 220)
  botón_comparar.place(x = 40, y = 280)
  
  
  label_Obligatoriedad.pack(padx= 0, pady= 200)
  
  opciones_del_widget = {
                                         1: [(txBox_NombreAlumno,label_NombreAlumno, 100), (txBox_FechaNacimiento, label_FechaNacimiento, 150), (txBox_IDAlumno, label_IDAlumno, 200)],
                                         2: [(txBox_EstadoDeAsistencia, label_EstadoDeAsistencia, 100), (txBox_IDAsistencia, label_IDAsistencia, 150)],
                                         3: [(txBox_NombreCarrera, label_NombreCarrera, 100), (txBox_Duración, label_Duración, 150), (txBox_IDCarrera, label_IDCarrera, 200)],
                                         4: [(txBox_NombreMateria, label_NombreMateria,100), (txBox_HorarioCorrespondiente, label_HorarioCorrespondiente, 150), (txBox_IDMateria, label_IDMateria, 200)],
                                         5: [(txBox_NombreProfesor, label_NombreProfesor, 100), (txBox_HorasTrabajadas, label_HorasTrabajadas, 150), (txBox_IDProfesor, label_IDProfesor, 200)],
                                         6: [(txBox_NotaCalificadaUNO, label_NotaCalificadaUNO, 50), (txBox_NotaCalificadaDOS, label_NotaCalificadaDOS, 100), (txBox_IDNota, label_IDNota, 250)]
                                       }
  
  if botón_seleccionado in opciones_del_widget:
    for entry, label, y_pos in opciones_del_widget[botón_seleccionado]:
      entry.place(x=150, y=y_pos)
      label.place(relx=0.25, rely=0.15 + (y_pos - 50) / 500)

#Este obtiene la tabla a seleccionar cuando voy a seleccionar RadioButton
def obtener_tabla_seleccionada():
  tabla = {
                1: 'alumno', 
                2: 'asistencia',
                3: 'carrera',
                4: 'materia',
                5: 'profesor',
                6: 'nota'
              }
  nombre = tabla.get(opción.get(), None)
  return nombre

#Esta función validar_datos valida los datos para evitar redundancias
def validar_datos(nombre_de_la_tabla, datos):
  #El patrón_nombre contiene una expresión regular para permitir
  #letras con acentos y otros caracteres especiales
  patrón_nombre = re.compile(r"^[\w\sáéíóúÁÉÍÓÚñÑüÜ]+$")
  patrón_númerosDecimales = re.compile(r'^\d+(,\d+)?$')
  try:
    
    validaciones = {
                              'alumno':lambda: patrón_nombre.match(datos["Nombre"]) and datetime.strptime(datos["FechaDeNacimiento"], '%Y-%m-%d'),
                              'asistencia':lambda:patrón_nombre.match(datos["Estado"]),
                              'carrera': lambda: patrón_nombre.match(datos["Nombre"]),
                              'materia': lambda: patrón_nombre.match(datos["Nombre"]) and datetime.strptime(datos["Horario"], '%H:%M'),
                              'profesor': lambda: patrón_nombre.match(datos["Nombre"]),
                              'nota': lambda: patrón_númerosDecimales.match(datos["Nota_UNO"]) and patrón_númerosDecimales.match(datos["Nota_DOS"])
                            }
    
    if not nombre_de_la_tabla in validaciones:
      messagebox.showerror("Error", "La tabla solicitada no se encuentra")
      return False
    
    if not validaciones[nombre_de_la_tabla]:
      messagebox.showerror("Error", f"Uno de los datos no están correctos en la tabla {nombre_de_la_tabla}")
      return False  
    return True
  
  except ValueError:
    messagebox.showerror("Error", "El formato de uno de los campos es incorrecto")
    return False

#En esta función obtengo todos los datos del formulario de MySQL para agregar, modificar
#y eliminar algunos datos de la tabla
def obtener_datos_de_Formulario(nombre_de_la_tabla):
  
  campos_de_la_base_de_datos = {
                                                        'alumno':  ["Nombre", "FechaDeNacimiento", "ID_Alumno"],
                                                        'asistencia': ["Estado", "ID_Asistencia"],
                                                        'carrera':  ["Nombre", "Duración", "ID_Carrera"],
                                                        'materia': ["Nombre", "Horario", "ID_Materia"],
                                                        'profesor': ["Nombre", "HorasTrabajadas", "ID_Profesor"],
                                                        'nota':       ["Nota_UNO", "Nota_DOS", "ID_Nota"]
       }
  
  datos = {}
  
  cajasDeTexto = {
                              'alumno':  (txBox_NombreAlumno, txBox_FechaNacimiento, txBox_IDAlumno),
                              'asistencia': (txBox_EstadoDeAsistencia , txBox_IDAsistencia),
                              'carrera':  (txBox_NombreCarrera, txBox_Duración, txBox_IDCarrera),
                              'materia': (txBox_NombreMateria, txBox_HorarioCorrespondiente, txBox_IDMateria),
                              'profesor': (txBox_NombreProfesor, txBox_HorasTrabajadas, txBox_IDProfesor),
                              'nota':       (txBox_NotaCalificadaUNO, txBox_NotaCalificadaDOS, txBox_IDNota), 
        }

  #Este for es más escalable que el anterior, ya que esto me solucionó el problema de que no me imprimía la Nota 1 en la listBox
  for i, campo in enumerate(campos_de_la_base_de_datos[nombre_de_la_tabla]):
   datos[campo] = cajasDeTexto[nombre_de_la_tabla][i].get()
  
  #En esta condición, valido los datos de la tabla
  #antes de realizar un alta baja y modificación
  if validar_datos(nombre_de_la_tabla, datos):
    return datos
  else:
    return None

#Esta función llamada extraerIDs y sirve
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
  IDs = {
              'alumno': "ID_Alumno",
              'asistencia': "ID_Asistencia",
              'carrera': "ID_Carrera",
              'materia': "ID_Materia",
              'profesor': "ID_Profesor",
              'nota': "ID_Nota"
            }
  return IDs.get(nombre_de_la_tabla.strip().lower())

#Esta función sirve para actualizar la hora
def actualizar_la_hora():
  label_Hora.config(text=time.strftime("%I:%M:%S %p"))
  label_Hora.pack()
  interfaz.after(1000, actualizar_la_hora)
  
def acción_doble():
  seleccionar_y_consultar()
  habilitar_botones_e_inputs()

# --- CONFIGURACIÓN DE INTERFAZ Y ELEMENTOS IMPORTANTES DE TKINTER
# PARA LAS INSTRUCCIONES GUARDADOS EN LA FUNCIÓN pantalla_principal()---
def pantalla_principal():
  
  # --- EJECUCIÓN DE LA VENTANA PRINCIPAL ---
  mi_ventana = TK.Tk()
  mi_ventana.title("Sistema Gestor de Asistencia")
  mi_ventana.geometry("1250x400")
  mi_ventana.minsize(1250, 400)
  mi_ventana.maxsize(1250, 400)
  mi_ventana.configure(bg=rosado_claro)
  mi_ventana.iconbitmap(ícono)
  mi_ventana.attributes("-alpha", 1)
  
  # --- BOTONES NECESARIOS ---
  global botón_agregar, botón_eliminar, botón_modificar, botón_comparar
  #Agregar
  botón_agregar = TK.Button(text="Agregar Dato", command=lambda:insertar_datos(obtener_tabla_seleccionada()), width= 10,height= 1)
  botón_agregar.config(fg="black", bg=verde, font=("Arial", 8))

  #Modificar
  botón_modificar = TK.Button(text="Modificar Dato", command=lambda:modificar_datos(obtener_tabla_seleccionada()), width= 10,height= 1)
  botón_modificar.config(fg="black", bg="red", font=("Arial", 8))

  #Eliminar
  botón_eliminar = TK.Button(text="Eliminar Dato", command=lambda:eliminar_datos(obtener_tabla_seleccionada()), width= 10,height= 1)
  botón_eliminar.config(fg="black", bg="blue", font=("Arial", 8))

  #Comparar
  botón_comparar = TK.Button(text="Comparar", width= 10,height= 1)
  botón_comparar.config(fg="black", bg=dorado, font=("Arial", 8))

  # --- ETIQUETAS ---
  global label_NombreAlumno, label_FechaNacimiento, label_IDAlumno, label_EstadoDeAsistencia, label_IDAsistencia, label_NombreCarrera, label_Duración, label_IDCarrera, label_NombreMateria, label_HorarioCorrespondiente, label_IDMateria, label_NombreProfesor, label_HorasTrabajadas, label_IDProfesor, label_NotaCalificadaUNO, label_NotaCalificadaDOS, label_IDNota, label_Hora, label_Obligatoriedad
  #Etiquetas para la tabla de alumno
  label_NombreAlumno = TK.Label(mi_ventana, text="Nombre del Alumno *")
  label_NombreAlumno.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

  label_FechaNacimiento = TK.Label(mi_ventana, text="Fecha que nació: Formato YYYY-MM-DD *")
  label_FechaNacimiento.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

  label_IDAlumno = TK.Label(mi_ventana, text="ID *")
  label_IDAlumno.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

  #Etiquetas para la tabla de asistencias
  
  label_EstadoDeAsistencia = TK.Label(mi_ventana, text="Estado de Asistencia *")
  label_EstadoDeAsistencia.config(fg="Black", bg=rosado_claro, font=("Arial", 12))
  
  label_IDAsistencia = TK.Label(mi_ventana, text="ID *")
  label_IDAsistencia.config(fg="Black", bg=rosado_claro, font=("Arial", 12))

  #Etiquetas para la tabla de carrera
  label_NombreCarrera = TK.Label(mi_ventana, text="Nombre de la Carrera *")
  label_NombreCarrera.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

  label_Duración = TK.Label(mi_ventana, text="Duración *")
  label_Duración.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

  label_IDCarrera = TK.Label(mi_ventana, text="ID *")
  label_IDCarrera.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

  #Etiquetas para la tabla de materia
  label_NombreMateria = TK.Label(mi_ventana, text="Nombre de la Materia *")
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
  label_NotaCalificadaUNO = TK.Label(mi_ventana, text="Calificación 1*")
  label_NotaCalificadaUNO.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

  label_NotaCalificadaDOS = TK.Label(mi_ventana, text="Calificación 2*")
  label_NotaCalificadaDOS.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

  label_Promedio = TK.Label(mi_ventana, text="Promedio")
  label_Promedio.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

  label_IDNota = TK.Label(mi_ventana, text="ID *")
  label_IDNota.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

  #Etiqueta para mostrar la hora
  label_Hora = TK.Label(mi_ventana, text="")
  label_Hora.config(fg="Black", bg=rosado_claro, font=("Arial", 25))
  #Etiqueta para indicar que significa el asterisco
  label_Obligatoriedad = TK.Label(mi_ventana, text="el * significa que son obligatorio seleccionar los datos")
  label_Obligatoriedad.config(fg="Black",bg=rosado_claro, font=("Arial", 8))

  #--- ENTRIES ---
  global txBox_NombreAlumno, txBox_FechaNacimiento, txBox_IDAlumno, txBox_EstadoDeAsistencia, txBox_IDAsistencia, txBox_NombreCarrera, txBox_Duración, txBox_IDCarrera, txBox_NombreMateria, txBox_HorarioCorrespondiente, txBox_IDMateria, txBox_NombreProfesor, txBox_HorasTrabajadas, txBox_IDProfesor,  txBox_NotaCalificadaUNO, txBox_NotaCalificadaDOS, txBox_IDNota, opción, Lista_de_datos
  #Tabla alumno
  txBox_NombreAlumno = TK.Entry(mi_ventana)
  txBox_FechaNacimiento = TK.Entry(mi_ventana)
  txBox_IDAlumno = TK.Entry(mi_ventana)

  #Tabla asistencia
  txBox_EstadoDeAsistencia = TK.Entry(mi_ventana)
  txBox_IDAsistencia = TK.Entry(mi_ventana)

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
  txBox_NotaCalificadaUNO = TK.Entry(mi_ventana)
  txBox_NotaCalificadaDOS = TK.Entry(mi_ventana)
  txBox_IDNota = TK.Entry(mi_ventana)

  # --- RADIOBUTTONS ---
  opción = TK.IntVar()

  Botón_Tabla_de_Alumno = TK.Radiobutton(mi_ventana, text="Alumno", variable=opción, value= 1, command=acción_doble)
  Botón_Tabla_de_Alumno.config(bg=rosado_claro, font=("Arial", 12))

  Botón_Tabla_de_Asistencia = TK.Radiobutton(mi_ventana, text="Asistencia", variable=opción, value= 2, command=acción_doble)
  Botón_Tabla_de_Asistencia.config(bg=rosado_claro, font=("Arial", 12))

  Botón_Tabla_de_Carrera = TK.Radiobutton(mi_ventana, text="Carrera", variable=opción, value= 3, command=acción_doble)
  Botón_Tabla_de_Carrera.config(bg=rosado_claro, font=("Arial", 12))

  Botón_Tabla_de_Materia = TK.Radiobutton(mi_ventana, text="Materia", variable=opción, value= 4, command=acción_doble)
  Botón_Tabla_de_Materia.config(bg=rosado_claro, font=("Arial", 12))

  Botón_Tabla_de_Profesor = TK.Radiobutton(mi_ventana, text="Profesor", variable=opción, value= 5, command=acción_doble)
  Botón_Tabla_de_Profesor.config(bg=rosado_claro, font=("Arial", 12))

  Botón_Tabla_de_Notas = TK.Radiobutton(mi_ventana, text="Nota", variable=opción, value= 6, command=acción_doble)
  Botón_Tabla_de_Notas.config(bg=rosado_claro, font=("Arial", 12))

  Botón_Tabla_de_Alumno.place(x= 40, y = 350)
  Botón_Tabla_de_Asistencia.place(x = 150, y = 350)
  Botón_Tabla_de_Carrera.place(x = 260, y = 350)
  Botón_Tabla_de_Materia.place(x = 370, y = 350)
  Botón_Tabla_de_Profesor.place(x = 480, y = 350)
  Botón_Tabla_de_Notas.place(x = 590, y = 350)

  #--- LISTBOX ---
  Lista_de_datos = TK.Listbox(mi_ventana, width= 40, height= 30)
  Lista_de_datos.config(fg="blue",bg=amarillo_claro, font=("Arial", 15))
  Lista_de_datos.place(x= 800, y= 0)
  
  return mi_ventana

interfaz = pantalla_principal()

#Mejoré mi función de insertar datos para agregarlo
#dinámicamente sin tener que entrar a MySQL
def insertar_datos(nombre_de_la_tabla):
  datosNecesarios = obtener_datos_de_Formulario(nombre_de_la_tabla)
  
  if datosNecesarios:
    try:
      conexión = conectar_base_de_datos()
      if conexión is None:
        messagebox.showerror("ERROR", "NO SE HA PODIDO CONECTAR A LA BASE DE DATOS")
        return
        
      cursor = conexión.cursor()
        
      campos = ', '.join(datosNecesarios.keys())
      values = ', '.join([f"'{valor}'" for valor in datosNecesarios.values()])
      query = f"INSERT INTO {nombre_de_la_tabla} ({campos}) VALUES ({values})"
      cursor.execute(query)
      conexión.commit()
      consultar_tabla(nombre_de_la_tabla)
      messagebox.showinfo("CORRECTO", "SE AGREGÓ LOS DATOS NECESARIOS")
      desconectar_base_de_datos(conexión)
      
    except Error as e:
      messagebox.showerror("ERROR", f"ERROR INESPERADO AL INSERTAR: {e}")

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
  
  datosNecesarios = obtener_datos_de_Formulario(nombre_de_la_tabla)
  CampoID = conseguir_campo_ID(nombre_de_la_tabla)
  if not datosNecesarios:
    messagebox.showwarning("FALTA DE DATOS", "FALTA LOS DATOS NECESARIOS")
    return
  try:
    with conectar_base_de_datos() as conexión:
      cursor = conexión.cursor()
      columnas = ', '.join([f"{k} = %s" for k in datosNecesarios.keys()])
      values = list(datosNecesarios.values()) + [ID_Seleccionado]
      query = f"UPDATE {nombre_de_la_tabla} SET {columnas} WHERE {CampoID} = %s"
      cursor.execute(query, values)
      conexión.commit()
      messagebox.showinfo("CORRECTO", "SE MODIFICÓ EXITOSAMENTE")
      consultar_tabla(nombre_de_la_tabla)
  except Error as e:
    messagebox.showerror("ERROR", f"ERROR INESPERADO AL MODIFICAR: {e}")
  
#Mejoré mi función de insertar datos para eliminar
#dinámicamente sin tener que entrar a MySQL y puse una
#función que extrae el ID en todas las palabras ya que
#no siempre tiene un valor fijo
def eliminar_datos(nombre_de_la_tabla):
  columna_seleccionada = Lista_de_datos.curselection()
  CampoID = conseguir_campo_ID(nombre_de_la_tabla)
  
  if not CampoID:
    messagebox.showerror("ERROR", "No se ha podido determinar el campo ID para esta tabla")
    return
  
  if columna_seleccionada:
      try:
        with conectar_base_de_datos() as conexión:
          cursor = conexión.cursor()
          for index in columna_seleccionada:
            selección = Lista_de_datos.get(index)
            ID_Seleccionado = extraerIDs(selección)
            values = (ID_Seleccionado,)
            if ID_Seleccionado is not None:
              query = f"DELETE FROM {nombre_de_la_tabla} where {CampoID} = %s"
              cursor.execute(query, values)
            else:
              messagebox.showerror("ERROR", "NO SE HA ENCONTRADO EL ID VÁLIDO")
            conexión.commit()
            consultar_tabla(nombre_de_la_tabla)
            messagebox.showinfo("ÉXITOS", "Ha sido eliminada exitosamente")
      except Error as e:
         messagebox.showerror("ERROR", f"ERROR INESPERADO AL ELIMINAR: {e}")
  else:
    messagebox.showwarning("ADVERTENCIA", "NO SELECCIONASTE NINGUNA COLUMNA")

actualizar_la_hora()
interfaz.mainloop()