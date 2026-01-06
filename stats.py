import numpy as np


def calibrar_curva(data: np.ndarray):
    data[:, 0] = data[:, 0] - data[0, 0]  # corrige tempo 0

    data[:, 1] = data[:, 1] * -4.51e-3 + 37900  # corrige escala de empuxo  # todo: entrar com constantes de calibração
    data[:, 1] = data[:, 1] - data[0, 1]  # corrige offset de empuxo

    return data


def impulso_total(data: np.ndarray):
    return np.trapezoid(data[:, 1], data[:, 0]/1000)  # ms para s

def empuxo_medio(data: np.ndarray):
    return np.mean(data[:, 1])

def empuxo_maximo(data: np.ndarray):
    return np.max(data[:, 1])

def tempo_queima(data: np.ndarray):
    return data[-1, 0] - data[0, 0]

def tempo_pico(data: np.ndarray):
    i_max = np.argmax(data[:, 1])  # índice do pico
    return data[i_max, 0]

def classe_motor(impulso):
    classes = [
        (1.26, 2.5, "A"), (2.5, 5, "B"), (5, 10, "C"), (10, 20, "D"),
        (20, 40, "E"), (40, 80, "F"), (80, 160, "G"), (160, 320, "H"),
        (320, 640, "I"), (640, 1280, "J"), (1280, 2560, "K"), (2560, 5120, "L"),
        (5120, 10240, "M"), (10240, 20480, "N"), (20480, 40960, "O"), (40960, 81920, "P"),
        (81920, 163840, "Q"), (163840, 327680, "R"), (327680, 655360, "S"),
        (655360, 1310720, "T"), (1310720, 2621440, "U"), (2621440, 5242880, "V")
    ]

    for minimo, maximo, classe in classes:
        if minimo <= impulso < maximo:
            return classe
    return "Fora da classificação"
