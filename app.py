import PySimpleGUI as sg

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')

import numpy as np

import pyvisa
rm = pyvisa.ResourceManager('@py')

from time import sleep
import csv
import os

import threading
THREAD_EVENT = '-THREAD-'
THREAD_MESURE = '-THREAD_MESURE-'
THREAD_ANALYSE = '-THREAD_ANALYSE-'

""" 

try:
    get_ipython
except NameError:
    banner=exit_msg=''
else:
    banner = '*** Nested interpreter ***'
    exit_msg = '*** Back in main IPython ***'
 """
#---------------------------------------------------------------------------
# Prepare IPython for Debug button
# First import the embed function
""" from IPython.terminal.embed import InteractiveShellEmbed
# Now create the IPython shell instance. Put ipshell() anywhere in your code
# where you want it to open.
ipshell = InteractiveShellEmbed(banner1=banner, exit_msg=exit_msg)
 """
#---------------------------------------------------------------------------
# This code will load an embeddable IPython shell always with no changes for
# nested embededings.

from IPython import embed
# Now embed() will open IPython anywhere in the code.
#embed()
#---------------------------------------------------------------------------
# This code loads an embeddable shell only if NOT running inside
# IPython. Inside IPython, the embeddable shell variable ipshell is just a
# dummy function.
""" 
try:
    get_ipython
except NameError:
    from IPython.terminal.embed import InteractiveShellEmbed
    ipshell = InteractiveShellEmbed()
    # Now ipshell() will open IPython anywhere in the code
else:
    # Define a dummy ipshell() so the same code doesn't crash inside an
    # interactive IPython
    def ipshell(): pass """
# END
# ---------------------------------------------------------------------------

def commuter_relais(agilent, temps):
    # fonction pour commuter les relais
    # avec l'alimentation Agilent
    # agilent: objet
    agilent.write('OUTPUT ON')
    sleep(temps)
    agilent.write('OUTPUT OFF')
    sleep(temps)

def agilentOutputOn(agilent,rm,args):
    count = 0
    while count < 3:
        try:
            agilent.write('OUTPUT ON')
            break
        except:
            connecter_agilent(rm)
            parametrer_agilent(agilent,args)
            count+=1


def agilentOutputOff(agilent,rm,args):
    count = 0
    while count < 3:
        try:
            agilent.write('OUTPUT OFF')
            break
        except:
            connecter_agilent(rm)
            parametrer_agilent(agilent,args)
            count+=1



def parametrer_agilent(agilent, args):
    # parametrer Tension et Courant
    agilent.write(f"VOLT {args[0]}")
    sleep(1)
    agilent.write(f"CURRENT {args[1]}")
    sleep(1)


def connecter_agilent(rm):
    #return [agilent,msg(*IDN)]
    agilent = rm.open_resource('ASRL/dev/FTDI_USB::INSTR')
    sleep(0.5)
    agilent.write_termination='\r\n'
    sleep(0.5)
    agilent.read_termination = '\r\n'
    sleep(0.5)
    msg = agilent.query('*IDN?')
    sleep(0.5)
    if not(int("AGILENT" in msg)):
        msg = 'error'
    return [agilent,msg]

def connecter_fluke(rm):
    fluke = rm.open_resource('TCPIP:xxx::3490::SOCKET')
    sleep(0.5)
    fluke.write_termination = '\r\n'
    sleep(0.5)
    fluke.read_termination = '\r\n'
    sleep(0.5)
    msg = fluke.query('*IDN?')
    sleep(0.5)
    if not(int("FLUKE" in msg)):
        msg = 'error'
    return [fluke,msg]

def parametrer_fluke(fluke):
    fluke.write('*RST')
    sleep(1)
    while not(int(fluke.query('*OPC?'))):
        continue
    fluke.write('CONF:RES')
    #fluke.write('CONF:FRES')
    sleep(1)
    while not(int(fluke.query('*OPC?'))):
        continue
    fluke.write('SAMPLE:COUNT 3')
    sleep(1)
    while not(int(fluke.query('*OPC?'))):
        continue

