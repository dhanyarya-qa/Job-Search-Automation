"""
Export Jobs - Export job data to Excel and PDF
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

import structlog
from sqlalchemy import select
from app.database.session import get_async_session
from app.database.models.job import Job

logger = structlog.get_logger(__name__)


async def export_to_excel(output_file: str = None):
    """Export jobs to Excel file"""
    try:
        import pandas as pd
    except ImportError:
        print("❌ pandas not installed. Run: pip install pandas openpyxl")
        return
    
    print("=" * 60)
    print("📊 EXPORTING JOBS TO EXCEL")
    print("=" * 60)
    print()
    
    async for session in get_async_session():
        # Get all jobs
        result = await session.execute(
            select(Job).order_by(Job.created_at.desc())
        )
        jobs = result.scalars().all()
        
        if not jobs:
            print("❌ No jobs found in database")
            return
        
        print(f"📦 Found {len(jobs)} jobs")
        
        # Convert to DataFrame
        data = []
        for job in jobs:
            data.append({
                "Job Title": job.job_title,
                "Company": job.company_name,
                "Location": job.location or "",
                "Salary": job.salary or "",
                "Job Type": job.job_type or "",
                "Experience Level": job.experience_level or "",
                "Platform": job.source_platform,
                "Job URL": job.job_url,
                "Apply Email": job.apply_email or "",
                "Apply Link": job.apply_link or "",
                "Is Remote": "Yes" if job.is_remote else "No",
                "Is Priority": "Yes" if job.is_priority else "No",
                "Sent to Telegram": "Yes" if job.sent_to_telegram else "No",
                "Posted Date": job.posted_date.strftime("%Y-%m-%d %H:%M") if job.posted_date else "",
                "Expires At": job.expires_at.strftime("%Y-%m-%d") if job.expires_at else "",
                "Created At": job.created_at.strftime("%Y-%m-%d %H:%M"),
            })
        
        df = pd.DataFrame(data)
        
        # Generate filename
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"outputs/jobs_export_{timestamp}.xlsx"
        
        # Ensure directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Export to Excel
        df.to_excel(output_file, index=False, sheet_name="Jobs")
        
        print(f"✅ Exported to: {output_file}")
        print(f"📊 Total rows: {len(df)}")
        print(f"📋 Columns: {len(df.columns)}")
        print()
        print("=" * 60)


async def export_to_csv(output_file: str = None):
    """Export jobs to CSV file"""
    try:
        import pandas as pd
    except ImportError:
        print("❌ pandas not installed. Run: pip install pandas")
        return
    
    print("=" * 60)
    print("📄 EXPORTING JOBS TO CSV")
    print("=" * 60)
    print()
    
    async for session in get_async_session():
        # Get all jobs
        result = await session.execute(
            select(Job).order_by(Job.created_at.desc())
        )
        jobs = result.scalars().all()
        
        if not jobs:
            print("❌ No jobs found in database")
            return
        
        print(f"📦 Found {len(jobs)} jobs")
        
        # Convert to DataFrame
        data = []
        for job in jobs:
            data.append({
                "Job Title": job.job_title,
                "Company": job.company_name,
                "Location": job.location or "",
                "Salary": job.salary or "",
                "Job Type": job.job_type or "",
                "Experience Level": job.experience_level or "",
                "Platform": job.source_platform,
                "Job URL": job.job_url,
                "Apply Email": job.apply_email or "",
                "Apply Link": job.apply_link or "",
                "Is Remote": "Yes" if job.is_remote else "No",
                "Is Priority": "Yes" if job.is_priority else "No",
                "Created At": job.created_at.strftime("%Y-%m-%d %H:%M"),
            })
        
        df = pd.DataFrame(data)
        
        # Generate filename
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"outputs/jobs_export_{timestamp}.csv"
        
        # Ensure directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Export to CSV
        df.to_csv(output_file, index=False, encoding="utf-8")
        
        print(f"✅ Exported to: {output_file}")
        print(f"📊 Total rows: {len(df)}")
        print()
        print("=" * 60)


async def export_to_pdf(output_file: str = None):
    """Export jobs to PDF file"""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.units import inch
    except ImportError:
        print("❌ reportlab not installed. Run: pip install reportlab")
        return
    
    print("=" * 60)
    print("📑 EXPORTING JOBS TO PDF")
    print("=" * 60)
    print()
    
    async for session in get_async_session():
        # Get all jobs
        result = await session.execute(
            select(Job).order_by(Job.created_at.desc()).limit(100)  # Limit for PDF
        )
        jobs = result.scalars().all()
        
        if not jobs:
            print("❌ No jobs found in database")
            return
        
        print(f"📦 Found {len(jobs)} jobs (showing first 100)")
        
        # Generate filename
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"outputs/jobs_export_{timestamp}.pdf"
        
        # Ensure directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        # Create PDF
        doc = SimpleDocTemplate(output_file, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
        )
        title = Paragraph(f"Job Listings Report", title_style)
        elements.append(title)
        
        # Subtitle
        subtitle = Paragraph(
            f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}<br/>Total Jobs: {len(jobs)}",
            styles['Normal']
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 0.3*inch))
        
        # Add each job
        for i, job in enumerate(jobs, 1):
            # Job header
            job_title = Paragraph(f"<b>{i}. {job.job_title}</b>", styles['Heading2'])
            elements.append(job_title)
            
            # Job details
            details = f"""
            <b>Company:</b> {job.company_name}<br/>
            <b>Location:</b> {job.location or 'N/A'}<br/>
            <b>Salary:</b> {job.salary or 'Not specified'}<br/>
            <b>Platform:</b> {job.source_platform.title()}<br/>
            <b>Posted:</b> {job.created_at.strftime('%d %b %Y')}<br/>
            """
            
            if job.apply_email:
                details += f"<b>Email:</b> {job.apply_email}<br/>"
            
            if job.job_url:
                details += f"<b>URL:</b> <link href='{job.job_url}'>{job.job_url[:50]}...</link><br/>"
            
            details_para = Paragraph(details, styles['Normal'])
            elements.append(details_para)
            elements.append(Spacer(1, 0.2*inch))
            
            # Page break every 5 jobs
            if i % 5 == 0 and i < len(jobs):
                elements.append(PageBreak())
        
        # Build PDF
        doc.build(elements)
        
        print(f"✅ Exported to: {output_file}")
        print(f"📄 Total jobs: {len(jobs)}")
        print()
        print("=" * 60)


async def main():
    if len(sys.argv) < 2:
        print("Usage: python export_jobs.py <format> [output_file]")
        print("Formats: excel, csv, pdf, all")
        print("Example: python export_jobs.py excel")
        print("Example: python export_jobs.py csv my_jobs.csv")
        return
    
    format_type = sys.argv[1].lower()
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if format_type == "excel":
        await export_to_excel(output_file)
    elif format_type == "csv":
        await export_to_csv(output_file)
    elif format_type == "pdf":
        await export_to_pdf(output_file)
    elif format_type == "all":
        await export_to_excel()
        await export_to_csv()
        await export_to_pdf()
    else:
        print(f"❌ Unknown format: {format_type}")
        print("Available formats: excel, csv, pdf, all")


if __name__ == "__main__":
    asyncio.run(main())
