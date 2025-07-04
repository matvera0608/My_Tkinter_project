import os
from mysql.connector import Error
from datetime import datetime
from tkinter import messagebox,  filedialog, font
from reportlab.pdfgen import canvas
import tkinter as tk, re
import mysql.connector as MySql
import time
from reportlab.lib.pagesizes import letter

# --- COLORES EN HEXADECIMALES ---
colores = {
    "rosado_claro": "#FFECEC",
    "rojo_claro": "#FFAEAE",
    "verde": "#00FF00",
    "rojo": "#FF0000",
    "verde_claro": "#AEFFAE",
    "azul_claro": "#6060FF",
    "amarillo_claro": "#FBFFBF",
    "dorado": "#FFDF00",
    "dorado_claro": "#FFF1A9",
    "agua": "#00FDFD",
    "agua_claro": "#A9FFFF"
}

# --- CONEXIÓN CON LA BASE DE DATOS MySQL WORKBENCH
# --- Y UN ÍCONO PARA LA IMPLEMENTACIÓN ---
#la variable dirección_del_ícono contiene la dirección de forma dinámica y variable
#para que no se vea la dirección de la computadora
dirección_del_ícono = os.path.dirname(__file__)
ícono = os.path.join(dirección_del_ícono,"escuela.ico")

def conectar_base_de_datos():
  try:
    cadena_de_conexión = MySql.connect(
        host = 'localhost',
        user = 'root',
        password = 'aHQfu3.4JW8rX/cd!K',
        database = 'escuela', )
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

#Se creó una lista para que la función extraerIDs
#funcione correctamente cuando están ocultos esos
# #campos clave.

#--- FUNCIONES DEL ABM (ALTA, BAJA Y MODIFICACIÓN) ---

