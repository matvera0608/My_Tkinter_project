import os
from mysql.connector import Error as error_sql
from datetime import datetime, date as fecha, time as hora
from tkinter import messagebox as mensajeTexto, filedialog as diálogo
from reportlab.pdfgen import canvas
import tkinter as tk, re
import mysql.connector as MySql
import time as hora_del_sistema
from reportlab.lib.pagesizes import letter
from PIL import Image, ImageTk

# --- COLORES EN HEXADECIMALES ---
colores = {
    "rosado_claro": "#FFEBEB",
    "rojo_claro": "#FFAEAE",
    "verde": "#00FF00",
    "rojo": "#FF0000",
    "verde_claro": "#AEFFAE",
    "azul": "#0000FF",
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

ruta_base = os.path.dirname(__file__)
ruta_imagen = os.path.join(ruta_base, "imágenes")

def conectar_base_de_datos():
  try:
    cadena_de_conexión = MySql.connect(
        host = 'localhost',
        user = 'root',
        password = 'admin',
        database = 'escuela', )
    conexión_exitosa = cadena_de_conexión.is_connected()
    if conexión_exitosa:
      return cadena_de_conexión
  except error_sql as e:
    print(f"Error inesperado al conectar MySql {e}")
    return None

def desconectar_base_de_datos(conexión):
  desconectando_db = conexión.is_connected()
  if desconectando_db:
    conexión.close()

#--- FUNCIONES DEL ABM (ALTA, BAJA Y MODIFICACIÓN) ---

lista_IDs = []
def consultar_tabla(nombre_de_la_tabla):
  global lista_IDs
  try:
    conexión = conectar_base_de_datos()
    if conexión:
        cursor = conexión.cursor()
        match nombre_de_la_tabla.lower():
          case "alumno":
            cursor.execute("""SELECT a.ID_Alumno, a.Nombre, DATE_FORMAT(a.FechaDeNacimiento, '%d/%m/%Y'), a.Edad
                          FROM alumno AS a;""")
          case "asistencia":
            cursor.execute("""SELECT asis.ID_Asistencia, asis.Estado, DATE_FORMAT(asis.Fecha_Asistencia, '%d/%m/%Y'), al.Nombre
                          FROM asistencia AS asis
                          JOIN alumno AS al ON asis.IDAlumno = al.ID_Alumno;""")
          case "carrera":
            cursor.execute("""SELECT c.ID_Carrera, c.Nombre, c.Duración
                          FROM carrera AS c;""")
          case "materia":
            cursor.execute("""SELECT m.ID_Materia, m.Nombre, TIME_FORMAT(m.Horario,'%H:%i'), c.Nombre
                          FROM materia AS m
                          JOIN carrera AS c ON m.IDCarrera = c.ID_Carrera;""")
          case "profesor":
            cursor.execute("""SELECT pro.ID_Profesor, pro.Nombre, m.Nombre
                              FROM profesor AS pro
                              JOIN enseñanza AS e ON e.IDProfesor = pro.ID_Profesor
                              JOIN materia AS m ON e.IDMateria = m.ID_Materia;""")
          case "nota":
            cursor.execute("""SELECT REPLACE(CAST(n.valorNota AS CHAR(10)), '.', ',') AS valorNota, tipoNota, al.Nombre, m.Nombre
                              FROM nota as n
                              JOIN alumno as al ON n.IDAlumno = al.ID_Alumno
                              JOIN materia as m ON n.IDMateria = m.ID_Materia;""")
          case _:
            cursor.execute(f"SELECT * FROM {nombre_de_la_tabla};")
        
        resultado = cursor.fetchall()
        Lista_de_datos.delete(0, tk.END)

        if not resultado:
          mensajeTexto.showinfo("Sin datos", "No hay datos disponibles para mostrar.")
          return

        lista_IDs.clear()
        
        #Creé una variable para alinear bien los registros.
        ancho_de_tablas = []
        
        #Este for hace que el ID se tome en cuenta a la hora de hacer
        #UPDATE o DELETE, es decir, tomar en cuenta o guardar el ID en paralelo.
        
        for fila in resultado:
          idReal = fila[0]
          lista_IDs.append(idReal)
          filaVisible = fila[1:] if nombre_de_la_tabla != "nota" else fila
          
          #Este controla que el ancho de las tablas se ajuste
          #dependiendo de la cantidad de registros que tenga para facilitar la lectura al usuario
          while len(ancho_de_tablas) < len(filaVisible):
            ancho_de_tablas.append(0)
          
          for i, valor in enumerate(filaVisible):
            valorTipoCadena = str(valor)
            ancho_de_tablas[i] = max(ancho_de_tablas[i], len(valorTipoCadena))
        
        formato = "|".join("{:<" + str(ancho) + "}" for ancho in ancho_de_tablas)
 
        for fila in resultado:
          filaVisible = list(fila[1:] if nombre_de_la_tabla != "nota" else fila)
          match nombre_de_la_tabla.lower():
            case "alumno":
              filaVisible[2] = f"{filaVisible[2]} años"
            case "materia":
              filaVisible[1] = f"{filaVisible[1]} horas"
          filaTipoCadena = [str(valor) for valor in filaVisible]
          #Se agrega una separación para que no se vea pegado
          if len(filaTipoCadena) == len(ancho_de_tablas):
            filas_formateadas = formato.format(*filaTipoCadena)
            Lista_de_datos.insert(tk.END, filas_formateadas)
          else:
            print("❗ Columnas desalineadas:", filaTipoCadena)
            print("🔍 Longitudes -> fila:", len(filaTipoCadena), "| ancho_de_tablas:", len(ancho_de_tablas))
    
    desconectar_base_de_datos(conexión)
  except Exception as Exc:
    mensajeTexto.showerror("ERROR", f"Algo no está correcto o no tiene nada de datos: {Exc}")
  
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
    mensajeTexto.showerror(f"Error al consultar la tabla: {e}")
    return None
#Definí una función para poder mostrar 
#cuando uno de los radioButtons esté seleccionado
def habilitar_botones_e_inputs():

  txBoxes = [
              txBox_FechaNacimiento, label_FechaNacimiento, txBox_NombreAlumno, label_NombreAlumno,
              txBox_EstadoDeAsistencia, label_EstadoDeAsistencia ,txBox_FechaAsistencia, label_Fecha, txBox_FechaAsistencia, label_Fecha,
              txBox_NombreCarrera, label_NombreCarrera, txBox_Duración, label_Duración,
              txBox_NombreMateria, label_NombreMateria, txBox_HorarioCorrespondiente, label_HorarioCorrespondiente,
              txBox_NombreProfesor, label_NombreProfesor,
              txBox_Valor, label_Valor, txBox_Tipo, label_Tipo
            ]

  for widget in txBoxes:
    widget.place_forget()

  botón_seleccionado = opción.get()
  
  # Botón Exportar (arriba a la izquierda)
  botón_exportar.place(relx=0.010, rely=0.05)
  botón_agregar.place(relx=0.010, rely=0.17)
  botón_modificar.place(relx=0.010, rely=0.29)
  botón_eliminar.place(relx=0.010, rely=0.41)
  botón_ordenar.place(relx=0.010, rely=0.53)

  
  label_Obligatoriedad.pack(padx= 100, pady= 40)
  
  opciones_del_widget = {
                                         1: [(txBox_FechaNacimiento, label_FechaNacimiento, 100), (txBox_NombreAlumno,label_NombreAlumno, 150)],
                                         2: [(txBox_EstadoDeAsistencia, label_EstadoDeAsistencia, 100), (txBox_FechaAsistencia, label_Fecha, 150)],
                                         3: [(txBox_NombreCarrera, label_NombreCarrera, 100), (txBox_Duración, label_Duración, 150)],
                                         4: [(txBox_NombreMateria, label_NombreMateria,100), (txBox_HorarioCorrespondiente, label_HorarioCorrespondiente, 150)],
                                         5: [(txBox_NombreProfesor, label_NombreProfesor, 100)],
                                         6: [(txBox_Valor, label_Valor, 100), (txBox_Tipo, label_Tipo, 150)]
                        }
  
  #Esta condición lo que hace es mover de forma proporcional el entry y label
  if botón_seleccionado in opciones_del_widget:
    #Este for me permite dinámicamente agregar los entrys y labels dependiendo de la tabla seleccionada
    for entry, label, y_pos in opciones_del_widget[botón_seleccionado]:
      label.place(relx=0.30, rely=0.15 + (y_pos - 50) / 500)
      entry.place(relx=0.15, rely=0.15 + (y_pos - 50) / 500)

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
    mensajeTexto.showerror("Error", "Selección inválida. Los valores están entre el 1 y 6")
    return None
  else:
    return nombre

#Esta función validar_datos valida los datos antes de agregarlo a la listbox para evitar redundancias
def validar_datos(nombre_de_la_tabla, datos):
  try:
    conexión = conectar_base_de_datos()
    cursor = conexión.cursor()
    patrón_nombre = re.compile(r'^[A-Za-záéíóúÁÉÍÓÚñÑüÜ\s]+$')
    patrón_númerosDecimales = re.compile(r'^\d+([.,]\d+)?$')
    patrón_alfanumérico = re.compile(r'^[A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ\s]+$')
    patron_alfanumerico_con_espacios = re.compile(r'^[A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ\s]+$')
    
    tabla_a_validar = {"alumno":    ["Nombre", "FechaDeNacimiento"],
                      "carrera":    ["Nombre", "Duración"],
                      "materia":    ["Nombre", "Horario"],
                      "profesor":   ["Nombre",],
                      "asistencia": [],
                      "nota":       ["valorNota", "TipoNota"]
                      }
    
    if nombre_de_la_tabla not in tabla_a_validar:
      mensajeTexto.showerror("Error", "La tabla solicitada no se encuentra")
      return False
    
    
    ##Este bloque de validación está bien? ME GUSTARÍA QUE VUELVA A FUNCIONAR COMO ESTABA ANTES
    ##SIN AFECTAR LA CONVERSIÓN DE FECHA Y HORA
    if nombre_de_la_tabla == "nota":
      datos = normalizar_datos_nota(datos)
      if not datos:
        return
    
    tipos_validos = {"Parcial", "Parcial 1", "Parcial 2", "Final", "TP"}
    
    validaciones = {
      'alumno': {
              "Nombre": lambda valor : patrón_nombre.match(valor),
              "FechaDeNacimiento": validar_fecha,
      },
      'asistencia': {
              "Estado": lambda valor: valor.isalpha(),
              "Fecha_Asistencia": validar_fecha,
      },
      'carrera': {
              "Nombre": lambda valor :patrón_nombre.match(valor),
              "Duración": lambda valor :patron_alfanumerico_con_espacios.match(valor),
      },
      'materia': {
              "Nombre": lambda valor :patrón_nombre.match(valor),
              "Horario": validar_hora,
      },
      'profesor': {
              "Nombre": lambda valor :patrón_nombre.match(valor),
      },
      'nota': {
              "tpoNota": lambda valor: valor.strip().title() in tipos_validos,
              "valorNota": lambda valor: patrón_númerosDecimales.match(valor),
      }
    }

    for campo, valor in datos.items():
      if campo in validaciones[nombre_de_la_tabla]:
        # Validar vacío solo si es str
        if isinstance(valor, str) and not valor.strip():
            mensajeTexto.showerror("Error", f"El campo '{campo}' está vacío.")
            return False
        validador = validaciones[nombre_de_la_tabla][campo]
        esVálido = validador(valor) if callable(validador)  else bool(validador.match(valor))
        if not esVálido:
          mensajeTexto.showerror("Error", f"El campo '{campo}' tiene un valor inválido.")
          cursor.close()
          return
    if nombre_de_la_tabla in ["alumno", "profesor", "carrera"]: 
      campo_único = "Nombre"
      cursor.execute(f"SELECT COUNT(*) FROM {nombre_de_la_tabla} WHERE {campo_único} = %s", (datos[campo_único],))
      resultado = cursor.fetchone()
      if resultado[0] > 0:
        mensajeTexto.showinfo("Aviso", "Ya existe datos repetidos")
        cursor.close()
        return False
      cursor.close()
      desconectar_base_de_datos(conexión)
      return True
  except ValueError as error_de_validación:
    print(f"Error de validación: {error_de_validación}")
    return False
  desconectar_base_de_datos(conexión)
  return True

#En esta función obtengo todos los datos del formulario de MySQL para agregar, modificar
#y eliminar algunos datos de la tabla
#ASÍ TENGO ESTA FUNCIÓN BIEN CORREGIDA.
def obtener_datos_de_Formulario(nombre_de_la_tabla, validarDatos):
  global cajasDeTexto, datos, campos_de_la_base_de_datos

  campos_de_la_base_de_datos = {
      'alumno':     ["FechaDeNacimiento", "Nombre"],
      'asistencia': ["Estado", "Fecha_Asistencia"],
      'carrera':    ["Nombre", "Duración"],
      'materia':    ["Nombre", "Horario"],
      'profesor':   ["Nombre"],
      'nota':       ["valorNota", "tipoNota"]
  }

  cajasDeTexto = {
      'alumno':  (txBox_FechaNacimiento, txBox_NombreAlumno),
      'asistencia': (txBox_EstadoDeAsistencia, txBox_FechaAsistencia),
      'carrera':  (txBox_NombreCarrera, txBox_Duración),
      'materia': (txBox_NombreMateria, txBox_HorarioCorrespondiente),
      'profesor': (txBox_NombreProfesor,),
      'nota':     (txBox_Valor, txBox_Tipo)
  }

  datos = {}

  for campo, caja in zip(campos_de_la_base_de_datos[nombre_de_la_tabla], cajasDeTexto[nombre_de_la_tabla]):
    texto = caja.get().strip()

    try:
      if texto.count("/") == 2:
        texto = datetime.strptime(texto, "%d/%m/%Y").date()
      elif texto.count(":") == 1 and len(texto) <= 5:
        texto = datetime.strptime(texto, "%H:%M").time()
    except ValueError:
      mensajeTexto.showerror("Error", f"Formato inválido en '{campo}': {texto}")
      return None
    datos[campo] = texto
  
  if validarDatos:
    if not validar_datos(nombre_de_la_tabla, datos):
      return None

  return datos


#Esta función me permite obtener el ID de cualquier tabla que se encuentre en mi base de datos antes de eliminar
#ya que SQL obliga poner una condición antes de ejecutar una tarea
def conseguir_campo_ID(nombre_de_la_tabla):
  IDs = {
              'alumno': "ID_Alumno",
              'asistencia': "ID_Asistencia",
              'carrera': "ID_Carrera",
              'materia': "ID_Materia",
              'profesor': "ID_Profesor",
              'nota': ["IDAlumno", "IDMateria"]
        }
  return IDs.get(nombre_de_la_tabla.strip().lower())

#Esta función sirve para actualizar la hora
def actualizar_la_hora(interfaz):
  label_Hora.config(text=hora_del_sistema.strftime("%I:%M:%S"), font=("Arial", 24), fg="blue", bg=None)
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
  selección = Lista_de_datos.curselection()
  
  if not selección:
    return
  índice = selección[0]
  id = lista_IDs[índice]

  if nombre_de_la_tabla == "nota":
    seleccionado = Lista_de_datos.get(índice)
    partes = seleccionado.split("|")
    
    if len(partes) > 2:
      nota = partes[0].strip()
      tipo = partes[1].strip()
      cajasDeTexto["nota"][0].delete(0, tk.END)
      cajasDeTexto["nota"][0].insert(0, nota)

      cajasDeTexto["nota"][1].delete(0, tk.END)
      cajasDeTexto["nota"][1].insert(0, tipo)
    return

  conexión = conectar_base_de_datos()
  if conexión:
    try:
      #Diccionario de claves primarias según la tabla
      PKs = {
        "alumno": "ID_Alumno",
        "asistencia": "ID_Asistencia",
        "carrera": "ID_Carrera",
        "materia": "ID_Materia",
        "profesor": "ID_Profesor",
        "nota": ["IDAlumno", "IDMateria"]
      }
      
      clave = PKs.get(nombre_de_la_tabla)
      ## Estas condiciones sobre el ID de cada tabla, cuando voy a Nota ya me tira el mensaje de que no se pudo
      ## detectar el campo ID de esta tabla
      if not clave:
        mensajeTexto.showerror("ERROR", "No se pudo determinar la superclave para esta tabla.")
        return
      cursor = conexión.cursor()
      
      # Verificamos si una clave es simple o compuesta como en el caso de la tabla Nota
      if isinstance(clave, list):
        if not isinstance(id, tuple):
          return
        datos["IDAlumno"], datos["IDMateria"] = id

        if None in id:
          mensajeTexto.showerror("ERROR", "Faltan datos de clave para la tabla.")
          return
        condiciones = ' AND '.join([f"{campo} = %s" for campo in clave])
        valores = tuple(datos.get(campo) for campo in clave)
        campos = ', '.join(datos.keys())
        consulta = f"SELECT {campos} FROM {nombre_de_la_tabla} WHERE {condiciones}"
        cursor.execute(consulta, valores)
      else:
        datos[clave] = id
        if not id:
          mensajeTexto.showerror("ERROR", "ID no especificado")
          return
        campos = ', '.join(datos.keys())
        consulta = f"SELECT {campos} FROM {nombre_de_la_tabla} WHERE {clave} = %s"
        cursor.execute(consulta, (id,))
      fila_seleccionada = cursor.fetchone()
      if fila_seleccionada is None:
        mensajeTexto.showwarning("ADVERTENCIA", "NO SE ENCONTRÓ LA FILA")
        return
      for caja, valor in zip(cajasDeTexto[nombre_de_la_tabla], fila_seleccionada):
        caja.delete(0, tk.END)
        caja.insert(0, str(valor))
      convertir_datos(nombre_de_la_tabla)
    except error_sql as error:
      mensajeTexto.showerror("ERROR", f"ERROR INESPERADO AL SELECCIONAR: {str(error)}")
    finally:
      if cursor:
        cursor.close()
      desconectar_base_de_datos(conexión)


def convertir_datos(nombre_de_la_tabla):
  for campo, caja in zip(campos_de_la_base_de_datos[nombre_de_la_tabla], cajasDeTexto[nombre_de_la_tabla]):
    valor = caja.get()
    # Si el campo es una fecha, lo convierte al formato "DD/MM/YYYY"
    if isinstance(valor, str) and "fecha" in campo.lower():
        try:
            fecha_obj = datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            continue
        valor = fecha_obj
    # Si el campo es una hora, lo convierte al formato "HH:MM"
    elif isinstance(valor, str) and "hora" in campo.lower():
        try:
            hora_obj = datetime.strptime(valor, "%H:%M:%S").strftime("%H:%M")
        except ValueError:
            continue  # Si no es una hora válida, no la convierte
        valor = hora_obj
    caja.delete(0, tk.END)  # Limpia el entry
    caja.insert(0, str(valor))  # Inserta el valor convertido


def normalizar_datos_nota(datos):
    if "tipoNota" in datos:
        valor = datos["tipoNota"].strip().lower()
        if "parcial 1" in valor or valor == "parcial1":
            datos["tipoNota"] = "Parcial 1"
        elif "parcial 2" in valor or valor == "parcial2":
            datos["tipoNota"] = "Parcial 2"
        elif "parcial" in valor:
            datos["tipoNota"] = "Parcial"
        elif "final" in valor or valor == "examen final":
            datos["tipoNota"] = "Examen Final"
        elif "tp" in valor or "trabajo" in valor:
            datos["tipoNota"] = "TP"
        else:
            return False
          
    if "valorNota" in datos:
      valor = datos["valorNota"].strip().lower().replace(",", ".")
      try:
        número = float(valor)
        datos["valorNota"] = f"{número:.2f}"
      except ValueError:
        return False
    return datos


def validar_fecha(valor):
  if isinstance(valor, fecha):
    return True
  if isinstance(valor, str):
    try:
      datetime.strptime(valor, '%d/%m/%Y').date()
      return True
    except ValueError:
      return False
  return False

def validar_hora(valor):
  if isinstance(valor, hora):
    return True # ya es una hora válida
  if isinstance(valor, str):
    try:
      datetime.strptime(valor, '%H:%M').time()
      return True
    except ValueError:
      return False
  return False

mi_ventana = tk.Tk()
#Esta función me permite cargar las imágenes de forma dinámica
#y que se puedan usar en los radioButtons.
def cargar_imagen(nombre_imagen):
  ruta = os.path.join(ruta_imagen, nombre_imagen)
  if(not os.path.exists(ruta)):
    print(f"Imagen no encontrada: {ruta}")
    return None
  imagen = Image.open(ruta)
  imagen = imagen.resize((25, 25), Image.Resampling.LANCZOS)
  return ImageTk.PhotoImage(imagen)

#Estas son imagenes implementadas para colocar en el
#radioButton.
alumno_imagen = cargar_imagen("alumno.png")
asistencia_imagen = cargar_imagen("asistencia.png")
carrera_imagen = cargar_imagen("carrera.png")
materia_imagen = cargar_imagen("materia.png")
profesor_imagen = cargar_imagen("profesor.png")
nota_imagen = cargar_imagen("nota.png")

# --- CONFIGURACIÓN DE INTERFAZ Y ELEMENTOS IMPORTANTES DE tkINTER
# PARA LAS INSTRUCCIONES GUARDADOS EN LA FUNCIÓN pantalla_principal() ---
def pantalla_principal(ventana):

  # --- EJECUCIÓN DE LA VENTANA PRINCIPAL ---
  ventana = mi_ventana
  ventana.title("Sistema Gestor de Asistencia")
  ventana.geometry("1250x625")
  ventana.minsize(1250, 100)
  ventana.configure(bg=colores["rosado_claro"])
  ventana.iconbitmap(ícono)
  ventana.attributes("-alpha", 1)

  # --- BOTONES NECESARIOS ---
  global botón_agregar, botón_eliminar, botón_modificar, botón_ordenar, botón_exportar

  #Agregar
  botón_agregar = tk.Button(ventana, text="Agregar", command=lambda:insertar_datos(obtener_tabla_seleccionada()), width=15, height=1)
  botón_agregar.config(fg="black", bg=colores["verde"], font=("Arial", 8), cursor='hand2', activebackground=colores["verde"])
  botón_agregar.bind("<Return>", ejecutar_acción_presionando_Enter)

  #Modificar
  botón_modificar = tk.Button(ventana, text="Modificar", command=lambda:modificar_datos(obtener_tabla_seleccionada()), width=15, height=1)
  botón_modificar.config(fg="black", bg="red", font=("Arial", 8), cursor='hand2', activebackground=colores["rojo"])
  botón_modificar.bind("<Return>", ejecutar_acción_presionando_Enter)

  #Eliminar
  botón_eliminar = tk.Button(ventana, text="Eliminar", command=lambda:eliminar_datos(obtener_tabla_seleccionada()), width=15, height=1)
  botón_eliminar.config(fg="black", bg="blue", font=("Arial", 8), cursor='hand2', activebackground=colores["azul"])
  botón_eliminar.bind("<Return>", ejecutar_acción_presionando_Enter)

  #Comparar
  botón_ordenar = tk.Button( ventana, text="Ordenar", command=lambda:ordenar_datos(obtener_tabla_seleccionada(), tabla=obtener_tabla_seleccionada()), width=15, height=1)
  botón_ordenar.config(fg="black", bg=colores["dorado"], font=("Arial", 8), cursor='hand2', activebackground=colores["dorado_claro"])
  botón_ordenar.bind("<Return>", ejecutar_acción_presionando_Enter)
  
  #Exportar como PDF
  botón_exportar = tk.Button(ventana, text="Exportar", command=lambda:exportar_en_PDF(obtener_tabla_seleccionada()), width=15, height=1)
  botón_exportar.config(fg="black", bg=colores["agua"], font=("Arial", 8), cursor='hand2', activebackground=colores["agua_claro"])
  botón_exportar.bind("<Return>", ejecutar_acción_presionando_Enter)
  

  # --- ETIQUETAS ---
  global label_NombreAlumno, label_FechaNacimiento, label_EstadoDeAsistencia, label_Fecha, label_NombreCarrera, label_Duración, label_NombreMateria, label_HorarioCorrespondiente, label_NombreProfesor, label_Valor, label_Tipo, label_Hora, label_Obligatoriedad
  #Etiquetas para la tabla de alumno
  label_NombreAlumno = tk.Label(ventana, text="Nombre del Alumno *")
  label_NombreAlumno.config(fg="Black",bg=colores["rosado_claro"], font=("Arial", 12))

  label_FechaNacimiento = tk.Label(ventana, text="Fecha que nació: Formato Día-Mes-Año *")
  label_FechaNacimiento.config(fg="Black",bg=colores["rosado_claro"], font=("Arial", 12))

  #Etiquetas para la tabla de asistencias

  label_EstadoDeAsistencia = tk.Label(ventana, text="Estado de Asistencia *")
  label_EstadoDeAsistencia.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  label_Fecha = tk.Label(ventana, text="Fecha que asistió *")
  label_Fecha.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  #Etiquetas para la tabla de carrera
  label_NombreCarrera = tk.Label(ventana, text="Nombre de la Carrera *")
  label_NombreCarrera.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  label_Duración = tk.Label(ventana, text="Duración *")
  label_Duración.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  #Etiquetas para la tabla de materia
  label_NombreMateria = tk.Label(ventana, text="Nombre de la Materia *")
  label_NombreMateria.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  label_HorarioCorrespondiente = tk.Label(ventana, text="Horario correspondiente: Formato %H:%M *")
  label_HorarioCorrespondiente.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  #Etiquetas para la tabla de profesor
  label_NombreProfesor = tk.Label(ventana, text="Nombre del Profesor *")
  label_NombreProfesor.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  #Etiquetas para la tabla de nota
  label_Valor = tk.Label(ventana, text="Nota*")
  label_Valor.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  label_Tipo = tk.Label(ventana, text="Tipo*")
  label_Tipo.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  #Etiqueta para mostrar la hora
  label_Hora = tk.Label(ventana, text="")
  label_Hora.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 10))
  #Etiqueta para indicar que significa el asterisco
  label_Obligatoriedad = tk.Label(ventana, text="el * significa que es obligatorio seleccionar los datos")
  label_Obligatoriedad.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 8))

  #--- ENTRIES ---
  global txBox_NombreAlumno, txBox_FechaNacimiento, txBox_EstadoDeAsistencia, txBox_FechaAsistencia, txBox_NombreCarrera, txBox_Duración, txBox_NombreMateria, txBox_HorarioCorrespondiente, txBox_NombreProfesor, txBox_Valor, txBox_Tipo, opción, Lista_de_datos
  #Tabla alumno
  txBox_NombreAlumno = tk.Entry(ventana)
  txBox_NombreAlumno.config(width=30)
  txBox_FechaNacimiento = tk.Entry(ventana)
  txBox_FechaNacimiento.config(width=30)

  #Tabla asistencia
  txBox_EstadoDeAsistencia = tk.Entry(ventana)
  txBox_EstadoDeAsistencia.config(width=30)
  txBox_FechaAsistencia = tk.Entry(ventana)
  txBox_FechaAsistencia.config(width=30)

  #Tabla carrera
  txBox_NombreCarrera = tk.Entry(ventana)
  txBox_NombreCarrera.config(width=30)
  txBox_Duración = tk.Entry(ventana)
  txBox_Duración.config(width=10)
  
  #Tabla materia
  txBox_NombreMateria = tk.Entry(ventana)
  txBox_NombreMateria.config(width=30)
  txBox_HorarioCorrespondiente = tk.Entry(ventana)
  txBox_HorarioCorrespondiente.config(width=10)
  
  #Tabla profesor
  txBox_NombreProfesor = tk.Entry(ventana)
  txBox_NombreProfesor.config(width=30)

  #Tabla nota
  txBox_Valor = tk.Entry(ventana)
  txBox_Valor.config(width=5)
  txBox_Tipo = tk.Entry(ventana)
  txBox_Tipo.config(width=20)

  # --- RADIOBUTTONS ---
  global Botón_Tabla_de_Alumno, Botón_Tabla_de_Asistencia, Botón_Tabla_de_Carrera, Botón_Tabla_de_Materia, Botón_Tabla_de_Profesor, Botón_Tabla_de_Notas, opción
  
  opción = tk.IntVar()
  color_fondo = ventana.cget("bg")
  
  Botón_Tabla_de_Alumno = tk.Radiobutton(ventana, text="Alumno", image=alumno_imagen, compound="left",
                                                       variable=opción, value= 1, command=lambda:acción_doble())
  Botón_Tabla_de_Alumno.config(bg=color_fondo, activebackground=color_fondo, highlightthickness=0, bd=0, font=("Arial", 12), cursor='hand2')


  Botón_Tabla_de_Asistencia = tk.Radiobutton(ventana, text="Asistencia", image=asistencia_imagen, compound="left",
                                                           variable=opción, value= 2, command=lambda: acción_doble())
  Botón_Tabla_de_Asistencia.config(bg=color_fondo, activebackground=color_fondo, highlightthickness=0, bd=0, font=("Arial", 12), cursor='hand2')


  Botón_Tabla_de_Carrera = tk.Radiobutton(ventana, text="Carrera", image=carrera_imagen, compound="left",
                                                      variable=opción, value= 3, command=lambda:acción_doble())
  Botón_Tabla_de_Carrera.config(bg=color_fondo, activebackground=color_fondo, highlightthickness=0, bd=0, font=("Arial", 12), cursor='hand2')


  Botón_Tabla_de_Materia = tk.Radiobutton(ventana, text="Materia", image=materia_imagen, compound="left",
                                                      variable=opción, value= 4, command=lambda:acción_doble())
  Botón_Tabla_de_Materia.config(bg=color_fondo, activebackground=color_fondo, highlightthickness=0, bd=0, font=("Arial", 12), cursor='hand2')


  Botón_Tabla_de_Profesor = tk.Radiobutton(ventana, text="Profesor", image=profesor_imagen, compound="left",
                                                       variable=opción, value= 5, command=lambda:acción_doble())
  Botón_Tabla_de_Profesor.config(bg=color_fondo, activebackground=color_fondo, highlightthickness=0, bd=0, font=("Arial", 12), cursor='hand2')


  Botón_Tabla_de_Notas = tk.Radiobutton(ventana, text="Nota", image=nota_imagen, compound="left",
                                                      variable=opción, value= 6, command=lambda:acción_doble())
  Botón_Tabla_de_Notas.config(bg=color_fondo, activebackground=color_fondo, highlightthickness=0, bd=0, font=("Arial", 12), cursor='hand2')


  Botón_Tabla_de_Alumno.place(relx=0.01, rely=0.85, relwidth=0.1)
  Botón_Tabla_de_Asistencia.place(relx=0.11, rely=0.85, relwidth=0.1)
  Botón_Tabla_de_Carrera.place(relx=0.21, rely=0.85, relwidth=0.1)
  Botón_Tabla_de_Materia.place(relx=0.31, rely=0.85, relwidth=0.1)
  Botón_Tabla_de_Profesor.place(relx=0.41, rely=0.85, relwidth=0.1)
  Botón_Tabla_de_Notas.place(relx=0.51, rely=0.85, relwidth=0.1)
  Botón_Tabla_de_Alumno.focus_set()
  
  #--- LISTBOX ---
  barraDesplazadora()
  
  actualizar_la_hora(ventana)
  
  ventana.bind_all("<Key>", mover_con_flechas)
    
  return ventana

