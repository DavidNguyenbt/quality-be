from typing import Optional
from app.core.ResponseApi import ResponseAPI
from app.qc_dashboard.model import TYPE_DESC, DashboardDecorateRequest, DashboardNotDecorateRequest, DataRequest, JobRequest, get_type_desc
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, StreamingResponse
from app.qc_dashboard.service import ParamConfigService
from openpyxl import Workbook
from io import BytesIO
from datetime import datetime

qc_dashboard_router = APIRouter()

service = ParamConfigService()


@qc_dashboard_router.post('/dashboard-no-decorate')
def select_notdecorate(req: DashboardNotDecorateRequest):
    # Chỉ truyền dữ liệu đã parse vào service
    results = service.dashboard_notdecorate(
        starttime=req.starttime,
        endtime=req.endtime,
        fac=req.fac,
        supp=req.supp,
        dept=req.dept
    )
    if isinstance(results, JSONResponse):
        return results
    return ResponseAPI(data=results)

@qc_dashboard_router.post('/dashboard-decorate')
def select_decorate(req: DashboardDecorateRequest):
    results = service.dashboard_decorate(
        fac=req.fac,
        starttime=req.starttime,
        endtime=req.endtime,
        dept=req.dept
    )
    if isinstance(results, JSONResponse):
        return results
    return ResponseAPI(data=results)

@qc_dashboard_router.get('/getsubcon')
def select_Subcon():
    results = service.getSubcon()
    if isinstance(results, JSONResponse):
        return results
    return ResponseAPI(data=results)



@qc_dashboard_router.get('/getalldepartment')
def select_AllSubcon():
    results = service.getAllSubcon()
    if isinstance(results, JSONResponse):
        return results
    return ResponseAPI(data=results)


@qc_dashboard_router.post('/searchStyleByText')
def searchStyleByText(data: JobRequest):
    results = service.searchStyleByText(data.text)
    if isinstance(results, JSONResponse):
        return results
    return ResponseAPI(data=results)
    
@qc_dashboard_router.post('/getCTQDashboard')
def getCTQDashboard(data: DataRequest):
    if data.url == 99:
        results = service.getCTQDashboard(data.fac, data.line, data.date_from, data.date_to)
    else :
        results = service.getCTQDashboardEndline(data.fac, data.line, data.date_from, data.date_to)
    if isinstance(results, JSONResponse):
        return results
    return ResponseAPI(data=results)

@qc_dashboard_router.get('/getCTQEndLine/{fac}/{date_from}/{date_to}/{type}')
def getCTQEndLine(fac: str, date_from: str, date_to: str, type: int, style: str | None = Query(default=None)):

    results = service.getCTQEndLine(fac, date_from, date_to, type, style)

    if isinstance(results, JSONResponse):
        return results

    if not results:
        return ResponseAPI(
            data=None,
            message="No data",
            code=204
        )

    type_desc = get_type_desc(type)

    wb = Workbook()
    ws = wb.active
    if ws is None:
        raise Exception("Worksheet is None")
    ws.title = type_desc[:31] 

    headers = list(results[0].keys())
    ws.append(headers)

    for row in results:
        ws.append(list(row.values()))

    ws.freeze_panes = "A2"
    ws.auto_filter.ref = ws.dimensions

    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    filename = (
        f"{type_desc}_{fac}_"
        f"{date_from}_{date_to}_"
        f"{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
    )

    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
    
@qc_dashboard_router.get('/getAllFactory')
def getAllFactory():
    results = service.getAllFactory()
    if isinstance(results, JSONResponse):
        return results
    return ResponseAPI(data=results)