def connecter_mux(rm):
    CR1 = rm.open_resource('TCPIP:xxx::3490::SOCKET')
    sleep(0.5)
    CR1.write_termination = '\r\n'
    sleep(0.5)
    CR1.read_termination = '\r\n'
    sleep(0.5)
    CR1_msg = CR1.query('*ST?')
    sleep(0.5)
    if not(int("OK" in CR1_msg)):
        CR1_msg = 'error_CR1'
    
    CR2 = rm.open_resource('TCPIP:xxx::3490::SOCKET')
    sleep(0.5)
    CR2.write_termination = '\r\n'
    sleep(0.5)
    CR2.read_termination = '\r\n'
    sleep(0.5)
    CR2_msg = CR2.query('*ST?')
    sleep(0.5)
    if not(int("OK" in CR2_msg)):
        CR2_msg = 'error_CR2'
    
    CR3 = rm.open_resource('TCPIP:xxx::3490::SOCKET')
    sleep(0.5)
    CR3.write_termination = '\r\n'
    sleep(0.5)
    CR3.read_termination = '\r\n'
    sleep(0.5)
    CR3_msg = CR3.query('*ST?')
    sleep(0.5)
    if not(int("OK" in CR3_msg)):
        CR3_msg = 'error_CR3'    

    CR4 = rm.open_resource('TCPIP:xxx::3490::SOCKET')
    sleep(0.5)
    CR4.write_termination = '\r\n'
    sleep(0.5)
    CR4.read_termination = '\r\n'
    sleep(0.5)
    CR4_msg = CR4.query('*ST?')
    sleep(0.5)
    if not(int("OK" in CR4_msg)):
        CR4_msg = 'error_CR4'
    mux = [CR1,CR2,CR3,CR4]
    mux_msg = [CR1_msg,CR2_msg,CR3_msg,CR4_msg]
    return([mux,mux_msg])