def insertar_datos(nombre_de_la_tabla):
  conexión = conectar_base_de_datos()
  datos = obtener_datos_de_Formulario(nombre_de_la_tabla, validarDatos=True)

  if not datos or not validar_datos(nombre_de_la_tabla, datos):
      return

  valores_sql = []
  campos_sql = []
  for campo, valor in datos.items():
    valores_sql.append(valor)
    campos_sql.append(campo)

  campos = ', '.join(datos.keys())
  valores = ', '.join(['%s'] * len(datos))
  consulta = f"INSERT INTO {nombre_de_la_tabla} ({campos}) VALUES ({valores})"

  try:
      cursor = conexión.cursor()
      cursor.execute(consulta, tuple(valores_sql))
      conexión.commit()
      consultar_tabla(nombre_de_la_tabla)
      mensajeTexto.showinfo("CORRECTO", "SE AGREGÓ LOS DATOS NECESARIOS")
      for i, (campo, valor) in enumerate(datos.items()):
        entry = cajasDeTexto[nombre_de_la_tabla][i]
        entry.delete(0, tk.END)
  except Exception as e:
      mensajeTexto.showerror("ERROR", f"ERROR INESPERADO AL INSERTAR: {str(e)}")
  finally:
      desconectar_base_de_datos(conexión)


