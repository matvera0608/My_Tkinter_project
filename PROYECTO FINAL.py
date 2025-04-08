import os
from mysql.connector import Error
from datetime import datetime
from tkinter import messagebox,  filedialog
from reportlab.pdfgen import canvas
import tkinter as TK, re
import mysql.connector as MySql
import time
from reportlab.lib.pagesizes import letter

# --- COLORES EN HEXADECIMALES ---
rosado_claro = "#FEE"
rojo_claro= "#FFAEAE"
verde = "#00FF00"
verde_claro = "#AEFFAE"
azul_claro = "#8932FF"
amarillo_claro = "#FBFFBF"
dorado = "#FFDF00"
dorado_claro = "#FFF1A9"
agua = "#00FDFD"
agua_claro = "#A9FFFF"

# --- CONEXIÓN CON LA BASE DE DATOS MySQL WORKBENCH
# --- Y UN ÍCONO PARA LA IMPLEMENTACIÓN ---
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
  botón_exportar.place(x= 20, y= 50)
  
  label_Obligatoriedad.pack(padx= 0, pady= 150)
  
  opciones_del_widget = {
                                         1: [(txBox_NombreAlumno,label_NombreAlumno, 100), (txBox_FechaNacimiento, label_FechaNacimiento, 150), (txBox_IDAlumno, label_IDAlumno, 200)],
                                         2: [(txBox_EstadoDeAsistencia, label_EstadoDeAsistencia, 100), (txBox_IDAsistencia, label_IDAsistencia, 150)],
                                         3: [(txBox_NombreCarrera, label_NombreCarrera, 100), (txBox_Duración, label_Duración, 150), (txBox_IDCarrera, label_IDCarrera, 200)],
                                         4: [(txBox_NombreMateria, label_NombreMateria,100), (txBox_HorarioCorrespondiente, label_HorarioCorrespondiente, 150), (txBox_IDMateria, label_IDMateria, 200)],
                                         5: [(txBox_NombreProfesor, label_NombreProfesor, 100), (txBox_HorasTrabajadas, label_HorasTrabajadas, 150), (txBox_IDProfesor, label_IDProfesor, 200)],
                                         6: [(txBox_NotaCalificadaUNO, label_NotaCalificadaUNO, 100), (txBox_NotaCalificadaDOS, label_NotaCalificadaDOS, 150), (txBox_IDNota, label_IDNota, 200)]
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

#Esta función validar_datos valida los datos antes de agregarlo a la listbox para evitar redundancias
def validar_datos(nombre_de_la_tabla, datos):
  #El patrón_nombre contiene una expresión regular para permitir
  #letras con acentos y otros caracteres especiales
  conexión = conectar_base_de_datos()
  cursor = conexión.cursor()
  patrón_nombre = re.compile(r"^[A-Za-záéíóúÁÉÍÓÚñÑüÜ\s]+$") #Esta variable regular contiene la expresión de solo para letras
  patrón_númerosDecimales = re.compile(r'^\d+([.,]\d+)?$')
  try:
    tabla_a_validar = {"alumno" : ["Nombre", "FechaDeNacimiento", "ID_Alumno"],
                                  "materia": ["Nombre", "Horario", "ID_Materia"],
                                  "profesor": ["Nombre", "HorasTrabajadas", "ID_Profesor"],
                                  "nota" : ["ID_Nota"],
                                  "asistencia": ["ID_Asistencia"],
                                  "carrera" : ["Nombre", "Duración", "ID_Carrera"]
                                  }
    
    if nombre_de_la_tabla in tabla_a_validar:
      campo = tabla_a_validar[nombre_de_la_tabla]
      
      if len(campo) == 1:
        consulta = f"SELECT COUNT(*) FROM {nombre_de_la_tabla} WHERE {campo[0]} = %s"
        cursor.execute(consulta, (datos[campo[0]],))
      elif len(campo) > 1:
        consulta = f"SELECT COUNT(*) FROM {nombre_de_la_tabla} WHERE {campo[0]} = %s AND {campo[1]} = %s AND {campo[2]} = %s"
        cursor.execute(consulta, (datos[campo[0]], datos[campo[1]], datos[campo[2]]))
      resultado = cursor.fetchone()
    else:
      messagebox.showerror("Error", "La tabla solicitada no se encuentra")
      return False
  
    
    validaciones = {
      'alumno': {
              "Nombre": lambda valor:patrón_nombre.match(valor),
              "FechaDeNacimiento": lambda valor: valor.strip() and time.strptime(valor, '%Y-%m-%d'),
              "ID_Alumno": lambda valor: valor.isdigit()
      },
      'asistencia': {
              "Estado": lambda valor: valor.isalpha(),
              "ID_Asistencia": lambda valor: valor.isdigit()
      },
      'carrera': {
              "Nombre": lambda valor :patrón_nombre.match(valor),
              "Duración": lambda valor :re.match(r'^[A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ\s]+$', valor), #en Duración cambié la expresión regular para que acepte letras, números y espacios.
              "ID_Carrera": lambda valor: valor.isdigit()
      },
      'materia': {
              "Nombre": lambda valor :patrón_nombre.match(valor),
              "Horario": lambda valor :datetime.strptime(valor, '%H:%M'),
              "ID_Materia": lambda valor: valor.isdigit()
      },
      'profesor': {
              "Nombre": lambda valor :patrón_nombre.match(valor),
              "HorasTrabajadas": lambda valor :patrón_númerosDecimales.match(valor),
              "ID_Profesor": lambda valor: valor.isdigit()
      },
      'nota': {
              "Nota_UNO": lambda valor :patrón_númerosDecimales.match(valor),
              "Nota_DOS": lambda valor :patrón_númerosDecimales.match(valor),
              "ID_Nota": lambda valor: valor.isdigit()
      }
    }
    
    if not nombre_de_la_tabla in validaciones:
      messagebox.showerror("Error", "La tabla solicitada no se encuentra")
      return False
    #en este for controlo que los datos estén puestos correctamente, en caso contrario
    #no me agregan o modifican. Condiciones a llevar en cuenta:
    #no se puede agregar con campos totalmente vacíos
    #el formato debe cumplir estrictamente con las validaciones, que es un diccionario para control
    for campo, valor in datos.items():
      if campo in validaciones[nombre_de_la_tabla] and not valor.strip():
        messagebox.showerror("Error", "Los campos no pueden estar vacíos")
        return False
      elif campo in validaciones[nombre_de_la_tabla] and not validaciones[nombre_de_la_tabla][campo](valor):
        messagebox.showerror("Error", f"El campo {campo} tiene un formato inválido con valor {valor}")
        return False
      elif campo == "Estado" and valor.lower() not in ["presente", "ausente"]:
         messagebox.showerror("Error", "La asistencia sólo permite poner presente o ausente")
         return False
      elif campo in ["Nota_UNO", "Nota_DOS"]:
        if not patrón_númerosDecimales.match(valor):
          messagebox.showerror("Error", f"El campo {campo} tiene que ser un número válido")
          return False
        elif (float(valor) < 1 or float(valor) > 10):
          messagebox.showerror("Error", f"El campo que tiene una nota menor que 1 o mayor que 10 es {campo}")
          return False
        
      #en esta condición verifico si el valor ya existe en la base de datos o si un registro se repite o no
      if resultado and resultado[0] > 0:
        messagebox.showwarning("Advertencia", f"El valor '{valor}' en '{campo}' ya existe en la base de datos")
        return False
         
  except ValueError as vE:
    messagebox.showerror("Error", F"El formato de uno de los campos es incorrecto: {str(vE)}")
    return False
  finally:
    desconectar_base_de_datos(conexión)

  return True

#En esta función obtengo todos los datos del formulario de MySQL para agregar, modificar
#y eliminar algunos datos de la tabla

def obtener_datos_de_Formulario(nombre_de_la_tabla, validarDatos):
  global cajasDeTexto, datos
  
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

  #Este for es más escalable, ya que esto me solucionó el problema de que no me imprimía la Nota 1 en la listBox
  for índice, campo in enumerate(campos_de_la_base_de_datos[nombre_de_la_tabla]):
   datos[campo] = cajasDeTexto[nombre_de_la_tabla][índice].get()
  
  #En esta condición, valido los datos de la tabla
  #antes de agregarlo a la listBox. Puse un condicional
  #donde si las entrys de cada registro, no me tiren error. Además validarDatos
  #como variable me sirve para que no me tire error de que no existe la tabla antes de indicar un registro de la listBox
  if validarDatos:
    if validar_datos(nombre_de_la_tabla, datos):
      return datos
    else:
      return None
  else:
    return datos

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
#de cualquier tabla que se encuentre en mi base de datos antes de eliminar
#ya que SQL obliga poner una condición antes de ejecutar una tarea
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
  
#acción_doble es una función que me muestra cada registro de la tabla
#y a la vez habiltar los botones y entrys
def acción_doble():
  seleccionar_y_consultar()
  habilitar_botones_e_inputs()

#Esta función me permite seleccionar datos dentro de la listBox para modificarlo 
#sin tener que presionar botón Modificar constantemente
def seleccionar_registro():
  nombre_de_la_tabla = obtener_tabla_seleccionada()
  conexión = conectar_base_de_datos()
  consulta = {
    f"{nombre_de_la_tabla}": f"SELECT * FROM {nombre_de_la_tabla};"
    }
  if conexión:
    try:
      cursor = conexión.cursor()
      cursor.execute(consulta[nombre_de_la_tabla])
      selección = Lista_de_datos.curselection()
      resultado = cursor.fetchall()
    
      if not resultado:
        messagebox.showwarning("ADVERTENCIA", "NO HAY DATOS EN LA TABLA")
        return
    
      if selección:
        fila_seleccionada = resultado[selección[0]]
        #Este if me permite controlar que nombre de la tabla no exista en la caja de textos pueda llamar a la función obtener_datos_de_Formulario
        #y no me tire error de que no existe la tabla en la base de datos, además para que pueda agregarlo a la listBox.
        obtener_datos_de_Formulario(nombre_de_la_tabla, validarDatos=False)
          
        #Este for me limpia los campos de texto después de agregarlo
        for caja, valor in zip(cajasDeTexto[nombre_de_la_tabla], fila_seleccionada):
          caja.delete(0, TK.END)
          caja.insert(0, str(valor))
    except Error as error:
      messagebox.showerror("ERROR", f"ERROR INESPERADO AL SELECCIONAR: {str(error)}")
    finally:
      if cursor:
        cursor.close()
      desconectar_base_de_datos(conexión)

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
  global botón_agregar, botón_eliminar, botón_modificar, botón_comparar, botón_exportar
  #Agregar
  botón_agregar = TK.Button(text="Agregar Dato", command=lambda:insertar_datos(obtener_tabla_seleccionada()), width= 10,height= 1)
  botón_agregar.config(fg="black", bg=verde, font=("Arial", 8), cursor='hand2', activebackground=verde_claro)

  #Modificar
  botón_modificar = TK.Button(text="Modificar Dato", command=lambda:modificar_datos(obtener_tabla_seleccionada()), width= 10,height= 1)
  botón_modificar.config(fg="black", bg="red", font=("Arial", 8), cursor='hand2', activebackground=rojo_claro)

  #Eliminar
  botón_eliminar = TK.Button(text="Eliminar Dato", command=lambda:eliminar_datos(obtener_tabla_seleccionada()), width= 10,height= 1)
  botón_eliminar.config(fg="black", bg="blue", font=("Arial", 8), cursor='hand2', activebackground=azul_claro)

  #Comparar
  botón_comparar = TK.Button(text="Comparar",command=lambda:comparar_datos(obtener_tabla_seleccionada()), width= 10,height= 1)
  botón_comparar.config(fg="black", bg=dorado, font=("Arial", 8), cursor='hand2', activebackground=dorado_claro)
  
  botón_exportar = TK.Button(text="Exportar",command=lambda:exportar_en_PDF(obtener_tabla_seleccionada()), width=10, height=1)
  botón_exportar.config(fg="black", bg=agua, font=("Arial", 8), cursor='hand2', activebackground=agua_claro)

  # --- ETIQUETAS ---
  global label_NombreAlumno, label_FechaNacimiento, label_IDAlumno, label_EstadoDeAsistencia, label_IDAsistencia, label_NombreCarrera, label_Duración, label_IDCarrera, label_NombreMateria, label_HorarioCorrespondiente, label_IDMateria, label_NombreProfesor, label_HorasTrabajadas, label_IDProfesor, label_NotaCalificadaUNO, label_NotaCalificadaDOS, label_IDNota, label_Hora, label_Obligatoriedad
  #Etiquetas para la tabla de alumno
  label_NombreAlumno = TK.Label(mi_ventana, text="Nombre del Alumno *")
  label_NombreAlumno.config(fg="Black",bg=rosado_claro, font=("Arial", 12))

  label_FechaNacimiento = TK.Label(mi_ventana, text="Fecha que nació: Formato Año-Mes-Día *")
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

  Botón_Tabla_de_Alumno = TK.Radiobutton(mi_ventana, text="Alumno", variable=opción, value= 1, command=lambda:acción_doble())
  Botón_Tabla_de_Alumno.config(bg=rosado_claro, font=("Arial", 12), cursor='hand2')

  Botón_Tabla_de_Asistencia = TK.Radiobutton(mi_ventana, text="Asistencia", variable=opción, value= 2, command=lambda: acción_doble())
  Botón_Tabla_de_Asistencia.config(bg=rosado_claro, font=("Arial", 12), cursor='hand2')

  Botón_Tabla_de_Carrera = TK.Radiobutton(mi_ventana, text="Carrera", variable=opción, value= 3, command=lambda:acción_doble())
  Botón_Tabla_de_Carrera.config(bg=rosado_claro, font=("Arial", 12), cursor='hand2')

  Botón_Tabla_de_Materia = TK.Radiobutton(mi_ventana, text="Materia", variable=opción, value= 4, command=lambda:acción_doble())
  Botón_Tabla_de_Materia.config(bg=rosado_claro, font=("Arial", 12), cursor='hand2')

  Botón_Tabla_de_Profesor = TK.Radiobutton(mi_ventana, text="Profesor", variable=opción, value= 5, command=lambda:acción_doble())
  Botón_Tabla_de_Profesor.config(bg=rosado_claro, font=("Arial", 12), cursor='hand2')

  Botón_Tabla_de_Notas = TK.Radiobutton(mi_ventana, text="Nota", variable=opción, value= 6, command=lambda:acción_doble())
  Botón_Tabla_de_Notas.config(bg=rosado_claro, font=("Arial", 12), cursor='hand2')

  Botón_Tabla_de_Alumno.place(x= 40, y = 350)
  Botón_Tabla_de_Asistencia.place(x = 150, y = 350)
  Botón_Tabla_de_Carrera.place(x = 260, y = 350)
  Botón_Tabla_de_Materia.place(x = 370, y = 350)
  Botón_Tabla_de_Profesor.place(x = 480, y = 350)
  Botón_Tabla_de_Notas.place(x = 590, y = 350)

  #--- LISTBOX ---
  Lista_de_datos = TK.Listbox(mi_ventana, width= 90, height= 30)
  Lista_de_datos.config(fg="blue",bg=amarillo_claro, font=("Arial", 8))
  Lista_de_datos.place(x= 800, y= 0)
  Lista_de_datos.bind("<<ListboxSelect>>", manejar_selección)
  #--- SCROLLBAR ---
  
  return mi_ventana

def manejar_selección(event):
  seleccionar_registro()

interfaz = pantalla_principal()

#Mejoré mi función de insertar datos para agregarlo
#dinámicamente sin tener que entrar a MySQL
def insertar_datos(nombre_de_la_tabla):
  conexión = conectar_base_de_datos()
  if conexión is None:
    messagebox.showerror("ERROR DE CONEXIÓN", "NO SE HA PODIDO CONECTAR A LA BASE DE DATOS")
    return
  else:
    print("CONEXIÓN EXITOSA", "SE HA CONECTADO A LA BASE DE DATOS")
    datosNecesarios = obtener_datos_de_Formulario(nombre_de_la_tabla, validarDatos=True)
    if not datosNecesarios:
      return
    try:
      cursor = conexión.cursor()
      campos = ', '.join(datosNecesarios.keys())
      values = ', '.join([f"'{valor}'" for valor in datosNecesarios.values()])
      query = f"INSERT INTO {nombre_de_la_tabla} ({campos}) VALUES ({values})"
      cursor.execute(query)
      conexión.commit()
      consultar_tabla(nombre_de_la_tabla)
      messagebox.showinfo("CORRECTO", "SE AGREGÓ LOS DATOS NECESARIOS")
      #Este for me limpia los campos de texto después de agregarlo
      #para que no quede el último valor que se agregó y se repita continuamente
      for i, (campo, valor) in enumerate(datosNecesarios.items()):
        entry = cajasDeTexto[nombre_de_la_tabla][i]
        entry.delete(0, TK.END)
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
  else:
    selección = Lista_de_datos.get(columna_seleccionada[0])
    ID_Seleccionado = extraerIDs(selección)
    if ID_Seleccionado is None:
      messagebox.showerror("ERROR", "NO SE HA ENCONTRADO EL ID VÁLIDO")
      return
  
  datosNecesarios = obtener_datos_de_Formulario(nombre_de_la_tabla, validarDatos=True)
  CampoID = conseguir_campo_ID(nombre_de_la_tabla)
  if not datosNecesarios:
    return
  try:
    with conectar_base_de_datos() as conexión:
      cursor = conexión.cursor()
      columnas = ', '.join([f"{k} = %s" for k in datosNecesarios.keys()])
      values = list(datosNecesarios.values()) + [ID_Seleccionado]
      query = f"UPDATE {nombre_de_la_tabla} SET {columnas} WHERE {CampoID} = %s"
      cursor.execute(query, values)
      conexión.commit()
      consultar_tabla(nombre_de_la_tabla)
      messagebox.showinfo("CORRECTO", "SE MODIFICÓ EXITOSAMENTE")
      #Este for me limpia los campos de texto después de agregarlo
      #para que no quede el último valor que se agregó y se repita continuamente
      for i, (campo, valor) in enumerate(datosNecesarios.items()):
        entry = cajasDeTexto[nombre_de_la_tabla][i]
        entry.delete(0, TK.END)
      desconectar_base_de_datos(conexión)
  except Error as e:
    messagebox.showerror("ERROR", f"ERROR INESPERADO AL MODIFICAR: {e}")
  
#Mejoré mi función de insertar datos para eliminar
#dinámicamente sin tener que entrar a MySQL y puse una
#función que extrae el ID en todas las palabras ya que
#no siempre tiene un valor fijo
def eliminar_datos(nombre_de_la_tabla):
  columna_seleccionada = Lista_de_datos.curselection()
  datosNecesarios = obtener_datos_de_Formulario(nombre_de_la_tabla, validarDatos=False)
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
            #Este for me limpia los campos de texto después de agregarlo
            #para que no quede el último valor que se agregó y se repita continuamente
            for i, (campo, valor) in enumerate(datosNecesarios.items()):
              entry = cajasDeTexto[nombre_de_la_tabla][i]
              entry.delete(0, TK.END)
      except Error as e:
         messagebox.showerror("ERROR", f"ERROR INESPERADO AL ELIMINAR: {e}")
  else:
    messagebox.showwarning("ADVERTENCIA", "NO SELECCIONASTE NINGUNA COLUMNA")

#En esta función comparar relaciono una tabla con la otra
#pero coincidiendo cada valor para que se pueda leer con facilidad
#y saber si uno de los alumnos están presentes o no
def comparar_datos(nombre_de_la_tabla):
  try:
    conexión = conectar_base_de_datos()
    if conexión is None:
      messagebox.showerror("ERROR DE CONEXIÓN", "NO SE PUDO CONECTAR A LA BASE DE DATOS")
      return
    cursor = conexión.cursor()
    
    #Ahora actualicé más la función para que pueda elegir la tabla a comparar.
    #Puse una ventana que dispare un cuadro de texto para que el usuario pueda elegir la tabla a comparar escribiendo el nombre de la tabla.
    elegir_Tabla = TK.simpledialog.askstring("Comparar", "Ingrese el nombre de la tabla a comparar: ")
    if elegir_Tabla is None:
      return None
    else:
      match elegir_Tabla:
        case "alumno":
          consulta = "SELECT alumno.Nombre, asistencia.Estado FROM alumno JOIN asistencia on alumno.ID_Alumno = asistencia.ID_Asistencia;"
        case "asistencia":
          consulta = "SELECT asistencia.Estado, alumno.Nombre FROM asistencia JOIN alumno on asistencia.ID_Asistencia = alumno.ID_Alumno;"
        case "carrera":
          consulta = "SELECT carrera.Nombre, alumno.Nombre FROM carrera JOIN alumno on carrera.ID_Carrera = alumno.ID_Alumno;"
        case "profesor":
          consulta = "SELECT profesor.Nombre, materia.Nombre FROM profesor JOIN materia on profesor.ID_Profesor = materia.ID_Materia;"
        case "materia":
          consulta = "SELECT materia.Nombre, materia.Horario, profesor.Nombre FROM materia JOIN profesor on materia.ID_Materia = profesor.ID_Profesor;"
        case "nota":
          consulta = "SELECT nota.Promedio, nota.Estado, alumno.Nombre FROM nota JOIN alumno on nota.ID_Nota = alumno.ID_Alumno;"
        case _:
          messagebox.showerror("ERROR", "LA TABLA NO EXISTE EN LA BASE DE DATOS")
          return
    
    # query = {
    #               'alumno': """
    #               SELECT a.Nombre, b.Estado
    #               FROM alumno a
    #               JOIN asistencia b ON a.ID_Alumno = b.ID_Asistencia; 
    #               """,
    #              'nota': """
    #               SELECT  n.Promedio, a.Nombre
    #               FROM alumno a
    #               JOIN nota n ON a.ID_Alumno = n.ID_Nota;
    #              """,
    #              'carrera': """
    #               SELECT  c.Nombre, a.Nombre
    #               FROM alumno a
    #               JOIN carrera c ON a.ID_Alumno = c.ID_Carrera;
    #              """,
    #               'profesor': """
    #               SELECT  p.Nombre, m.Nombre
    #               FROM materia m
    #               JOIN profesor p ON m.ID_Materia = p.ID_Profesor;
    #              """,
    #               'asistencia': """
    #               SELECT  a.Estado, p.Nombre
    #               FROM profesor p
    #               JOIN asistencia a ON p.ID_Profesor = a.ID_Asistencia;
    #              """,
    #               'materia': """
    #               SELECT  m.Nombre, m.Horario, p.Nombre
    #               FROM profesor p
    #               JOIN materia m ON p.ID_Profesor = m.ID_Materia;
    #              """,
    #             }
    # sql_query = query.get(nombre_de_la_tabla, None)
    
    # #Controlo que la tabla seleccionada coincida con el diccionario de query
    
    # if sql_query is None:
    #   messagebox.showerror("ERROR", "NO SE ENCONTRÓ LA TABLA ESPECIFICADA")
    #   return
    
    cursor.execute(consulta)
    resultado = cursor.fetchall()

    #Controlo que haya resultados, en caso contrario, me imprime un mensaje de que no hay resultados para criterios específicos
    if not resultado:
      messagebox.showinfo("SIN RESULTADOS", "NO SE ENCONTRARON REGISTROS PARA LOS CRITERIOS ESPECÍFICOS")
      return
    
    Lista_de_datos.delete(0, TK.END)
    
    for fila in resultado:
      Lista_de_datos.insert(TK.END, " | ".join(map(lambda x: str(x) if x is not None else "", fila )))
    
  except Error as e:
     messagebox.showerror("ERROR", f"HA OCURRIDO UN ERROR AL RELACIONAR LA TABLA CON LA OTRA: {str(e)}")
  finally:
    desconectar_base_de_datos(conexión)

#En este código voy a exportar en PDF el archivo de datos Tkinter
def exportar_en_PDF(nombre_de_la_tabla):
  try:
    conexión = conectar_base_de_datos()
    if conexión is None:
      return

    cursor = conexión.cursor()
    
    match nombre_de_la_tabla:
      case 'alumno':
        consulta = "SELECT * FROM alumno"
      case 'asistencia':
        consulta = "SELECT * FROM asistencia"
      case 'carrera':
        consulta = "SELECT * FROM carrera"
      case 'materia':
        consulta = "SELECT * FROM materia"
      case 'profesor':
        consulta = "SELECT * FROM profesor"
      case 'nota':
        consulta = "SELECT * FROM nota"
      case _:
        messagebox.showerror("ERROR", "NO SE ENCONTRÓ LA TABLA ESPECIFICADA")
        return
      
    cursor.execute(consulta)
    fila = cursor.fetchall()
    
    datos = Lista_de_datos.get(0, TK.END)
    
    ventana_exportar = filedialog.asksaveasfilename(
      defaultextension=".pdf",
      filetypes=[("Archivo PDF","*.pdf")],
      initialfile="Sistema Gestor de Asistencia",
      title="Exportar archivo PDF"
    )
    
    #Cuando presione cancelar, se ejecuta este código
    if not ventana_exportar:
      return
    
    #aquí empiezo a crear el archivo PDF para exportar la información del Sistema Gestor de Asistencias 
    canva = canvas.Canvas(ventana_exportar)
    canva.setFont("Helvetica", 20)
    y = 780
    
    canva = canvas.Canvas(ventana_exportar, pagesize=letter)
    y -= 20
    #Aquí empiezo a iterar los datos para luego imprimir el reporte
    for fila in datos:
      canva.drawString(100, y, f"{fila}")
      y -= 20
      
    canva.save()
    
    messagebox.showwarning("ÉXITOS", "EXPORTADO CORRECTAMENTE")
    
  except Error as e:
    messagebox.showerror("OCURRIÓ UN ERROR", f"Error al exportar en PDF la información detallada: {str(e)}")
  
actualizar_la_hora()
interfaz.mainloop()