def threadMesure(window,fluke,mux,REL_C,stop):
    # @param: REL_C is a list of [RELx,Tx]
    # @param: mux = [CR1,CR2,CR3,CR4]
    finished = False
    while not(finished):
        if stop():
            # N'oublier pas de faire une sauvegarde avant fermer le Thread
            break
        # Couper l'alimentation des charges
        mux[3].write('SR 1 ON')
        sleep(0.5)
        mux[3].write('SR 3 ON')
        sleep(0.5)
        mux[3].write('SR 5 ON')
        sleep(0.5)
        # ---------------------------------

        # Router le contact à mesurer vers le Fluke
        REL = REL_C[0]
        if not(REL in ['REL1','REL2','REL3','REL4','REL5','REL6','REL7','REL8','REL9','REL10']):
            # Don't forget to return an error msg
            break
        
        Contact = REL_C[1]
        if not(Contact in ['T1','T3','T5']):
            # Don't forget to return an error msg
            break

        match REL:
            case 'REL1':
                if Contact == 'T1':
                    mux[0].write('SR 1 ON')
                    sleep(0.5)
                    mux[0].write('SR 24 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 1 ON')
                    sleep(0.5)
                    mux[1].write('SR 24 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 1 ON')
                    sleep(0.5)
                    mux[2].write('SR 24 ON')
                    sleep(0.5)
            case 'REL2':
                if Contact == 'T1':
                    mux[0].write('SR 2 ON')
                    sleep(0.5)
                    mux[0].write('SR 23 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 2 ON')
                    sleep(0.5)
                    mux[1].write('SR 23 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 2 ON')
                    sleep(0.5)
                    mux[2].write('SR 23 ON')
                    sleep(0.5)
            case 'REL3':
                if Contact == 'T1':
                    mux[0].write('SR 3 ON')
                    sleep(0.5)
                    mux[0].write('SR 22 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 3 ON')
                    sleep(0.5)
                    mux[1].write('SR 22 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 3 ON')
                    sleep(0.5)
                    mux[2].write('SR 22 ON')
                    sleep(0.5)
            case 'REL4':
                if Contact == 'T1':
                    mux[0].write('SR 4 ON')
                    sleep(0.5)
                    mux[0].write('SR 21 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 4 ON')
                    sleep(0.5)
                    mux[1].write('SR 21 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 4 ON')
                    sleep(0.5)
                    mux[2].write('SR 21 ON')
                    sleep(0.5)
            case 'REL5':
                if Contact == 'T1':
                    mux[0].write('SR 5 ON')
                    sleep(0.5)
                    mux[0].write('SR 20 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 5 ON')
                    sleep(0.5)
                    mux[1].write('SR 20 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 5 ON')
                    sleep(0.5)
                    mux[2].write('SR 20 ON')
                    sleep(0.5)
            case 'REL6':
                if Contact == 'T1':
                    mux[0].write('SR 6 ON')
                    sleep(0.5)
                    mux[0].write('SR 19 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 6 ON')
                    sleep(0.5)
                    mux[1].write('SR 19 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 6 ON')
                    sleep(0.5)
                    mux[2].write('SR 19 ON')
                    sleep(0.5)
            case 'REL7':
                if Contact == 'T1':
                    mux[0].write('SR 7 ON')
                    sleep(0.5)
                    mux[0].write('SR 18 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 7 ON')
                    sleep(0.5)
                    mux[1].write('SR 18 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 7 ON')
                    sleep(0.5)
                    mux[2].write('SR 18 ON')
                    sleep(0.5)
            case 'REL8':
                if Contact == 'T1':
                    mux[0].write('SR 8 ON')
                    sleep(0.5)
                    mux[0].write('SR 17 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 8 ON')
                    sleep(0.5)
                    mux[1].write('SR 17 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 8 ON')
                    sleep(0.5)
                    mux[2].write('SR 17 ON')
                    sleep(0.5)
            case 'REL9':
                if Contact == 'T1':
                    mux[0].write('SR 9 ON')
                    sleep(0.5)
                    mux[0].write('SR 16 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 9 ON')
                    sleep(0.5)
                    mux[1].write('SR 16 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 9 ON')
                    sleep(0.5)
                    mux[2].write('SR 16 ON')
                    sleep(0.5)
            case 'REL10':
                if Contact == 'T1':
                    mux[0].write('SR 10 ON')
                    sleep(0.5)
                    mux[0].write('SR 15 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 10 ON')
                    sleep(0.5)
                    mux[1].write('SR 15 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 10 ON')
                    sleep(0.5)
                    mux[2].write('SR 15 ON')
                    sleep(0.5)
        # ---------------------------------
    
        try:
            fluke.write('INIT')
            sleep(1)
            fluke.write('FETCH?')
            sleep(3)
            mesure = fluke.read()
            sleep(.5)
        except:
            mesure = 'error'
        
        finished = True
        # Remettre le chemin mux
        match REL:
            case 'REL1':
                if Contact == 'T1':
                    mux[0].write('SR 1 OFF')
                    sleep(0.5)
                    mux[0].write('SR 24 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 1 OFF')
                    sleep(0.5)
                    mux[1].write('SR 24 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 1 OFF')
                    sleep(0.5)
                    mux[2].write('SR 24 OFF')
                    sleep(0.5)
            case 'REL2':
                if Contact == 'T1':
                    mux[0].write('SR 2 OFF')
                    sleep(0.5)
                    mux[0].write('SR 23 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 2 OFF')
                    sleep(0.5)
                    mux[1].write('SR 23 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 2 OFF')
                    sleep(0.5)
                    mux[2].write('SR 23 OFF')
                    sleep(0.5)
            case 'REL3':
                if Contact == 'T1':
                    mux[0].write('SR 3 OFF')
                    sleep(0.5)
                    mux[0].write('SR 22 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 3 OFF')
                    sleep(0.5)
                    mux[1].write('SR 22 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 3 OFF')
                    sleep(0.5)
                    mux[2].write('SR 22 OFF')
                    sleep(0.5)
            case 'REL4':
                if Contact == 'T1':
                    mux[0].write('SR 4 OFF')
                    sleep(0.5)
                    mux[0].write('SR 21 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 4 OFF')
                    sleep(0.5)
                    mux[1].write('SR 21 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 4 OFF')
                    sleep(0.5)
                    mux[2].write('SR 21 OFF')
                    sleep(0.5)
            case 'REL5':
                if Contact == 'T1':
                    mux[0].write('SR 5 OFF')
                    sleep(0.5)
                    mux[0].write('SR 20 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 5 OFF')
                    sleep(0.5)
                    mux[1].write('SR 20 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 5 OFF')
                    sleep(0.5)
                    mux[2].write('SR 20 OFF')
                    sleep(0.5)
            case 'REL6':
                if Contact == 'T1':
                    mux[0].write('SR 6 OFF')
                    sleep(0.5)
                    mux[0].write('SR 19 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 6 OFF')
                    sleep(0.5)
                    mux[1].write('SR 19 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 6 OFF')
                    sleep(0.5)
                    mux[2].write('SR 19 OFF')
                    sleep(0.5)
            case 'REL7':
                if Contact == 'T1':
                    mux[0].write('SR 7 OFF')
                    sleep(0.5)
                    mux[0].write('SR 18 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 7 OFF')
                    sleep(0.5)
                    mux[1].write('SR 18 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 7 OFF')
                    sleep(0.5)
                    mux[2].write('SR 18 OFF')
                    sleep(0.5)
            case 'REL8':
                if Contact == 'T1':
                    mux[0].write('SR 8 OFF')
                    sleep(0.5)
                    mux[0].write('SR 17 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 8 OFF')
                    sleep(0.5)
                    mux[1].write('SR 17 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 8 OFF')
                    sleep(0.5)
                    mux[2].write('SR 17 OFF')
                    sleep(0.5)
            case 'REL9':
                if Contact == 'T1':
                    mux[0].write('SR 9 OFF')
                    sleep(0.5)
                    mux[0].write('SR 16 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 9 OFF')
                    sleep(0.5)
                    mux[1].write('SR 16 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 9 OFF')
                    sleep(0.5)
                    mux[2].write('SR 16 OFF')
                    sleep(0.5)
            case 'REL10':
                if Contact == 'T1':
                    mux[0].write('SR 10 OFF')
                    sleep(0.5)
                    mux[0].write('SR 15 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 10 OFF')
                    sleep(0.5)
                    mux[1].write('SR 15 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 10 OFF')
                    sleep(0.5)
                    mux[2].write('SR 15 OFF')
                    sleep(0.5)
        # ---------------------------------

    window.write_event_value('-THREAD_MESURE-',[mesure,finished])
    return(mesure)

