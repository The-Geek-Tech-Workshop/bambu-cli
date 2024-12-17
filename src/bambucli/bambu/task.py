from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class AmsDetailMapping:
    ams: int
    sourceColor: str
    targetColor: str
    filamentId: str
    filamentType: str
    targetFilamentType: str
    weight: float

    @staticmethod
    def from_json(data: dict) -> 'AmsDetailMapping':
        return AmsDetailMapping(
            ams=data.get('ams', 0),
            sourceColor=data.get('sourceColor', ''),
            targetColor=data.get('targetColor', ''),
            filamentId=data.get('filamentId', ''),
            filamentType=data.get('filamentType', ''),
            targetFilamentType=data.get('targetFilamentType', ''),
            weight=data.get('weight', 0.0)
        )


@dataclass
class Material:
    id: str
    name: str

    @staticmethod
    def from_json(data: dict) -> 'Material':
        return Material(
            id=data.get('id', ''),
            name=data.get('name', '')
        )


@dataclass
class Task:
    id: int
    designId: int
    designTitle: str
    designTitleTranslated: str
    instanceId: int
    modelId: str
    title: str
    cover: str
    status: int
    feedbackStatus: int
    startTime: datetime
    endTime: datetime
    weight: float
    length: int
    costTime: int
    profileId: int
    plateIndex: int
    plateName: str
    deviceId: str
    amsDetailMapping: List[AmsDetailMapping]
    mode: str
    isPublicProfile: bool
    isPrintable: bool
    isDelete: bool
    deviceModel: str
    deviceName: str
    bedType: str
    jobType: int
    material: Material
    platform: str
    stepSummary: List[str]

    @staticmethod
    def from_json(data: dict) -> 'Task':
        return Task(
            id=data.get('id', 0),
            designId=data.get('designId', 0),
            designTitle=data.get('designTitle', ''),
            designTitleTranslated=data.get('designTitleTranslated', ''),
            instanceId=data.get('instanceId', 0),
            modelId=data.get('modelId', ''),
            title=data.get('title', ''),
            cover=data.get('cover', ''),
            status=data.get('status', 0),
            feedbackStatus=data.get('feedbackStatus', 0),
            startTime=datetime.fromisoformat(data.get('startTime')),
            endTime=datetime.fromisoformat(data.get('endTime')),
            weight=data.get('weight', 0.0),
            length=data.get('length', 0),
            costTime=data.get('costTime', 0),
            profileId=data.get('profileId', 0),
            plateIndex=data.get('plateIndex', 0),
            plateName=data.get('plateName', ''),
            deviceId=data.get('deviceId', ''),
            amsDetailMapping=[AmsDetailMapping.from_json(
                item) for item in data.get('amsDetailMapping', [])],
            mode=data.get('mode', ''),
            isPublicProfile=data.get('isPublicProfile', False),
            isPrintable=data.get('isPrintable', False),
            isDelete=data.get('isDelete', False),
            deviceModel=data.get('deviceModel', ''),
            deviceName=data.get('deviceName', ''),
            bedType=data.get('bedType', ''),
            jobType=data.get('jobType', 0),
            material=Material.from_json(data.get('material', {})),
            platform=data.get('platform', ''),
            stepSummary=data.get('stepSummary', [])
        )