lista_IDs = []
def consultar_tabla(nombre_de_la_tabla):
  global lista_IDs
  try:
    conexión = conectar_base_de_datos()
    #Mejora de la función consultar_tabla para que sea más escalable,
    #voy a hacer que cada consulta sea dinámica depediendo de la tabla que se seleccione
    #y también las consultas serán relacionadas dependiendo del ID que coincida con la tabla
    if conexión:
        cursor = conexión.cursor()
        match nombre_de_la_tabla.lower():
          case "alumno":
            cursor.execute("""SELECT a.ID_Alumno, a.Nombre, DATE_FORMAT(a.FechaDeNacimiento, '%d/%m/%Y'), a.Edad
                          FROM alumno AS a;""")
          case "asistencia":
            cursor.execute("""SELECT asis.ID_Asistencia, asis.Estado, DATE_FORMAT(asis.Fecha_Asistencia, '%d/%m/%Y'), al.Nombre
                          FROM asistencia AS asis
                          JOIN alumno AS al ON asis.ID_Alumno = al.ID_Alumno;""")
          case "carrera":
            cursor.execute("""SELECT c.ID_Carrera, c.Nombre, c.Duración
                          FROM carrera AS c;""")
          case "materia":
            cursor.execute("""SELECT m.ID_Materia, m.Nombre, c.Nombre, TIME_FORMAT(m.Horario,'%H:%i')
                          FROM materia AS m
                          JOIN carrera AS c ON m.IDCarrera = c.ID_Carrera;""")
          case "profesor":
            cursor.execute("""SELECT pro.ID_Profesor, pro.Nombre, m.Nombre, pro.HorasTrabajadas
                              FROM profesor AS pro
                              JOIN enseñanza AS e ON pro.ID_Profesor = e.ID_Profesor
                              JOIN materia AS m ON e.ID_Materia = m.ID_Materia;""")
          case "nota":
            cursor.execute("SELECT * FROM nota as n;")
          case _:
            cursor.execute(f"SELECT * FROM {nombre_de_la_tabla};")
        
        resultado = cursor.fetchall()
        Lista_de_datos.delete(0, tk.END)

        lista_IDs.clear()
        
        #Creé una variable para alinear bien los registros. El -1 sirve
        #para no contar el ID ya que está oculto
        ancho_de_tablas = [0] * (len(resultado[0]) - 1)
        
        #Este for hace que el ID se tome en cuenta a la hora de hacer
        #UPDATE o DELETE, es decir, tomar en cuenta o guardar el ID en paralelo.
        for fila in resultado:
          idReal = fila[0]
          lista_IDs.append(idReal)
          #MEJORA: la tabla nota no tiene el ID, por lo tanto necesito mostrar la primer columna del registro valor o tipoNota.
          # índice = Lista_de_datos.curselection()
          # if índice:
          #   idReal = lista_IDs[índice[0]]
          
          for i, valor in enumerate(filaVisible):
            valorTipoCadena = str(valor)
            ancho_de_tablas[i] = max(ancho_de_tablas[i], len(valorTipoCadena))
        
        formato = "|".join("{:<" + str(ancho) + "}" for ancho in ancho_de_tablas)

  
        for fila in resultado:
          #Copio la parte sin depender de su ID.
          filaVisible = list(fila[1:])
          match nombre_de_la_tabla.lower():
            case "alumno":
              filaVisible[2] = f"{filaVisible[2]} años"
            case "materia" | "profesor":
              if len(filaVisible) >= 2:
                filaVisible[2] = f"{filaVisible[2]} horas"
          filaTipoCadena = [str(valor) for valor in filaVisible]
          #Se agrega una separación para que no se vea pegado
          filaVisible = fila[1:] if nombre_de_la_tabla != "nota" else fila
          filas_formateadas = formato.format(*filaTipoCadena)
          Lista_de_datos.insert(tk.END, filas_formateadas)
    
    desconectar_base_de_datos(conexión)
  except Exception as Exc:
    messagebox.showerror("ERROR", f"Algo no está correcto o no tiene nada de datos: {Exc}")
  
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
                     txBox_FechaNacimiento, label_FechaNacimiento, txBox_NombreAlumno, label_NombreAlumno, txBox_IDAlumno, label_IDAlumno,
                     txBox_EstadoDeAsistencia, label_EstadoDeAsistencia ,txBox_FechaAsistencia, label_Fecha, txBox_FechaAsistencia, label_Fecha,
                     txBox_NombreCarrera, label_NombreCarrera, txBox_Duración, label_Duración, txBox_IDCarrera, label_IDCarrera,
                     txBox_NombreMateria, label_NombreMateria, txBox_HorarioCorrespondiente, label_HorarioCorrespondiente, txBox_IDMateria, label_IDMateria,
                     txBox_NombreProfesor, label_NombreProfesor, txBox_HorasTrabajadas, label_HorasTrabajadas, txBox_IDProfesor, label_IDProfesor,
                     txBox_Valor, label_Valor, txBox_Tipo, label_Tipo
            ]

  for widget in txBoxes:
    widget.place_forget()

  botón_seleccionado = opción.get()
  
  botón_agregar.place(x = 40, y = 100)
  botón_modificar.place(x = 40, y = 160)
  botón_eliminar.place(x = 40, y = 220)
  botón_comparar.place(x = 40, y = 280)
  botón_exportar.place(x= 20, y= 50)
  
  label_Obligatoriedad.pack(padx= 100, pady= 50)
  
  opciones_del_widget = {
                                         1: [(txBox_FechaNacimiento, label_FechaNacimiento, 100), (txBox_NombreAlumno,label_NombreAlumno, 150), (txBox_IDAlumno, label_IDAlumno, 200)],
                                         2: [(txBox_EstadoDeAsistencia, label_EstadoDeAsistencia, 100), (txBox_FechaAsistencia, label_Fecha, 150)],
                                         3: [(txBox_NombreCarrera, label_NombreCarrera, 100), (txBox_Duración, label_Duración, 150), (txBox_IDCarrera, label_IDCarrera, 200)],
                                         4: [(txBox_NombreMateria, label_NombreMateria,100), (txBox_HorarioCorrespondiente, label_HorarioCorrespondiente, 150), (txBox_IDMateria, label_IDMateria, 200)],
                                         5: [(txBox_NombreProfesor, label_NombreProfesor, 100), (txBox_HorasTrabajadas, label_HorasTrabajadas, 150), (txBox_IDProfesor, label_IDProfesor, 200)],
                                         6: [(txBox_Valor, label_Valor, 100), (txBox_Tipo, label_Tipo, 150)]
                                       }
  
  if botón_seleccionado in opciones_del_widget:
    #Este for me permite dinámicamente agregar los entrys y labels dependiendo de la tabla seleccionada
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
  if nombre is None:
    messagebox.showerror("Error", "Selección inválida. Los valores están entre el 1 y 6")
    return None
  else:
    return nombre

