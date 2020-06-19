from PySide2.QtGui import QFontDatabase, QFont
from PySide2.QtMultimedia import QAudio


def logarithmic_to_linear_volume(volume: float) -> float:
    scaled = volume / 100
    linear_volume = QAudio.convertVolume(
        scaled, QAudio.LogarithmicVolumeScale, QAudio.LinearVolumeScale
    )
    return linear_volume * 100


def linear_to_decibel_volume(volume: float) -> float:
    scaled = volume / 100
    decibel = QAudio.convertVolume(
        scaled, QAudio.LinearVolumeScale, QAudio.DecibelVolumeScale
    )
    return decibel


def decibel_to_linear_volume(decibel: float) -> float:
    linear_volume = QAudio.convertVolume(
        decibel, QAudio.DecibelVolumeScale, QAudio.LinearVolumeScale
    )
    return linear_volume * 100


def add_decibel_to_linear_volume(volume: float, decibel: float) -> float:
    volume_in_decibel = linear_to_decibel_volume(volume)
    volume_in_decibel += decibel
    return decibel_to_linear_volume(volume_in_decibel)


def load_dwarf_fortress_font() -> QFont:
    id_ = QFontDatabase.addApplicationFont(":/DwarfFortressVan.ttf")
    family = QFontDatabase.applicationFontFamilies(id_)[0]
    return QFont(family, 12)