def modificar_datos(nombre_de_la_tabla):
  columna_seleccionada = Lista_de_datos.curselection()
  if not columna_seleccionada:
    mensajeTexto.showwarning("ADVERTENCIA", "FALTA SELECCIONAR UNA FILA")
    return

  selección = columna_seleccionada[0]
  ID_Seleccionado = lista_IDs[selección]

  if nombre_de_la_tabla != "nota" and ID_Seleccionado is None:
    mensajeTexto.showerror("ERROR", "NO SE HA ENCONTRADO EL ID VÁLIDO")
    return

  datos = obtener_datos_de_Formulario(nombre_de_la_tabla, validarDatos=True)
  if not datos:
      return

  if nombre_de_la_tabla == "nota":
    datos = normalizar_datos_nota(datos)
    if not datos:
        mensajeTexto.showerror("Error", "❌ Tipo de nota o valor inválido.")
        return

  if not validar_datos(nombre_de_la_tabla, datos):
      return

  valores_sql = []
  campos_sql = []

  for campo, valor in datos.items():
    valores_sql.append(valor)
    campos_sql.append(f"{campo} = %s")



  CampoID = conseguir_campo_ID(nombre_de_la_tabla)
  
  try:
    with conectar_base_de_datos() as conexión:
        cursor = conexión.cursor()
        set_sql = ', '.join(campos_sql)
        if nombre_de_la_tabla == "nota":
          consulta = f"UPDATE {nombre_de_la_tabla} SET {set_sql} WHERE IDAlumno = %s AND IDMateria = %s"
          valores_sql.append(datos["IDAlumno"])
          valores_sql.append(datos["IDMateria"])
        else:
          consulta = f"UPDATE {nombre_de_la_tabla} SET {set_sql} WHERE {CampoID} = %s"
          valores_sql.append(ID_Seleccionado)
        cursor.execute(consulta, tuple(valores_sql))
        conexión.commit()
        consultar_tabla(nombre_de_la_tabla)
        mensajeTexto.showinfo("CORRECTO", "SE MODIFICÓ EXITOSAMENTE")
        for i, (campo, valor) in enumerate(datos.items()):
          entry = cajasDeTexto[nombre_de_la_tabla][i]
          entry.delete(0, tk.END)
        cursor.close()
  except Exception as e:
      mensajeTexto.showerror("ERROR", f"❌ ERROR AL MODIFICAR: {e}")
  finally:
      desconectar_base_de_datos(conexión)


