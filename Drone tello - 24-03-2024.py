from tkinter import *
from tkinter import messagebox
import threading 
import socket
import sys
import time
import platform  
import cv2
import os
from cv2 import VideoWriter, VideoWriter_fourcc
import imageio
import numpy as np
from PIL import Image, ImageTk



#------------------- Inicio das Funções ----------------------------------
is_recording = False
out = None
recording_mutex = threading.Lock()
entry_video_name = None

def on_closing():
    global is_recording, out
    with recording_mutex:
        is_recording = False
    if out is not None:
        out.close()
    root.destroy()
    os._exit(1)
    
def recv():
    while True:
        try:
            data, server = sock.recvfrom(1518)
            addLog(data.decode(encoding="utf-8"))
        except Exception:
            print('\nExit . . .\n')
            break


def addLog(txt):
    terminalList.insert(0, txt)

def startCam():
    global cap
    sock.sendto('streamon'.encode('utf-8'), tello_address)
    cap = cv2.VideoCapture('udp://192.168.10.1:11111')
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 60)

    camThread = threading.Thread(target=camStream)
    camThread.start()


def startCon():
    addLog('Conectando')
    sock.sendto('command'.encode('utf-8'), tello_address)
    label_status_con.config(text='Conectado', fg='green')
    label_status_aircraft.config(text='Pousado')



def takeoff():
    addLog('Decolando')
    sock.sendto('takeoff'.encode('utf-8'), tello_address)
    label_status_aircraft.config(text='Voando', fg='green')
    
def start_recording():
    global is_recording, out
    with recording_mutex:
        is_recording = True
        if out is None:
            video_name = entry_video_name.get() or 'output'
            out = imageio.get_writer(f'{video_name}.mp4', fps=80)

