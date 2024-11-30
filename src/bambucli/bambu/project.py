from dataclasses import dataclass
from typing import Optional
import json


@dataclass
class Project:
    project_id: str
    user_id: str
    model_id: str
    status: str
    name: str
    content: Optional[str]
    create_time: str
    update_time: str

    @staticmethod
    def from_json(json_payload: dict) -> 'Project':
        return Project(
            project_id=json_payload.get('project_id'),
            user_id=json_payload.get('user_id'),
            model_id=json_payload.get('model_id'),
            status=json_payload.get('status'),
            name=json_payload.get('name'),
            content=json_payload.get('content'),
            create_time=json_payload.get('create_time'),
            update_time=json_payload.get('update_time')
        )
