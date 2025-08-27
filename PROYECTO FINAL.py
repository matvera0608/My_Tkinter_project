import os
import mysql.connector as MySql
from mysql.connector import Error as error_sql
from datetime import datetime, date as fecha, time as hora
from tkinter import messagebox as mensajeTexto, filedialog as dialogo 
import tkinter as tk
from tkinter import ttk
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics as métricasPDF
from reportlab.pdfbase.ttfonts import TTFont as fuente_TTFont

from PIL import Image, ImageTk

métricasPDF.registerFont(fuente_TTFont("Arial", "Arial.ttf"))


# --- COLORES EN HEXADECIMALES ---
colores = {
  "blanco": "#FFFFFF",
  "gris": "#AAAAAA",
  "negro": "#000000",
  "negro_resaltado": "#3A3A3A"
}

dirección_del_ícono = os.path.dirname(__file__)
ícono = os.path.join(dirección_del_ícono,"escuela.ico")

ruta_base = os.path.dirname(__file__)
ruta_imagen = os.path.join(ruta_base, "imágenes")

#Esta es mi función para conectar a la base de datos,
# es decir, contiene la cadena de conexión
def conectar_base_de_datos():
  try:
    cadena_de_conexión = MySql.connect(
        host = 'localhost',
        user = 'root',
        password = 'admin',
        database = 'escuela')
    conexión_exitosa = cadena_de_conexión.is_connected()
    if conexión_exitosa:
      return cadena_de_conexión
  except error_sql as e:
    print(f"Error inesperado al conectar MySql {e}")
    return None

#Y este es para desconectar la base de datos
def desconectar_base_de_datos(conexión):
  desconectando_db = conexión.is_connected()
  if desconectando_db:
    conexión.close()

mi_ventana = tk.Tk()

# --- EJECUCIÓN DE LA VENTANA PRINCIPAL ---
def pantallaLogin():
  ventana = mi_ventana
  ventana.title("Sistema Gestor de Asistencias")
  ventana.geometry("600x200")
  ventana.configure(bg=colores["blanco"])
  ventana.iconbitmap(ícono)
  ventana.register("Arial", "Arial.ttf")
  ventana.resizable(width=False, height=False)
  ventana.grid_columnconfigure(0, weight=1)
  ventana.grid_rowconfigure(2, weight=1)

  global label_Hora

  #Etiqueta para rol
  label_usuario_rol = tk.Label(ventana, text="ROL", bg=colores["blanco"], fg=colores["negro"], font=("Arial", 15, "bold"))
  label_usuario_rol.grid(row=0, column=0, pady=(20, 5), sticky="n")
  
  #Entry para el usuario
  txBox_usuario = tk.Entry(ventana, font=("Arial", 15), width=20, fg=colores["negro_resaltado"])
  txBox_usuario.grid(row=1, column=0, pady=(0, 20), sticky="n")
  txBox_usuario.insert(0, "docente")
  
  #Esta función controla que rol es cada usuario
  def validarRol():
    rol = txBox_usuario.get().strip().lower()
    rolesVálidos = ["profesor", "docente", "administrativo", "personal administrativo"]
    
    if rol in rolesVálidos:
      mostrar_pestañas(ventana)
    else:
      mensajeTexto.showerror("Error de Login", f"Los roles permitidos son: {', '.join(rolesVálidos).title()}. Ingresar bien los datos")
      return

  #Iniciar Sesión
  botón_login = tk.Button(ventana, text="Iniciar Sesión", width=15)
  botón_login.config(fg="black", bg=colores["gris"], font=("Arial", 15), cursor='hand2', activebackground=colores["gris"],  command= validarRol)
  botón_login.grid(row=2, column=0, pady=30, sticky="s")
  
  return ventana


def mostrar_pestañas(ventana):
  global notebook, tablaAlumno, tablaAsistencia, tablaCarrera, tablaMateria, tablaMateria_Profesor, tablaProfesor, tablaNota

  for widget in ventana.winfo_children():
    widget.destroy()
    
  notebook = ttk.Notebook(ventana)
  notebook.pack(expand=True, fill="both")
  
  
  tablaAlumno = tk.Frame(notebook)
  tablaAsistencia = tk.Frame(notebook)
  tablaCarrera = tk.Frame(notebook)
  tablaMateria = tk.Frame(notebook)
  tablaMateria_Profesor = tk.Frame(notebook)
  tablaProfesor = tk.Frame(notebook)
  tablaNota = tk.Frame(notebook)

  notebook.add(tablaAlumno, text="Alumno")
  notebook.add(tablaAsistencia, text="Asistencia")
  notebook.add(tablaCarrera, text="Carrera")
  notebook.add(tablaMateria, text="Materia")
  notebook.add(tablaMateria_Profesor, text="Enseñanza")
  notebook.add(tablaProfesor, text="Profesor")
  notebook.add(tablaNota, text="Nota")
  
  # Este diccionario mapea el nombre de la pestaña a su widget Frame
  frames_por_nombre = {
      "Alumno": tablaAlumno,
      "Asistencia": tablaAsistencia,
      "Carrera": tablaCarrera,
      "Materia": tablaMateria,
      "Enseñanza": tablaMateria_Profesor,
      "Profesor": tablaProfesor,
      "Nota": tablaNota
  }

  notebook.bind("<<NotebookTabChanged>>", lambda event: abrir_tablas(frames_por_nombre[notebook.tab(notebook.select(), "text")], notebook.tab(notebook.select(), "text").lower()))

  
