from PySide2.QtMultimedia import QAudio


def logarithmic_to_linear_volume(volume: int) -> int:
    scaled = volume / 100
    linear_volume = QAudio.convertVolume(
        scaled, QAudio.LogarithmicVolumeScale, QAudio.LinearVolumeScale
    )
    return linear_volume * 100


def linear_to_decibel_volume(volume: int) -> int:
    scaled = volume / 100
    decibel = QAudio.convertVolume(
        scaled, QAudio.LinearVolumeScale, QAudio.DecibelVolumeScale
    )
    return decibel


def decibel_to_linear_volume(decibel: int) -> int:
    linear_volume = QAudio.convertVolume(
        decibel, QAudio.DecibelVolumeScale, QAudio.LinearVolumeScale
    )
    return linear_volume * 100


def add_decibel_to_linear_volume(volume: int, decibel: int) -> int:
    volume_in_decibel = linear_to_decibel_volume(volume)
    volume_in_decibel += decibel
    return decibel_to_linear_volume(volume_in_decibel)
