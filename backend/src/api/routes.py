from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from ..services.scraping_service import WebScraperService
from ..services.analysis_service import AnalysisService
from ..services.report_service import PDFReportService
from ..models.data_models import URLAnalysisRequest, AnalysisReport, ProcessedContent
import io

router = APIRouter()

def get_scraper_service():
    return WebScraperService()

def get_analysis_service():
    return AnalysisService()

@router.post("/analyze", response_model=AnalysisReport)
async def analyze_url(
    request: URLAnalysisRequest,
    scraper: WebScraperService = Depends(get_scraper_service),
    analyzer: AnalysisService = Depends(get_analysis_service)
):
    try:
        # --- THE FIX IS HERE: add 'await' ---
        processed_data = await scraper.scrape_url(str(request.url))

        # Assemble the ProcessedContent model from the scraped data
        content_analysis = ProcessedContent.parse_obj(processed_data)

        # Send the main text to the AI for summary and analysis
        ai_summary = analyzer.analyze_content(content_analysis.main_content_text)

        # Assemble the final, comprehensive report
        final_report = AnalysisReport(
            url=request.url,
            content_analysis=content_analysis,
            ai_summary=ai_summary
        )
        return final_report

    except (ValueError, ConnectionError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Catch other exceptions and provide a detailed error
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred in the analysis pipeline: {e}")

@router.post("/export/pdf")
async def export_pdf(report: AnalysisReport):
    try:
        report_service = PDFReportService()
        pdf_bytes = report_service.generate_report(report)
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment;filename=analysis_report.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {e}")