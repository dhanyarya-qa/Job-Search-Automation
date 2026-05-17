"""
Statistics Dashboard - Visualize job search data
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, func
from app.database.session import get_async_session
from app.database.models.job import Job
from app.database.models.application_tracking import ApplicationTracking


st.set_page_config(page_title="Job Statistics", page_icon="📊", layout="wide")


async def get_job_stats():
    """Get job statistics from database"""
    async for session in get_async_session():
        # Total jobs
        result = await session.execute(select(func.count(Job.id)))
        total_jobs = result.scalar()
        
        # Jobs today
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        result = await session.execute(
            select(func.count(Job.id)).where(Job.created_at >= today)
        )
        jobs_today = result.scalar()
        
        # Jobs this week
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        result = await session.execute(
            select(func.count(Job.id)).where(Job.created_at >= week_ago)
        )
        jobs_this_week = result.scalar()
        
        # Priority jobs
        result = await session.execute(
            select(func.count(Job.id)).where(Job.is_priority == True)
        )
        priority_jobs = result.scalar()
        
        # Remote jobs
        result = await session.execute(
            select(func.count(Job.id)).where(Job.is_remote == True)
        )
        remote_jobs = result.scalar()
        
        # Sent to Telegram
        result = await session.execute(
            select(func.count(Job.id)).where(Job.sent_to_telegram == True)
        )
        sent_to_telegram = result.scalar()
        
        return {
            "total_jobs": total_jobs,
            "jobs_today": jobs_today,
            "jobs_this_week": jobs_this_week,
            "priority_jobs": priority_jobs,
            "remote_jobs": remote_jobs,
            "sent_to_telegram": sent_to_telegram,
        }


async def get_jobs_by_platform():
    """Get job count by platform"""
    async for session in get_async_session():
        result = await session.execute(
            select(Job.source_platform, func.count(Job.id))
            .group_by(Job.source_platform)
            .order_by(func.count(Job.id).desc())
        )
        return result.all()


async def get_jobs_by_company():
    """Get top companies by job count"""
    async for session in get_async_session():
        result = await session.execute(
            select(Job.company_name, func.count(Job.id))
            .group_by(Job.company_name)
            .order_by(func.count(Job.id).desc())
            .limit(10)
        )
        return result.all()


async def get_jobs_over_time():
    """Get jobs created over time (last 30 days)"""
    async for session in get_async_session():
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        result = await session.execute(
            select(Job).where(Job.created_at >= thirty_days_ago).order_by(Job.created_at)
        )
        jobs = result.scalars().all()
        
        # Group by date
        jobs_by_date = {}
        for job in jobs:
            date_key = job.created_at.date()
            jobs_by_date[date_key] = jobs_by_date.get(date_key, 0) + 1
        
        return jobs_by_date


async def get_application_stats():
    """Get application tracking statistics"""
    async for session in get_async_session():
        result = await session.execute(select(ApplicationTracking))
        trackings = result.scalars().all()
        
        stats = {
            "total": len(trackings),
            "by_status": {},
        }
        
        for tracking in trackings:
            status = tracking.status
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        return stats


def main():
    st.title("📊 Job Search Statistics")
    st.markdown("---")
    
    # Get data
    stats = asyncio.run(get_job_stats())
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Jobs", f"{stats['total_jobs']:,}")
    
    with col2:
        st.metric("Jobs Today", f"{stats['jobs_today']:,}")
    
    with col3:
        st.metric("This Week", f"{stats['jobs_this_week']:,}")
    
    with col4:
        st.metric("Priority Jobs", f"{stats['priority_jobs']:,}")
    
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric("Remote Jobs", f"{stats['remote_jobs']:,}")
    
    with col6:
        st.metric("Sent to Telegram", f"{stats['sent_to_telegram']:,}")
    
    with col7:
        remote_pct = (stats['remote_jobs'] / stats['total_jobs'] * 100) if stats['total_jobs'] > 0 else 0
        st.metric("Remote %", f"{remote_pct:.1f}%")
    
    with col8:
        priority_pct = (stats['priority_jobs'] / stats['total_jobs'] * 100) if stats['total_jobs'] > 0 else 0
        st.metric("Priority %", f"{priority_pct:.1f}%")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Jobs by Platform")
        platform_data = asyncio.run(get_jobs_by_platform())
        
        if platform_data:
            df_platform = pd.DataFrame(platform_data, columns=["Platform", "Count"])
            fig = px.bar(
                df_platform,
                x="Platform",
                y="Count",
                title="Job Distribution by Platform",
                color="Count",
                color_continuous_scale="Blues",
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")
    
    with col2:
        st.subheader("🏢 Top 10 Companies")
        company_data = asyncio.run(get_jobs_by_company())
        
        if company_data:
            df_company = pd.DataFrame(company_data, columns=["Company", "Count"])
            fig = px.bar(
                df_company,
                x="Count",
                y="Company",
                orientation="h",
                title="Top Companies by Job Count",
                color="Count",
                color_continuous_scale="Greens",
            )
            fig.update_layout(showlegend=False, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available")
    
    # Jobs over time
    st.subheader("📅 Jobs Over Time (Last 30 Days)")
    jobs_over_time = asyncio.run(get_jobs_over_time())
    
    if jobs_over_time:
        df_time = pd.DataFrame(
            list(jobs_over_time.items()),
            columns=["Date", "Count"]
        )
        df_time = df_time.sort_values("Date")
        
        fig = px.line(
            df_time,
            x="Date",
            y="Count",
            title="Daily Job Postings",
            markers=True,
        )
        fig.update_traces(line_color="#1f77b4", line_width=3)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available")
    
    # Application Tracking Stats
    st.markdown("---")
    st.subheader("📋 Application Tracking")
    
    app_stats = asyncio.run(get_application_stats())
    
    if app_stats["total"] > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Applications Tracked", f"{app_stats['total']:,}")
        
        with col2:
            # Pie chart of application status
            if app_stats["by_status"]:
                df_status = pd.DataFrame(
                    list(app_stats["by_status"].items()),
                    columns=["Status", "Count"]
                )
                
                fig = px.pie(
                    df_status,
                    values="Count",
                    names="Status",
                    title="Application Status Distribution",
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No application tracking data yet")
    
    # Refresh button
    st.markdown("---")
    if st.button("🔄 Refresh Data"):
        st.rerun()


if __name__ == "__main__":
    main()
