from datetime import datetime
from typing import Dict, Optional, Tuple

from flask import abort
from flask_login import current_user
from sources import models, services
from sources.extensions import db
from sqlalchemy import func


def get(retrosynthesis_id: int) -> models.Retrosynthesis:
    """Returns a retrosynthesis object using the retrosynthesis id"""
    return (
        db.session.query(models.Retrosynthesis)
        .filter(models.Retrosynthesis.id == retrosynthesis_id)
        .first()
    )


def add(
    name: str,
    target_smiles: str,
    uuid: str,
    workbook_id: int,
    conditions: Dict[str, any],
    sustainability: Dict[str, any],
    routes: Dict[str, any],
) -> models.Retrosynthesis:
    # TODO check types of jsons
    creator = current_user.person
    retrosynthesis = models.Retrosynthesis(
        name=name,
        creator=creator,
        workbook=workbook_id,
        conditions=conditions,
        sustainability=sustainability,
        # time_of_creation=datetime.now(),
        routes=routes,
        target_smiles=target_smiles,
        uuid=uuid,
    )
    db.session.add(retrosynthesis)
    db.session.commit()
    return retrosynthesis


def list_from_workbook(selected_workbook_id: int):
    return (
        db.session.query(models.Retrosynthesis)
        .join(models.WorkBook)
        .filter(models.WorkBook.id == selected_workbook_id)
        .all()
    )
