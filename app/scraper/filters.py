"""
Job Filters - Filter jobs based on criteria
"""
from __future__ import annotations

import re
from typing import Any


class JobFilter:
    """Filter jobs based on various criteria"""
    
    def __init__(
        self,
        locations: list[str] | None = None,
        min_salary: int | None = None,
        max_salary: int | None = None,
        job_types: list[str] | None = None,
        experience_levels: list[str] | None = None,
        required_keywords: list[str] | None = None,
        excluded_keywords: list[str] | None = None,
        excluded_companies: list[str] | None = None,
        priority_companies: list[str] | None = None,
    ):
        self.locations = [loc.lower() for loc in locations] if locations else []
        self.min_salary = min_salary
        self.max_salary = max_salary
        self.job_types = [jt.lower() for jt in job_types] if job_types else []
        self.experience_levels = [el.lower() for el in experience_levels] if experience_levels else []
        self.required_keywords = [kw.lower() for kw in required_keywords] if required_keywords else []
        self.excluded_keywords = [kw.lower() for kw in excluded_keywords] if excluded_keywords else []
        self.excluded_companies = [c.lower() for c in excluded_companies] if excluded_companies else []
        self.priority_companies = [c.lower() for c in priority_companies] if priority_companies else []
    
    def filter_job(self, job: dict[str, Any]) -> tuple[bool, str, bool]:
        """
        Filter a single job
        
        Returns:
            (should_include, reason, is_priority)
        """
        title = job.get("job_title", "").lower()
        company = job.get("company_name", "").lower()
        location = job.get("location", "").lower()
        description = job.get("description", "").lower()
        salary = job.get("salary", "").lower()
        
        # Check excluded companies (blacklist)
        if self.excluded_companies:
            for excluded in self.excluded_companies:
                if excluded in company:
                    return False, f"Company blacklisted: {excluded}", False
        
        # Check excluded keywords
        if self.excluded_keywords:
            for keyword in self.excluded_keywords:
                if keyword in title or keyword in description:
                    return False, f"Excluded keyword found: {keyword}", False
        
        # Check location
        if self.locations:
            location_match = False
            for loc in self.locations:
                if loc in location:
                    location_match = True
                    break
            if not location_match:
                return False, f"Location not in filter: {location}", False
        
        # Check job type
        if self.job_types:
            job_type_match = False
            for jt in self.job_types:
                if jt in title or jt in description:
                    job_type_match = True
                    break
            if not job_type_match:
                return False, "Job type not in filter", False
        
        # Check experience level
        if self.experience_levels:
            exp_match = False
            for exp in self.experience_levels:
                if exp in title or exp in description:
                    exp_match = True
                    break
            if not exp_match:
                return False, "Experience level not in filter", False
        
        # Check required keywords
        if self.required_keywords:
            for keyword in self.required_keywords:
                if keyword not in title and keyword not in description:
                    return False, f"Required keyword missing: {keyword}", False
        
        # Check salary range
        if self.min_salary or self.max_salary:
            salary_value = self._extract_salary(salary)
            if salary_value:
                if self.min_salary and salary_value < self.min_salary:
                    return False, f"Salary below minimum: {salary_value}", False
                if self.max_salary and salary_value > self.max_salary:
                    return False, f"Salary above maximum: {salary_value}", False
        
        # Check if priority company
        is_priority = False
        if self.priority_companies:
            for priority in self.priority_companies:
                if priority in company:
                    is_priority = True
                    break
        
        return True, "Passed all filters", is_priority
    
    def _extract_salary(self, salary_text: str) -> int | None:
        """Extract numeric salary from text"""
        if not salary_text:
            return None
        
        # Remove common words
        salary_text = salary_text.lower()
        salary_text = re.sub(r'(rp|idr|usd|\$|,|\.)', '', salary_text)
        
        # Extract numbers
        numbers = re.findall(r'\d+', salary_text)
        if not numbers:
            return None
        
        # Take the first number (usually the minimum)
        salary = int(numbers[0])
        
        # Handle millions/thousands
        if 'juta' in salary_text or 'million' in salary_text:
            salary *= 1_000_000
        elif 'ribu' in salary_text or 'thousand' in salary_text or 'k' in salary_text:
            salary *= 1_000
        
        return salary
    
    def filter_jobs(self, jobs: list[dict[str, Any]]) -> tuple[list[dict], list[dict]]:
        """
        Filter a list of jobs
        
        Returns:
            (filtered_jobs, priority_jobs)
        """
        filtered = []
        priority = []
        
        for job in jobs:
            should_include, reason, is_priority = self.filter_job(job)
            
            if should_include:
                job['filter_reason'] = reason
                job['is_priority'] = is_priority
                
                if is_priority:
                    priority.append(job)
                else:
                    filtered.append(job)
        
        return filtered, priority


# Default filter configuration
DEFAULT_FILTER = JobFilter(
    # Relax location filter - accept any location
    locations=[],  # Empty = accept all locations
    # Relax job type filter - accept any type
    job_types=[],  # Empty = accept all types
    # Relax experience level filter - accept any level
    experience_levels=[],  # Empty = accept all levels
    # Only exclude obvious bad keywords
    excluded_keywords=["intern", "magang", "unpaid", "volunteer"],
    # No company blacklist
    excluded_companies=[],
    # Priority companies
    priority_companies=["google", "tokopedia", "gojek", "shopee", "grab", "bukalapak", "traveloka", "blibli"],
)