#En esta función deseo meter la lógica de cada ABM, entries, labels, botones del CRUD y una listBox
def abrir_tablas(frame_principal, nombre_de_la_tabla): 
  def crear_etiqueta(contenedor, texto, tamaño_letra):
    color_padre = contenedor.cget('bg')
    return tk.Label(contenedor, text=texto, fg=colores["negro"], bg=color_padre, font=("Arial", tamaño_letra))

  def crear_entrada(contenedor, ancho, tamaño_letra=10):
    return tk.Entry(contenedor, width=ancho, font=("Arial", tamaño_letra))

  def crear_botón(frameActivo, texto, comando, ancho):
    ancho = len(texto) + 5 if ancho is None else ancho
    return tk.Button(frameActivo, text=texto, width=ancho, command=comando)

  ventanaSecundaria = tk.Toplevel()
  ventanaSecundaria.title(f"{nombre_de_la_tabla.upper()}")
  ventanaSecundaria.geometry("800x800")
  ventanaSecundaria.configure(bg=colores["blanco"])
  ventanaSecundaria.resizable(width=False, height=False)

  # Configuración del grid para los widgets dentro de la ventanaSecundaria
  ventanaSecundaria.grid_columnconfigure(0, weight=0)
  ventanaSecundaria.grid_columnconfigure(1, weight=1)
  ventanaSecundaria.grid_columnconfigure(2, weight=2)
  ventanaSecundaria.grid_rowconfigure(0, weight=1)
  
  # Diccionario que mapea los nombres de las tablas a sus campos
  campos_por_tabla = {
      "alumno": [
          ("Nombre *", "txBox_NombreAlumno"),
          ("Fecha que nació *", "txBox_FechaNacimiento"),
          ("Carrera *","txBox_NombreCarrera")
      ],
      "asistencia": [
          ("Estado *", "txBox_EstadoDeAsistencia"),
          ("Fecha que asistió *", "txBox_FechaAsistencia")
      ],
      "carrera": [
          ("Nombre *", "txBox_NombreCarrera"),
          ("Duración *", "txBox_Duración")
      ],
      "materia": [
          ("Nombre *", "txBox_NombreMateria"),
          ("Horario *", "txBox_HorarioCorrespondiente")
      ],
      "enseñanza": [
          ("Nombre de la asignatura*", "txBox_NombreMateria"),
          ("Nombre del profesor*", "txBox_NombreProfesor")
      ],
      "profesor": [
          ("Nombre *", "txBox_NombreProfesor")
      ],
      "nota": [
          ("Nota *", "txBox_Valor"),
          ("Tipo de evaluación *", "txBox_Tipo"),
          ("Fecha y Hora *", "txBox_Fecha"),
          ("Nombre del estudiante *", "txBox_NombreAlumno"),
          ("Nombre de la asignatura*", "txBox_NombreMateria"),
      ]
  }

  campos = campos_por_tabla.get(nombre_de_la_tabla, None)
  if not campos:
    return
  
  for i, (texto_etiqueta, _) in enumerate(campos):
    crear_etiqueta(ventanaSecundaria, texto_etiqueta, 10).grid(row=i, column=0, sticky="w", padx=5, pady=5)
    crear_entrada(ventanaSecundaria, 30).grid(row=i, column=1, sticky="ew", padx=5, pady=5)

  Lista_de_datos = tk.Listbox(ventanaSecundaria, width=60, height=15)
  Lista_de_datos.grid(row=0, column=2, rowspan=len(campos) + 5, padx=10, pady=10, sticky="nsew")
  
  crear_etiqueta(frame_principal, "el * significa que es obligatorio seleccionar los datos", 8).grid(row=8, column=0, columnspan=2, padx=5,pady=15)

  fila_botones = len(campos) #Esta fila contiene la longitud de cada campo

  crear_botón(ventanaSecundaria, "Agregar", None, 10).grid(row=fila_botones, column=0, columnspan=2, pady=5, sticky="ew")
  # botón_agregar.bind("<Return>", ejecutar_acción_presionando_Enter)

  crear_botón(ventanaSecundaria, "Modificar", None, 10).grid(row=fila_botones + 1, column=0, columnspan=2, pady=5, sticky="ew")
  # botón_modificar.bind("<Return>", ejecutar_acción_presionando_Enter)

  crear_botón(ventanaSecundaria, "Eliminar", None, 10).grid(row=fila_botones + 2, column=0, columnspan=2, pady=5, sticky="ew")
  # botón_eliminar.bind("<Return>", ejecutar_acción_presionando_Enter)

  crear_botón(ventanaSecundaria, "Ordenar", None, 10).grid(row=fila_botones + 3, column=0, columnspan=2, pady=5, sticky="ew")
  # botón_ordenar.bind("<Return>", ejecutar_acción_presionando_Enter)

  crear_botón(ventanaSecundaria, "Exportar", None, 10).grid(row=fila_botones + 4, column=0, columnspan=2, pady=5, sticky="ew")
  # botón_exportar.bind("<Return>", ejecutar_acción_presionando_Enter)
  

# --- INICIO DEL SISTEMA ---
pantallaLogin()
mi_ventana.mainloop()
