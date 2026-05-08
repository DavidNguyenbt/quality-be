from typing import List
from app.core.ResponseApi import ResponseAPI
from app.qc_dashboard.model import RFT, DefectData, DefectImageData, SupCode
import pyodbc
from fastapi import HTTPException
from app.core.config import settings


class ParamConfigRepository:
    def __init__(self):
        self.connection_string = (
            f"DRIVER={{{settings.DB_DRIVER}}};"
            f"SERVER={settings.DB_SERVER};"
            f"DATABASE={settings.DB_NAME};"
            f"UID={settings.DB_USER};"
            f"PWD={settings.DB_PASSWORD};"
            f"Encrypt={settings.DB_ENCRYPT};"
            f"TrustServerCertificate={settings.DB_TRUST_SERVER_CERTIFICATE};"
        )

    def connect(self):
        try:
            return pyodbc.connect(self.connection_string)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Database connection error: {e}")

    def execute_query(self, query: str):
        """Thực thi query và trả về tất cả các result set"""
        results = []
        settings.MESSAGE = ''
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    while True:
                        rows = cursor.fetchall()
                        results.append(rows)
                        if not cursor.nextset():
                            break
            return results
        except Exception as e:
            settings.MESSAGE = f"Internal Server Error: {str(e)}"
            return []
        
    def get_first_result(self, query: str):
        result = self.execute_query(query)
        if isinstance(result, list):
            return result[0] if result else []
        return []

    def get_subcon(self):
        try:
            query = "SELECT * FROM dbo.DecorationDepartment WHERE NO >10"
            return self.get_first_result(query)
        except Exception as e:
            return {"error": f"Internal Server Error: {str(e)}"}

    def get_all_subcon(self):
        settings.MESSAGE = ''
        try:
            query = "SELECT * FROM dbo.DecorationDepartment WHERE NO >10"
            return self.get_first_result(query)
        except Exception as e:
            settings.MESSAGE = f"Internal Server Error: {str(e)}"
            return []

    def dashboard_notdecorate(self, starttime: str, endtime: str, fac: str, supp: str, dept: int):
        settings.MESSAGE = ''
        try:
            query = ""
            if dept == 11:
                query = f"SET nocount on; EXEC dbo.InlineFBDashboard_Config '{starttime}','{endtime}','{fac}','{supp}'"
            else:
                query = f"SET nocount on; EXEC dbo.InlineAccWHDashboard_Config '{starttime}','{endtime}','{fac}',N'{supp}'"
            print(query)
            # Kết nối 1 lần
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query)
                    all_tables = []
                    while True:
                        rows = cursor.fetchall()
                        all_tables.append(rows)
                        if not cursor.nextset():
                            break

            # Khởi tạo list kết quả
            results_list = []
            results_list1 = []
            results_list2 = []
            results_list3 = []
            results_list4 = []

            # Supp = All --> chỉ dùng 3 bảng
            if supp == "All":
                if len(all_tables) >= 1:
                    for row in all_tables[0]:
                        results_list.append(
                            SupCode(SupCode=row[0], RFT=row[1] if row[1] is not None else 0))

                if len(all_tables) >= 2:
                    for row in all_tables[1]:
                        results_list1.append(DefectData(
                            DefectName=row[1], TTP=row[2], Per=row[3]))

                if len(all_tables) >= 3:
                    for row in all_tables[2]:
                        raw_img = row[2] if row[2] else ""

                        # Nếu có nhiều ảnh, tách bằng dấu phẩy và lấy ảnh đầu
                        first_img = raw_img.split(",")[0] if raw_img else ""

                        # Bỏ phần .jpg nếu có
                        img = first_img.split(".")[0] if first_img else ""
                        results_list2.append(
                            DefectImageData(
                                DefectName=row[1],
                                ImgSrc=f"{settings.IMAGE_URL}/{'FbwarehouseImg' if dept==11 else 'AccWHImageDF'}/{img}.jpg",
                                Item=row[3],
                                SupCode=row[4] if len(row) > 4 else ""
                            )
                        )

                return {
                    "databar": results_list,
                    "datapie": results_list1,
                    "datalist": results_list2
                }

            # Supp != All --> dùng 5 bảng
            else:
                if len(all_tables) >= 1:
                    for row in all_tables[0]:
                        results_list.append(
                            RFT(M=row[0], RFT=row[1] if row[1] is not None else 0))

                if len(all_tables) >= 2:
                    for row in all_tables[1]:
                        results_list1.append(DefectData(
                            DefectName=row[1], TTP=row[2], Per=row[3]))

                if len(all_tables) >= 3:
                    for row in all_tables[2]:
                        raw_img = row[2] if row[2] else ""

                        # Nếu có nhiều ảnh, tách bằng dấu phẩy và lấy ảnh đầu
                        first_img = raw_img.split(",")[0] if raw_img else ""

                        # Bỏ phần .jpg nếu có
                        img = first_img.split(".")[0] if first_img else ""
                        results_list2.append(
                            DefectImageData(
                                DefectName=row[1],
                                ImgSrc=f"{settings.IMAGE_URL}/{'FbwarehouseImg' if dept==11 else 'AccWHImageDF'}/{img}.jpg",
                                Item=row[3],
                                SupCode=row[4] if len(row) > 4 else ""
                            )
                        )

                if len(all_tables) >= 4:
                    for row in all_tables[3]:
                        results_list3.append(DefectData(
                            DefectName=row[0], TTP=row[1], Per=row[2]))

                if len(all_tables) >= 5:
                    for row in all_tables[4]:
                        raw_img = row[1] if row[1] else ""

                        # Nếu có nhiều ảnh, tách bằng dấu phẩy và lấy ảnh đầu
                        first_img = raw_img.split(",")[0] if raw_img else ""

                        # Bỏ phần .jpg nếu có
                        img = first_img.split(".")[0] if first_img else ""
                        results_list4.append(
                            DefectImageData(
                                DefectName=row[0],
                                ImgSrc=f"{settings.IMAGE_URL}/{'FbwarehouseImg' if dept==11 else 'AccWHImageDF'}/{img}.jpg",
                                Item="",
                                SupCode=""
                            )
                        )

                return {
                    "databar": results_list,
                    "datapie": results_list1,
                    "datalist": results_list2,
                    "datapie1": results_list3,
                    "datalist1": results_list4
                }

        except Exception as e:
            settings.MESSAGE = f"Internal Server Error: {str(e)}"
            return []


    def searchStyleByText(self, text: str):
        settings.MESSAGE = ''
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:

                    if not text:  # text rỗng hoặc None
                        query = """
                            SELECT DISTINCT TOP 10 [STYLE_NO]
                            FROM [DtradeProduction].[dbo].[InlineQcLayout]
                            WHERE [STYLE_NO] IS NOT NULL
                        """
                        cursor.execute(query)
                    else:
                        text = text.upper()  # convert chữ hoa
                        query = """
                            SELECT DISTINCT [STYLE_NO]
                            FROM [DtradeProduction].[dbo].[InlineQcLayout]
                            WHERE UPPER([STYLE_NO]) LIKE ?
                        """
                        cursor.execute(query, (f"%{text}%",))

                    table = cursor.fetchall()

                    results_list = [
                        {"style": row[0]}
                        for row in table
                    ]

                    return results_list

        except Exception as e:
            settings.MESSAGE = f"Internal Server Error: {str(e)}" 
            return []

    def getCTQDashboard(self, fac_prefix: str, line: List[str], date_from: str, date_to: str):
        settings.MESSAGE = ''
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    is_all = len(line) == 1 and line[0] == "All"
                    sql=""
                    if is_all:
                        sql = """
                        SET NOCOUNT ON;

                        IF OBJECT_ID('tempdb..#t1') IS NOT NULL DROP TABLE #t1;
                        IF OBJECT_ID('tempdb..#t2') IS NOT NULL DROP TABLE #t2;
                        IF OBJECT_ID('tempdb..#t3') IS NOT NULL DROP TABLE #t3;
                        IF OBJECT_ID('tempdb..#t4') IS NOT NULL DROP TABLE #t4;
                        SELECT *
                        INTO #t1
                        FROM InlineQcLayout WITH (NOLOCK)
                        WHERE LEFT(LINEST,2) = ?
                        AND DATEST BETWEEN ? AND ?;

                        CREATE CLUSTERED INDEX IX1 ON #t1 (BARCODE, RANGETIME, ORDNUM);

                        -- STEP 2
                        SELECT
                            a.BARCODE,
                            a.RANGETIME,
                            a.ORDNUM,
                            a.CODEDEFECT,
                            a.DEFECT,
                            b.DFNAMEVN,
                            b.DFNAMEEN
                        INTO #t2
                        FROM SubInlineQc a WITH (NOLOCK)
                        LEFT JOIN InlineQcDefectCodeName b WITH (NOLOCK)
                            ON a.CODEDEFECT = b.DFCODEIN
                        WHERE a.BARCODE IN (SELECT BARCODE FROM #t1 WHERE BARCODE <> '');

                        CREATE CLUSTERED INDEX IX2 ON #t2 (BARCODE, RANGETIME, ORDNUM);

                        -- FINAL
                        SELECT DISTINCT
                        t1.*,
                        CAST(ISNULL(m.RFT,0) AS BIT) AS CRI,
                        CAST(ISNULL(m.CTQ,0) AS BIT) AS CTQ,
                        CAST(ISNULL(m.CTP,0) AS BIT) AS CTP,
                        t2.CODEDEFECT,
                        t2.DEFECT,
                        t2.DFNAMEVN,
                        t2.DFNAMEEN,
                        adm.Code,
                        adm.DefectEN,
                        adm.DefectVN
                        INTO #t3
                        FROM #t1 t1
                        LEFT JOIN MasterLayout m
                        ON t1.LINEST   = m.LINEST
                        AND t1.STYLE_NO = m.STYLE_NO
                        AND t1.CODEOPT  = m.CODEOPT
                        LEFT JOIN #t2 t2
                        ON t1.BARCODE   = t2.BARCODE
                        AND t1.RANGETIME = t2.RANGETIME
                        AND t1.ORDNUM    = t2.ORDNUM
                        LEFT JOIN ADSDefectManager adm WITH (NOLOCK)
                        ON t2.CODEDEFECT = adm.Code

                        SELECT  
                            d.LINEST,
                            d.STYLE_NO,
                            d.OPERATION,
                            d.DEFECT,
                            d.DefectEN,
                            d.DefectVN,
                            d.QTY,
                            d.CTQ,
                            d.CTP,
                            emp.fullname AS EMPLOYEE,
                            qc.fullname  AS NAMEQC

                        INTO #t4
                        FROM #t3 AS d
                        LEFT JOIN [HR].[dbo].[staff] AS emp 
                            ON emp.id_staff COLLATE SQL_Latin1_General_CP1_CI_AS
                            = d.EMPLOYEE COLLATE SQL_Latin1_General_CP1_CI_AS

                        LEFT JOIN [HR].[dbo].[staff] AS qc 
                            ON qc.id_staff COLLATE SQL_Latin1_General_CP1_CI_AS
                            = d.NAMEQC COLLATE SQL_Latin1_General_CP1_CI_AS

                        select 
                        d.LINEST,
                        d.STYLE_NO,
                        d.OPERATION,
                        CASE 
                            WHEN d.CTQ = 1 AND d.CTP = 1 THEN 'CTQ, CTP'
                            WHEN d.CTQ = 1 THEN 'CTQ'
                            WHEN d.CTP = 1 THEN 'CTP'
                        END AS TYPE,
                        SUM(d.DEFECT) as DEFECT,
                        d.DefectEN,
                        d.DefectVN,
                        t.TOTAL_QTY AS TOTAL_QTY,
                        CAST(
                            SUM(d.DEFECT) * 100.0 / NULLIF(t.TOTAL_QTY, 0)
                            AS DECIMAL(10,2)
                        ) AS DEFECT_RATE,
                        d.EMPLOYEE,
                        d.NAMEQC
                        FROM #t4 as d
                        LEFT JOIN (
                            SELECT
                            LINEST,
                            STYLE_NO,
                            OPERATION,
                            SUM(QTY) AS TOTAL_QTY
                            FROM #t4

                            GROUP BY
                            LINEST,
                            STYLE_NO,
                            OPERATION
                        ) AS t
                        ON  t.LINEST    = d.LINEST
                        AND t.STYLE_NO  = d.STYLE_NO
                        AND t.OPERATION = d.OPERATION
                        WHERE (d.CTQ = 1 OR d.CTP =1 ) AND d.DEFECT >= 1
                        GROUP BY
                        d.LINEST,
                        d.STYLE_NO,
                        d.OPERATION,
                        CASE 
                            WHEN d.CTQ = 1 AND d.CTP = 1 THEN 'CTQ, CTP'
                            WHEN d.CTQ = 1 THEN 'CTQ'
                            WHEN d.CTP = 1 THEN 'CTP'
                        END,
                        d.DefectEN,
                        d.DefectVN,
                        t.TOTAL_QTY,
                        d.EMPLOYEE,
                        d.NAMEQC ;
                        """
                        params=(fac_prefix, date_from, date_to)
                    else:
                        if not line:
                            return []
                        placeholders = ",".join("?" for _ in line)
                        sql= f"""
                        SET NOCOUNT ON;

                        IF OBJECT_ID('tempdb..#t1') IS NOT NULL DROP TABLE #t1;
                        IF OBJECT_ID('tempdb..#t2') IS NOT NULL DROP TABLE #t2;
                        IF OBJECT_ID('tempdb..#t3') IS NOT NULL DROP TABLE #t3;
                        IF OBJECT_ID('tempdb..#t4') IS NOT NULL DROP TABLE #t4;
                        SELECT *
                        INTO #t1
                        FROM InlineQcLayout WITH (NOLOCK)
                        WHERE LINEST IN ({placeholders})
                        AND DATEST BETWEEN ? AND ?;
                        
                        CREATE CLUSTERED INDEX IX1 ON #t1 (BARCODE, RANGETIME, ORDNUM);

                        -- STEP 2
                        SELECT
                            a.BARCODE,
                            a.RANGETIME,
                            a.ORDNUM,
                            a.CODEDEFECT,
                            a.DEFECT,
                            b.DFNAMEVN,
                            b.DFNAMEEN
                        INTO #t2
                        FROM SubInlineQc a WITH (NOLOCK)
                        LEFT JOIN InlineQcDefectCodeName b WITH (NOLOCK)
                            ON a.CODEDEFECT = b.DFCODEIN
                        WHERE a.BARCODE IN (SELECT BARCODE FROM #t1 WHERE BARCODE <> '');

                        CREATE CLUSTERED INDEX IX2 ON #t2 (BARCODE, RANGETIME, ORDNUM);

                        -- FINAL
                        SELECT DISTINCT
                        t1.*,
                        CAST(ISNULL(m.RFT,0) AS BIT) AS CRI,
                        CAST(ISNULL(m.CTQ,0) AS BIT) AS CTQ,
                        CAST(ISNULL(m.CTP,0) AS BIT) AS CTP,
                        t2.CODEDEFECT,
                        t2.DEFECT,
                        t2.DFNAMEVN,
                        t2.DFNAMEEN,
                        adm.Code,
                        adm.DefectEN,
                        adm.DefectVN
                        INTO #t3
                        FROM #t1 t1
                        LEFT JOIN MasterLayout m
                        ON t1.LINEST   = m.LINEST
                        AND t1.STYLE_NO = m.STYLE_NO
                        AND t1.CODEOPT  = m.CODEOPT
                        LEFT JOIN #t2 t2
                        ON t1.BARCODE   = t2.BARCODE
                        AND t1.RANGETIME = t2.RANGETIME
                        AND t1.ORDNUM    = t2.ORDNUM
                        LEFT JOIN ADSDefectManager adm WITH (NOLOCK)
                        ON t2.CODEDEFECT = adm.Code

                        SELECT  
                            d.LINEST,
                            d.STYLE_NO,
                            d.OPERATION,
                            d.DEFECT,
                            d.DefectEN,
                            d.DefectVN,
                            d.QTY,
                            d.CTQ,
                            d.CTP,
                            emp.fullname AS EMPLOYEE,
                            qc.fullname  AS NAMEQC

                        INTO #t4
                        FROM #t3 AS d
                        LEFT JOIN [HR].[dbo].[staff] AS emp 
                            ON emp.id_staff COLLATE SQL_Latin1_General_CP1_CI_AS
                            = d.EMPLOYEE COLLATE SQL_Latin1_General_CP1_CI_AS

                        LEFT JOIN [HR].[dbo].[staff] AS qc 
                            ON qc.id_staff COLLATE SQL_Latin1_General_CP1_CI_AS
                            = d.NAMEQC COLLATE SQL_Latin1_General_CP1_CI_AS

                        select 
                        d.LINEST,
                        d.STYLE_NO,
                        d.OPERATION,
                        CASE 
                            WHEN d.CTQ = 1 AND d.CTP = 1 THEN 'CTQ, CTP'
                            WHEN d.CTQ = 1 THEN 'CTQ'
                            WHEN d.CTP = 1 THEN 'CTP'
                        END AS TYPE,
                        SUM(d.DEFECT) as DEFECT,
                        d.DefectEN,
                        d.DefectVN,
                        t.TOTAL_QTY AS TOTAL_QTY,
                        CAST(
                            SUM(d.DEFECT) * 100.0 / NULLIF(t.TOTAL_QTY, 0)
                            AS DECIMAL(10,2)
                        ) AS DEFECT_RATE,
                        d.EMPLOYEE,
                        d.NAMEQC
                        FROM #t4 as d
                        LEFT JOIN (
                            SELECT
                            LINEST,
                            STYLE_NO,
                            OPERATION,
                            SUM(QTY) AS TOTAL_QTY
                            FROM #t4

                            GROUP BY
                            LINEST,
                            STYLE_NO,
                            OPERATION
                        ) AS t
                        ON  t.LINEST    = d.LINEST
                        AND t.STYLE_NO  = d.STYLE_NO
                        AND t.OPERATION = d.OPERATION
                        WHERE (d.CTQ = 1 OR d.CTP =1 ) AND d.DEFECT >= 1
                        GROUP BY
                        d.LINEST,
                        d.STYLE_NO,
                        d.OPERATION,
                        CASE 
                            WHEN d.CTQ = 1 AND d.CTP = 1 THEN 'CTQ, CTP'
                            WHEN d.CTQ = 1 THEN 'CTQ'
                            WHEN d.CTP = 1 THEN 'CTP'
                        END,
                        d.DefectEN,
                        d.DefectVN,
                        t.TOTAL_QTY,
                        d.EMPLOYEE,
                        d.NAMEQC ;
                        """
                        params = (*line, date_from, date_to)

                    cursor.execute(sql, params)

                    rows = cursor.fetchall()
                    columns = [c[0] for c in cursor.description]

                    return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            settings.MESSAGE = f"Internal Server Error: {str(e)}"
            return []

    def getCTQDashboardEndline(self, fac_prefix: str, line: List[str], date_from: str, date_to: str):
        settings.MESSAGE = ''
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:
                    is_all = len(line) == 1 and line[0] == "All"
                    if is_all:
                        sql = """
                            SET NOCOUNT ON;
                            SELECT 
                                a.FacLine,
                                a.JobNo,
                                a.Color,
                                a.PONO,
                                a.RWCard,
                                b.DefectCode,
                                CASE 
                                    WHEN c.ZoneA = 1 THEN 'CD' 
                                    ELSE '' 
                                END AS CriticalDefect,
                                c.DefectEN,
                                c.DefectVN,
                                b.Operation,
                                a.ReleaseDate,
                                a.ReturnDate,
                                a.SysCreateDate
                            INTO #TLSReport
                            FROM EndlineQCRWCard a WITH (NOLOCK)
                            JOIN EndlineQCRWCardDefect b WITH (NOLOCK)
                                ON a.RejectCode = b.RejectCode
                            JOIN ADSDefectManager c WITH (NOLOCK)
                                ON b.DefectCode = c.Code
                            WHERE a.Factory = RIGHT( ? , 2)
                            AND CONVERT(nvarchar(8), a.SysCreateDate, 112) BETWEEN ? AND ?;
                            
                                SELECT
                                    t.FacLine,
                                    t.JobNo,
                                    t.Color,
                                    t.PONO,
                                    t.RWCard,
                                    t.DefectCode,
                                    t.CriticalDefect,
                                    t.DefectEN,
                                    t.DefectVN,
                                    t.Operation,
                                    g.Style,          -- Style từ Garment
                                    g.InsQty,
                                    g.RejQty,
                                    t.SysCreateDate
                                INTO #Merge1
                                FROM #TLSReport t
                                JOIN EndlineQcReportGmtPass g WITH (NOLOCK)
                                    ON t.JobNo = g.Size
                                AND t.PONO  = g.PONO
                                AND CAST(t.ReleaseDate AS DATE) = CAST(g.Date AS DATE)
                                WHERE RIGHT(g.Factory,2) = RIGHT(?,2)
                                AND g.Date BETWEEN ? AND ?;

                            SELECT distinct
                                m1.*, 
                                ml.CTQ,
                                1 AS DEFECT    
                            INTO #Merge2
                            FROM #Merge1 m1
                            LEFT JOIN DtradeProduction.dbo.MasterLayout ml WITH (NOLOCK)
                                ON m1.Style     = ml.STYLE_NO
                            AND m1.Operation = ml.OPERATION
                            AND m1.FacLine   = ml.LINEST;

                            SELECT 
                            m2.FacLine as LINEST,
                            m2.Style as STYLE_NO,
                            m2.Operation as OPERATION, 
                            COUNT(m2.DEFECT) as DEFECT,
                            m2.DefectVN as DefectVN, 
                            m2.DefectEN as DefectEN, 
                            m3.TOTAL_QTY,
                            CAST(
                            COUNT(m2.DEFECT) * 100.0 / NULLIF(SUM(m3.TOTAL_QTY), 0)
                            AS DECIMAL(10,2)
                            ) AS DEFECT_RATE
                            FROM #Merge2 m2
                            LEFT JOIN (
                                SELECT FacLine, Style, Operation, SUM(InsQty) as TOTAL_QTY, COUNT(DefectCode) as DEFECT FROM #Merge2
                                GROUP BY FacLine, Style, Operation
                            ) m3 ON m3.FacLine=m2.FacLine AND m3.Style=m2.Style AND m3.Operation= m2.Operation

                            WHERE m2.CTQ = 1 
                            Group by 
                            m2.FacLine, m2.Style, m2.Operation, m2.DefectVN ,m2.DefectEN, m3.TOTAL_QTY
                            Order by m2.FacLine, m2.Style, m2.Operation

                            DROP TABLE #Merge2;
                            DROP TABLE #Merge1;
                            DROP TABLE #TLSReport;

                        """
                        params = (fac_prefix, date_from, date_to, fac_prefix, date_from, date_to)
                    else:
                        if not line:
                            return []
                        placeholders = ",".join("?" for _ in line)
                        sql = f"""
                            SET NOCOUNT ON;
                            SELECT 
                                a.FacLine,
                                a.JobNo,
                                a.Color,
                                a.PONO,
                                a.RWCard,
                                b.DefectCode,
                                CASE 
                                    WHEN c.ZoneA = 1 THEN 'CD' 
                                    ELSE '' 
                                END AS CriticalDefect,
                                c.DefectEN,
                                c.DefectVN,
                                b.Operation,
                                a.ReleaseDate,
                                a.ReturnDate,
                                a.SysCreateDate
                            INTO #TLSReport
                            FROM EndlineQCRWCard a WITH (NOLOCK)
                            JOIN EndlineQCRWCardDefect b WITH (NOLOCK)
                                ON a.RejectCode = b.RejectCode
                            JOIN ADSDefectManager c WITH (NOLOCK)
                                ON b.DefectCode = c.Code
                            WHERE a.Factory = RIGHT( ? , 2)
                            AND CONVERT(nvarchar(8), a.SysCreateDate, 112) BETWEEN ? AND ?;
                            
                                SELECT
                                    t.FacLine,
                                    t.JobNo,
                                    t.Color,
                                    t.PONO,
                                    t.RWCard,
                                    t.DefectCode,
                                    t.CriticalDefect,
                                    t.DefectEN,
                                    t.DefectVN,
                                    t.Operation,
                                    g.Style,          -- Style từ Garment
                                    g.InsQty,
                                    g.RejQty,
                                    t.SysCreateDate
                                INTO #Merge1
                                FROM #TLSReport t
                                JOIN EndlineQcReportGmtPass g WITH (NOLOCK)
                                    ON t.JobNo = g.Size
                                AND t.PONO  = g.PONO
                                AND CAST(t.ReleaseDate AS DATE) = CAST(g.Date AS DATE)
                                WHERE RIGHT(g.Factory,2) = RIGHT(?,2)
                                AND g.Date BETWEEN ? AND ?;

                            SELECT distinct
                                m1.*, 
                                ml.CTQ,
                                1 AS DEFECT    
                            INTO #Merge2
                            FROM #Merge1 m1
                            LEFT JOIN DtradeProduction.dbo.MasterLayout ml WITH (NOLOCK)
                                ON m1.Style     = ml.STYLE_NO
                            AND m1.Operation = ml.OPERATION
                            AND m1.FacLine   = ml.LINEST;

                            SELECT 
                            m2.FacLine as LINEST,
                            m2.Style as STYLE_NO,
                            m2.Operation as OPERATION, 
                            COUNT(m2.DEFECT) as DEFECT,
                            m2.DefectVN as DefectVN, 
                            m2.DefectEN as DefectEN, 
                            m3.TOTAL_QTY,
                            CAST(
                            COUNT(m2.DEFECT) * 100.0 / NULLIF(SUM(m3.TOTAL_QTY), 0)
                            AS DECIMAL(10,2)
                            ) AS DEFECT_RATE
                            FROM #Merge2 m2
                            LEFT JOIN (
                                SELECT FacLine, Style, Operation, SUM(InsQty) as TOTAL_QTY, COUNT(DefectCode) as DEFECT FROM #Merge2
                                GROUP BY FacLine, Style, Operation
                            ) m3 ON m3.FacLine=m2.FacLine AND m3.Style=m2.Style AND m3.Operation= m2.Operation

                            WHERE m2.CTQ = 1 AND m2.FacLine IN ({placeholders})
                            Group by 
                            m2.FacLine, m2.Style, m2.Operation, m2.DefectVN ,m2.DefectEN, m3.TOTAL_QTY
                            Order by m2.FacLine, m2.Style, m2.Operation

                            DROP TABLE #Merge2;
                            DROP TABLE #Merge1;
                            DROP TABLE #TLSReport;

                            """
                        params = (fac_prefix, date_from, date_to, fac_prefix, date_from, date_to, *line)

                    cursor.execute(sql, params)

                    rows = cursor.fetchall()
                    columns = [c[0] for c in cursor.description]

                    return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            settings.MESSAGE = f"Internal Server Error: {str(e)}"
            return []


    def getTLS_report(self, fac_prefix: str, date_from: str, date_to: str):
        settings.MESSAGE = ''
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:

                    sql = """
                        SELECT 
                            a.FacLine,
                            a.JobNo,
                            a.Color,
                            a.PONO,
                            a.RWCard,
                            b.DefectCode,
                            CASE 
                                WHEN c.ZoneA = 1 THEN 'CD' 
                                ELSE '' 
                            END AS CriticalDefect,
                            c.DefectEN,
                            c.DefectVN,
                            b.Operation,
                            a.ReleaseDate,
                            a.ReturnDate,
                            a.SysCreateDate
                        FROM EndlineQCRWCard a WITH (NOLOCK)
                        JOIN EndlineQCRWCardDefect b WITH (NOLOCK)
                            ON a.RejectCode = b.RejectCode
                        JOIN ADSDefectManager c WITH (NOLOCK)
                            ON b.DefectCode = c.Code
                        WHERE a.Factory = RIGHT(?, 2)          -- F2
                        AND CONVERT(nvarchar(8), a.SysCreateDate, 112) BETWEEN ? AND ?;
                    """

                    cursor.execute(sql, (fac_prefix, date_from, date_to))

                    rows = cursor.fetchall()
                    columns = [c[0] for c in cursor.description]

                    return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            settings.MESSAGE = f"Internal Server Error: {str(e)}"
            return []


    def getGarment(self, fac_prefix: str, date_from: str, date_to: str):
        settings.MESSAGE = ''
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:

                    sql = """
                          SELECT * from EndlineQcReportGmtPass WITH(NOLOCK) where Factory = ? and Date between ? and ?
                    """

                    cursor.execute(sql, (fac_prefix, date_from, date_to))

                    rows = cursor.fetchall()
                    columns = [c[0] for c in cursor.description]

                    return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            settings.MESSAGE = f"Internal Server Error: {str(e)}"
            return []

    def getMerge1(self, fac_prefix: str, date_from: str, date_to: str):
        settings.MESSAGE = ''
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:

                    sql = """
                    WITH TLSReport AS (
                        SELECT 
                            a.FacLine,
                            a.JobNo,
                            a.Color,
                            a.PONO,
                            a.RWCard,
                            b.DefectCode,
                            CASE WHEN c.ZoneA = 1 THEN 'CD' ELSE '' END AS CriticalDefect,
                            c.DefectEN,
                            c.DefectVN,
                            b.Operation,
                            a.ReleaseDate,
                            a.ReturnDate,
                            a.SysCreateDate
                        FROM EndlineQCRWCard a WITH (NOLOCK)
                        JOIN EndlineQCRWCardDefect b WITH (NOLOCK)
                            ON a.RejectCode = b.RejectCode
                        JOIN ADSDefectManager c WITH (NOLOCK)
                            ON b.DefectCode = c.Code
                        WHERE a.Factory = RIGHT(?, 2)
                        AND CONVERT(char(8), a.SysCreateDate, 112)
                            BETWEEN ? AND ?
                    )
                    SELECT
                        t.FacLine,
                        t.JobNo,
                        t.Color,
                        t.PONO,
                        t.RWCard,
                        t.DefectCode,
                        t.CriticalDefect,
                        t.DefectEN,
                        t.DefectVN,
                        t.Operation,
                        g.Style,
                        g.InsQty,
		                g.RejQty,
                        t.SysCreateDate
                    FROM TLSReport t
                    JOIN EndlineQcReportGmtPass g WITH (NOLOCK)
                        ON t.JobNo = g.Size
                    AND t.PONO  = g.PONO
                    AND CAST(t.ReleaseDate AS DATE) = CAST(g.Date AS DATE)
                    WHERE g.Factory = ?
                    AND g.Date BETWEEN ? AND ?
                    """

                    params = (
                        fac_prefix,
                        date_from,
                        date_to,
                        fac_prefix,
                        date_from,
                        date_to
                    )

                    cursor.execute(sql, params)

                    rows = cursor.fetchall()
                    columns = [c[0] for c in cursor.description]

                    return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            settings.MESSAGE = f"Internal Server Error: {str(e)}"
            return []

    def getMerge2(self, fac_prefix: str, date_from: str, date_to: str):
        settings.MESSAGE = ''
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:

                    sql = """
                    WITH TLSReport AS (
                        SELECT 
                            a.FacLine,
                            a.JobNo,
                            a.Color,
                            a.PONO,
                            a.RWCard,
                            b.DefectCode,
                            CASE WHEN c.ZoneA = 1 THEN 'CD' ELSE '' END AS CriticalDefect,
                            c.DefectEN,
                            c.DefectVN,
                            b.Operation,
                            a.ReleaseDate,
                            a.ReturnDate,
                            a.SysCreateDate
                        FROM EndlineQCRWCard a WITH (NOLOCK)
                        JOIN EndlineQCRWCardDefect b WITH (NOLOCK)
                            ON a.RejectCode = b.RejectCode
                        JOIN ADSDefectManager c WITH (NOLOCK)
                            ON b.DefectCode = c.Code
                        WHERE a.Factory = RIGHT(?, 2)
                        AND CONVERT(char(8), a.SysCreateDate, 112)
                            BETWEEN ? AND ?
                    ),
                    Merge1 AS (
                        SELECT
                            t.FacLine,
                            t.JobNo,
                            t.Color,
                            t.PONO,
                            t.RWCard,
                            t.DefectCode,
                            t.CriticalDefect,
                            t.DefectEN,
                            t.DefectVN,
                            t.Operation,
                            g.Style,
                            g.InsQty,
		                    g.RejQty,
                            t.SysCreateDate
                        FROM TLSReport t
                        JOIN EndlineQcReportGmtPass g WITH (NOLOCK)
                            ON t.JobNo = g.Size       -- ✅ FIX
                        AND t.PONO  = g.PONO
                        AND CAST(t.ReleaseDate AS DATE) = CAST(g.Date AS DATE)
                        WHERE g.Factory = ?
                        AND g.Date BETWEEN ? AND ?
                    )
                    SELECT Distinct
                        m1.*, 
                        ml.CTQ   
                    FROM Merge1 m1
                    LEFT JOIN DtradeProduction.dbo.MasterLayout ml WITH (NOLOCK)
                        ON m1.Style     = ml.STYLE_NO
                    AND m1.Operation = ml.OPERATION
                    AND m1.FacLine   = ml.LINEST
                    ORDER BY
                        m1.JobNo,
                        m1.Operation,
                        m1.SysCreateDate;
                    """

                    params = (
                        fac_prefix,
                        date_from,
                        date_to,
                        fac_prefix,
                        date_from,
                        date_to
                    )

                    cursor.execute(sql, params)

                    rows = cursor.fetchall()
                    columns = [c[0] for c in cursor.description]

                    return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            settings.MESSAGE = f"Internal Server Error: {str(e)}"
            return []


    def getMasterLayout(self, style: str|None=None): 
        settings.MESSAGE = ''
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:

                    sql = """
                        SELECT * FROM [DtradeProduction].[dbo].[MasterLayout] where STYLE_NO = ?
                    """

                    params = (
                        style,
                    )

                    cursor.execute(sql, params)

                    rows = cursor.fetchall()
                    columns = [c[0] for c in cursor.description]

                    return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            settings.MESSAGE = f"Internal Server Error: {str(e)}"
            return []
            
    def getResultInline(self, fac_prefix: str, date_from: str, date_to: str):
        settings.MESSAGE = ''
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:

                    sql = """
                        SET NOCOUNT ON;
                        -- CLEAN UP
                        IF OBJECT_ID('tempdb..#t2') IS NOT NULL DROP TABLE #t2;
                        IF OBJECT_ID('tempdb..#t1') IS NOT NULL DROP TABLE #t1;
                        IF OBJECT_ID('tempdb..#t3') IS NOT NULL DROP TABLE #t3;
                        IF OBJECT_ID('tempdb..#t4') IS NOT NULL DROP TABLE #t4;
                        -- STEP 1
                        SELECT *
                        INTO #t1
                        FROM InlineQcLayout WITH (NOLOCK)
                        WHERE LEFT(LINEST,2) = RIGHT(?,2)
                        AND DATEST BETWEEN ? AND ?;

                        CREATE CLUSTERED INDEX IX1 ON #t1 (BARCODE, RANGETIME, ORDNUM);

                        -- STEP 2
                        SELECT
                            a.BARCODE,
                            a.RANGETIME,
                            a.ORDNUM,
                            a.CODEDEFECT,
                            a.DEFECT,
                            b.DFNAMEVN,
                            b.DFNAMEEN
                        INTO #t2
                        FROM SubInlineQc a WITH (NOLOCK)
                        LEFT JOIN InlineQcDefectCodeName b WITH (NOLOCK)
                            ON a.CODEDEFECT = b.DFCODEIN
                        WHERE a.BARCODE IN (SELECT BARCODE FROM #t1 WHERE BARCODE <> '');

                        CREATE CLUSTERED INDEX IX2 ON #t2 (BARCODE, RANGETIME, ORDNUM);

                        -- FINAL
                        SELECT DISTINCT
                            t1.*,
                            CAST(ISNULL(m.RFT,0) AS BIT) AS CRI,
                            CAST(ISNULL(m.CTQ,0) AS BIT) AS CTQ,
                            t2.CODEDEFECT,
                            t2.DEFECT,
                            t2.DFNAMEVN,
                            t2.DFNAMEEN,
                            adm.Code,
                            adm.DefectEN,
                            adm.DefectVN
                        INTO #t3
                        FROM #t1 t1
                        LEFT JOIN MasterLayout m
                            ON t1.LINEST   = m.LINEST
                        AND t1.STYLE_NO = m.STYLE_NO
                        AND t1.CODEOPT  = m.CODEOPT
                        LEFT JOIN #t2 t2
                            ON t1.BARCODE   = t2.BARCODE
                        AND t1.RANGETIME = t2.RANGETIME
                        AND t1.ORDNUM    = t2.ORDNUM
                        LEFT JOIN ADSDefectManager adm WITH (NOLOCK)
                            ON t2.CODEDEFECT = adm.Code
                        -- END
                        SELECT
                            LINEST,
                            STYLE_NO,
                            OPERATION,
                            DEFECT,
                            DefectEN,
                            DefectVN,
                            SUM(QTY) AS QTY,
                            CTQ
                        INTO #t4
                        FROM #t3
                        GROUP BY
                            LINEST,
                            STYLE_NO,
                            OPERATION,
                            DEFECT,
                            DefectEN,
                            DefectVN,
                            CTQ


                        SELECT
                            d.LINEST,
                            d.STYLE_NO,
                            d.OPERATION,
                            d.DEFECT,
                            d.DefectEN,
                            d.DefectVN,
                            t.TOTAL_DEFECT,
                            t.TOTAL_QTY       AS TOTAL_QTY,
                            CAST(
                                SUM(t.TOTAL_DEFECT) * 100.0 / NULLIF(t.TOTAL_QTY, 0)
                                AS DECIMAL(10,2)
                            )                 AS DEFECT_RATE
                        FROM #t4 AS d
                        INNER JOIN (
                            SELECT
                                LINEST,
                                STYLE_NO,
                                OPERATION,
                                SUM(DEFECT) AS TOTAL_DEFECT,
                                SUM(QTY) AS TOTAL_QTY
                            FROM #t4
                            WHERE CTQ = 1
                            GROUP BY
                                LINEST,
                                STYLE_NO,
                                OPERATION
                        ) AS t
                            ON  t.LINEST    = d.LINEST
                            AND t.STYLE_NO  = d.STYLE_NO
                            AND t.OPERATION = d.OPERATION
                        WHERE
                            d.CTQ = 1
                            AND d.DEFECT >= 1
                        GROUP BY
                            d.LINEST,
                            d.STYLE_NO,
                            d.OPERATION,
                            d.DEFECT,
                            d.DefectEN,
                            d.DefectVN,
                            t.TOTAL_DEFECT,
                            t.TOTAL_QTY
                        ORDER BY
                            d.LINEST,
                            d.STYLE_NO,
                            d.OPERATION;

                    """

                    params = (
                        fac_prefix, date_from, date_to
                    )

                    cursor.execute(sql, params)

                    rows = cursor.fetchall()
                    columns = [c[0] for c in cursor.description]

                    return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            settings.MESSAGE = f"Internal Server Error: {str(e)}"
            return []


    def getResultInlineCTP(self, fac_prefix: str, date_from: str, date_to: str):
        settings.MESSAGE = ''
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:

                    sql = """
                        SET NOCOUNT ON;
                        IF OBJECT_ID('tempdb..#t1') IS NOT NULL DROP TABLE #t1;
                        IF OBJECT_ID('tempdb..#t2') IS NOT NULL DROP TABLE #t2;
                        SELECT *
                        INTO #t1
                        FROM InlineQcLayout WITH (NOLOCK)
                        WHERE LEFT(LINEST,2) = RIGHT(?,2)
                        AND DATEST BETWEEN ? AND ?;

                        CREATE CLUSTERED INDEX IX1 ON #t1 (BARCODE, RANGETIME, ORDNUM);

                        -- STEP 2
                        SELECT
                            a.BARCODE,
                            a.RANGETIME,
                            a.ORDNUM,
                            a.CODEDEFECT,
                            a.DEFECT,
                            b.DFNAMEVN,
                            b.DFNAMEEN
                        INTO #t2
                        FROM SubInlineQc a WITH (NOLOCK)
                        LEFT JOIN InlineQcDefectCodeName b WITH (NOLOCK)
                            ON a.CODEDEFECT = b.DFCODEIN
                        WHERE a.BARCODE IN (SELECT BARCODE FROM #t1 WHERE BARCODE <> '');

                        CREATE CLUSTERED INDEX IX2 ON #t2 (BARCODE, RANGETIME, ORDNUM);

                        -- FINAL
                        SELECT DISTINCT
                            t1.*,
                            CAST(ISNULL(m.RFT,0) AS BIT) AS CRI,
                            CAST(ISNULL(m.CTQ,0) AS BIT) AS CTQ,
                            CAST(ISNULL(m.CTP,0) AS BIT) AS CTP,
                            t2.CODEDEFECT,
                            t2.DEFECT,
                            t2.DFNAMEVN,
                            t2.DFNAMEEN,
                            adm.Code,
                            adm.DefectEN,
                            adm.DefectVN

                        FROM #t1 t1
                        LEFT JOIN MasterLayout m
                            ON t1.LINEST   = m.LINEST
                        AND t1.STYLE_NO = m.STYLE_NO
                        AND t1.CODEOPT  = m.CODEOPT
                        LEFT JOIN #t2 t2
                            ON t1.BARCODE   = t2.BARCODE
                        AND t1.RANGETIME = t2.RANGETIME
                        AND t1.ORDNUM    = t2.ORDNUM
                        LEFT JOIN ADSDefectManager adm WITH (NOLOCK)
                            ON t2.CODEDEFECT = adm.Code

                        DROP TABLE #t2;
                        DROP TABLE #t1;

                    """

                    params = (
                        fac_prefix, date_from, date_to
                    )

                    cursor.execute(sql, params)

                    rows = cursor.fetchall()
                    columns = [c[0] for c in cursor.description]

                    return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            settings.MESSAGE = f"Internal Server Error: {str(e)}"
            return []
            
            
    def getTest(self, fac_prefix: str, date_from: str, date_to: str):
        settings.MESSAGE = ''
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:

                    sql = """
                        SET NOCOUNT ON;

                        IF OBJECT_ID('tempdb..#t1') IS NOT NULL DROP TABLE #t1;
                        IF OBJECT_ID('tempdb..#t2') IS NOT NULL DROP TABLE #t2;
                        IF OBJECT_ID('tempdb..#t3') IS NOT NULL DROP TABLE #t3;
                        IF OBJECT_ID('tempdb..#t4') IS NOT NULL DROP TABLE #t4;
                        SELECT *
                        INTO #t1
                        FROM InlineQcLayout WITH (NOLOCK)
                        WHERE LEFT(LINEST,2) = RIGHT(?,2)
                        AND DATEST BETWEEN ? AND ?;

                        CREATE CLUSTERED INDEX IX1 ON #t1 (BARCODE, RANGETIME, ORDNUM);

                        -- STEP 2
                        SELECT
                        a.BARCODE,
                        a.RANGETIME,
                        a.ORDNUM,
                        a.CODEDEFECT,
                        a.DEFECT,
                        b.DFNAMEVN,
                        b.DFNAMEEN
                        INTO #t2
                        FROM SubInlineQc a WITH (NOLOCK)
                        LEFT JOIN InlineQcDefectCodeName b WITH (NOLOCK)
                        ON a.CODEDEFECT = b.DFCODEIN
                        WHERE a.BARCODE IN (SELECT BARCODE FROM #t1 WHERE BARCODE <> '');

                        CREATE CLUSTERED INDEX IX2 ON #t2 (BARCODE, RANGETIME, ORDNUM);

                        -- FINAL
                        SELECT DISTINCT
                        t1.*,
                        CAST(ISNULL(m.RFT,0) AS BIT) AS CRI,
                        CAST(ISNULL(m.CTQ,0) AS BIT) AS CTQ,
                        CAST(ISNULL(m.CTP,0) AS BIT) AS CTP,
                        t2.CODEDEFECT,
                        t2.DEFECT,
                        t2.DFNAMEVN,
                        t2.DFNAMEEN,
                        adm.Code,
                        adm.DefectEN,
                        adm.DefectVN
                        INTO #t3
                        FROM #t1 t1
                        LEFT JOIN MasterLayout m
                        ON t1.LINEST   = m.LINEST
                        AND t1.STYLE_NO = m.STYLE_NO
                        AND t1.CODEOPT  = m.CODEOPT
                        LEFT JOIN #t2 t2
                        ON t1.BARCODE   = t2.BARCODE
                        AND t1.RANGETIME = t2.RANGETIME
                        AND t1.ORDNUM    = t2.ORDNUM
                        LEFT JOIN ADSDefectManager adm WITH (NOLOCK)
                        ON t2.CODEDEFECT = adm.Code

                        SELECT  
                            d.LINEST,
                            d.STYLE_NO,
                            d.OPERATION,
                            d.DEFECT,
                            d.DefectEN,
                            d.DefectVN,
                            d.QTY,
                            d.CTQ,
                            d.CTP,
                            emp.fullname AS EMPLOYEE,
                            qc.fullname  AS NAMEQC

                        INTO #t4
                        FROM #t3 AS d
                        LEFT JOIN [HR].[dbo].[staff] AS emp 
                            ON emp.id_staff COLLATE SQL_Latin1_General_CP1_CI_AS
                            = d.EMPLOYEE COLLATE SQL_Latin1_General_CP1_CI_AS

                        LEFT JOIN [HR].[dbo].[staff] AS qc 
                            ON qc.id_staff COLLATE SQL_Latin1_General_CP1_CI_AS
                            = d.NAMEQC COLLATE SQL_Latin1_General_CP1_CI_AS

                        select 
                        d.LINEST,
                        d.STYLE_NO,
                        d.OPERATION,
                        CASE 
                            WHEN d.CTQ = 1 AND d.CTP = 1 THEN 'CTQ, CTP'
                            WHEN d.CTQ = 1 THEN 'CTQ'
                            WHEN d.CTP = 1 THEN 'CTP'
                        END AS TYPE,
                        SUM(d.DEFECT) as DEFECT,
                        d.DefectEN,
                        d.DefectVN,
                        t.TOTAL_QTY AS TOTAL_QTY,
                        CAST(
                            SUM(d.DEFECT) * 100.0 / NULLIF(t.TOTAL_QTY, 0)
                            AS DECIMAL(10,2)
                        ) AS DEFECT_RATE,
                        d.EMPLOYEE,
                        d.NAMEQC
                        FROM #t4 as d
                        LEFT JOIN (
                            SELECT
                            LINEST,
                            STYLE_NO,
                            OPERATION,
                            SUM(QTY) AS TOTAL_QTY
                            FROM #t4

                            GROUP BY
                            LINEST,
                            STYLE_NO,
                            OPERATION
                        ) AS t
                        ON  t.LINEST    = d.LINEST
                        AND t.STYLE_NO  = d.STYLE_NO
                        AND t.OPERATION = d.OPERATION
                        WHERE (d.CTQ = 1 OR d.CTP =1 ) AND d.DEFECT >= 1
                        GROUP BY
                        d.LINEST,
                        d.STYLE_NO,
                        d.OPERATION,
                        CASE 
                            WHEN d.CTQ = 1 AND d.CTP = 1 THEN 'CTQ, CTP'
                            WHEN d.CTQ = 1 THEN 'CTQ'
                            WHEN d.CTP = 1 THEN 'CTP'
                        END,
                        d.DefectEN,
                        d.DefectVN,
                        t.TOTAL_QTY,
                        d.EMPLOYEE,
                        d.NAMEQC ;

                    """

                    params = (
                        fac_prefix, date_from, date_to
                    )

                    cursor.execute(sql, params)

                    rows = cursor.fetchall()
                    columns = [c[0] for c in cursor.description]

                    return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            settings.MESSAGE = f"Internal Server Error: {str(e)}"
            return []
            
    def getAllFactory(self):
        settings.MESSAGE = ''
        try:
            with self.connect() as conn:
                with conn.cursor() as cursor:

                    sql = """
                        select [FaclineId], [Facline], [Factory], [FactoryName] FROM [DtradeProduction].[dbo].[Facline]
                    """
                    cursor.execute(sql)

                    rows = cursor.fetchall()
                    columns = [c[0] for c in cursor.description]

                    return [dict(zip(columns, row)) for row in rows]

        except Exception as e:
            settings.MESSAGE = f"Internal Server Error: {str(e)}"
            return []