#Esta función validar_datos valida los datos antes de agregarlo a la listbox para evitar redundancias
def validar_datos(nombre_de_la_tabla, datos):
  #El patrón_nombre contiene una expresión regular para permitir
  #letras con acentos y otros caracteres especiales
  conexión = conectar_base_de_datos()
  cursor = conexión.cursor()
  patrón_nombre = re.compile(r'^[A-Za-záéíóúÁÉÍÓÚñÑüÜ\s]+$') #Esta variable regular contiene la expresión de solo para letras
  patrón_númerosDecimales = re.compile(r'^\d+([.,]\d+)?$')
  try:
    tabla_a_validar = {"alumno":    ["Nombre", "FechaDeNacimiento", "ID_Alumno"],
                      "materia":    ["Nombre", "Horario", "ID_Materia"],
                      "profesor":    ["Nombre", "HorasTrabajadas", "ID_Profesor"],
                      "asistencia": ["Fecha_Asistencia"],
                      "nota":          ["valorNota", "TipoNota"],
                      "carrera":     ["Nombre", "Duración", "ID_Carrera"]
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
              "Fecha_Asistencia": lambda valor: time.strptime(valor, '%Y-%m-%d')
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
                                                        'alumno':     [ "FechaDeNacimiento", "Nombre", "ID_Alumno"],
                                                        'asistencia': ["Estado", "Fecha_Asistencia"],
                                                        'carrera':    ["Nombre", "Duración", "ID_Carrera"],
                                                        'materia':    ["Nombre", "Horario", "ID_Materia"],
                                                        'profesor':   ["Nombre", "HorasTrabajadas", "ID_Profesor"],
                                                        'nota':       ["valorNota", "tipoNota"]
                                                      }
  
  datos = {}

  cajasDeTexto = {
                              'alumno':  (txBox_FechaNacimiento, txBox_NombreAlumno,  txBox_IDAlumno),
                              'asistencia': (txBox_EstadoDeAsistencia , txBox_FechaAsistencia),
                              'carrera':  (txBox_NombreCarrera, txBox_Duración, txBox_IDCarrera),
                              'materia': (txBox_NombreMateria, txBox_HorarioCorrespondiente, txBox_IDMateria),
                              'profesor': (txBox_NombreProfesor, txBox_HorasTrabajadas, txBox_IDProfesor),
                              'nota':     (txBox_Valor, txBox_Tipo)
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
# # def extraerIDs(selección):
# #   partes = selección.split('|')
# #   for parte in partes:
# #     parte = parte.strip()
# #     dígito = parte.isdigit()
# #     if dígito:
# #       return int(parte)
# #   return None

#Esta función me permite obtener el ID 
#de cualquier tabla que se encuentre en mi base de datos antes de eliminar
#ya que SQL obliga poner una condición antes de ejecutar una tarea
def conseguir_campo_ID(nombre_de_la_tabla):
  IDs = {
              'alumno': "ID_Alumno",
              'asistencia': "ID_Asistencia",
              'carrera': "ID_Carrera",
              'materia': "ID_Materia",
              'profesor': "ID_Profesor"
        }
  return IDs.get(nombre_de_la_tabla.strip().lower())

#Esta función sirve para actualizar la hora
def actualizar_la_hora(interfaz):
  
  label_Hora.config(text=time.strftime("%I:%M:%S %p"))
  label_Hora.pack()
  interfaz.after(1000, actualizar_la_hora, interfaz)
  
#acción_doble es una función que me muestra cada registro de la tabla
#y a la vez habiltar los botones y entrys
def acción_doble():
  seleccionar_y_consultar()
  habilitar_botones_e_inputs()

#Esta función me permite seleccionar datos dentro de la listBox para modificarlo 
#sin tener que presionar botón Modificar constantemente
def seleccionar_registro():
  nombre_de_la_tabla = obtener_tabla_seleccionada()
  datos = obtener_datos_de_Formulario(nombre_de_la_tabla, validarDatos=False)
  conexión = conectar_base_de_datos()
  #Esta variable consulta me permite obtener los datos de la tabla de forma ordenada dependiendo del orden de la caja de texto
  #{', '.join([campo for campo in datos.keys()])} este es un método que me permite agregar los campos en las cajas de texto de forma dinámica
  consulta = {
    nombre_de_la_tabla: f"SELECT {', '.join([campo for campo in datos.keys()])} FROM {nombre_de_la_tabla};"
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
          caja.delete(0, tk.END)
          caja.insert(0, str(valor))
    except Error as error:
      messagebox.showerror("ERROR", f"ERROR INESPERADO AL SELECCIONAR: {str(error)}")
    finally:
      if cursor:
        cursor.close()
      desconectar_base_de_datos(conexión)

# --- CONFIGURACIÓN DE INTERFAZ Y ELEMENTOS IMPORTANTES DE tkINTER
# PARA LAS INSTRUCCIONES GUARDADOS EN LA FUNCIÓN pantalla_principal()---
def pantalla_principal():
  
  global mi_ventana
  # --- EJECUCIÓN DE LA VENTANA PRINCIPAL ---
  mi_ventana = tk.Tk()
  mi_ventana.title("Sistema Gestor de Asistencia")
  mi_ventana.geometry("1250x400")
  mi_ventana.minsize(1250, 400)
  mi_ventana.maxsize(1250, 400)
  mi_ventana.configure(bg=colores["rosado_claro"])
  mi_ventana.iconbitmap(ícono)
  mi_ventana.attributes("-alpha", 1)
  mi_ventana.resizable(False, False)
  
  # --- BOTONES NECESARIOS ---
  global botón_agregar, botón_eliminar, botón_modificar, botón_comparar, botón_exportar
  
  # for botón in [botón_agregar, botón_modificar, botón_eliminar, botón_comparar, botón_exportar]:
    
  
  #Agregar
  botón_agregar = tk.Button(mi_ventana, text="Agregar Dato", command=lambda:insertar_datos(obtener_tabla_seleccionada()), width=10, height=1)
  botón_agregar.config(fg="black", bg=colores["verde"], font=("Arial", 8), cursor='hand2', activebackground=colores["verde_claro"])
  botón_agregar.bind("<Return>", ejecutar_acción_presionando_Enter)

  #Modificar
  botón_modificar = tk.Button(mi_ventana, text="Modificar Dato", command=lambda:modificar_datos(obtener_tabla_seleccionada()), width=10, height=1)
  botón_modificar.config(fg="black", bg="red", font=("Arial", 8), cursor='hand2', activebackground=colores["rojo_claro"])
  botón_modificar.bind("<Return>", ejecutar_acción_presionando_Enter)

  #Eliminar
  botón_eliminar = tk.Button(mi_ventana, text="Eliminar Dato", command=lambda:eliminar_datos(obtener_tabla_seleccionada()), width=10, height=1)
  botón_eliminar.config(fg="black", bg="blue", font=("Arial", 8), cursor='hand2', activebackground=colores["azul_claro"])
  botón_eliminar.bind("<Return>", ejecutar_acción_presionando_Enter)

  #Comparar
  botón_comparar = tk.Button(mi_ventana, text="Comparar", command=lambda:comparar_datos(obtener_tabla_seleccionada()), width=10, height=1)
  botón_comparar.config(fg="black", bg=colores["dorado"], font=("Arial", 8), cursor='hand2', activebackground=colores["dorado_claro"])
  botón_comparar.bind("<Return>", ejecutar_acción_presionando_Enter)
  
  #Exportar como PDF
  botón_exportar = tk.Button(mi_ventana, text="Exportar", command=lambda:exportar_en_PDF(obtener_tabla_seleccionada()), width=10, height=1)
  botón_exportar.config(fg="black", bg=colores["agua"], font=("Arial", 8), cursor='hand2', activebackground=colores["agua_claro"])
  botón_exportar.bind("<Return>", ejecutar_acción_presionando_Enter)
  

  # --- ETIQUETAS ---
  global label_NombreAlumno, label_FechaNacimiento, label_IDAlumno, label_EstadoDeAsistencia, label_Fecha, label_NombreCarrera, label_Duración, label_IDCarrera, label_NombreMateria, label_HorarioCorrespondiente, label_IDMateria, label_NombreProfesor, label_HorasTrabajadas, label_IDProfesor, label_Valor, label_Tipo, label_Hora, label_Obligatoriedad
  #Etiquetas para la tabla de alumno
  label_NombreAlumno = tk.Label(mi_ventana, text="Nombre del Alumno *")
  label_NombreAlumno.config(fg="Black",bg=colores["rosado_claro"], font=("Arial", 12))

  label_FechaNacimiento = tk.Label(mi_ventana, text="Fecha que nació: Formato Año-Mes-Día *")
  label_FechaNacimiento.config(fg="Black",bg=colores["rosado_claro"], font=("Arial", 12))

  label_IDAlumno = tk.Label(mi_ventana, text="ID *")
  label_IDAlumno.config(fg="Black",bg=colores["rosado_claro"], font=("Arial", 12))

  #Etiquetas para la tabla de asistencias
  
  label_EstadoDeAsistencia = tk.Label(mi_ventana, text="Estado de Asistencia *")
  label_EstadoDeAsistencia.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))
  
  label_Fecha = tk.Label(mi_ventana, text="Fecha que asistió *")
  label_Fecha.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  #Etiquetas para la tabla de carrera
  label_NombreCarrera = tk.Label(mi_ventana, text="Nombre de la Carrera *")
  label_NombreCarrera.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  label_Duración = tk.Label(mi_ventana, text="Duración *")
  label_Duración.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  label_IDCarrera = tk.Label(mi_ventana, text="ID *")
  label_IDCarrera.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  #Etiquetas para la tabla de materia
  label_NombreMateria = tk.Label(mi_ventana, text="Nombre de la Materia *")
  label_NombreMateria.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  label_HorarioCorrespondiente = tk.Label(mi_ventana, text="Horario correspondiente: Formato %H:%M *")
  label_HorarioCorrespondiente.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  label_IDMateria = tk.Label(mi_ventana, text="ID *")
  label_IDMateria.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  #Etiquetas para la tabla de profesor
  label_NombreProfesor = tk.Label(mi_ventana, text="Nombre del Profesor *")
  label_NombreProfesor.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  label_HorasTrabajadas = tk.Label(mi_ventana, text="Horas trabajadas *")
  label_HorasTrabajadas.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  label_IDProfesor = tk.Label(mi_ventana, text="ID *")
  label_IDProfesor.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  #Etiquetas para la tabla de nota
  label_Valor = tk.Label(mi_ventana, text="Nota*")
  label_Valor.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  label_Tipo = tk.Label(mi_ventana, text="Tipo*")
  label_Tipo.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  #Etiqueta para mostrar la hora
  label_Hora = tk.Label(mi_ventana, text="")
  label_Hora.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 10))
  #Etiqueta para indicar que significa el asterisco
  label_Obligatoriedad = tk.Label(mi_ventana, text="el * significa que son obligatorio seleccionar los datos")
  label_Obligatoriedad.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 8))

  #--- ENTRIES ---
  global txBox_NombreAlumno, txBox_FechaNacimiento, txBox_IDAlumno, txBox_EstadoDeAsistencia, txBox_FechaAsistencia, txBox_NombreCarrera, txBox_Duración, txBox_IDCarrera, txBox_NombreMateria, txBox_HorarioCorrespondiente, txBox_IDMateria, txBox_NombreProfesor, txBox_HorasTrabajadas, txBox_IDProfesor,  txBox_Valor, txBox_Tipo, txBox_IDNota, opción, Lista_de_datos
  #Tabla alumno
  txBox_NombreAlumno = tk.Entry(mi_ventana)
  txBox_FechaNacimiento = tk.Entry(mi_ventana)
  txBox_IDAlumno = tk.Entry(mi_ventana)

  #Tabla asistencia
  txBox_EstadoDeAsistencia = tk.Entry(mi_ventana)
  txBox_FechaAsistencia = tk.Entry(mi_ventana)

  #Tabla carrera
  txBox_NombreCarrera = tk.Entry(mi_ventana)
  txBox_Duración = tk.Entry(mi_ventana)
  txBox_IDCarrera = tk.Entry(mi_ventana)

  #Tabla materia
  txBox_NombreMateria = tk.Entry(mi_ventana)
  txBox_HorarioCorrespondiente = tk.Entry(mi_ventana)
  txBox_IDMateria = tk.Entry(mi_ventana)

  #Tabla profesor
  txBox_NombreProfesor = tk.Entry(mi_ventana)
  txBox_HorasTrabajadas = tk.Entry(mi_ventana)
  txBox_IDProfesor = tk.Entry(mi_ventana)

  #Tabla nota
  txBox_Valor = tk.Entry(mi_ventana)
  txBox_Tipo = tk.Entry(mi_ventana)
  txBox_IDNota = tk.Entry(mi_ventana)

  # --- RADIOBUTTONS ---
  global Botón_Tabla_de_Alumno, Botón_Tabla_de_Asistencia, Botón_Tabla_de_Carrera, Botón_Tabla_de_Materia, Botón_Tabla_de_Profesor, Botón_Tabla_de_Notas, opción
  
  opción = tk.IntVar()

  Botón_Tabla_de_Alumno = tk.Radiobutton(mi_ventana, text="Alumno", variable=opción, value= 1, command=lambda:acción_doble())
  Botón_Tabla_de_Alumno.config(bg=colores["rosado_claro"], font=("Arial", 12), cursor='hand2')


  Botón_Tabla_de_Asistencia = tk.Radiobutton(mi_ventana, text="Asistencia", variable=opción, value= 2, command=lambda: acción_doble())
  Botón_Tabla_de_Asistencia.config(bg=colores["rosado_claro"], font=("Arial", 12), cursor='hand2')


  Botón_Tabla_de_Carrera = tk.Radiobutton(mi_ventana, text="Carrera", variable=opción, value= 3, command=lambda:acción_doble())
  Botón_Tabla_de_Carrera.config(bg=colores["rosado_claro"], font=("Arial", 12), cursor='hand2')


  Botón_Tabla_de_Materia = tk.Radiobutton(mi_ventana, text="Materia", variable=opción, value= 4, command=lambda:acción_doble())
  Botón_Tabla_de_Materia.config(bg=colores["rosado_claro"], font=("Arial", 12), cursor='hand2')


  Botón_Tabla_de_Profesor = tk.Radiobutton(mi_ventana, text="Profesor", variable=opción, value= 5, command=lambda:acción_doble())
  Botón_Tabla_de_Profesor.config(bg=colores["rosado_claro"], font=("Arial", 12), cursor='hand2')


  Botón_Tabla_de_Notas = tk.Radiobutton(mi_ventana, text="Nota", variable=opción, value= 6, command=lambda:acción_doble())
  Botón_Tabla_de_Notas.config(bg=colores["rosado_claro"], font=("Arial", 12), cursor='hand2')


  Botón_Tabla_de_Alumno.place(x= 40, y = 350)
  Botón_Tabla_de_Asistencia.place(x = 150, y = 350)
  Botón_Tabla_de_Carrera.place(x = 260, y = 350)
  Botón_Tabla_de_Materia.place(x = 370, y = 350)
  Botón_Tabla_de_Profesor.place(x = 480, y = 350)
  Botón_Tabla_de_Notas.place(x = 590, y = 350)
  Botón_Tabla_de_Alumno.focus_set()
  
  #--- LISTBOX ---
  barraDesplazadora()
  
  actualizar_la_hora(mi_ventana)
  
  mi_ventana.bind_all("<Key>", mover_con_flechas)
    
  return mi_ventana