def camStream():
    global is_recording, out
    while True:
        _, frame = cap.read()

        # Verifica se o quadro foi capturado corretamente
        if frame is not None:
            cv2.imshow('cap', frame)

            # Adiciona gravação de vídeo dentro do bloco de mutex
            with recording_mutex:
                if is_recording:
                    if out is None:
                        video_name = entry_video_name.get() or 'output'
                        out = imageio.get_writer(f'{video_name}.mp4', fps=80)

                    out.append_data(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        key = cv2.waitKey(1)

        if key == 27:  # 27 corresponde à tecla Esc
            break

    with recording_mutex:
        if out is not None:
            out.close()
    cv2.destroyAllWindows()

def land():
    addLog('Pousando')
    sock.sendto('land'.encode('utf-8'), tello_address)
    label_status_aircraft.config(text='Pousado')
    
def emergency():
    addLog('Parada de emergencia')
    sock.sendto('emergency'.encode('utf-8'), tello_address)
    label_status_aircraft.config(text='Pousado')


def move_up():
    addLog('Subindo')
    sock.sendto('up 20'.encode('utf-8'), tello_address)

def move_down():
    addLog('Descendo')
    sock.sendto('down 20'.encode('utf-8'), tello_address)

def move_cw():
    addLog('Girando para direita')
    sock.sendto('cw 20'.encode('utf-8'), tello_address)

def move_ccw():
    addLog('Girando para esquerda')
    sock.sendto('ccw 20'.encode('utf-8'), tello_address)

def move_forward():
    addLog('Indo para frente')
    sock.sendto('forward 40'.encode('utf-8'), tello_address)
def move_back():
    addLog('Indo para tras')
    sock.sendto('back 40'.encode('utf-8'), tello_address)

def move_left():
    addLog('Indo para esquerda')
    sock.sendto('left 40'.encode('utf-8'), tello_address)

def move_right():
    addLog('Indo para direita')
    sock.sendto('right 40'.encode('utf-8'), tello_address)

def battery():
    addLog('Nivel da bateria')
    sock.sendto('battery?'.encode('utf-8'), tello_address)

# Funções para iniciar e finalizar a gravação

def start_recording():
    global is_recording, out, video_name
    is_recording = True
    video_name = entry_video_name.get()
    if video_name:
        out = imageio.get_writer(f'{video_name}.mp4', fps=80)
    else:
        messagebox.showwarning("Aviso", "Por favor, insira um nome de vídeo válido.")

def stop_recording():
    global is_recording
    is_recording = False

#------------------- PRE CONFIG ----------------------


host = ''
port = 9000
locaddr = (host,port) 

cap = None

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

tello_address = ('192.168.10.1', 8889)

sock.bind(locaddr)

recvThread = threading.Thread(target=recv)
recvThread.start()

#---------- MAIN FRAME ----------
root = Tk()
root.protocol("WM_DELETE_WINDOW", on_closing)
root.geometry('600x600+200+200')
root.wm_title("TCC - Wellington")

#---------- Comandos FRAME ----------

commandsFrame = LabelFrame(root, text="Comandos", bg="white")
commandsFrame.place(rely=0, relx=0, relwidth=1, relheight=0.7)

entry_video_name = Entry(commandsFrame)
entry_video_name.place(relx=0.05, relwidth=0.6, relheight=0.1, rely=0.1)

label_port = Label(commandsFrame, text="Nome do Video", font=("Helvetica", 12), bg="white")
label_port.place(rely=0, relwidth=0.2, relheight=0.1, relx=0)

btn_connect = Button(commandsFrame, text="Conectar", command=startCon, bg="green", fg="white")
btn_connect.place(relx=0.05, relwidth=0.2, relheight=0.1, rely=0.2)

btn_connect_cam = Button(commandsFrame, text="Camera", command=startCam,  bg="green", fg="white")
btn_connect_cam.place(relx=0.45, relwidth=0.2, relheight=0.1, rely=0.2)

btn_connect_cam = Button(commandsFrame, text="Bateria", command=battery,  bg="green", fg="white")
btn_connect_cam.place(relx=0.25, relwidth=0.2, relheight=0.1, rely=0.2)


# Carregue a imagem do logotipo do IFSC

ifsc_logo_image = Image.open("ifsc_logo.png")
ifsc_logo_image = ifsc_logo_image.resize((240, 200))
ifsc_logo_photo = ImageTk.PhotoImage(ifsc_logo_image)
label_status_con = Label(commandsFrame,image=ifsc_logo_photo )
label_status_con.place(rely=0, relwidth=0.35, relheight=0.45, relx=0.65)

btn_takeoff = Button(commandsFrame, text="Decolar", command=takeoff,  bg="green", fg="white")
btn_takeoff.place(relx=0.05, relwidth=0.2, relheight=0.1, rely=0.3)

btn_land = Button(commandsFrame, text="Pousar", command=land,  bg="green", fg="white")
btn_land.place(relx=0.25, relwidth=0.2, relheight=0.1, rely=0.3)

btn_emergency = Button(commandsFrame, text="Emergencia", command=emergency,  bg="green", fg="white")
btn_emergency.place(relx=0.45, relwidth=0.2, relheight=0.1, rely=0.3)

#------------------ Rotação -----------------

btn_move_up = Button(commandsFrame, text="Subir", command=move_up, bg="green", fg="white")
btn_move_up.place(relx=0.15, relwidth=0.2, relheight=0.1, rely=0.5)

btn_move_cw = Button(commandsFrame, text="Girar Esq", command=move_ccw,  bg="green", fg="white")
btn_move_cw.place(relx=0.05, relwidth=0.2, relheight=0.1, rely=0.6)

btn_move_down = Button(commandsFrame, text="Descer", command=move_down,  bg="green", fg="white")
btn_move_down.place(relx=0.15, relwidth=0.2, relheight=0.1, rely=0.7)

btn_move_ccw = Button(commandsFrame, text="Girar Dir", command=move_cw,  bg="green", fg="white")
btn_move_ccw.place(relx=0.25, relwidth=0.2, relheight=0.1, rely=0.6)

#----------------------- Movimentos -------------------

btn_move_up = Button(commandsFrame, text="Frente", command=move_forward,  bg="green", fg="white")
btn_move_up.place(relx=0.65, relwidth=0.2, relheight=0.1, rely=0.5)

btn_move_cc = Button(commandsFrame, text="Esquerda", command=move_left,  bg="green", fg="white")
btn_move_cc.place(relx=0.55, relwidth=0.2, relheight=0.1, rely=0.6)

btn_move_down = Button(commandsFrame, text="Tras", command=move_back,  bg="green", fg="white")
btn_move_down.place(relx=0.65, relwidth=0.2, relheight=0.1, rely=0.7)

btn_move_cc = Button(commandsFrame, text="Direita", command=move_right,  bg="green", fg="white")
btn_move_cc.place(relx=0.75, relwidth=0.2, relheight=0.1, rely=0.6)


# botões para iniciar e finalizar a gravação
btn_start_recording = Button(commandsFrame, text="Iniciar Gravação", command=start_recording,  bg="green", fg="white")
btn_start_recording.place(relx=0.05, relwidth=0.2, relheight=0.1, rely=0.88)

btn_stop_recording = Button(commandsFrame, text="Parar Gravação", command=stop_recording,  bg="green", fg="white")
btn_stop_recording.place(relx=0.25, relwidth=0.2, relheight=0.1, rely=0.88)

#---------- TERMINAL FRAME ----------
terminalFrame = LabelFrame(root, text="Terminal")
terminalFrame.place(rely=0.7, relx=0, relwidth=1, relheight=0.3)

terminalList = Listbox(terminalFrame)
terminalList.pack(fill="both", expand=1)

#---------- START APP ----------
root.mainloop()
