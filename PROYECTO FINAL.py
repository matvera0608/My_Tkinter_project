import os
from mysql.connector import Error as error_sql
from datetime import datetime
from tkinter import messagebox as mensajeTexto, filedialog as diálogo
from reportlab.pdfgen import canvas
import tkinter as tk, re
import mysql.connector as MySql
import time as hora_del_sistema
from reportlab.lib.pagesizes import letter

# --- COLORES EN HEXADECIMALES ---
colores = {
    "rosado_claro": "#FFECEC",
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
            cursor.execute("""SELECT n.valorNota, n.tipoNota, al.Nombre, m.Nombre
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
  
  botón_agregar.place(x = 40, y = 100)
  botón_modificar.place(x = 40, y = 160)
  botón_eliminar.place(x = 40, y = 220)
  botón_ordenar.place(x = 40, y = 280)
  botón_exportar.place(x= 20, y= 50)
  
  label_Obligatoriedad.pack(padx= 100, pady= 50)
  
  opciones_del_widget = {
                                         1: [(txBox_FechaNacimiento, label_FechaNacimiento, 100), (txBox_NombreAlumno,label_NombreAlumno, 150)],
                                         2: [(txBox_EstadoDeAsistencia, label_EstadoDeAsistencia, 100), (txBox_FechaAsistencia, label_Fecha, 150)],
                                         3: [(txBox_NombreCarrera, label_NombreCarrera, 100), (txBox_Duración, label_Duración, 150)],
                                         4: [(txBox_NombreMateria, label_NombreMateria,100), (txBox_HorarioCorrespondiente, label_HorarioCorrespondiente, 150)],
                                         5: [(txBox_NombreProfesor, label_NombreProfesor, 100)],
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
    mensajeTexto.showerror("Error", "Selección inválida. Los valores están entre el 1 y 6")
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
  patrón_alfanumérico = re.compile(r'^[A-Za-z0-9áéíóúÁÉÍÓÚñÑüÜ\s]+$') #Esta variable regular contiene la expresión de letras y números
  try:
    tabla_a_validar = {"alumno":     ["Nombre", "FechaDeNacimiento",],
                       "carrera":    ["Nombre", "Duración",],
                       "materia":    ["Nombre", "Horario",],
                       "profesor":   ["Nombre",],
                       "asistencia": ["Fecha_Asistencia", "Estado",],
                       "nota":       ["valorNota", "TipoNota",]
                      }
    

    if nombre_de_la_tabla in tabla_a_validar:
      campo = tabla_a_validar[nombre_de_la_tabla]
      #FORZAR EL CAMBIO DE FECHA
      for campo in datos:
        valor = datos[campo]
        if isinstance(valor, str) and '/' in valor:
          try:
            datos[campo] = datetime.strptime(valor, "%d/%m/%Y").strftime("%Y-%m-%d")
          except:
            pass  # No convertir si no es fecha
      
      if len(campo) == 1:
        consulta = f"SELECT COUNT(*) FROM {nombre_de_la_tabla} WHERE {campo[0]} = %s"
        cursor.execute(consulta, (datos[campo[0]],))
      elif len(campo) > 1:
        consulta = f"SELECT COUNT(*) FROM {nombre_de_la_tabla} WHERE {campo[0]} = %s AND {campo[1]} = %s"
        cursor.execute(consulta, (datos[campo[0]], datos[campo[1]]))
      resultado = cursor.fetchone()
    else:
      mensajeTexto.showerror("Error", "La tabla solicitada no se encuentra")
      return False
  
    
    validaciones = {
      'alumno': {
              "Nombre": lambda valor:patrón_nombre.match(valor),
              "FechaDeNacimiento": lambda valor: valor.strip() and datetime.strptime(valor, '%d/%m/%Y'),
      },
      'asistencia': {
              "Estado": lambda valor: valor.isalpha(),
              "Fecha_Asistencia": lambda valor: datetime.strptime(valor, '%d/%m/%Y')
      },
      'carrera': {
              "Nombre": lambda valor :patrón_nombre.match(valor),
              "Duración": lambda valor :patrón_alfanumérico.match(valor), #en Duración cambié la expresión regular para que acepte letras, números y espacios.
      },
      'materia': {
              "Nombre": lambda valor :patrón_nombre.match(valor),
              "Horario": lambda valor :datetime.strptime(valor, '%H:%M'),
      },
      'profesor': {
              "Nombre": lambda valor :patrón_nombre.match(valor),
      },
      'nota': {
              "valorNota": lambda valor :patrón_númerosDecimales.match(valor),
              "tipoNota": lambda valor : patrón_alfanumérico.match(valor) #tipoNota sólo acepta letras,
      }
    }
    
    if not nombre_de_la_tabla in validaciones:
      mensajeTexto.showerror("Error", "La tabla solicitada no se encuentra")
      return False
    #en este for controlo que los datos estén puestos correctamente, en caso contrario
    #no me agregan o modifican. Condiciones a llevar en cuenta:
    #no se puede agregar con campos totalmente vacíos
    #el formato debe cumplir estrictamente con las validaciones, que es un diccionario para control
    for campo, valor in datos.items():
      if campo in validaciones[nombre_de_la_tabla] and not valor.strip():
        mensajeTexto.showerror("Error", "Los campos no pueden estar vacíos")
        return False
      elif campo in validaciones[nombre_de_la_tabla] and not validaciones[nombre_de_la_tabla][campo](valor):
        mensajeTexto.showerror("Error", f"El campo {campo} tiene un formato inválido con valor {valor}")
        return False
      elif campo == "Estado" and valor.lower() not in ["presente", "ausente"]:
         mensajeTexto.showerror("Error", "La asistencia sólo permite poner presente o ausente")
         return False
      elif campo in ["valorNota", "tipoNota"]:
        if "tipoNota" and valor.lower() not in ["Parcial 1", "Parcial 2", "Parcial 3","Parcial 4","Trabajo Práctico 1","Trabajo Práctico 2","Exámen Final"]:
          mensajeTexto.showerror("Error", f"El campo {campo} tiene que ser un número válido")
          return False
        elif (float(valor) < 1 or float(valor) > 10):
          mensajeTexto.showerror("Error", f"El campo que tiene una nota menor que 1 o mayor que 10 es {campo}")
          return False
        
      #en esta condición verifico si el valor ya existe en la base de datos o si un registro se repite o no
      if resultado and resultado[0] > 0:
        mensajeTexto.showwarning("Advertencia", f"El valor '{valor}' en '{campo}' ya existe en la base de datos")
        return False
         
  except ValueError as vE:
    mensajeTexto.showerror("Error", f"Formato de uno de los campos no es válido: {vE}")
  except error_sql as e:
    mensajeTexto.showerror("Error", f"Error al consultar la base de datos: {e}")
  finally:
    desconectar_base_de_datos(conexión)

  return True

#En esta función obtengo todos los datos del formulario de MySQL para agregar, modificar
#y eliminar algunos datos de la tabla
def obtener_datos_de_Formulario(nombre_de_la_tabla, validarDatos):
  global cajasDeTexto, datos, campos_de_la_base_de_datos
  ##Tengo 3 diccionarios, pero cada uno cumple sus funciones


  campos_de_la_base_de_datos = {
                                      'alumno':     ["FechaDeNacimiento", "Nombre"],
                                      'asistencia': ["Estado", "Fecha_Asistencia"],
                                      'carrera':    ["Nombre", "Duración"],
                                      'materia':    ["Nombre", "Horario"],
                                      'profesor':   ["Nombre"],
                                      'nota':       ["valorNota", "tipoNota"]
                               }
  
  datos = {}

  cajasDeTexto = {
                              'alumno':  (txBox_FechaNacimiento, txBox_NombreAlumno),
                              'asistencia': (txBox_EstadoDeAsistencia , txBox_FechaAsistencia),
                              'carrera':  (txBox_NombreCarrera, txBox_Duración),
                              'materia': (txBox_NombreMateria, txBox_HorarioCorrespondiente),
                              'profesor': (txBox_NombreProfesor,),
                              'nota':     (txBox_Valor, txBox_Tipo)
                 }

  

  for campo, caja in zip(campos_de_la_base_de_datos[nombre_de_la_tabla], cajasDeTexto[nombre_de_la_tabla]):
      datos[campo] = caja.get()


  #En esta condición, valido los datos de la tabla
  #antes de agregarlo a la listBox. Puse un condicional
  #donde si las entrys de cada registro, no me tiren error. Además validarDatos
  #como variable me sirve para que no me tire error de que no existe la tabla antes de indicar un registro de la listBox
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
              'profesor': "ID_Profesor"
        }
  return IDs.get(nombre_de_la_tabla.strip().lower())

#Esta función ayuda a forzar poner la fecha formateada en el país donde uno vive
#porque SQL te obliga a poner en formato de Año-Mes-Día, esta es la única solución.
#Lo mismo con la hora, que SQL te obliga a poner en formato de Hora:Minuto:Segundo.
#Pero el usuario necesita solo que muestre la Hora:Minuto.
def preparar_para_sql(datos):
    datos_convertidos = {}
    for campo, valor in datos.items():
        if "fecha" in campo.lower():  # Verifica si el campo es una fecha con alternativas sin bastar con una sola.
          try:
              fecha_obj = datetime.strptime(valor, '%d/%m/%Y').strftime('%Y-%m-%d')
          except ValueError:
              try:
                  fecha_obj = datetime.strptime(valor, '%Y-%m-%d').strftime('%Y-%m-%d')
              except ValueError:
                  print(f"Error al convertir la fecha en el campo {campo}: {valor}")
                  continue
          datos_convertidos[campo] = fecha_obj
        elif "hora" in campo.lower() or "horario" in campo.lower():  # Verifica si el campo es una hora
            try:
              hora_obj = datetime.strptime(valor.strip(), "%H:%M").strftime("%H:%M")
            except ValueError:
              print(f"Error al convertir la hora en el campo {campo}: {valor}")
              continue
            datos_convertidos[campo] = hora_obj
        else:
            datos_convertidos[campo] = valor.strip()
        return datos_convertidos

#Estoy teniendo un problema con la función preparar_para_sql, ya que no está manejando correctamente los datos de entrada. Necesito asegurarme de que las fechas y horas se conviertan al formato adecuado antes de enviarlos a la base de datos.
#QUE HACER AHORA? ESTOY RE ENOJADO PORQUE ME TIRA UN ERROR.
#Esta función me permite insertar datos en la base de datos

#Esta función se encarga de convertir los datos de entrada para mostrar en el entry
#en el formato que el usuario espera, por ejemplo, convertir fechas de "YYYY-MM-DD" a "DD/MM/YYYY"
def convertir_datos(nombre_de_la_tabla):
  for campo, caja in zip(campos_de_la_base_de_datos[nombre_de_la_tabla], cajasDeTexto[nombre_de_la_tabla]):
    valor = caja.get()
    # Si el campo es una fecha, lo convierte al formato "DD/MM/YYYY"
    if isinstance(valor, str) and "fecha" in campo.lower():
        try:
            fecha_obj = datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
        except ValueError:
            continue  # Si no es una fecha válida, no la convierte
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


#Esta función sirve para actualizar la hora
def actualizar_la_hora(interfaz):
  label_Hora.config(text=hora_del_sistema.strftime("%I:%M:%S %p"))
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
  ID_Campo = conseguir_campo_ID(nombre_de_la_tabla)
  selección = Lista_de_datos.curselection()
  
  if not selección:
    return
  índice = selección[0]
  id = lista_IDs[índice]

  conexión = conectar_base_de_datos()
  if conexión:
    try:
      cursor = conexión.cursor()
      if not ID_Campo:
        mensajeTexto.showerror("ERROR", "No se pudo determinar el campo ID para esta tabla.")
        return

      if id is None:
        mensajeTexto.showerror("ERROR", "No se pudo determinar el ID del registro seleccionado.")
        return
      if nombre_de_la_tabla != "nota":
        campos = ', '.join([campo for campo in datos.keys()])
        consulta = f"SELECT {campos} FROM {nombre_de_la_tabla} WHERE {ID_Campo} = %s"
        cursor.execute(consulta, (id,))
        fila_seleccionada = cursor.fetchone()
      
      if fila_seleccionada is None:
        mensajeTexto.showwarning("ADVERTENCIA", "NO SE ENCONTRÓ LA FILA")
        return
      
      #AHORA YA NO ME MUESTRAN NADA DE SQL, SÓLO LAS ENTRYS VACÍAS.
      if selección:
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
  global botón_agregar, botón_eliminar, botón_modificar, botón_ordenar, botón_exportar

  #Agregar
  botón_agregar = tk.Button(mi_ventana, text="Agregar", command=lambda:insertar_datos(obtener_tabla_seleccionada()), width=10, height=1)
  botón_agregar.config(fg="black", bg=colores["verde"], font=("Arial", 8), cursor='hand2', activebackground=colores["verde"])
  botón_agregar.bind("<Return>", ejecutar_acción_presionando_Enter)

  #Modificar
  botón_modificar = tk.Button(mi_ventana, text="Modificar", command=lambda:modificar_datos(obtener_tabla_seleccionada()), width=10, height=1)
  botón_modificar.config(fg="black", bg="red", font=("Arial", 8), cursor='hand2', activebackground=colores["rojo"])
  botón_modificar.bind("<Return>", ejecutar_acción_presionando_Enter)

  #Eliminar
  botón_eliminar = tk.Button(mi_ventana, text="Eliminar", command=lambda:eliminar_datos(obtener_tabla_seleccionada()), width=10, height=1)
  botón_eliminar.config(fg="black", bg="blue", font=("Arial", 8), cursor='hand2', activebackground=colores["azul"])
  botón_eliminar.bind("<Return>", ejecutar_acción_presionando_Enter)

  #Comparar
  botón_ordenar = tk.Button(mi_ventana, text="Ordenar", command=lambda:ordenar_datos(obtener_tabla_seleccionada()), width=10, height=1)
  botón_ordenar.config(fg="black", bg=colores["dorado"], font=("Arial", 8), cursor='hand2', activebackground=colores["dorado_claro"])
  botón_ordenar.bind("<Return>", ejecutar_acción_presionando_Enter)
  
  #Exportar como PDF
  botón_exportar = tk.Button(mi_ventana, text="Exportar", command=lambda:exportar_en_PDF(obtener_tabla_seleccionada()), width=10, height=1)
  botón_exportar.config(fg="black", bg=colores["agua"], font=("Arial", 8), cursor='hand2', activebackground=colores["agua_claro"])
  botón_exportar.bind("<Return>", ejecutar_acción_presionando_Enter)
  

  # --- ETIQUETAS ---
  global label_NombreAlumno, label_FechaNacimiento, label_EstadoDeAsistencia, label_Fecha, label_NombreCarrera, label_Duración, label_NombreMateria, label_HorarioCorrespondiente, label_NombreProfesor, label_Valor, label_Tipo, label_Hora, label_Obligatoriedad
  #Etiquetas para la tabla de alumno
  label_NombreAlumno = tk.Label(mi_ventana, text="Nombre del Alumno *")
  label_NombreAlumno.config(fg="Black",bg=colores["rosado_claro"], font=("Arial", 12))

  label_FechaNacimiento = tk.Label(mi_ventana, text="Fecha que nació: Formato Año-Mes-Día *")
  label_FechaNacimiento.config(fg="Black",bg=colores["rosado_claro"], font=("Arial", 12))

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

  #Etiquetas para la tabla de materia
  label_NombreMateria = tk.Label(mi_ventana, text="Nombre de la Materia *")
  label_NombreMateria.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  label_HorarioCorrespondiente = tk.Label(mi_ventana, text="Horario correspondiente: Formato %H:%M *")
  label_HorarioCorrespondiente.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  #Etiquetas para la tabla de profesor
  label_NombreProfesor = tk.Label(mi_ventana, text="Nombre del Profesor *")
  label_NombreProfesor.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  #Etiquetas para la tabla de nota
  label_Valor = tk.Label(mi_ventana, text="Nota*")
  label_Valor.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  label_Tipo = tk.Label(mi_ventana, text="Tipo*")
  label_Tipo.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 12))

  #Etiqueta para mostrar la hora
  label_Hora = tk.Label(mi_ventana, text="")
  label_Hora.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 10))
  #Etiqueta para indicar que significa el asterisco
  label_Obligatoriedad = tk.Label(mi_ventana, text="el * significa que es obligatorio seleccionar los datos")
  label_Obligatoriedad.config(fg="Black", bg=colores["rosado_claro"], font=("Arial", 8))

  #--- ENTRIES ---
  global txBox_NombreAlumno, txBox_FechaNacimiento, txBox_EstadoDeAsistencia, txBox_FechaAsistencia, txBox_NombreCarrera, txBox_Duración, txBox_NombreMateria, txBox_HorarioCorrespondiente, txBox_NombreProfesor, txBox_Valor, txBox_Tipo, opción, Lista_de_datos
  #Tabla alumno
  txBox_NombreAlumno = tk.Entry(mi_ventana)
  txBox_FechaNacimiento = tk.Entry(mi_ventana)

  #Tabla asistencia
  txBox_EstadoDeAsistencia = tk.Entry(mi_ventana)
  txBox_FechaAsistencia = tk.Entry(mi_ventana)

  #Tabla carrera
  txBox_NombreCarrera = tk.Entry(mi_ventana)
  txBox_Duración = tk.Entry(mi_ventana)
  
  #Tabla materia
  txBox_NombreMateria = tk.Entry(mi_ventana)
  txBox_HorarioCorrespondiente = tk.Entry(mi_ventana)
  
  #Tabla profesor
  txBox_NombreProfesor = tk.Entry(mi_ventana)

  #Tabla nota
  txBox_Valor = tk.Entry(mi_ventana)
  txBox_Tipo = tk.Entry(mi_ventana)

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


def insertar_datos(nombre_de_la_tabla):
  conexión = conectar_base_de_datos()
  
  datosNecesarios = obtener_datos_de_Formulario(nombre_de_la_tabla, validarDatos=True)
  
  if not datosNecesarios:
    return
  
  datos_sql = preparar_para_sql(datosNecesarios) #Acá se ubica la función de preparar_para_sql, ayuda a forzar agregar o modificar la fecha
  
  if not validar_datos(nombre_de_la_tabla, datos_sql):
    return

  cursor = conexión.cursor()
  campos = ', '.join(datos_sql.keys())
  placeholder = ', '.join(['%s'] * len(datos_sql))
  values = list(datos_sql.values())
  query = f"INSERT INTO {nombre_de_la_tabla} ({campos}) VALUES ({placeholder})"
  try:
    cursor.execute(query, values)
    conexión.commit()
    consultar_tabla(nombre_de_la_tabla)
    mensajeTexto.showinfo("CORRECTO", "SE AGREGÓ LOS DATOS NECESARIOS")
    # for i, (campo, valor) in enumerate(datosNecesarios.items()):
    #   entry = cajasDeTexto[nombre_de_la_tabla][i]
    #   entry.delete(0, tk.END)
    desconectar_base_de_datos(conexión)
  except Exception as e:
    mensajeTexto.showerror("ERROR", f"ERROR INESPERADO AL INSERTAR: {e}")


def modificar_datos(nombre_de_la_tabla):
  columna_seleccionada = Lista_de_datos.curselection()
  if not columna_seleccionada:
    mensajeTexto.showwarning("ADVERTENCIA", "FALTA SELECCIONAR UNA FILA")
    return
    
  selección = columna_seleccionada[0]
  ID_Seleccionado = lista_IDs[selección]
    
  if ID_Seleccionado is None:
      mensajeTexto.showerror("ERROR", "NO SE HA ENCONTRADO EL ID VÁLIDO")
      return


  datosNecesarios = obtener_datos_de_Formulario(nombre_de_la_tabla, validarDatos=True)
  if not datosNecesarios:
      return

  datos_sql = preparar_para_sql(datosNecesarios)
  
  CampoID = conseguir_campo_ID(nombre_de_la_tabla)  # ej. "id_usuario"
  
  if not validar_datos(nombre_de_la_tabla, datos_sql):
    return
  
  try:
    with conectar_base_de_datos() as conexión:
      cursor = conexión.cursor()
      campos = ', '.join([f"{campo} = %s" for campo in datos_sql.keys()])
      valores = list(datos_sql.values()) + [ID_Seleccionado]
      consulta = f"UPDATE {nombre_de_la_tabla} SET {campos} WHERE {CampoID} = %s"
      
      cursor.execute(consulta, valores)
      conexión.commit()
      
      consultar_tabla(nombre_de_la_tabla)
      mensajeTexto.showinfo("CORRECTO", "SE MODIFICÓ EXITOSAMENTE")
  except Exception as e:
      mensajeTexto.showerror("ERROR", f"❌ ERROR AL MODIFICAR: {e}")
  
#Mejoré mi función de insertar datos para eliminar
#dinámicamente sin tener que entrar a MySQL y puse una
#función que extrae el ID en todas las palabras ya que
#no siempre tiene un valor fijo
def eliminar_datos(nombre_de_la_tabla):
  columna_seleccionada = Lista_de_datos.curselection()
  datosNecesarios = obtener_datos_de_Formulario(nombre_de_la_tabla, validarDatos=False)
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
              query = f"DELETE FROM {nombre_de_la_tabla} where {CampoID} = %s"
              cursor.execute(query, (ID_Seleccionado,))
              #Este for me limpia los campos de texto después de agregarlo
              #para que no quede el último valor que se agregó y se repita continuamente
              for i, (campo, valor) in enumerate(datosNecesarios.items()):
                entry = cajasDeTexto[nombre_de_la_tabla][i]
                entry.delete(0, tk.END)
            else:
              mensajeTexto.showerror("ERROR", "NO SE HA ENCONTRADO EL ID VÁLIDO")
            conexión.commit()
            consultar_tabla(nombre_de_la_tabla)
            print(f"Eliminando de {nombre_de_la_tabla} con {CampoID} = {ID_Seleccionado}")
            mensajeTexto.showinfo("ÉXITOS", "Ha sido eliminada exitosamente")
      except error_sql as e:
         mensajeTexto.showerror("ERROR", f"ERROR INESPERADO AL ELIMINAR: {e}")
  else:
    mensajeTexto.showwarning("ADVERTENCIA", "NO SELECCIONASTE NINGUNA COLUMNA")

#En esta función comparar relaciono una tabla con la otra
#pero coincidiendo cada valor para que se pueda leer con facilidad
#y saber si uno de los alumnos están presentes o no
def ordenar_datos(nombre_de_la_tabla):
  try:
    conexión = conectar_base_de_datos()
    if conexión is None:
      mensajeTexto.showerror("ERROR DE CONEXIÓN", "NO SE PUDO CONECTAR A LA BASE DE DATOS")
      return
    cursor = conexión.cursor()
    ordenar_Campo = tk.simpledialog.askstring("Ordenar", f"Que campo quieres ordenar los datos en {nombre_de_la_tabla}? ")
    campos_de_la_base_de_datos = obtener_datos_de_Formulario(nombre_de_la_tabla, validarDatos=False)
    
    if ordenar_Campo is None:
      return None
    else:
      ordenar_Campo = ordenar_Campo.strip().lower()
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
      botónSeleccionado = tabla_a_seleccionar.get(ordenar_Campo)
      
      if not botónSeleccionado:
        mensajeTexto.showerror("ERROR", "NO SE HA INGRESADO NINGUNA TABLA")
        return
      
      botónSeleccionado.select() #Esto selecciona el botón correspondiente a la tabla elegida por el usuario
        
    # cursor.execute(consulta)
    resultado = cursor.fetchall()

    #Controlo que haya resultados, en caso contrario, me imprime un mensaje de que no hay resultados para criterios específicos
    if not resultado:
      mensajeTexto.showinfo("SIN RESULTADOS", "NO SE ENCONTRARON REGISTROS PARA LOS CRITERIOS ESPECÍFICOS")
      return
    
    Lista_de_datos.delete(0, tk.END)
    
    for fila in resultado:
      Lista_de_datos.insert(tk.END, " | ".join(map(lambda x: str(x) if x is not None else "", fila )))
    
  except error_sql as e:
     mensajeTexto.showerror("ERROR", f"HA OCURRIDO UN ERROR AL RELACIONAR LA TABLA CON LA OTRA: {str(e)}")
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
  Frame_Lista.pack_propagate(False)
  
  barraVertical = tk.Scrollbar(Frame_Lista, orient="vertical")
  barraVertical.pack(side=tk.RIGHT, fill=tk.Y)
  
  #Acá creé una barra de desplazamiento horizontal para desplazar
  #en la tabla donde dice materias cuando son largas
  barraHorizontal = tk.Scrollbar(Frame_Lista, orient="horizontal")
  barraHorizontal.pack(side=tk.BOTTOM, fill=tk.X)
  
  # La ListBox se define con dimensiones menores para no ocupar toda la pantalla
  Lista_de_datos = tk.Listbox(Frame_Lista, exportselection=0, width=90, height=40)
  Lista_de_datos.config(fg="blue", bg=colores["amarillo_claro"], font=("Courier New", 12, "bold"))
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
  
  cajasDeTexto = [ txBox_FechaNacimiento, txBox_NombreAlumno, 
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
interfaz = pantalla_principal()
interfaz.mainloop()