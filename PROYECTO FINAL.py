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
  ventana.title("Sistema Gestor de Asistencia")
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
  
  notebook.bind("<<NotebookTabChanged>>", lambda event: abrir_tablas())


def crear_etiqueta(frameActivo, texto, tamaño_letra):
  return tk.Label(frameActivo, text=texto, fg=colores["negro"], bg=colores["blanco"], font=("Arial", tamaño_letra))

def crear_entrada(frameActivo, ancho):
  return tk.Entry(frameActivo, width=ancho)  

def crear_botón(frameActivo, texto, comando, ancho):
  return tk.Button(frameActivo, text=texto, width=ancho, command=comando)



def abrir_tabla_alumno():
  ventanaSecundaria = tk.Toplevel()
  ventanaSecundaria.title("Alumno")
  ventanaSecundaria.geometry("400x400")
  
  txBox_NombreAlumno = crear_entrada(ventanaSecundaria, 30)
  txBox_NombreAlumno.grid(row=0, column=1, pady=5)
  crear_etiqueta(ventanaSecundaria, "Nombre *", 10).grid(row=0, column=0, sticky="w", pady=5)

  txBox_FechaNacimiento = crear_entrada(ventanaSecundaria, 30)
  txBox_FechaNacimiento.grid(row=1, column=1, pady=5)
  crear_etiqueta(ventanaSecundaria, "Fecha que nació *", 10).grid(row=1, column=0, sticky="w", pady=5)

def abrir_tabla_asistencia():
  
  ventanaSecundaria = tk.Toplevel()
  ventanaSecundaria.title("Asistencia")
  ventanaSecundaria.geometry("400x400")
  
  txBox_EstadoDeAsistencia = crear_entrada(ventanaSecundaria, 30)
  txBox_EstadoDeAsistencia.grid(row=0, column=1, pady=5)
  crear_etiqueta(ventanaSecundaria, "Estado *", 10).grid(row=0, column=0, sticky="w", pady=5)
  
  txBox_FechaAsistencia = crear_entrada(ventanaSecundaria, 30)
  txBox_FechaAsistencia.grid(row=1, column=1, pady=5)
  crear_etiqueta(ventanaSecundaria, "Fecha que asistió *", 10).grid(row=1, column=0, sticky="w", pady=5)
  
def abrir_tabla_carrera():
  
  ventanaSecundaria = tk.Toplevel()
  ventanaSecundaria.title("Carrera")
  ventanaSecundaria.geometry("400x400")
  
  txBox_NombreCarrera = crear_entrada(ventanaSecundaria, 30)
  txBox_NombreCarrera.grid(row=0, column=1, pady=5)
  crear_etiqueta(ventanaSecundaria, "Nombre *", 10).grid(row=0, column=0, sticky="w", pady=5)

  txBox_Duración = crear_entrada(ventanaSecundaria, 30)
  txBox_Duración.grid(row=1, column=1, pady=5)
  crear_etiqueta(ventanaSecundaria, "Duración *", 10).grid(row=1, column=0, sticky="w", pady=5)

def abrir_tabla_materia():
  
  ventanaSecundaria = tk.Toplevel()
  ventanaSecundaria.title("Materia")
  ventanaSecundaria.geometry("400x400")
  
  txBox_NombreMateria = crear_entrada(ventanaSecundaria, 30)
  txBox_NombreMateria.grid(row=0, column=1, pady=5)
  crear_etiqueta(ventanaSecundaria, "Nombre *", 10).grid(row=0, column=0, sticky="w", pady=5)

  txBox_HorarioCorrespondiente = crear_entrada(ventanaSecundaria, 30)
  txBox_HorarioCorrespondiente.grid(row=1, column=1, pady=5)
  crear_etiqueta(ventanaSecundaria, "Horario *", 10).grid(row=1, column=0, sticky="w", pady=5)