def nothreadMesure(fluke,mux,REL_C,stop):
    # @param: REL_C is a list of [RELx,Tx]
    # @param: mux = [CR1,CR2,CR3,CR4]
    finished = False
    while not(finished):
        if stop():
            # N'oublier pas de faire une sauvegarde avant fermer le Thread
            break
        # Couper l'alimentation des charges
        mux[3].write('SR 1 ON')
        sleep(0.5)
        mux[3].write('SR 3 ON')
        sleep(0.5)
        mux[3].write('SR 5 ON')
        sleep(0.5)
        # ---------------------------------

        # Router le contact à mesurer vers le Fluke
        REL = REL_C[0]
        if not(REL in ['REL1','REL2','REL3','REL4','REL5','REL6','REL7','REL8','REL9','REL10']):
            # Don't forget to return an error msg
            break
        
        Contact = REL_C[1]
        if not(Contact in ['T1','T3','T5']):
            # Don't forget to return an error msg
            break

        match REL:
            case 'REL1':
                if Contact == 'T1':
                    mux[0].write('SR 1 ON')
                    sleep(0.5)
                    mux[0].write('SR 24 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 1 ON')
                    sleep(0.5)
                    mux[1].write('SR 24 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 1 ON')
                    sleep(0.5)
                    mux[2].write('SR 24 ON')
                    sleep(0.5)
            case 'REL2':
                if Contact == 'T1':
                    mux[0].write('SR 2 ON')
                    sleep(0.5)
                    mux[0].write('SR 23 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 2 ON')
                    sleep(0.5)
                    mux[1].write('SR 23 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 2 ON')
                    sleep(0.5)
                    mux[2].write('SR 23 ON')
                    sleep(0.5)
            case 'REL3':
                if Contact == 'T1':
                    mux[0].write('SR 3 ON')
                    sleep(0.5)
                    mux[0].write('SR 22 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 3 ON')
                    sleep(0.5)
                    mux[1].write('SR 22 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 3 ON')
                    sleep(0.5)
                    mux[2].write('SR 22 ON')
                    sleep(0.5)
            case 'REL4':
                if Contact == 'T1':
                    mux[0].write('SR 4 ON')
                    sleep(0.5)
                    mux[0].write('SR 21 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 4 ON')
                    sleep(0.5)
                    mux[1].write('SR 21 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 4 ON')
                    sleep(0.5)
                    mux[2].write('SR 21 ON')
                    sleep(0.5)
            case 'REL5':
                if Contact == 'T1':
                    mux[0].write('SR 5 ON')
                    sleep(0.5)
                    mux[0].write('SR 20 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 5 ON')
                    sleep(0.5)
                    mux[1].write('SR 20 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 5 ON')
                    sleep(0.5)
                    mux[2].write('SR 20 ON')
                    sleep(0.5)
            case 'REL6':
                if Contact == 'T1':
                    mux[0].write('SR 6 ON')
                    sleep(0.5)
                    mux[0].write('SR 19 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 6 ON')
                    sleep(0.5)
                    mux[1].write('SR 19 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 6 ON')
                    sleep(0.5)
                    mux[2].write('SR 19 ON')
                    sleep(0.5)
            case 'REL7':
                if Contact == 'T1':
                    mux[0].write('SR 7 ON')
                    sleep(0.5)
                    mux[0].write('SR 18 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 7 ON')
                    sleep(0.5)
                    mux[1].write('SR 18 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 7 ON')
                    sleep(0.5)
                    mux[2].write('SR 18 ON')
                    sleep(0.5)
            case 'REL8':
                if Contact == 'T1':
                    mux[0].write('SR 8 ON')
                    sleep(0.5)
                    mux[0].write('SR 17 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 8 ON')
                    sleep(0.5)
                    mux[1].write('SR 17 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 8 ON')
                    sleep(0.5)
                    mux[2].write('SR 17 ON')
                    sleep(0.5)
            case 'REL9':
                if Contact == 'T1':
                    mux[0].write('SR 9 ON')
                    sleep(0.5)
                    mux[0].write('SR 16 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 9 ON')
                    sleep(0.5)
                    mux[1].write('SR 16 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 9 ON')
                    sleep(0.5)
                    mux[2].write('SR 16 ON')
                    sleep(0.5)
            case 'REL10':
                if Contact == 'T1':
                    mux[0].write('SR 10 ON')
                    sleep(0.5)
                    mux[0].write('SR 15 ON')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 10 ON')
                    sleep(0.5)
                    mux[1].write('SR 15 ON')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 10 ON')
                    sleep(0.5)
                    mux[2].write('SR 15 ON')
                    sleep(0.5)
        # ---------------------------------
    
        try:
            fluke.write('INIT')
            sleep(1)
            fluke.write('FETCH?')
            sleep(3)
            mesure = fluke.read()
            sleep(.5)
        except:
            mesure = 'error'
        
        finished = True
        # Remettre le chemin mux
        match REL:
            case 'REL1':
                if Contact == 'T1':
                    mux[0].write('SR 1 OFF')
                    sleep(0.5)
                    mux[0].write('SR 24 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 1 OFF')
                    sleep(0.5)
                    mux[1].write('SR 24 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 1 OFF')
                    sleep(0.5)
                    mux[2].write('SR 24 OFF')
                    sleep(0.5)
            case 'REL2':
                if Contact == 'T1':
                    mux[0].write('SR 2 OFF')
                    sleep(0.5)
                    mux[0].write('SR 23 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 2 OFF')
                    sleep(0.5)
                    mux[1].write('SR 23 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 2 OFF')
                    sleep(0.5)
                    mux[2].write('SR 23 OFF')
                    sleep(0.5)
            case 'REL3':
                if Contact == 'T1':
                    mux[0].write('SR 3 OFF')
                    sleep(0.5)
                    mux[0].write('SR 22 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 3 OFF')
                    sleep(0.5)
                    mux[1].write('SR 22 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 3 OFF')
                    sleep(0.5)
                    mux[2].write('SR 22 OFF')
                    sleep(0.5)
            case 'REL4':
                if Contact == 'T1':
                    mux[0].write('SR 4 OFF')
                    sleep(0.5)
                    mux[0].write('SR 21 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 4 OFF')
                    sleep(0.5)
                    mux[1].write('SR 21 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 4 OFF')
                    sleep(0.5)
                    mux[2].write('SR 21 OFF')
                    sleep(0.5)
            case 'REL5':
                if Contact == 'T1':
                    mux[0].write('SR 5 OFF')
                    sleep(0.5)
                    mux[0].write('SR 20 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 5 OFF')
                    sleep(0.5)
                    mux[1].write('SR 20 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 5 OFF')
                    sleep(0.5)
                    mux[2].write('SR 20 OFF')
                    sleep(0.5)
            case 'REL6':
                if Contact == 'T1':
                    mux[0].write('SR 6 OFF')
                    sleep(0.5)
                    mux[0].write('SR 19 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 6 OFF')
                    sleep(0.5)
                    mux[1].write('SR 19 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 6 OFF')
                    sleep(0.5)
                    mux[2].write('SR 19 OFF')
                    sleep(0.5)
            case 'REL7':
                if Contact == 'T1':
                    mux[0].write('SR 7 OFF')
                    sleep(0.5)
                    mux[0].write('SR 18 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 7 OFF')
                    sleep(0.5)
                    mux[1].write('SR 18 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 7 OFF')
                    sleep(0.5)
                    mux[2].write('SR 18 OFF')
                    sleep(0.5)
            case 'REL8':
                if Contact == 'T1':
                    mux[0].write('SR 8 OFF')
                    sleep(0.5)
                    mux[0].write('SR 17 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 8 OFF')
                    sleep(0.5)
                    mux[1].write('SR 17 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 8 OFF')
                    sleep(0.5)
                    mux[2].write('SR 17 OFF')
                    sleep(0.5)
            case 'REL9':
                if Contact == 'T1':
                    mux[0].write('SR 9 OFF')
                    sleep(0.5)
                    mux[0].write('SR 16 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 9 OFF')
                    sleep(0.5)
                    mux[1].write('SR 16 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 9 OFF')
                    sleep(0.5)
                    mux[2].write('SR 16 OFF')
                    sleep(0.5)
            case 'REL10':
                if Contact == 'T1':
                    mux[0].write('SR 10 OFF')
                    sleep(0.5)
                    mux[0].write('SR 15 OFF')
                    sleep(0.5)
                elif Contact == 'T3':
                    mux[1].write('SR 10 OFF')
                    sleep(0.5)
                    mux[1].write('SR 15 OFF')
                    sleep(0.5)
                elif Contact == 'T5':
                    mux[2].write('SR 10 OFF')
                    sleep(0.5)
                    mux[2].write('SR 15 OFF')
                    sleep(0.5)
        # ---------------------------------

    return(mesure)