def eliminar_datos(nombre_de_la_tabla):
  columna_seleccionada = Lista_de_datos.curselection()
  datos = obtener_datos_de_Formulario(nombre_de_la_tabla, validarDatos=False)
  CampoID = conseguir_campo_ID(nombre_de_la_tabla)
  if not CampoID:
    mensajeTexto.showerror("ERROR", "No se ha podido determinar el campo ID para esta tabla")
    return
  
  if columna_seleccionada:
      try:
        with conectar_base_de_datos() as conexión:
          cursor = conexión.cursor()
          for index in columna_seleccionada:
            ID_Seleccionado = lista_IDs[index]
            if ID_Seleccionado is not None:
              if nombre_de_la_tabla == "nota":
                query = f"DELETE FROM {nombre_de_la_tabla} WHERE IDAlumno = %s AND IDMateria = %s"
                if not isinstance(ID_Seleccionado, tuple):
                  mensajeTexto.showerror("ERROR", "ID de nota no es una tupla válida")
                  return
              else:
                query = f"DELETE FROM {nombre_de_la_tabla} where {CampoID} = %s"
              cursor.execute(query, (ID_Seleccionado,))
              for i, (campo, valor) in enumerate(datos.items()):
                entry = cajasDeTexto[nombre_de_la_tabla][i]
                entry.delete(0, tk.END)
            else:
              mensajeTexto.showerror("ERROR", "NO SE HA ENCONTRADO EL ID VÁLIDO")
            conexión.commit()
            consultar_tabla(nombre_de_la_tabla)
            print(f"Eliminando de {nombre_de_la_tabla} con {CampoID} = {ID_Seleccionado}")
            mensajeTexto.showinfo("ÉXITOS", "Ha sido eliminada exitosamente")
      except error_sql as e:
         mensajeTexto.showerror("ERROR", f"ERROR INESPERADO AL ELIMINAR: {str(e)}")
  else:
    mensajeTexto.showwarning("ADVERTENCIA", "NO SELECCIONASTE NINGUNA COLUMNA")