def abrir_tabla_enseñanza():
  
  ventanaSecundaria = tk.Toplevel()
  ventanaSecundaria.title("Enseñanza")
  ventanaSecundaria.geometry("400x400")
  
  txBox_NombreMateria = crear_entrada(ventanaSecundaria, 30)
  txBox_NombreMateria.grid(row=0, column=1, pady=5)
  crear_etiqueta(ventanaSecundaria, "Nombre de la asignatura*", 10).grid(row=0, column=0, sticky="w", pady=5)
  
  txBox_NombreProfesor = crear_entrada(ventanaSecundaria, 30)
  txBox_NombreProfesor.grid(row=1, column=1, pady=5)
  crear_etiqueta(ventanaSecundaria, "Nombre del profesor*", 10).grid(row=1, column=0, sticky="w", pady=5)


def abrir_tabla_profesor():
  
  ventanaSecundaria = tk.Toplevel()
  ventanaSecundaria.title("Profesor")
  ventanaSecundaria.geometry("400x400")
  
  txBox_NombreProfesor = crear_entrada(ventanaSecundaria, 30)
  txBox_NombreProfesor.grid(row=0, column=1, pady=5)
  crear_etiqueta(ventanaSecundaria, "Nombre *", 10).grid(row=0, column=0, sticky="w", pady=5)
  
def abrir_tabla_nota():
  
  ventanaSecundaria = tk.Toplevel()
  ventanaSecundaria.title("Nota")
  ventanaSecundaria.geometry("400x400")
  
  txBox_Valor = crear_entrada(ventanaSecundaria, 30)
  txBox_Valor.grid(row=0, column=1, pady=5)
  crear_etiqueta(ventanaSecundaria, "Nota *", 10).grid(row=0, column=0, sticky="w", pady=5)

  txBox_Tipo = crear_entrada(ventanaSecundaria, 30)
  txBox_Tipo.grid(row=1, column=1, pady=5)
  crear_etiqueta(ventanaSecundaria, "Tipo de evaluación*", 10).grid(row=1, column=0, sticky="w", pady=5)

#En esta función deseo meter la lógica de cada ABM, entries, labels, botones del CRUD y una listBox
def abrir_tablas():
  global txBox_NombreAlumno, txBox_FechaNacimiento, txBox_EstadoDeAsistencia, txBox_FechaAsistencia, txBox_NombreCarrera, txBox_Duración, txBox_NombreMateria, txBox_HorarioCorrespondiente, txBox_NombreProfesor, txBox_Valor, txBox_Tipo
  
  seleccionado = notebook.select()
  frameActivo = notebook.nametowidget(seleccionado)
  
  for widget in frameActivo.winfo_children():
    widget.destroy()

  frameActivo.grid_columnconfigure(1, weight=1)

  if frameActivo == tablaAlumno:
    abrir_tabla_alumno()
  elif frameActivo == tablaAsistencia:
    abrir_tabla_asistencia()
  elif frameActivo == tablaCarrera:
    abrir_tabla_carrera()
  elif frameActivo == tablaMateria:
    abrir_tabla_materia()
  elif frameActivo == tablaMateria_Profesor:
    abrir_tabla_enseñanza()
  elif frameActivo == tablaProfesor:
    abrir_tabla_profesor()
  elif frameActivo == tablaNota:
    abrir_tabla_nota()
    
  # Lista_de_datos = tk.Listbox(frameActivo, width=60, height=15)
  # Lista_de_datos.grid(row=2, column=0, columnspan=2, pady=10)
  crear_etiqueta(frameActivo, "el * significa que es obligatorio seleccionar los datos", 8).grid(row=8, column=0, columnspan=2, pady=15)
  
  botón_agregar = crear_botón(frameActivo, "Agregar", None, 15)
  # botón_agregar.bind("<Return>", ejecutar_acción_presionando_Enter)

  botón_modificar = crear_botón(frameActivo, "Modificar", None, 15)
  # botón_modificar.bind("<Return>", ejecutar_acción_presionando_Enter)

  botón_eliminar = crear_botón(frameActivo, "Eliminar", None, 15)
  # botón_eliminar.bind("<Return>", ejecutar_acción_presionando_Enter)

  botón_ordenar = crear_botón(frameActivo, "Ordenar", None, 15)
  # botón_ordenar.bind("<Return>", ejecutar_acción_presionando_Enter)
  
  botón_exportar = crear_botón(frameActivo, "Exportar", None, 15)
  # botón_exportar.bind("<Return>", ejecutar_acción_presionando_Enter)
  

# --- INICIO DEL SISTEMA ---
pantallaLogin()
mi_ventana.mainloop()