sg.theme("Light Blue 6")
sg.set_options(font=("Parisine Office",12))

# ------------------------------- Beginning of Matplotlib helper code -----------------------

def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

# ------------------------------- PASTE YOUR MATPLOTLIB CODE HERE -------------------------------
#
# # Goal is to have your plot contained in the variable  "fig"

def delete_figure_agg(figure_agg):
    figure_agg.get_tk_widget().forget()
    #plt.close('all')
    #plt.cla()
    plt.clf()




menu_bar = [['&Fichier'],['&Editer'], ['A propos']]

""" agilent_layout = [[sg.Button('Connecter',key='-agilent_connect-'),sg.Text("", size=(0,1),key='-agilent_connect_state-')],
                   [sg.Text('Consigne de tension'),sg.InputText(default_text='24',key='-agilent_volt-')],
                   [sg.Text('Consigne de courant'),sg.InputText(default_text='2',key='-agilent_ampere-')],
                ] """

agilent_layout = [ [sg.Text('Consigne de tension'),sg.InputText(default_text='24',key='-agilent_volt-')],
                   [sg.Text('Consigne de courant'),sg.InputText(default_text='2',key='-agilent_ampere-')],
                   [sg.Text('Consigne de mesure'),sg.InputText(default_text='5',key='-freq-')]
                ]


