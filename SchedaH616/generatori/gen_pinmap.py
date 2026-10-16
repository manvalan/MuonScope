"""Scrive docs/pinmap-h616.md dalla netlist esportata (kicadxml) e dalla ball map del datasheet: python3 gen_pinmap.py netlist.xml"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

SC = os.path.dirname(os.path.abspath(__file__))
BALLS = json.load(open(os.path.join(SC, "h616_balls.json")))
BALLS.pop("D17")
BALLS["C17"] = ["AC_VRA1", "AO", "AC+EPHY"]
net_of = {}
for n in ET.parse(sys.argv[1]).getroot().iter("net"):
    for x in n.iter("node"):
        if x.get("ref") == "U301":
            net_of[x.get("pin")] = n.get("name").split("/")[-1]


def key(b):
    return ("ABCDEFGHJKLMNPRTUV".index(b[0]), int(b[1:]))


GPIO_ORDER = lambda name: (re.match(r"P([A-Z])(\d+)", name).group(1), int(re.match(r"P([A-Z])(\d+)", name).group(2)))
out = ["# H616: mappa dei pin della SchedaH616", "",
       "Generata da `generatori/gen_pinmap.py` a partire dalla netlist dello schema e dalla ball map del datasheet",
       "Allwinner H616 V1.0 (tabella 4-2, controllata sfera per sfera sulla figura 7-1).", "",
       "Unica differenza tra tabella e figura: **AC_VRA1** e' D17 nella tabella 4-2 e C17 nella figura 7-1. Lo schema usa C17,",
       "confermato dal footprint EasyEDA C5365289 e dallo schema Orange Pi Zero2 (H616) v1.3.", "",
       "## GPIO", "", "| Pin | Sfera | Dominio | Net | Funzione |", "|---|---|---|---|---|"]
FUNC = {
    "EMMC_": "SMHC2 eMMC 8 bit", "SD_": "SMHC0 microSD", "WL_SDIO": "SMHC1 SDIO AP6256", "BT_UART": "UART1 Bluetooth",
    "RGMII_": "EMAC0 RGMII", "PHY_MD": "MDIO", "UART0": "UART0 debug", "SPI1_": "SPI1 condiviso BUS_POWER/MAIN + EEPROM",
    "PWR_SPI_": "chip select GPIO (cs-gpios)", "MAIN_SPI_CS": "SPI1_CS0 / CS_MASTER", "MAIN_I2C": "TWI2 bus MIKILAB",
    "MAIN_SPI_ALERT": "EINT, ALERT# del bus", "MAIN_HIT": "EINT, HIT# del bus (pin 28 MAIN)", "GNSS_PPS": "EINT, PPS del NEO-M9N",
    "GNSS_EXTINT": "EINT, time mark (solo ingresso)", "GNSS_UART2": "UART2 GNSS", "SOC_ADDR": "ADDR del bus (100R serie)",
    "SOC_PREFIX": "PREFIX del bus (100R serie)", "WIFI_32K": "X32KFOUT, LPO AP6256", "PMU-": "S_TWI0: AXP313A, FUSB302B, TCA6416A",
    "IOX_INT": "INT del TCA6416A (open-drain, 1.8 V)", "PD_INT": "INT del FUSB302B (open-drain, 1.8 V)",
    "USB1_OC": "FAULT del TPS2553 (open-drain, 1.8 V)"}
DOM = {"C": "VCC_PC 1.8 V", "F": "VCC_IO 3.3 V", "G": "VCC_PG 3.3 V", "H": "VCC_IO 3.3 V", "I": "VCC_PI 3.3 V", "L": "VCC_PLL 1.8 V"}
gp = sorted([(v[0], b) for b, v in BALLS.items() if re.match(r"P[A-Z]\d+$", v[0])], key=lambda t: GPIO_ORDER(t[0]))
for name, b in gp:
    n = net_of.get(b, "")
    n = "" if n.startswith("unconnected") else n
    f = next((v for k, v in FUNC.items() if n.startswith(k)), "libero" if not n else "")
    out.append(f"| {name} | {b} | {DOM[name[1]]} | {n or '-'} | {f} |")
out += ["", "## Altre sfere (non GPIO)", "", "| Sfera | Nome | Net |", "|---|---|---|"]
for b in sorted([b for b, v in BALLS.items() if not re.match(r"P[A-Z]\d+$", v[0])], key=key):
    n = net_of.get(b, "")
    out.append(f"| {b} | {BALLS[b][0]} | {'NC' if not n or n.startswith('unconnected') else n} |")
open(os.path.join(SC, "..", "docs", "pinmap-h616.md"), "w").write("\n".join(out) + "\n")
print("sfere:", len(BALLS), "collegate:", sum(1 for b in BALLS if b in net_of and not net_of[b].startswith("unconnected")))
