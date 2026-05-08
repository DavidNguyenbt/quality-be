from typing import List, Optional
from pydantic import BaseModel, Field

class DefectData(BaseModel):
    DefectName: str
    TTP: float
    Per: float

class DefectImageData(BaseModel):
    DefectName: str
    ImgSrc: str
    Item: str
    SupCode: str

class RFT(BaseModel):
    M: str
    RFT: Optional[float]

class SupCode(BaseModel):
    SupCode: str
    RFT: Optional[float]

class DefectImageDataAcc(BaseModel):
    TopN: float
    DefectName: str
    TTP: float
    Per: float
    ImgSrc: str

class DefectImageDataAcc1(DefectImageDataAcc):
    NameVn: str

class RFTAcc(BaseModel):
    Dept: str
    FacLine: str
    TransMonth: str
    TotalBundleQty: float
    TotalDefectQty: float
    RFT: float
    target: float

class Subcon(BaseModel):
    id: int
    department: str

class DashboardNotDecorateRequest(BaseModel):
    starttime: str
    endtime: str
    fac: str
    supp: str
    dept: int

class DashboardDecorateRequest(BaseModel):
    fac: str
    starttime: str
    endtime: str
    dept: int
    
class JobRequest(BaseModel):
    text: str
    
class DataRequest(BaseModel):
    fac: str = Field(
        ..., 
        description="Prefix của line",
        json_schema_extra={"example": "A1AF2"}
    )

    line: List[str] = Field(
        default_factory=list,
        description="Danh sách line, rỗng = All",
        json_schema_extra={"example": ["F2A01", "F2A02"]}
    )

    date_from: str = Field(
        ..., 
        json_schema_extra={"example": "20251224"}
    )

    date_to: str = Field(
        ..., 
        json_schema_extra={"example": "20251224"}
    )

    url: int = Field(
        ..., 
        json_schema_extra={"example": 100}
    )
    
from enum import IntEnum

class CTQType(IntEnum):
    TLS = 1
    GARMENT = 2
    MERGE1 = 3
    CTQ = 4
    MASTER_LAYOUT = 5
    INLINE = 6
    INLINE_CTP= 7
    INLINE_CTP_RAW_DATA= 8

TYPE_DESC = {
    CTQType.TLS: "TLS_Report_QC_Defect",
    CTQType.GARMENT: "Garment_Pass",
    CTQType.MERGE1: "Merge1_TLS_Garment",
    CTQType.CTQ: "CTQ_Endline",
    CTQType.MASTER_LAYOUT: "MASTER_LAYOUT",
    CTQType.INLINE: "INLINE",
    CTQType.INLINE_CTP: "INLINE_CTP",
    CTQType.INLINE_CTP_RAW_DATA: "INLINE_CTP_RAW_DATA"
} 

def get_type_desc(type: int) -> str:
    return TYPE_DESC.get(CTQType(type), "Unknown_Type")