#Mejoré mi función de insertar datos para agregarlo
#dinámicamente sin tener que entrar a MySQL
def insertar_datos(nombre_de_la_tabla):
  conexión = conectar_base_de_datos()
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
      entry.delete(0, tk.END)
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
    selección = columna_seleccionada[0]
    ID_Seleccionado = lista_IDs[selección]
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
      print(f"Edad actualizada: {values}")
      messagebox.showinfo("CORRECTO", "SE MODIFICÓ EXITOSAMENTE")
      #Este for me limpia los campos de texto después de agregarlo
      #para que no quede el último valor que se agregó y se repita continuamente
      for i, (campo, valor) in enumerate(datosNecesarios.items()):
        entry = cajasDeTexto[nombre_de_la_tabla][i]
        entry.delete(0, tk.END)
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
            ID_Seleccionado = lista_IDs[index]
            if ID_Seleccionado is not None:
              query = f"DELETE FROM {nombre_de_la_tabla} where {CampoID} = %s"
              cursor.execute(query, (ID_Seleccionado,))
              #Este for me limpia los campos de texto después de agregarlo
              #para que no quede el último valor que se agregó y se repita continuamente
              for i, (campo, valor) in enumerate(datosNecesarios.items()):
                entry = cajasDeTexto[nombre_de_la_tabla][i]
                entry.delete(0, tk.END)
            else:
              messagebox.showerror("ERROR", "NO SE HA ENCONTRADO EL ID VÁLIDO")
            conexión.commit()
            consultar_tabla(nombre_de_la_tabla)
            print(f"Eliminando de {nombre_de_la_tabla} con {CampoID} = {ID_Seleccionado}")
            messagebox.showinfo("ÉXITOS", "Ha sido eliminada exitosamente")
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
    elegir_Tabla = tk.simpledialog.askstring("Comparar", "Ingrese el nombre de la tabla a comparar: ")

    if elegir_Tabla is None:
      return None #Ocurre cuando el usuario presiona cancelar en el cuadro de texto
    else:
      elegir_Tabla = elegir_Tabla.strip().lower() #Acá verifico que el usuario no ingrese espacios en blanco al principio o al final del nombre de la tabla, 
                                                                          #si por casualidad el mismo lo pone corta los espacios y lo convierte a minúscula.
      tabla_a_seleccionar = {
        "alumno": Botón_Tabla_de_Alumno,
        "asistencia": Botón_Tabla_de_Asistencia,
        "carrera": Botón_Tabla_de_Carrera,
        "profesor": Botón_Tabla_de_Profesor,
        "materia": Botón_Tabla_de_Materia,
        "nota": Botón_Tabla_de_Notas
      }
      
      #Esta variable guarda el botón seleccionado dependiendo de la tabla que elija el usuario
      #y si no existe, me tira un error de que no se ha ingresado ninguna tabla
      botónSeleccionado = tabla_a_seleccionar.get(elegir_Tabla)
      
      if not botónSeleccionado:
        messagebox.showerror("ERROR", "NO SE HA INGRESADO NINGUNA TABLA")
        return
      
      botónSeleccionado.select() #Esto selecciona el botón correspondiente a la tabla elegida por el usuario
      
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
        
    cursor.execute(consulta)
    resultado = cursor.fetchall()

    #Controlo que haya resultados, en caso contrario, me imprime un mensaje de que no hay resultados para criterios específicos
    if not resultado:
      messagebox.showinfo("SIN RESULTADOS", "NO SE ENCONTRARON REGISTROS PARA LOS CRITERIOS ESPECÍFICOS")
      return
    
    Lista_de_datos.delete(0, tk.END)
    
    for fila in resultado:
      Lista_de_datos.insert(tk.END, " | ".join(map(lambda x: str(x) if x is not None else "", fila )))
    
  except Error as e:
     messagebox.showerror("ERROR", f"HA OCURRIDO UN ERROR AL RELACIONAR LA TABLA CON LA OTRA: {str(e)}")
  finally:
    desconectar_base_de_datos(conexión)

