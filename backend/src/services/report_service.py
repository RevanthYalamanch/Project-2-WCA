import io
import matplotlib.pyplot as plt
from fpdf import FPDF
from ..models.data_models import AnalysisReport, SentimentAnalysis

class PDFReportService:
    """
    Creates professional, structured PDF reports from AI analysis results,
    including data visualizations.
    """
    def _add_title(self, pdf, title):
        pdf.set_font("Arial", 'B', 18)
        pdf.cell(0, 10, title, 0, 1, 'C')
        pdf.ln(5)

    def _add_section_header(self, pdf, header):
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, header, 0, 1, 'L')
        pdf.ln(2)

    def _write_body(self, pdf, text):
        pdf.set_font("Arial", '', 11)
        # Use multi_cell for better text wrapping
        pdf.multi_cell(0, 6, text.encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(5)

    def _write_bullet_points(self, pdf, points):
        pdf.set_font("Arial", '', 11)
        for point in points:
            pdf.multi_cell(0, 6, f"  •  {point}".encode('latin-1', 'replace').decode('latin-1'))
        pdf.ln(5)

    def _generate_sentiment_chart(self, sentiment_data: SentimentAnalysis) -> io.BytesIO:
        """
        Creates a simple horizontal bar chart for sentiment visualization.
        """
        sentiment = sentiment_data.sentiment.lower()
        score_map = {'positive': 8.5, 'neutral': 5.0, 'negative': 2.0}
        score = score_map.get(sentiment, 5.0)
        color = 'forestgreen' if score > 6 else 'crimson' if score < 4 else 'gold'

        fig, ax = plt.subplots(figsize=(6, 1))
        # Background bar
        ax.barh([0], [10], color='whitesmoke')
        # Sentiment score bar
        ax.barh([0], [score], color=color)
        
        ax.set_xlim(0, 10)
        ax.set_yticks([])
        ax.set_title(f"Sentiment Analysis: {sentiment.capitalize()}", loc='left')
        plt.box(False) # Remove frame
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        return buf

    def generate_report(self, report_data: AnalysisReport) -> bytes:
        """
        Combines all AI analysis results into a professional PDF report.
        """
        pdf = FPDF()
        pdf.add_page()

        # Report Title
        self._add_title(pdf, "Web Content Analysis Report")
        pdf.set_font("Arial", 'I', 11)
        pdf.cell(0, 10, f"URL Analyzed: {report_data.url}", 0, 1, 'C')
        pdf.ln(10)

        # Executive Summary Generation
        self._add_section_header(pdf, "1. Executive Summary")
        self._write_body(pdf, report_data.ai_summary.summary)

        # Detailed Analysis Sections
        self._add_section_header(pdf, "2. Key Points")
        self._write_bullet_points(pdf, report_data.ai_summary.key_points)

        # Visual Data Representations
        self._add_section_header(pdf, "3. Sentiment & Tone")
        self._write_body(pdf, f"The overall sentiment of the content is {report_data.ai_summary.sentiment_analysis.sentiment} with a primarily {report_data.ai_summary.sentiment_analysis.tone} tone.")
        chart_buffer = self._generate_sentiment_chart(report_data.ai_summary.sentiment_analysis)
        pdf.image(chart_buffer, x=pdf.get_x(), w=150)
        pdf.ln(5)

        # Actionable Recommendations
        self._add_section_header(pdf, "4. SEO Recommendations")
        self._write_bullet_points(pdf, report_data.ai_summary.seo_analysis.recommendations)
        self._add_section_header(pdf, "Identified Target Keywords")
        self._write_body(pdf, ", ".join(report_data.ai_summary.seo_analysis.target_keywords))

        # Competitive Benchmarking
        self._add_section_header(pdf, "5. Competitive Positioning")
        self._write_body(pdf, report_data.ai_summary.competitive_positioning)
        
        return pdf.output(dest='S').encode('latin-1')