"""
Company Research Script - Get company info from multiple sources
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import structlog
from app.notifications.telegram_notifier import TelegramNotifier
from playwright.async_api import async_playwright

logger = structlog.get_logger(__name__)


async def search_glassdoor(company_name: str) -> dict:
    """Search Glassdoor for company reviews"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            search_url = f"https://www.glassdoor.com/Search/results.htm?keyword={company_name.replace(' ', '+')}"
            await page.goto(search_url, timeout=30000)
            await page.wait_for_timeout(2000)
            
            # Try to extract rating
            rating_el = await page.query_selector("[data-test='rating']")
            rating = await rating_el.inner_text() if rating_el else "N/A"
            
            # Try to extract review count
            reviews_el = await page.query_selector("[data-test='review-count']")
            reviews = await reviews_el.inner_text() if reviews_el else "N/A"
            
            await browser.close()
            
            return {
                "rating": rating,
                "reviews": reviews,
                "url": search_url,
            }
    except Exception as e:
        logger.error("Glassdoor search failed", error=str(e))
        return {"rating": "N/A", "reviews": "N/A", "url": ""}


async def search_linkedin_company(company_name: str) -> dict:
    """Search LinkedIn for company info"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            search_url = f"https://www.linkedin.com/search/results/companies/?keywords={company_name.replace(' ', '%20')}"
            await page.goto(search_url, timeout=30000)
            await page.wait_for_timeout(2000)
            
            # Try to get first company result
            company_card = await page.query_selector(".entity-result")
            
            if company_card:
                name_el = await company_card.query_selector(".entity-result__title-text")
                name = await name_el.inner_text() if name_el else company_name
                
                subtitle_el = await company_card.query_selector(".entity-result__primary-subtitle")
                industry = await subtitle_el.inner_text() if subtitle_el else "N/A"
                
                link_el = await company_card.query_selector("a")
                url = await link_el.get_attribute("href") if link_el else ""
            else:
                name = company_name
                industry = "N/A"
                url = search_url
            
            await browser.close()
            
            return {
                "name": name,
                "industry": industry,
                "url": url,
            }
    except Exception as e:
        logger.error("LinkedIn search failed", error=str(e))
        return {"name": company_name, "industry": "N/A", "url": ""}


async def search_company_news(company_name: str) -> list[dict]:
    """Search Google News for company news"""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            search_url = f"https://news.google.com/search?q={company_name.replace(' ', '+')}"
            await page.goto(search_url, timeout=30000)
            await page.wait_for_timeout(2000)
            
            news_items = []
            articles = await page.query_selector_all("article")
            
            for article in articles[:5]:
                try:
                    title_el = await article.query_selector("h3, h4")
                    title = await title_el.inner_text() if title_el else ""
                    
                    link_el = await article.query_selector("a")
                    link = await link_el.get_attribute("href") if link_el else ""
                    if link and link.startswith("./"):
                        link = f"https://news.google.com{link[1:]}"
                    
                    if title:
                        news_items.append({"title": title, "url": link})
                except Exception:
                    continue
            
            await browser.close()
            return news_items
    except Exception as e:
        logger.error("News search failed", error=str(e))
        return []


async def research_company(company_name: str) -> dict:
    """Comprehensive company research"""
    print(f"🔍 Researching: {company_name}")
    print("=" * 60)
    
    # Run all searches in parallel
    glassdoor_task = search_glassdoor(company_name)
    linkedin_task = search_linkedin_company(company_name)
    news_task = search_company_news(company_name)
    
    glassdoor, linkedin, news = await asyncio.gather(
        glassdoor_task, linkedin_task, news_task
    )
    
    research = {
        "company_name": company_name,
        "glassdoor": glassdoor,
        "linkedin": linkedin,
        "news": news,
    }
    
    # Print results
    print(f"\n📊 Glassdoor:")
    print(f"  Rating: {glassdoor['rating']}")
    print(f"  Reviews: {glassdoor['reviews']}")
    
    print(f"\n💼 LinkedIn:")
    print(f"  Industry: {linkedin['industry']}")
    
    print(f"\n📰 Recent News ({len(news)} articles):")
    for i, article in enumerate(news[:3], 1):
        print(f"  {i}. {article['title'][:60]}...")
    
    print("\n" + "=" * 60)
    
    return research


async def send_research_to_telegram(company_name: str):
    """Research company and send to Telegram"""
    research = await research_company(company_name)
    
    notifier = TelegramNotifier()
    
    # Build message
    text = f"🔍 <b>Company Research: {company_name}</b>\n\n"
    
    # Glassdoor
    text += f"📊 <b>Glassdoor</b>\n"
    text += f"⭐ Rating: {research['glassdoor']['rating']}\n"
    text += f"💬 Reviews: {research['glassdoor']['reviews']}\n"
    if research['glassdoor']['url']:
        text += f"🔗 <a href=\"{research['glassdoor']['url']}\">View on Glassdoor</a>\n"
    text += "\n"
    
    # LinkedIn
    text += f"💼 <b>LinkedIn</b>\n"
    text += f"🏭 Industry: {research['linkedin']['industry']}\n"
    if research['linkedin']['url']:
        text += f"🔗 <a href=\"{research['linkedin']['url']}\">View on LinkedIn</a>\n"
    text += "\n"
    
    # News
    if research['news']:
        text += f"📰 <b>Recent News</b>\n"
        for i, article in enumerate(research['news'][:3], 1):
            title = article['title'][:60]
            if article['url']:
                text += f"{i}. <a href=\"{article['url']}\">{title}</a>\n"
            else:
                text += f"{i}. {title}\n"
    
    await notifier.send_message(text)
    print("\n✅ Research sent to Telegram!")


async def main():
    if len(sys.argv) < 2:
        print("Usage: python research_company.py <company_name>")
        print("Example: python research_company.py 'Tokopedia'")
        return
    
    company_name = " ".join(sys.argv[1:])
    await send_research_to_telegram(company_name)


if __name__ == "__main__":
    asyncio.run(main())