#En este código voy a exportar en PDF el archivo de datos tkinter
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
    
    datos = Lista_de_datos.get(0, tk.END)
    
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

# --- EVENTOS PARA BOTONES ---

#Esta función me permite desplazar con barra verticalmente
#la ListBox para que se pueda ver muchos registros en la tabla
def barraDesplazadora():
  global Lista_de_datos, Frame_Lista
  # Definimos un frame con tamaño fijo y evitamos que se redimensione automáticamente
  Frame_Lista = tk.Frame(mi_ventana, width=400, height=500)
  Frame_Lista.pack(side=tk.RIGHT, padx=10, pady=10)
  Frame_Lista.pack_propagate(False)
  
  barraVertical = tk.Scrollbar(Frame_Lista, orient="vertical")
  barraVertical.pack(side=tk.RIGHT, fill=tk.Y)
  
  #Acá creé una barra de desplazamiento horizontal para desplazar
  #en la tabla donde dice materias cuando son largas
  barraHorizontal = tk.Scrollbar(Frame_Lista, orient="horizontal")
  barraHorizontal.pack(side=tk.BOTTOM, fill=tk.X)
  
  # La ListBox se define con dimensiones menores para no ocupar toda la pantalla
  Lista_de_datos = tk.Listbox(Frame_Lista, exportselection=0, width=90, height=40)
  Lista_de_datos.config(fg="blue", bg=colores["amarillo_claro"], font=("Courier New", 15, "bold"))
  Lista_de_datos.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
  
  Lista_de_datos.config(yscrollcommand=barraVertical.set)
  Lista_de_datos.config(xscrollcommand=barraHorizontal.set)
  barraVertical.config(command=Lista_de_datos.yview)
  barraHorizontal.config(command=Lista_de_datos.xview)
  
  Lista_de_datos.bind("<<ListboxSelect>>", manejar_selección)
  Lista_de_datos.bind("<Down>", mover_con_flechas)
  Lista_de_datos.bind("<Up>", mover_con_flechas)
  