def ordenar_datos(nombre_de_la_tabla, tabla, campo=None, ascendencia=True):
  conexión = conectar_base_de_datos()
  cursor = conexión.cursor()
  if conexión is None:
    mensajeTexto.showerror("ERROR DE CONEXIÓN", "NO SE PUDO CONECTAR A LA BASE DE DATOS")
    return

  Lista_de_datos.delete(0, tk.END)

  #Controla que se obtenga nombre reales de las columnas
  cursor.execute(f"SHOW COLUMNS FROM {nombre_de_la_tabla}")
  columna = [col[0] for col in cursor.fetchall()]
  
  #Si el campo no se especifica, entonces va a preguntar el usuario que campo quiere ordenar la tabla
  
  consultar_tabla(nombre_de_la_tabla)
  
  if campo is None:
    nombre_columna = ', '.join(columna)
    campo = tk.simpledialog.askstring("Ordenar", f"¿Qué campo querés ordenar los datos de {nombre_de_la_tabla}?\nCampos válidos: {nombre_columna}")
    if not campo:
      return
    campo = campo.strip()
  
  coincidencia = [col for col in columna if col.lower() == campo.lower()]
  
  if not coincidencia:
    mensajeTexto.showerror("ERROR", f"No existe el campo {campo} en la tabla {nombre_de_la_tabla}")
    return
  campo_real = coincidencia[0]
  orden = "ASC" if ascendencia else "DESC"
  try:
    consulta = {
      "alumno": f"SELECT a.id, a.nombre, a.edad FROM {nombre_de_la_tabla} AS a ORDER BY {campo_real} {orden}",
      "asistencia": f"SELECT a.id, a.fecha, a.presente FROM {nombre_de_la_tabla} AS a ORDER BY {campo_real} {orden}",
      "profesor": f"SELECT p.id, p.nombre, p.asignatura FROM {nombre_de_la_tabla} AS p ORDER BY {campo_real} {orden}",
      "materia": f"SELECT m.id, m.nombre, m.creditos FROM {nombre_de_la_tabla} AS m ORDER BY {campo_real} {orden}",
      "nota": f"SELECT n.id, n.alumno_id, n.materia_id, n.calificacion FROM {nombre_de_la_tabla} AS n ORDER BY {campo_real} {orden}"
    }
    cursor.execute(consulta)
    resultado = cursor.fetchall()
    
    
    tabla_a_seleccionar = {
        "alumno": Botón_Tabla_de_Alumno,
        "asistencia": Botón_Tabla_de_Asistencia,
        "carrera": Botón_Tabla_de_Carrera,
        "profesor": Botón_Tabla_de_Profesor,
        "materia": Botón_Tabla_de_Materia,
        "nota": Botón_Tabla_de_Notas
      }
    
    #Controlo que haya resultados, en caso contrario, me imprime un mensaje de que no hay resultados para criterios específicos
    if not resultado:
      mensajeTexto.showinfo("SIN RESULTADOS", "NO SE ENCONTRARON REGISTROS PARA LOS CRITERIOS ESPECÍFICOS")
      return
    
    #Esta lógica ya pertenece al formato de filas, para que quede bien derechito con el fin de evitar cualquier mezcla o confusión al usuario.
    
    filaVisible = resultado[0][1:] if nombre_de_la_tabla != "nota" else resultado[0]
    
    ancho_de_tablas = [0] * len(filaVisible)
    

    for fila in resultado:
      filaVisible = list(fila[1:] if nombre_de_la_tabla != "nota" else fila)
      
      for i, valor in enumerate(filaVisible):
        valorTipoCadena = str(valor)
        ancho_de_tablas[i] = max(ancho_de_tablas[i], len(valorTipoCadena))
      
      
      formato = "|".join("{:<" + str(ancho) + "}" for ancho in ancho_de_tablas)
      
    #Recorro las filas.
    for fila in resultado:
      filaVisible = list(fila[1:] if nombre_de_la_tabla != "nota" else fila)
    
      match nombre_de_la_tabla.lower():
        case "alumno":
          filaVisible[2] = f"{filaVisible[2]} años"
        case "materia":
          filaVisible[1] = f"{filaVisible[1]} horas"
      filaTipoCadena = [str(valor) for valor in filaVisible]
      #Se agrega una separación para que no se vea pegado
      if len(filaTipoCadena) == len(ancho_de_tablas):
        filas_formateadas = formato.format(*filaTipoCadena)
        Lista_de_datos.insert(tk.END, filas_formateadas)
      else:
        print("❗ Columnas desalineadas:", filaTipoCadena)
        print("🔍 Longitudes -> fila:", len(filaTipoCadena), "| ancho_de_tablas:", len(ancho_de_tablas))
  
    radioButton_seleccionado = tabla_a_seleccionar.get(nombre_de_la_tabla.lower()) 
    if radioButton_seleccionado:
      radioButton_seleccionado.select()
    
  except error_sql as e:
     mensajeTexto.showerror("ERROR", f"HA OCURRIDO UN ERROR AL ORDENAR LA TABLA: {str(e)}")
  finally:
    desconectar_base_de_datos(conexión)

