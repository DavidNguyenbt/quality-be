from http.client import HTTPException
from typing import List
from app.core.ResponseApi import ResponseAPI
from app.qc_dashboard.model import RFT, DefectData, DefectImageData, DefectImageDataAcc, DefectImageDataAcc1, RFTAcc, SupCode
from app.qc_dashboard.repository import ParamConfigRepository
import time
import app.core.config as settings

def convert_string(s: str) -> str:
    return s.upper().replace(' ', '_')

class ParamConfigService:
    def __init__(self):
        self.repository = ParamConfigRepository()

    def dashboard_notdecorate(self, starttime: str, endtime: str, fac: str, supp: str, dept: int):
        return self.repository.dashboard_notdecorate(starttime, endtime, fac, supp, dept)

    def dashboard_decorate(self, fac: str, starttime: str, endtime: str, dept: int):
        try:
            query1 = f"SET nocount on; EXEC [DtradeProduction].[dbo].[usp_EndlineDecorationReport_GetRFT] {dept},'{fac}','{starttime}','{endtime}',1"
            query2 = f"SET nocount on; EXEC [DtradeProduction].[dbo].[usp_EndlineDecorationReport_GetRFT] {dept},'{fac}','{starttime}','{endtime}',2"

            rft_rows = self.repository.get_first_result(query1)
            defect_rows = self.repository.get_first_result(query2)

            results_list = [RFTAcc(
                Dept=row[0],
                FacLine=row[1],
                TransMonth=row[3],
                TotalBundleQty=row[4],
                TotalDefectQty=row[5],
                RFT=row[6],
                target=row[7]
            ) for row in rft_rows]

            total_quantity = sum(row[3] if dept<=7 or dept>=20 else row[4] for row in defect_rows)
            results_list1 = []

            for row in defect_rows:
                if dept <= 7 or dept >= 20:
                    results_list1.append(DefectImageDataAcc(
                        TopN=row[0],
                        DefectName=row[1],
                        TTP=row[2],
                        Per=round((row[3]/total_quantity)*100, 2),
                        ImgSrc=row[4]
                    ))
                else:
                    results_list1.append(DefectImageDataAcc1(
                        TopN=row[0],
                        DefectName=row[1],
                        TTP=row[3],
                        Per=round((row[4]/total_quantity)*100, 2),
                        ImgSrc=row[5],
                        NameVn=row[2]
                    ))

            return {"datalinebar": results_list, "datapie": results_list1}

        except Exception as e:
            return ResponseAPI(
                data=None,
                message=f"Internal Server Error: {str(e)}",
                code=500
            ).to_json_response()

    def getSubcon(self):
        try:
            rows = self.repository.get_subcon()
            return {"subcon": [{"id": row[0], "department": row[1]} for row in rows]}
        except Exception as e:
            return ResponseAPI(
                data=None,
                message=f"Internal Server Error: {str(e)}",
                code=500
            ).to_json_response()

    def getAllSubcon(self):
        try:
            rows = self.repository.get_all_subcon()
            static_subcon_data = [
                {"id": 1, "department": "Cutting"},
                {"id": 2, "department": "Heat Transfer"},
                {"id": 3, "department": "Embroidery"},
                {"id": 4, "department": "Pad Print"},
                {"id": 5, "department": "Bonding"},
                {"id": 8, "department": "SEWING LINE- ENDLINE"},
                {"id": 9, "department": "SEWING LINE- INLINE"},
                {"id": 10, "department": "FINAL"},
            ]
            results_list = [{"id": row[0], "department": row[1]} for row in rows]
            results_list.extend(static_subcon_data)
            return {"subcon": results_list}
        except Exception as e:
            return ResponseAPI(
                data=None,
                message=f"Internal Server Error: {str(e)}",
                code=500
            ).to_json_response()

    def searchStyleByText(self, text: str):
        return self.repository.searchStyleByText(text.upper())
    
    def getCTQDashboard(self, fac_prefix: str, line: List[str], date_from: str, date_to: str):
        start = time.perf_counter()
        result = self.repository.getCTQDashboard(fac_prefix, line, date_from, date_to)
        duration = time.perf_counter() - start
        print(f"[InlineQC] get_data took {duration:.3f}s | rows = {len(result)}")
        return result
    
    def getCTQDashboardEndline(self, fac_prefix: str, line: List[str], date_from: str, date_to: str):
        start = time.perf_counter()
        result = self.repository.getCTQDashboardEndline(fac_prefix, line, date_from, date_to)
        duration = time.perf_counter() - start
        print(f"[EndlineQC] get_data took {duration:.3f}s | rows = {len(result)}")
        return result
    
    
    def getCTQEndLine(self, fac_prefix: str, date_from: str, date_to: str, type: int, style: str | None = None):

        match type:
            case 1:
                # TLS Report (QC Endline lỗi)
                return self.repository.getTLS_report(fac_prefix, date_from, date_to)

            case 2:
                # Garment (EndlineQcReportGmtPass)
                return self.repository.getGarment(fac_prefix, date_from, date_to)

            case 3:
                # Merge 1: TLS + Garment
                return self.repository.getMerge1(fac_prefix, date_from, date_to)

            case 4:
                # Merge 2: Merge1 + MasterLayout (CTQ)
                return self.repository.getMerge2(fac_prefix, date_from, date_to)
            case 5:
                return self.repository.getMasterLayout(style)
            case 6:
                return self.repository.getResultInline(fac_prefix, date_from, date_to)
            case 7:
                return self.repository.getResultInlineCTP(fac_prefix, date_from, date_to)
            
            case 8:
                return self.repository.getTest(fac_prefix, date_from, date_to)

            case _:
                return ResponseAPI(
                    data=None,
                    message="Invalid type parameter",
                    code=400
                ).to_json_response()
                
                
    def getAllFactory(self):
        return self.repository.getAllFactory()