#Esta función maneja la selección de la ListBox con todos los registros de la base de datos
#y me permite seleccionar un registro para modificarlo o eliminarlo más facilemnte
def manejar_selección(event=None):
  global cajasDeTexto
  índice_seleccionado = Lista_de_datos.curselection()
  if índice_seleccionado:
    Lista_de_datos.activate(índice_seleccionado[0])
    Lista_de_datos.selection_set(índice_seleccionado[0])
    seleccionar_registro()
  else:
    try:
      for txBox in cajasDeTexto.values():
        txBox.delete(0, tk.END)
    except:
      return

#Este evento me sirve para agregar, modificar y eliminar un registro de la tabla
#sin la necesidad de tener que presionar el botón cada vez que quiero agregar, modificar o eliminar un registro haciendo click en la ListBox
def ejecutar_acción_presionando_Enter(event):
  if event.widget == botón_agregar:
    insertar_datos(obtener_tabla_seleccionada())
  elif event.widget == botón_modificar:
    modificar_datos(obtener_tabla_seleccionada())
  elif event.widget == botón_eliminar:
    eliminar_datos(obtener_tabla_seleccionada())
  elif event.widget == botón_comparar:
    comparar_datos(obtener_tabla_seleccionada())
  elif event.widget == botón_exportar:
    exportar_en_PDF(obtener_tabla_seleccionada())
  return "break"
  
