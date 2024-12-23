from dataclasses import dataclass
from typing import Dict, List, Any

from bambucli.bambu.printer import PrinterModel


@dataclass
class Hardware:
    revision: int
    typeId: int

    @staticmethod
    def from_json(data: Dict[str, Any]) -> 'Hardware':
        return Hardware(
            revision=data['revision'],
            typeId=data['typeid']
        )


@dataclass
class Memory:
    total: int
    used: int

    @staticmethod
    def from_json(data: Dict[str, Any]) -> 'Memory':
        return Memory(
            total=data['total'],
            used=data['used']
        )


@dataclass
class Time:
    utc: float

    @staticmethod
    def from_json(data: Dict[str, Any]) -> 'Time':
        return Time(utc=data['utc'])


@dataclass
class SystemInfo:
    country: str
    display_message: Dict[str, Any]
    firmware: str
    guid: str
    hardware: Hardware
    hostname: str
    language: str
    log: List[str]
    memory: Memory
    name: str
    platform: str
    time: Time
    type: str
    uptime: int
    variant: str

    @staticmethod
    def from_json(data: Dict[str, Any]) -> 'SystemInfo':
        return SystemInfo(
            country=data['country'],
            display_message=data['display_message'],
            firmware=data['firmware'],
            guid=data['guid'],
            hardware=Hardware.from_json(data['hardware']),
            hostname=data['hostname'],
            language=data['language'],
            log=data['log'],
            memory=Memory.from_json(data['memory']),
            name=data['name'],
            platform=data['platform'],
            time=Time.from_json(data['time']),
            type=data['type'],
            uptime=data['uptime'],
            variant=data['variant']
        )

    def printer_model(self) -> PrinterModel:
        return PrinterModel.from_ultimaker_hardware_type_id(self.hardware.typeid)
