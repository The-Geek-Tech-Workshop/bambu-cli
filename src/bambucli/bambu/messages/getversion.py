from dataclasses import dataclass
from typing import List, Optional

from bambucli.bambu.printer import PrinterModel


@dataclass
class ModuleInfo:
    name: str
    project_name: str
    sw_ver: str
    hw_ver: str
    sn: str
    flag: int
    new_ver: Optional[str] = None
    loader_ver: Optional[str] = None

    @staticmethod
    def from_json(json_payload: dict) -> 'ModuleInfo':
        return ModuleInfo(
            name=json_payload.get('name'),
            project_name=json_payload.get('project_name'),
            sw_ver=json_payload.get('sw_ver'),
            hw_ver=json_payload.get('hw_ver'),
            sn=json_payload.get('sn'),
            flag=json_payload.get('flag'),
            new_ver=json_payload.get('new_ver'),
            loader_ver=json_payload.get('loader_ver')
        )


@dataclass
class GetVersionMessage:
    command: str
    sequence_id: str
    modules: List[ModuleInfo]
    result: str
    reason: str

    @staticmethod
    def from_json(json_payload: dict) -> 'GetVersionMessage':
        return GetVersionMessage(
            command=json_payload.get('command'),
            sequence_id=json_payload.get('sequence_id'),
            modules=[ModuleInfo.from_json(module)
                     for module in json_payload.get('module', [])],
            result=json_payload.get('result'),
            reason=json_payload.get('reason')
        )

    def printer_model(self) -> PrinterModel:
        for module in self.modules:
            if module.name == 'ota':
                return PrinterModel.from_model_code(module.project_name)
        return PrinterModel.UNKNOWN