#Esta función sirve para mover con flechas tanto en la ListBox, entre los RadioButtons y entre los 5 botones funcionales.
def mover_con_flechas(event=None):
  global Lista_de_datos, caja_activa
  
  #En lugar de sólo crear condiciones con expresiones lógicas, lo que hago es guardar en una variable
  #para ser más entendible y que mi programa esté más castellanizado
  
  widget = event.widget
  tecla = event.keysym
  
  botones_funcionales = [ botón_agregar,
                                        botón_modificar, 
                                        botón_eliminar, 
                                        botón_comparar, 
                                        botón_exportar
                                      ]
  
  botones_excluyentes = [  Botón_Tabla_de_Alumno, 
                                          Botón_Tabla_de_Asistencia, 
                                          Botón_Tabla_de_Carrera,
                                          Botón_Tabla_de_Materia,
                                          Botón_Tabla_de_Profesor,
                                          Botón_Tabla_de_Notas
                                        ]
  
  cajasDeTexto = [ txBox_FechaNacimiento, txBox_NombreAlumno, txBox_IDAlumno, 
                             txBox_EstadoDeAsistencia, txBox_FechaAsistencia, 
                             txBox_NombreCarrera, txBox_Duración, txBox_IDCarrera, 
                             txBox_NombreMateria, txBox_HorarioCorrespondiente, txBox_IDMateria, 
                             txBox_NombreProfesor, txBox_HorasTrabajadas, txBox_IDProfesor, 
                             txBox_Valor, txBox_Tipo
                            ]
  
  caja_activa = []
  
  desde_lista_izquierda_hacia_caja = widget == Lista_de_datos and tecla == "Left"
  desde_lista_derecha_hacia_caja = widget == Lista_de_datos and tecla == "Right"
  
  tabla_de_alumno = opción.get() == 1
  tabla_de_asistencia = opción.get() == 2
  tabla_de_carrera = opción.get() == 3
  tabla_de_materia = opción.get() == 4
  tabla_de_profesor = opción.get() == 5
  tabla_de_nota = opción.get() == 6
  
  tecla_hacia_arriba = tecla == "Up"
  tecla_hacia_abajo = tecla == "Down"
  tecla_hacia_derecha = tecla == "Right"
  tecla_hacia_izquierda = tecla == "Left"
  
  en_la_lista = widget == Lista_de_datos
  en_los_botonesExcluyentes = widget in botones_excluyentes
  en_las_cajasDeTexto = widget in cajasDeTexto
  en_los_botonesCRUD = widget in botones_funcionales
  
  # Si el foco está en la ListBox, navegamos sus elementos. Pero esta sección es sólo para mover los registros
  if en_la_lista:
    if tecla_hacia_arriba and Lista_de_datos.curselection():
      índice_seleccionado = Lista_de_datos.curselection()[0]
      if índice_seleccionado > 0:
        Lista_de_datos.selection_clear(índice_seleccionado)
        Lista_de_datos.selection_set(índice_seleccionado - 1)
        Lista_de_datos.activate(índice_seleccionado - 1)
        seleccionar_registro()
        return "break"
    elif tecla_hacia_abajo and Lista_de_datos.curselection():
      índice_seleccionado = Lista_de_datos.curselection()[0]
      if índice_seleccionado < Lista_de_datos.size() - 1:
        Lista_de_datos.selection_clear(índice_seleccionado)
        Lista_de_datos.selection_set(índice_seleccionado + 1)
        Lista_de_datos.activate(índice_seleccionado + 1)
        seleccionar_registro()
        return "break"

    #Acá lo que hace es mover el foco desde la ListBox hacia la caja de texto correspondiente
    if desde_lista_izquierda_hacia_caja or desde_lista_derecha_hacia_caja:
      if tabla_de_alumno:
          txBox_NombreAlumno.focus_set()
          caja_activa = [txBox_FechaNacimiento, txBox_NombreAlumno, txBox_IDAlumno]
      elif tabla_de_asistencia:
          txBox_EstadoDeAsistencia.focus_set()
          caja_activa = [txBox_EstadoDeAsistencia, txBox_FechaAsistencia]
      elif tabla_de_carrera:
          txBox_NombreCarrera.focus_set()
          caja_activa = [txBox_NombreCarrera, txBox_Duración, txBox_IDCarrera]
      elif tabla_de_materia:
          txBox_NombreMateria.focus_set()
          caja_activa = [txBox_NombreMateria, txBox_HorarioCorrespondiente, txBox_IDMateria]
      elif tabla_de_profesor:
          txBox_NombreProfesor.focus_set()
          caja_activa = [txBox_NombreProfesor, txBox_HorasTrabajadas, txBox_IDProfesor]
      elif tabla_de_nota:
          txBox_Valor.focus_set()
          caja_activa = [txBox_Valor, txBox_Tipo]
      return "break"
    
  # Si el foco está en alguno de los RadioButtons, navegamos entre ellos.
  elif en_los_botonesExcluyentes:
    índice_actual = botones_excluyentes.index(widget)
    if tecla_hacia_izquierda:
      nuevo_índice =  (índice_actual - 1) % len(botones_excluyentes)
      botones_excluyentes[nuevo_índice].focus_set()
      return "break"
    elif tecla_hacia_derecha:
      nuevo_índice =  (índice_actual + 1) % len(botones_excluyentes)
      botones_excluyentes[nuevo_índice].focus_set()
      return "break"
    
  # Si el foco está en alguno de los 5 botones funcionales, navegamos entre ellos.
  elif en_los_botonesCRUD:
    índice_actual = botones_funcionales.index(widget)
    if tecla_hacia_arriba:
      botones_funcionales[índice_actual - 1].focus_set()
      return "break"
    elif tecla_hacia_abajo:
      botones_funcionales[índice_actual + 1].focus_set()
      return "break"
    
  # Estando en el foco de cajas de texto, lo que haré es activar el evento
  # que suba sin depender sólamente del mouse
  elif en_las_cajasDeTexto:
    if not caja_activa:
      if en_las_cajasDeTexto:
        if tabla_de_alumno:
          caja_activa = [txBox_FechaNacimiento, txBox_NombreAlumno, txBox_IDAlumno]
        elif tabla_de_asistencia:
          caja_activa = [txBox_EstadoDeAsistencia, txBox_FechaAsistencia]
        elif tabla_de_carrera:
          caja_activa = [txBox_NombreCarrera, txBox_Duración, txBox_IDCarrera]
        elif tabla_de_materia:
          caja_activa = [txBox_NombreMateria, txBox_HorarioCorrespondiente, txBox_IDMateria]
        elif tabla_de_profesor:
          caja_activa = [txBox_NombreProfesor, txBox_HorasTrabajadas, txBox_IDProfesor]
        elif tabla_de_nota:
          caja_activa = [txBox_Valor, txBox_Tipo]
      else:
        print("No hay cajas activas")
        
    if widget not in caja_activa:
      print("Widget no está en caja activa")
      return "break"
    
    índice_actual = caja_activa.index(widget)

    if tecla_hacia_arriba:
      nuevo_índice =  (índice_actual - 1) % len(caja_activa)
      caja_activa[nuevo_índice].focus_set()
      return "break"

    elif tecla_hacia_abajo:
      nuevo_índice =  (índice_actual + 1) % len(caja_activa)
      caja_activa[nuevo_índice].focus_set()
      return "break"


# --- INICIO DEL SISTEMA ---
interfaz = pantalla_principal()

interfaz.mainloop()