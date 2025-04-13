from typing import Optional

from pydantic import BaseModel, Field


class LawMetadata(BaseModel):
    number: str = Field(
        serialization_alias="norma_numero",
        alias="norma_numero",
    )
    title: str = Field(serialization_alias="norma_titulo", alias="norma_titulo")
    subject: str = Field(serialization_alias="norma_materia", alias="norma_materia")
    status: str = Field(serialization_alias="norma_estado", alias="norma_estado")
    category: str = Field(
        serialization_alias="norma_categoria", alias="norma_categoria"
    )
    rank: str = Field(serialization_alias="norma_rango", alias="norma_rango")
    pulication_date: str = Field(
        serialization_alias="norma_fecha_publicacion", alias="norma_fecha_publicacion"
    )
    approval_date: str = Field(
        serialization_alias="norma_fecha_aprobacion", alias="norma_fecha_aprobacion"
    )
    url: Optional[str] = Field(serialization_alias="norma_url", alias="norma_url")
    related_fields: Optional[list[dict]] = Field(
        serialization_alias="norma_archivos_relacionados",
        alias="norma_archivos_relacionados",
    )
    related_laws: Optional[str] = Field(
        serialization_alias="norma_relacionadas", alias="norma_relacionadas"
    )
    international_instrument_clasification: Optional[str] = Field(
        default=None,
        serialization_alias="instrumento_internacional_clasificacion",
        alias="instrumento_internacional_clasificacion",
    )
    international_instrument_type: Optional[str] = Field(
        default=None,
        serialization_alias="instrumento_internacional_tipo",
        alias="instrumento_internacional_tipo",
    )
    international_instrument_subscription_date: Optional[str] = Field(
        default=None,
        serialization_alias="instrumento_internacional_fecha_suscripcion",
        alias="instrumento_internacional_fecha_suscripcion",
    )
    international_instrument_subscription_place: Optional[str] = Field(
        default=None,
        serialization_alias="instrumento_internacional_lugar_suscripcion",
        alias="instrumento_internacional_lugar_suscripcion",
    )


class UserMetadata(BaseModel):
    password: str = Field(serialization_alias="user_password", alias="user_password")

    last_login: str = Field(serialization_alias="last_login", alias="last_login")

    super_user: str = Field(serialization_alias="super_user", alias="super_user")

    name: str = Field(serialization_alias="user_name",alias="user_name",)

    firstname: str = Field(serialization_alias="user_firstname", alias="user_firstname")
    
    lastname: str = Field(serialization_alias="user_lastname", alias="user_lastname")

    date_joined: str = Field(serialization_alias="date_joined", alias="date_joined")

    email: str = Field(serialization_alias="user_email", alias="user_email")

    active: str = Field(serialization_alias="active", alias="active")

    administrator: str = Field(serialization_alias="admin", alias="admin")
    
class LawData(BaseModel):
    id: str
    filename: str
    metadata: LawMetadata

class UserData(BaseModel):
    id: int
    metadata: UserMetadata

class LawDataFormContext(BaseModel):
    modal_header: str
    confirm_botton_text: str
    csrf_token: str
    statuses: list[str]
    administrator: list[str]
    categories: list[str]
    ranks: list[str]
    subjects: list[str]
    law_data: Optional[LawData] = Field(default=None)


class UserDataFormContext(BaseModel):
    modal_header: str
    confirm_botton_text: str
    csrf_token: str
    statuses: list[str]
    administrator: list[str]
    categories: list[str]
    ranks: list[str]
    subjects: list[str]
    user_data: Optional[UserData] = Field(default=None)


class LawDataTable(BaseModel):
    id: str
    title: str
    status: str
    publication_date: Optional[str]

class UserDataTable(BaseModel):
    id: int
    password: str
    last_login: str
    super_user: bool
    name: str
    firstname: str
    lastname: str
    date_joined: str
    email: str
    active: bool
    administrator: bool

statuses = [
    "Vigente",
    "Incorporación en Texto Consolidado",
    "Objeto Cumplido",
    "Derogación Expresa",
    "Consolidada",
    "Derogación Tácita",
    "Plazo Vencido",
    "Instrumento Internacional",
]

administrator = [
    "Yes",
    "No",
]

categories = [
    "Reglamento de Ley",
    "Decreto Ejecutivo",
    "Ley",
    "Decreto Legislativo",
    "Decreto-Ley",
    "Decreto con Fuerza de Ley",
    "Reglamento",
    "Otras Normas",
    "Instrumento Internacional",
]

ranks = [
    "Decreto Ejecutivo",
    "Ley",
    "Decreto Legislativo",
    "Decreto-Ley",
    "Decreto JGRN",
    "Decreto A.C.",
    "Acuerdo Legislativo",
    "Reglamento",
    "Acuerdo Ejecutivo",
    "Instrumento Internacional",
    "Acuerdo Presidencial",
]

subjects = [
    "Administrativa",
    "Aduanas",
]