fluke_layout = [[sg.Button('Connecter',key='-fluke_connect-'),sg.Text("", size=(0,1),key='-fluke_connect_state-')]]
ds28_1_layout = [[sg.Button('Connecter',key='-ds28_1_connect-'),sg.Text("", size=(0,1),key='-ds28_1_connect_state-')]]
ds28_2_layout = [[sg.Button('Connecter',key='-ds28_2_connect-'),sg.Text("", size=(0,1),key='-ds28_2_connect_state-')]]
ds28_3_layout = [[sg.Button('Connecter',key='-ds28_3_connect-'),sg.Text("", size=(0,1),key='-ds28_3_connect_state-')]]
ds28_4_layout = [[sg.Button('Connecter',key='-ds28_4_connect-'),sg.Text("", size=(0,1),key='-ds28_4_connect_state-')]]

appareil_layout = [[sg.Button('Connecter',key='-appareil_connect-'),sg.Button('Appareils non connectés',key='-appareil_state-',button_color=('white','red'))]]

contact_layout = [[sg.Text('STF/SFS/HSP (dinh-tuan.nguyen@ratp.fr)',justification='left')]]

debug_layout = [[sg.Button('Debug')]]

left_col = [[sg.Frame('Configuration', agilent_layout,expand_x=True)],
            [sg.Frame("Connexion d'appareils", appareil_layout,expand_x=True)],
            [sg.Button('Start'),sg.Button('Stop'),sg.Button('Exit')],
            [sg.Frame('Debug session',debug_layout)],
            ]

""" right_col=[[sg.Input(default_text=os.path.expanduser("~\\"),key='-File-',size=(30,2)),sg.FolderBrowse(button_text='Open')],
           [sg.Combo(['RL1','RL2','RL3','RL4','RL5','RL6','RL7','RL8','RL9','RL10'],default_value='RL1',key='-relais_select-'),sg.Combo(['T1','T3','T5'],default_value='T1',key='-contact_select-'),sg.Button('Tracer'),sg.Button('Effacer')],
           [sg.Canvas(key='-canvas-')],
           [sg.Text('Commutations en cours: '),sg.Multiline(size=10,key='-nbr_commutations-',reroute_stdout=False, write_only=True),sg.Button('Clear',key='-app_state-',button_color=('white','green'))],
           [sg.Table(values=[],key='-table_mesure-',headings=['Nombre de commutations','T1','T3','T5'],expand_x=True,auto_size_columns=True,display_row_numbers=False,vertical_scroll_only=True)]
        ] """

