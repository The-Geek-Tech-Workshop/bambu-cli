from dataclasses import dataclass
from datetime import timedelta
from enum import Enum
import json
from typing import List, Optional
from zipfile import ZipFile
import untangle
import re
from bambucli.bambu.printer import PrinterModel


class FilamentType(Enum):
    PLA = 'PLA'
    ABS = 'ABS'
    PETG = 'PETG'
    TPU = 'TPU'


@dataclass
class Plate:
    index: int
    filament_type: FilamentType
    filament_amount_grams: float
    print_time: timedelta


@dataclass
class ProjectFile:
    model: PrinterModel
    nozzle_diameter: float
    plates: List[Plate]


def extract_project_file_data(path: str) -> ProjectFile:
    with ZipFile(path) as zip_file:
        with zip_file.open('Metadata/project_settings.config') as project_file:
            project_settings = json.loads(
                project_file.read().decode('utf-8'))
            with zip_file.open('Metadata/slice_info.config') as slice_file:
                slice_info = untangle.parse(slice_file.read().decode('utf-8'))
                plates = slice_info.config.plate if hasattr(
                    slice_info.config, 'plate') else []
                plates = [plates] if not isinstance(plates, list) else plates
                return ProjectFile(
                    model=PrinterModel(re.findall(
                        r'Bambu Lab (.+)', project_settings['printer_model'])[0]),
                    nozzle_diameter=float(project_settings['printer_variant']),
                    plates=list(map(_extract_plate, plates))
                )


def _extract_plate(plate) -> Plate:
    new_plate = Plate(
        index=int(_get_metadata_value(
            plate.metadata, 'index')),
        filament_type=FilamentType(
            plate.filament['type']),
        filament_amount_grams=_get_metadata_value(
            plate.metadata, 'weight'),
        print_time=timedelta(
            seconds=float(_get_metadata_value(plate.metadata, 'prediction')))
    )
    return new_plate


def _get_metadata_value(metadata, key):
    return next(filter(lambda x: x['key'] == key, metadata))['value']
