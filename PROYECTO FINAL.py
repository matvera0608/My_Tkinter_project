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

def desconectar_base_de_datos(conexión):
  desconectando_db = conexión.is_connected()
  if desconectando_db:
    conexión.close()

mi_ventana = tk.Tk()

# --- EJECUCIÓN DE LA VENTANA PRINCIPAL ---
def pantallaLogin():
  ventana = mi_ventana
  ventana.title("Sistema Gestor de Asistencia")
  ventana.geometry("600x200")
  ventana.configure(bg=colores["blanco"])
  ventana.iconbitmap(ícono)
  ventana.register("Arial", "Arial.ttf")
  ventana.resizable(width=False, height=False)
  ventana.grid_columnconfigure(0, weight=1)
  ventana.grid_rowconfigure(2, weight=1)

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
  
  
  tablaAlumno = ttk.Frame(notebook)
  tablaAsistencia = ttk.Frame(notebook)
  tablaCarrera = ttk.Frame(notebook)
  tablaMateria = ttk.Frame(notebook)
  tablaMateria_Profesor = ttk.Frame(notebook)
  tablaProfesor = ttk.Frame(notebook)
  tablaNota = ttk.Frame(notebook)
  
  notebook.add(tablaAlumno, text="Alumno")
  notebook.add(tablaAsistencia, text="Asistencia")
  notebook.add(tablaCarrera, text="Carrera")
  notebook.add(tablaMateria, text="Materia")
  notebook.add(tablaMateria_Profesor, text="Enseñanza")
  notebook.add(tablaProfesor, text="Profesor")
  notebook.add(tablaNota, text="Nota")

#En esta función deseo meter la lógica de cada ABM, entries, labels, botones del CRUD y una listBox
def abrir_tablas(ventana):
  for widget in ventana.winfo_children():
    widget.destroy()
    
  def crear_etiqueta(ventana, texto, tamaño_letra):
    return tk.Label(ventana, text=texto, fg=colores["negro"], bg=colores["blanco"], font=("Arial", tamaño_letra))
  
  def crear_entrada(ventana, ancho):
    return tk.Entry(ventana, width=ancho)  
  
  def crear_botón(ventana, texto, comando, ancho):
    return tk.Button(ventana, text=texto, width=ancho, command=comando)
  
  frame = tk.Frame(ventana, bg=colores["blanco"])
  frame.pack(fill="both", expand=True, padx=20, pady=20)
    
  
  tablaSeleccionada = notebook.select()
  if tablaSeleccionada == str(tablaAlumno):
      txBox_NombreAlumno = crear_entrada(frame, 30)
      txBox_NombreAlumno.grid(row=0, column=1, pady=5)
      label_NombreAlumno = crear_etiqueta(frame, "Nombre *", 10)
      label_NombreAlumno.grid(row=0, column=0, sticky="w", pady=5)
      
      txBox_FechaNacimiento = crear_entrada(frame, 30)
      txBox_FechaNacimiento.grid(row=1, column=1, pady=5)
      label_FechaNacimiento = crear_etiqueta(frame, "Fecha que nació *", 10)
      label_FechaNacimiento.grid(row=1, column=0, sticky="w", pady=5)

  elif tablaSeleccionada == str(tablaAsistencia):
      txBox_EstadoDeAsistencia = crear_entrada(frame, 30)
      txBox_EstadoDeAsistencia.grid(row=0, column=1, pady=5)
      label_EstadoDeAsistencia = crear_etiqueta(frame, "Estado *", 10)
      label_EstadoDeAsistencia.grid(row=0, column=0, sticky="w", pady=5)
      
      txBox_FechaAsistencia = crear_entrada(frame, 30)
      txBox_FechaAsistencia.grid(row=1, column=1, pady=5)
      label_FechaAsistencia = crear_etiqueta(frame, "Fecha que asistió *", 10)
      label_FechaAsistencia.grid(row=1, column=0, sticky="w", pady=5)

  elif tablaSeleccionada == str(tablaCarrera):
      txBox_NombreCarrera = crear_entrada(frame, 30)
      txBox_NombreCarrera.grid(row=0, column=1, pady=5)
      label_NombreCarrera = crear_etiqueta(frame, "Nombre *", 10)
      label_NombreCarrera.grid(row=0, column=0, sticky="w", pady=5)

      txBox_Duración = crear_entrada(frame, 30)
      txBox_Duración.grid(row=1, column=1, pady=5)
      label_Duración = crear_etiqueta(frame, "Duración *", 10)
      label_Duración.grid(row=1, column=0, sticky="w", pady=5)

  elif tablaSeleccionada == str(tablaMateria):
      txBox_NombreMateria = crear_entrada(frame, 30)
      txBox_NombreMateria.grid(row=0, column=1, pady=5)
      label_NombreMateria = crear_etiqueta(frame, "Nombre *", 10)
      label_NombreMateria.grid(row=0, column=0, sticky="w", pady=5)

      txBox_HorarioCorrespondiente = crear_entrada(frame, 30)
      txBox_HorarioCorrespondiente.grid(row=1, column=1, pady=5)
      label_HorarioCorrespondiente = crear_etiqueta(frame, "Horario *", 10)
      label_HorarioCorrespondiente.grid(row=1, column=0, sticky="w", pady=5)

  elif tablaSeleccionada == str(tablaProfesor):
      txBox_NombreProfesor = crear_entrada(frame, 30)
      txBox_NombreProfesor.grid(row=0, column=1, pady=5)
      label_NombreProfesor = crear_etiqueta(frame, "Nombre *", 10)
      label_NombreProfesor.grid(row=0, column=0, sticky="w", pady=5)

  elif tablaSeleccionada == str(tablaNota):
      txBox_Valor = crear_entrada(frame, 30)
      txBox_Valor.grid(row=0, column=1, pady=5)
      label_Valor = crear_etiqueta(frame, "Nota *", 10)
      label_Valor.grid(row=0, column=0, sticky="w", pady=5)
      
      txBox_Tipo = crear_entrada(frame, 30)
      txBox_Tipo.grid(row=1, column=1, pady=5)
      label_Tipo = crear_etiqueta(frame, "Tipo de evaluación*", 10)
      label_Tipo.grid(row=1, column=0, sticky="w", pady=5)

  label_Obligatoriedad = tk.Label(ventana, text="el * significa que es obligatorio seleccionar los datos")
  label_Obligatoriedad.config(fg=colores["negro"], bg=colores["blanco"], font=("Arial", 8))
  
  

# --- INICIO DEL SISTEMA ---
pantallaLogin()
mi_ventana.mainloop()