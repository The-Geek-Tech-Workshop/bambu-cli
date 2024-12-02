from dataclasses import dataclass
from enum import Enum
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


def safe_int(value) -> Optional[int]:
    return int(value) if value is not None else None


def safe_float(value) -> Optional[float]:
    return float(value) if value is not None else None


def safe_bool(value) -> Optional[bool]:
    return bool(value) if value is not None else None


@dataclass
class IpcamConfig:
    ipcam_dev: str
    ipcam_record: str
    resolution: str
    timelapse: str

    @staticmethod
    def from_json(json_payload: dict) -> 'IpcamConfig':
        return IpcamConfig(
            ipcam_dev=json_payload.get('ipcam_dev'),
            ipcam_record=json_payload.get('ipcam_record'),
            resolution=json_payload.get('resolution'),
            timelapse=json_payload.get('timelapse')
        )


@dataclass
class XcamConfig:
    allow_skip_parts: bool
    buildplate_marker_detector: bool
    first_layer_inspector: bool
    halt_print_sensitivity: str
    print_halt: bool
    printing_monitor: bool
    spaghetti_detector: bool

    @staticmethod
    def from_json(json_payload: dict) -> 'XcamConfig':
        return XcamConfig(
            allow_skip_parts=json_payload.get('allow_skip_parts'),
            buildplate_marker_detector=json_payload.get(
                'buildplate_marker_detector'),
            first_layer_inspector=json_payload.get(
                'first_layer_inspector'),
            halt_print_sensitivity=json_payload.get(
                'halt_print_sensitivity'),
            print_halt=json_payload.get('print_halt'),
            printing_monitor=json_payload.get('printing_monitor'),
            spaghetti_detector=json_payload.get('spaghetti_detector')
        )


@dataclass
class TrayInfo:
    id: str
    bed_temp: str
    bed_temp_type: str
    cols: List[str]
    drying_temp: str
    drying_time: str
    nozzle_temp_max: str
    nozzle_temp_min: str
    remain: int
    tag_uid: str
    tray_color: str
    tray_diameter: str
    tray_id_name: str
    tray_info_idx: str
    tray_sub_brands: str
    tray_type: str
    tray_uuid: str
    tray_weight: str
    xcam_info: str

    @staticmethod
    def from_json(json_payload: dict) -> 'TrayInfo':
        return TrayInfo(
            id=json_payload.get('id'),
            bed_temp=json_payload.get('bed_temp'),
            bed_temp_type=json_payload.get('bed_temp_type'),
            cols=json_payload.get('cols'),
            drying_temp=json_payload.get('drying_temp'),
            drying_time=json_payload.get('drying_time'),
            nozzle_temp_max=json_payload.get('nozzle_temp_max'),
            nozzle_temp_min=json_payload.get('nozzle_temp_min'),
            remain=safe_int(json_payload.get('remain')),
            tag_uid=json_payload.get('tag_uid'),
            tray_color=json_payload.get('tray_color'),
            tray_diameter=json_payload.get('tray_diameter'),
            tray_id_name=json_payload.get('tray_id_name'),
            tray_info_idx=json_payload.get('tray_info_idx'),
            tray_sub_brands=json_payload.get('tray_sub_brands'),
            tray_type=json_payload.get('tray_type'),
            tray_uuid=json_payload.get('tray_uuid'),
            tray_weight=json_payload.get('tray_weight'),
            xcam_info=json_payload.get('xcam_info')
        )


@dataclass
class AmsModule:
    humidity: str
    id: str
    temp: str
    tray: List[TrayInfo]

    @staticmethod
    def from_json(json_payload: dict) -> 'AmsModule':
        return AmsModule(
            humidity=json_payload.get('humidity'),
            id=json_payload.get('id'),
            temp=json_payload.get('temp'),
            tray=[TrayInfo.from_json(tray)
                  for tray in json_payload.get('tray', [])]
        )


@dataclass
class AmsStatus:
    ams: List[AmsModule]
    ams_exist_bits: str
    insert_flag: bool
    power_on_flag: bool
    tray_exist_bits: str
    tray_is_bbl_bits: str
    tray_now: str
    tray_pre: str
    tray_read_done_bits: str
    tray_reading_bits: str
    tray_tar: str
    version: int

    @staticmethod
    def from_json(json_payload: dict) -> 'AmsStatus':
        return AmsStatus(
            ams=[AmsModule.from_json(ams)
                 for ams in json_payload.get('ams', [])],
            ams_exist_bits=json_payload.get('ams_exist_bits'),
            insert_flag=json_payload.get('insert_flag'),
            power_on_flag=json_payload.get('power_on_flag'),
            tray_exist_bits=json_payload.get('tray_exist_bits'),
            tray_is_bbl_bits=json_payload.get('tray_is_bbl_bits'),
            tray_now=json_payload.get('tray_now'),
            tray_pre=json_payload.get('tray_pre'),
            tray_read_done_bits=json_payload.get('tray_read_done_bits'),
            tray_reading_bits=json_payload.get('tray_reading_bits'),
            tray_tar=json_payload.get('tray_tar'),
            version=int(json_payload.get('version', 0))
        )


class PrintErrorCode(Enum):
    CANCELLED = 50348044
    FILE_NOT_FOUND = 83935248
    UNKNOWN = -1


