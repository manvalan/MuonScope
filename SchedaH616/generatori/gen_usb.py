"""Foglio USB host (USB1 del SoC su USB-C solo host, come SchedaA133) della scheda H616, serie 8xx."""
import os
import sys
SC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SC)
from kisheet import Sheet, box_symbol

PRJ = sys.argv[1]
u = Sheet("USB host", "usb.kicad_sch", 800, 10, ["5V_SYS"], ("USB1_",))
u.add_sym("H616:TPS2553DBV", box_symbol("H616", "TPS2553DBV",
          [("1", "IN", "L"), ("3", "EN", "L"), ("5", "ILIM", "L"), ("6", "OUT", "R"), ("4", "~{FAULT}", "R"), ("2", "GND", "R")],
          "TI TPS2553, load switch con limite di corrente regolabile e FAULT, SOT-23-6", w=10.16))
for k in ["Device:R", "Device:C", "Connector:USB_C_Receptacle_USB2.0_16P", "Power_Protection:USBLC6-2SC6", "Filter:Choke_CommonMode_FerriteCore_1234"]:
    u.std(k)
u.text("USB HOST: USB1 del SoC su USB-C (16 pin, HRO TYPE-C-31-M-12), solo host, come SchedaA133. Serie 8xx. Net USB1_* globali verso il foglio CPU.", 20, 15)
u.text("La porta non alimenta mai la scheda: VBUS esce solo dal load switch. Rp fissi da 22k a 5V_SYS su CC1/CC2 = sorgente 1.5 A (Type-C), niente controller PD.", 20, 20)

X, Y = 60, 70
u.text("TPS2553: EN attivo alto dall'espansore (P03) con 100k a GND, FAULT open-drain su PC12 (pull-up 10k a VCC-1V8 sul foglio CPU).", X - 40, Y - 22)
u.text("RILIM 26.1k 1% = 0.91 / 0.99 / 1.08 A (min/nom/max, tabella 2 del datasheet).", X - 40, Y - 17)
u.C("C1", "1uF", X - 30, Y, "5V_SYS", "GND_D")
u.place("H616:TPS2553DBV", "U1", "TPS2553DBVR", "Package_TO_SOT_SMD:SOT-23-6", X, Y,
        {"1": "5V_SYS", "3": "USB1_VBUS_EN", "5": "USB1_ILIM", "6": "USB1_VBUS", "4": "USB1_OC_N", "2": "GND_D"}, mpn="TPS2553DBVR")
u.R("R1", "26.1k 1%", X - 20, Y + 20, "USB1_ILIM", "GND_D")
u.R("R2", "100k", X - 10, Y + 20, "USB1_VBUS_EN", "GND_D")
u.C("C2", "100uF/10V", X + 45, Y, "USB1_VBUS", "GND_D", fp="Capacitor_SMD:C_1210_3225Metric")
u.C("C3", "0.1uF", X + 55, Y, "USB1_VBUS", "GND_D")

X, Y = 230, 110
u.text("J801 USB-C: DP/DM collegati su entrambi i lati (A6/B6, A7/B7), SBU non connessi, schermo a GND.", X - 40, Y - 35)
u.place("Connector:USB_C_Receptacle_USB2.0_16P", "J1", "TYPE-C-31-M-12", "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", X, Y,
        {"VBUS": "USB1_VBUS", "CC1": "USB1_CC1", "CC2": "USB1_CC2", "D+": "USB1_DP_C", "D-": "USB1_DM_C", "SBU1": "NC",
         "SBU2": "NC", "GND": "GND_D", "SHIELD": "GND_D"}, mpn="TYPE-C-31-M-12")
u.R("R4", "22k", X + 40, Y - 20, "5V_SYS", "USB1_CC1")
u.R("R5", "22k", X + 50, Y - 20, "5V_SYS", "USB1_CC2")
u.text("Rp 22k a 5 V = 1.5 A (tabella Type-C). Il TPS2553 limita comunque a circa 1 A.", X + 30, Y - 32)

X, Y = 150, 180
u.text("ESD USBLC6-2SC6 vicino al connettore su DP/DM e VBUS. Choke di modo comune DNP con 0R in parallelo (footprint sovrapposti).", X - 40, Y - 20)
u.place("Power_Protection:USBLC6-2SC6", "U2", "USBLC6-2SC6", "Package_TO_SOT_SMD:SOT-23-6", X, Y,
        {"1": "USB1_DP_C", "6": "USB1_DP_C", "3": "USB1_DM_C", "4": "USB1_DM_C", "5": "USB1_VBUS", "2": "GND_D"}, mpn="USBLC6-2SC6")
u.place("Filter:Choke_CommonMode_FerriteCore_1234", "L1", "90R@100MHz", "Inductor_SMD:L_CommonModeChoke_Coilcraft_0805USB", X + 50, Y,
        {"1": "USB1_DP", "2": "USB1_DP_C", "3": "USB1_DM", "4": "USB1_DM_C"}, dnp=True)
u.R("R6", "0R", X + 75, Y - 5, "USB1_DP", "USB1_DP_C")
u.R("R7", "0R", X + 85, Y - 5, "USB1_DM", "USB1_DM_C")
print("porte:", u.write(PRJ, 736.6, 38.1, f"{PRJ}/H616.kicad_sym"))
