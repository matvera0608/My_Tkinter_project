import os
from mysql.connector import Error
import mysql.connector as MySql
import time
import tkinter as TK

##Colores en hexadecimales
rosado_claro = "#FFDEDE"
verde = "#00FF00"
amarillo_claro = ""

ícono = os.path.join(os.path.dirname(__file__),"escuela.ico"

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
      print("QUE GRANDE ÍDOLO, NINGÚN ERROR DE CONEXIÓN")
      return cadena_de_conexión
  except Error as e:
    print(f"Error inesperado al conectar MySql {e}")
    return None

def desconectar_base_de_datos(conexión):
  desconectando_db = conexión.is_connected()
  if desconectando_db:
    conexión.close()
    print("SE HA CERRADO CON ÉXITO")

#En esta región tendré las funciones de base de datos MySQL como Consultar
def consultar_tabla(nombre_de_la_tabla):
  conexión = conectar_base_de_datos()
  if conexión:
    cursor = conexión.cursor()
    cursor.execute(f"SELECT * FROM {nombre_de_la_tabla};")
    resultado = cursor.fetchall()
    Lista_de_datos.delete(0, TK.END)
    
    #Este for muestra toda la tabla completa en la listbox de MySQL
    for fila in resultado:
      filas_formateadas = " | \t".join(map(str, fila))
      Lista_de_datos.insert(TK.END, filas_formateadas)
    
    desconectar_base_de_datos(conexión)

def consultar_tabla_Alumno():
  consultar_tabla('alumno')

def consultar_tabla_Carrera():
  consultar_tabla('carrera')

def consultar_tabla_Curso():
  consultar_tabla('curso')

def seleccionar_y_consultar():
  
  botón_seleccionado = opción.get()
  match botón_seleccionado:
    case 1:
      consultar_tabla_Alumno()
    case 2:
      consultar_tabla_Carrera()
    case 3:
      consultar_tabla_Curso()
    case _:
      print("LA OPCIÓN NO ES VÁLIDA")

#Esta función sirve para actualizar la hora
def actualizar_la_hora():
  label_Hora.config(text=time.strftime("%H:%M:%S"))
  mi_ventana.after(1000, actualizar_la_hora)

#Esta ventana es el comienzo de mi proyecto Tkinter
mi_ventana = TK.Tk()

mi_ventana.title("ABM de Alumnos")

mi_ventana.geometry("900x600")

mi_ventana.minsize(900, 600)

mi_ventana.maxsize(900, 600)

mi_ventana.configure(bg=rosado_claro)

mi_ventana.iconbitmap(ícono)

mi_ventana.attributes("-alpha", 1)

#Creo los botones necesarios para el ABM de alumnos
botón_agregar = TK.Button(text="Agregar Dato", command=lambda:insertar_datos('alumno'), width= 10,height= 1)
botón_agregar.config(fg="black", bg=verde, font=("Arial", 8))

botón_modificar = TK.Button(text="Modificar Dato", command=lambda:modificar_datos('alumno'), width= 10,height= 1)
botón_modificar.config(fg="black", bg="red", font=("Arial", 8))

botón_eliminar = TK.Button(text="Eliminar Dato", width= 10,height= 1)
botón_eliminar.config(fg="black", bg="blue", font=("Arial", 8))


botón_agregar.place(x = 20, y = 120)

botón_modificar.place(x = 20, y = 180)

botón_eliminar.place(x = 20, y = 240)

#Hice un pequeño desorden dentro de mi proyecto, porque creé la función insertar y modificar datos después de declarar
#las variables entry, es decir, textbox ya que en caso contrario la función me dirá que el txBox no se encuentra
def insertar_datos(nombre_de_la_tabla):
  Nombre = txBox_Nombre.get()
  Cantidad_de_notas = txBox_Nota.get()
  
  Datos_necesarios = Nombre and Cantidad_de_notas
  
  if Datos_necesarios:
    conexión = conectar_base_de_datos()
    
    try:
      if conexión:
        cursor = conexión.cursor()
        values = (Nombre, Cantidad_de_notas)
        query = f"INSERT INTO {nombre_de_la_tabla} (Nombre, Cantidad_de_notas) VALUES (%s, %s)"
        
        cursor.execute(query, values)
        conexión.commit()
        
        print("SE AGREGÓ LOS DATOS NECESARIOS")
        
        txBox_Nombre.delete(0, TK.END)
        txBox_Nota.delete(0, TK.END)
        
        consultar_tabla_Alumno()
    except Error as e:
      print(f"ERROR INESPERADO AL INSERTAR: {e}")
  else:
    print("No tiene todos los datos")

def modificar_datos(nombre_de_la_tabla):
  columna_seleccionada = listbox.curseselection()

  if columna_seleccionada:
    ID_Seleccionado = listbox.get(columna_seleccionada)

    Nombre = txBox_Nombre.get()
    Fecha_de_Nacimiento = txBox_FechaNacimiento.get()
    Cantidad_de_Notas = txBox_Nota.get()
  
    Datos_necesarios = Nombre and Fecha_de_Nacimiento and Cantidad_de_Notas
  
    if Datos_necesarios:
      conexión = conectar_base_de_datos()
      try:
        if conexión:
          cursor = conexión.cursor()
          values = (Nombre, Fecha_de_Nacimiento, Cantidad_de_Notas)
          query = "UPDATE {nombre_de_la_tabla} 
                  SET Nombre = %s,
                  Fecha_de_Nacimiento = %s,
                  SET Cantidad_de_Notas = %s
                  WHERE ID = %s"
        
          cursor.execute(query, values)
          conexión.commit()
      except Error as e:
        print(f"ERROR INESPERADO: {e}")
    else:
      print("Faltó completar los campos obligatorios")

  else:
    print("No se seleccionó ninguna columna")

def eliminar_datos(nombre_de_la_tabla):
  columna_seleccionada = listbox.curseselection()

  if columna_seleccionada:
    ID_Seleccionado = listbox.get(columna_seleccionada)
    conexión = conectar_base_de_datos()
    if conexión:
        cursor = conexión.cursor()
        values = (ID_Seleccionado,)
        query = f"DELETE FROM {nombre_de_la_tabla} where ID = %s"
        cursor.execute(query, values)
        conexión.commit()
        print("Una columna ha sido eliminada exitosamente")

    desconectar_base_de_datos()
  else:
    print("No seleccionaste la columna a eliminar")


#Aquí van las etiquetas necesarias como los datos necesarios del alumno
label_Nombre = TK.Label(mi_ventana, text="Nombre")
label_Nombre.config(fg="Black",bg=rosado_claro, font=("Arial", 12))
label_Nombre.place(x = 300, y = 100)

label_FechaNacimiento = TK.Label(mi_ventana, text="Fecha que nació: Formato YYYY-MM-DD")
label_FechaNacimiento.config(fg="Black",bg=rosado_claro, font=("Arial", 12))
label_FechaNacimiento.place(x = 300, y = 150)

label_Nota = TK.Label(mi_ventana, text="Cantidad de notas")
label_Nota.config(fg="Black",bg=rosado_claro, font=("Arial", 12))
label_Nota.place(x = 300, y = 200)

label_Hora = TK.Label(mi_ventana, text=time.strftime("%H:%M:%S"))
label_Hora.config(fg="Black",bg=rosado_claro, font=("Arial", 12))
label_Hora.pack()

#En esta región crearé un textBox a prueba
txBox_Nombre = TK.Entry(mi_ventana)
txBox_Nombre.place(x = 130, y = 100)

txBox_FechaNacimiento = TK.Entry(mi_ventana)
txBox_FechaNacimiento.place(x = 130, y = 150)

txBox_Nota = TK.Entry(mi_ventana)
txBox_Nota.place(x = 130, y = 200)

#En esta región tendrá RadioButtons
opción = TK.IntVar()

Botón_Tabla_de_Alumno = TK.Radiobutton(mi_ventana, text="Alumno", variable=opción, value= 1, command=seleccionar_y_consultar)
Botón_Tabla_de_Alumno.config(bg=rosado_claro, font=("Arial", 12))

Botón_Tabla_de_Carrera = TK.Radiobutton(mi_ventana, text="Carrera", variable=opción, value= 2, command=seleccionar_y_consultar)
Botón_Tabla_de_Carrera.config(bg=rosado_claro, font=("Arial", 12))

Botón_Tabla_de_Curso = TK.Radiobutton(mi_ventana, text="Curso", variable=opción, value= 3, command=seleccionar_y_consultar)
Botón_Tabla_de_Curso.config(bg=rosado_claro, font=("Arial", 12))

Botón_Tabla_de_Alumno.place(x= 60, y = 500)
Botón_Tabla_de_Carrera.place(x = 180, y = 500)
Botón_Tabla_de_Curso.place(x = 300, y = 500)

#En esta región habrá una listBox
Lista_de_datos = TK.Listbox(mi_ventana, width= 60, height= 40)
Lista_de_datos.config(fg="blue", font=("Arial", 10))
Lista_de_datos.place(x= 525, y= 0)


actualizar_la_hora()
mi_ventana.mainloop()