@dataclass
class OnPushStatusMessage:
    ams: Optional[AmsStatus]
    ams_rfid_status: int
    ams_status: int
    aux_part_fan: bool
    bed_target_temper: float
    bed_temper: float
    big_fan1_speed: str
    big_fan2_speed: str
    chamber_temper: float
    command: str
    cooling_fan_speed: str
    fail_reason: str
    fan_gear: int
    force_upgrade: bool
    gcode_file: str
    gcode_file_prepare_percent: str
    gcode_start_time: str
    gcode_state: str
    heatbreak_fan_speed: str
    home_flag: int
    hw_switch_state: int
    ipcam: IpcamConfig
    layer_num: int
    lifecycle: str
    lights_report: List[Dict[str, str]]
    maintain: int
    mc_percent: int
    mc_print_error_code: str
    mc_print_stage: str
    mc_print_sub_stage: int
    mc_remaining_time: int
    msg: int
    nozzle_diameter: str
    nozzle_target_temper: float
    nozzle_temper: float
    print_error: PrintErrorCode
    print_gcode_action: int
    print_real_action: int
    print_type: str
    profile_id: str
    project_id: str
    sdcard: bool
    sequence_id: str
    spd_lvl: int
    spd_mag: int
    stg: List[int]
    stg_cur: int
    subtask_id: str
    subtask_name: str
    task_id: str
    total_layer_num: int
    vt_tray: Optional[TrayInfo]
    wifi_signal: str
    xcam: XcamConfig
    xcam_status: str

    def isFullStatus(self) -> bool:
        return self.msg == 0

    @staticmethod
    def from_json(json_payload: dict) -> 'OnPushStatusMessage':
        def get_print_error(value) -> Optional[PrintErrorCode]:
            if value is None or value == 0:
                return None
            error_code = safe_int(value)
            try:
                return PrintErrorCode(error_code)
            except ValueError:
                logger.warning(f"Unknown print error code: {error_code}")
                return PrintErrorCode.UNKNOWN

        return OnPushStatusMessage(
            ams=AmsStatus.from_json(json_payload.get(
                'ams')) if json_payload.get('ams') else None,
            ams_rfid_status=safe_int(json_payload.get('ams_rfid_status')),
            ams_status=safe_int(json_payload.get('ams_status')),
            aux_part_fan=safe_bool(json_payload.get('aux_part_fan')),
            bed_target_temper=safe_float(
                json_payload.get('bed_target_temper')),
            bed_temper=safe_float(json_payload.get('bed_temper')),
            big_fan1_speed=json_payload.get('big_fan1_speed'),
            big_fan2_speed=json_payload.get('big_fan2_speed'),
            chamber_temper=safe_float(json_payload.get('chamber_temper')),
            command=json_payload.get('command'),
            cooling_fan_speed=json_payload.get('cooling_fan_speed'),
            fail_reason=json_payload.get('fail_reason'),
            fan_gear=safe_int(json_payload.get('fan_gear')),
            force_upgrade=safe_bool(json_payload.get('force_upgrade')),
            gcode_file=json_payload.get('gcode_file'),
            gcode_file_prepare_percent=json_payload.get(
                'gcode_file_prepare_percent'),
            gcode_start_time=json_payload.get('gcode_start_time'),
            gcode_state=json_payload.get('gcode_state'),
            heatbreak_fan_speed=json_payload.get('heatbreak_fan_speed'),
            home_flag=safe_int(json_payload.get('home_flag')),
            hw_switch_state=safe_int(json_payload.get('hw_switch_state')),
            ipcam=IpcamConfig.from_json(json_payload.get(
                'ipcam')) if json_payload.get('ipcam') else None,
            layer_num=safe_int(json_payload.get('layer_num')),
            lifecycle=json_payload.get('lifecycle'),
            lights_report=json_payload.get('lights_report'),
            maintain=safe_int(json_payload.get('maintain')),
            mc_percent=safe_int(json_payload.get('mc_percent')),
            mc_print_error_code=json_payload.get('mc_print_error_code'),
            mc_print_stage=json_payload.get('mc_print_stage'),
            mc_print_sub_stage=safe_int(
                json_payload.get('mc_print_sub_stage')),
            mc_remaining_time=safe_int(json_payload.get('mc_remaining_time')),
            msg=safe_int(json_payload.get('msg')),
            nozzle_diameter=json_payload.get('nozzle_diameter'),
            nozzle_target_temper=safe_float(
                json_payload.get('nozzle_target_temper')),
            nozzle_temper=safe_float(json_payload.get('nozzle_temper')),
            print_error=get_print_error(json_payload.get('print_error')),
            print_gcode_action=safe_int(
                json_payload.get('print_gcode_action')),
            print_real_action=safe_int(json_payload.get('print_real_action')),
            print_type=json_payload.get('print_type'),
            profile_id=json_payload.get('profile_id'),
            project_id=json_payload.get('project_id'),
            sdcard=safe_bool(json_payload.get('sdcard')),
            sequence_id=json_payload.get('sequence_id'),
            spd_lvl=safe_int(json_payload.get('spd_lvl')),
            spd_mag=safe_int(json_payload.get('spd_mag')),
            stg=json_payload.get('stg'),
            stg_cur=safe_int(json_payload.get('stg_cur')),
            subtask_id=json_payload.get('subtask_id'),
            subtask_name=json_payload.get('subtask_name'),
            task_id=json_payload.get('task_id'),
            total_layer_num=safe_int(json_payload.get('total_layer_num')),
            vt_tray=TrayInfo.from_json(json_payload.get(
                'vt_tray')) if json_payload.get('vt_tray') else None,
            wifi_signal=json_payload.get('wifi_signal'),
            xcam=XcamConfig.from_json(json_payload.get(
                'xcam')) if json_payload.get('xcam') else None,
            xcam_status=json_payload.get('xcam_status')
        )