#En este código voy a exportar en PDF el archivo de datos tkinter
def exportar_en_PDF(nombre_de_la_tabla):
  try:
    conexión = conectar_base_de_datos()
    if conexión is None:
      return
    cursor = conexión.cursor()
    cursor.execute()
    fila = cursor.fetchall()
    
    datos = Lista_de_datos.get(0, tk.END)
    
    ventana_exportar = diálogo.asksaveasfilename(
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
    canva.setFont("Arial", 20)
    y = 780
    
    canva = canvas.Canvas(ventana_exportar, pagesize=letter)
    y -= 20
    #Aquí empiezo a iterar los datos para luego imprimir el reporte
    for fila in datos:
      canva.drawString(100, y, f"{fila}")
      y -= 20
      
    canva.save()
    
    mensajeTexto.showwarning("ÉXITOS", "EXPORTADO CORRECTAMENTE")
    
  except error_sql as e:
    mensajeTexto.showerror("OCURRIÓ UN ERROR", f"Error al exportar en PDF la información detallada: {str(e)}")

# --- EVENTOS PARA BOTONES ---

#Esta función me permite desplazar con barra verticalmente
#la ListBox para que se pueda ver muchos registros en la tabla
def barraDesplazadora():
  global Lista_de_datos, Frame_Lista
  # Definimos un frame con tamaño fijo y evitamos que se redimensione automáticamente
  Frame_Lista = tk.Frame(mi_ventana, width=400, height=500)
  Frame_Lista.pack(side=tk.RIGHT, padx=10, pady=10)
  Frame_Lista.pack_propagate(True)
  
  barraVertical = tk.Scrollbar(Frame_Lista, orient="vertical")
  barraVertical.pack(side=tk.RIGHT, fill=tk.Y)
  
  #Acá creé una barra de desplazamiento horizontal para desplazar
  #en la tabla donde dice materias cuando son largas
  barraHorizontal = tk.Scrollbar(Frame_Lista, orient="horizontal")
  barraHorizontal.pack(side=tk.BOTTOM, fill=tk.X)
  
  # La ListBox se define con dimensiones menores para no ocupar toda la pantalla
  Lista_de_datos = tk.Listbox(Frame_Lista, exportselection=0, width=45, height=60)
  Lista_de_datos.config(fg="blue", bg=colores["amarillo_claro"], font=("Courier New", 12, "bold"))
  Lista_de_datos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
  
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
  elif event.widget == botón_ordenar:
    ordenar_datos(obtener_tabla_seleccionada())
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
                          botón_ordenar, 
                          botón_exportar
                        ]
  
  botones_excluyentes = [ Botón_Tabla_de_Alumno, 
                          Botón_Tabla_de_Asistencia, 
                          Botón_Tabla_de_Carrera,
                          Botón_Tabla_de_Materia,
                          Botón_Tabla_de_Profesor,
                          Botón_Tabla_de_Notas
                        ]
  
  cajasDeTexto = [  txBox_FechaNacimiento, txBox_NombreAlumno, 
                    txBox_EstadoDeAsistencia, txBox_FechaAsistencia, 
                    txBox_NombreCarrera, txBox_Duración, 
                    txBox_NombreMateria, txBox_HorarioCorrespondiente, 
                    txBox_NombreProfesor, 
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
          caja_activa = [txBox_FechaNacimiento, txBox_NombreAlumno]
      elif tabla_de_asistencia:
          txBox_EstadoDeAsistencia.focus_set()
          caja_activa = [txBox_EstadoDeAsistencia, txBox_FechaAsistencia]
      elif tabla_de_carrera:
          txBox_NombreCarrera.focus_set()
          caja_activa = [txBox_NombreCarrera, txBox_Duración]
      elif tabla_de_materia:
          txBox_NombreMateria.focus_set()
          caja_activa = [txBox_NombreMateria, txBox_HorarioCorrespondiente]
      elif tabla_de_profesor:
          txBox_NombreProfesor.focus_set()
          caja_activa = [txBox_NombreProfesor]
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
          caja_activa = [txBox_FechaNacimiento, txBox_NombreAlumno]
        elif tabla_de_asistencia:
          caja_activa = [txBox_EstadoDeAsistencia, txBox_FechaAsistencia]
        elif tabla_de_carrera:
          caja_activa = [txBox_NombreCarrera, txBox_Duración]
        elif tabla_de_materia:
          caja_activa = [txBox_NombreMateria, txBox_HorarioCorrespondiente]
        elif tabla_de_profesor:
          caja_activa = [txBox_NombreProfesor]
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
interfaz = pantalla_principal(mi_ventana)
interfaz.mainloop()