right_col=[[sg.Input(default_text=os.path.expanduser("~\\"),key='-File-',size=(30,2)),sg.FolderBrowse(button_text='Open')],
           [sg.Combo(['RL1','RL2','RL3','RL4','RL5','RL6','RL7','RL8','RL9','RL10'],default_value='RL1',key='-relais_select-'),sg.Combo(['T1','T3','T5'],default_value='T1',key='-contact_select-'),sg.Button('Tracer'),sg.Button('Effacer')],
           [sg.Canvas(key='-canvas-')],
           [sg.Text('Commutations en cours: '),sg.Multiline(size=10,key='-nbr_commutations-',reroute_stdout=False, write_only=True),sg.Button('Clear',key='-app_state-',button_color=('white','green'))],
           [sg.Button('Analyser')],
           [sg.Multiline('',size=(48,10),key='-output-',autoscroll = True,expand_y = True)]
        ]

layout = [[sg.Menu(menu_bar)],
          [sg.Column([[sg.Image('Ratp_logopetit.png'),]],justification='center')],
          [sg.Column(left_col,expand_x=True,vertical_alignment='top'),sg.Column(right_col,expand_x=True,vertical_alignment='top')],
          [sg.Text('Contact: STF/SFS/HSP (dinh-tuan.nguyen@ratp.fr)',justification='left')]
        ]

window = sg.Window("BdER",layout,default_element_size=(12,1),grab_anywhere=True,resizable=True,finalize=True,element_justification='center')


count=0
mesure_is_finished = False
stop_mesure = False
stop_analyse = False
t1_state = True

def threadCommutationcyclic(window,count_t,freq,stop):
    window.write_event_value('-THREAD-',count_t)
    if (count_t == 0):
        #agilentOutputOn(agilent)
        sleep(1)
        #agilentOutputOff(agilent)
        sleep(1)
        window.write_event_value('-THREAD-',count_t)
        print(['commuting',count_t])
        count_t += 1    
    if (count_t > 0):
        while (count_t % freq != 0):
            if stop():
                #agilentOutputOff(agilent)
                break
            #agilentOutputOn(agilent)
            sleep(1)
            #agilentOutputOff(agilent)
            sleep(1)
            window.write_event_value('-THREAD-',count_t)
            print(['commuting',count_t])
            count_t += 1
        while (count_t % freq == 0):
            #agilentOutputOn(agilent)
            sleep(1)
            #agilentOutputOff(agilent)
            sleep(1)
            window.write_event_value('-THREAD-',count_t)
            print(['commuting',count_t])
            count_t += 1
            print(['commuting',count_t])
            break 

def threadAnalyse(window,stop):
    for i in ['REL1','REL2','REL3','REL4','REL5','REL6','REL7','REL8','REL9','REL10']:
        for j in ['T1','T3','T5']:
            msg_outlier = [i,'&',j]
            nameFILE = values['-File-'] + "/"+ "mesure_"+ i + "_" + j +".csv"
            nameFILE = os.path.normpath(nameFILE)
            with open(nameFILE,newline='') as csvfile:
                dataTracer = csv.reader(csvfile, delimiter =',')
                X_val = []
                Y_val = []
                for row in dataTracer:
                    try:
                        dataRow = row[0]
                        dataRow = dataRow.replace('\"','')
                        dataRow = dataRow.split(',')
                        Y_int = [float(y) for y in dataRow][1:]
                        if len(Y_int) != 0:
                            X_val.append([float(x) for x in dataRow][0])
                            Y_val.append(sum(Y_int)/len(Y_int))
                    except:
                        continue
                Y_np = np.array(Y_val)
                std_cal = np.std(Y_np)
                mean_cal = np.mean(Y_np)
                for iter in range(len(Y_np)):
                    if (Y_np[iter] <= (mean_cal-3*std_cal)) or (Y_np[iter]>=(mean_cal+3*std_cal)):
                        msg_outlier.append(Y_np[iter])
            window.write_event_value('-THREAD_ANALYSE-',msg_outlier)

while True:             # Event Loop
    event, values = window.read(timeout=500)

    # if event == sg.TIMEOUT_KEY:
    #     continue 
   

    if event == '-appareil_connect-':
        fluke, msg_fluke = connecter_fluke(rm)
        if not(msg_fluke == 'error'):
            parametrer_fluke(fluke)
        sleep(1)
        agilent, msg_agilent = connecter_agilent(rm)
        if not(msg_agilent == 'error'):
            parametrer_agilent(agilent,[values['-agilent_volt-'],values['-agilent_ampere-']])
        sleep(1)
        mux, mux_msg = connecter_mux(rm)
        if not('error' in [msg_fluke,msg_agilent,mux_msg]):
            window['-appareil_state-'].update('Appreils connectés!')
            window['-appareil_state-'].update(button_color = ('white','green'))

    if event in (sg.WINDOW_CLOSED, 'Exit'):         # checks if user wants to exit
        break

    if event == 'Debug':
        embed()


    if (event == 'Start') or mesure_is_finished:
        stop_threads = False
        stop_mesure = False
        mesure_is_finished = False
        t1 = threading.Thread(target=threadCommutationcyclic, args=(window,count,int(values['-freq-']),lambda: stop_threads), daemon=True)
        t1.start()
        window['Start'].update(disabled=True)
        window['-app_state-'].update('Commutation')
        window['-app_state-'].update(button_color=('white','orange'))
        t1_state = t1.is_alive()    


    if event == THREAD_EVENT :
        count = values[THREAD_EVENT]
        window['-nbr_commutations-'].update(value=values[THREAD_EVENT])
    if event == 'Stop':
        stop_threads = True
        stop_mesure = True
        stop_analyse = True
        window['Start'].update(disabled=False)
        window['-app_state-'].update('Clear')
        window['-app_state-'].update(button_color=('white','green'))
        mesure_is_finished = False
    if (count > 0 ) and (count % int(values['-freq-']) == 0) and not(t1.is_alive()):
        # Effectuer les mesures
        window['-nbr_commutations-'].update(value=count)
        window['-app_state-'].update('Busy')
        window['-app_state-'].update(button_color=('white','red'))
        window.refresh()
        iter = 0
        while (iter < 20000000):
            iter += 1
        mesure_is_finished = True
        count += 1
        """ 
        for i in ['REL1','REL2','REL3','REL4','REL5','REL6','REL7','REL8','REL9','REL10']:
            for j in ['T1','T3','T5']:
                # The Mesure will block the whole app until finished
                #mesure = nothreadMesure(fluke,mux,[i,j],lambda:stop_mesure)
                t_mesure = threading.Thread(target=threadMesure,args=(window,fluke,mux,[i,j],lambda: stop_mesure),daemon = True)
                t_mesure.start()
                if event  == THREAD_MESURE:
                    mesure, mesure_is_finished = values[THREAD_MESURE]
                #mesure_sauvegarde = [count] + [sum([float(x) for x in mesure.split(",")])/len(mesure.split(","))]
                try:
                    mesure_sauvegarde = [count] + [float(x) for x in mesure.split(",")]
                except:
                    mesure_sauvegarde = [count] + [mesure] # in case of an 'error' is returned in mesure

                # Write mesure to file for each REL-Contact
                filename = values('-File-')+"mesure_"+ i + "_" + j +".csv"
                with open(filename,"a",newline="") as f:
                    writer = csv.writer(f)
                    writer.writerrows(mesure_sauvegarde)
 """
    if event == 'Effacer':
        if 'fig_canvas_agg' in locals():
            # delete existing fig before draw new ones
            # anticipate multiple clicks on Tracer button
            delete_figure_agg(fig_canvas_agg)

    if event == 'Tracer':
        nameREL = values['-relais_select-']
        nameCON = values['-contact_select-']
        nameFILE = values['-File-'] + "/"+ "mesure_"+ nameREL + "_" + nameCON +".csv"
        nameFILE = os.path.normpath(nameFILE)
        with open(nameFILE,newline='') as csvfile:
            dataTracer = csv.reader(csvfile, delimiter =',')
            X_val = []
            Y_val = []
            for row in dataTracer:
                try:
                    dataRow = row[0]
                    dataRow = dataRow.replace('\"','')
                    dataRow = dataRow.split(',')
                    Y_int = [float(y) for y in dataRow][1:]
                    if len(Y_int) != 0:
                        X_val.append([float(x) for x in dataRow][0])
                        Y_val.append(sum(Y_int)/len(Y_int))
                except:
                    continue
        if 'fig_canvas_agg' in locals():
            # delete existing fig before draw new ones
            # anticipate multiple clicks on Tracer button
            delete_figure_agg(fig_canvas_agg)

        fig = matplotlib.figure.Figure(figsize=(6, 4), dpi=70)
        ax = fig.add_subplot(111)
        ax.plot(X_val,Y_val,marker=".", color = 'blue')
        ax.set_facecolor('lightgrey')
        ax.grid(True,linestyle='--',color = 'white')
        ax.set_xlabel('Commutations')
        ax.set_ylabel(r'Résistance $(\Omega)$')
        ax.set_ylim(0,2)
        ax.get_xaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: (format(int(x),',')).replace(',',' ')))
        ax.set_title("Evolution de la résistance de contact " + nameCON + " du relais "+nameREL)
        fig_canvas_agg = draw_figure(window['-canvas-'].TKCanvas,fig)
        window.refresh()

    if event == 'Analyser':



window.close()

