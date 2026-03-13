import asyncio
import re
from playwright.async_api import async_playwright

async def get_attendance(username, password):
    """
    Scrapes attendance data from MITS IMS portal.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) # Run in headless mode for deployment
        # Set a realistic user agent
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            # 1. Open the website
            await page.goto("http://mitsims.in/", timeout=60000)

            # 2. Click the student login link
            await page.click("#studentLink", force=True)
            
            # Wait for student fields
            await page.wait_for_selector("#inputStuId", state="visible", timeout=10000)

            # 3. Enter credentials
            await page.fill("#studentForm #inputStuId", username)
            await page.fill("#studentForm #inputPassword", password)

            # 4. Click login
            await page.click("#studentSubmitButton", force=True)
            
            # 5. Handle potential errors or redirects
            try:
                # Wait for any of the success indicators
                # Dashboard elements: .dashboard, #studentIndex, #studentName
                await page.wait_for_selector(".dashboard, #studentIndex, #studentName, [href*='logout']", timeout=15000)
            except:
                # Check for error message onscreen
                error_msg = await page.locator(".alert-danger, #loginError, .errorMessage").text_content() if await page.locator(".alert-danger, #loginError, .errorMessage").count() > 0 else "Login failed. Please check credentials."
                return {"error": error_msg.strip()}
                
                # If we are stuck on a redirect page, give it a moment
                if "studentReDirect" in current_url:
                    try:
                        await page.wait_for_url("**/studentIndex.html", timeout=10000)
                    except:
                        pass

            # 6. Scraping Task - Hybrid Text-Line Analysis
            # This is the most robust way to handle the GEMS ExtJS layout.
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(5) # Give it plenty of time to render all components

            attendance_list = []
            
            # Get the full text of the page body
            full_text = await page.inner_text("body")
            lines = [l.strip() for l in full_text.split('\n') if l.strip()]
            
            # Pattern matching for Subject Codes (e.g., 20MAT101, APTITUDE, etc.)
            # Subject codes usually start with digits followed by letters, or are all caps
            for i, line in enumerate(lines):
                # Heuristic for Subject Code or Name:
                # 1. Matches 20MAT101 style: r'^\d*[A-Z]+\d+[A-Z0-9]*$'
                # 2. Or is a long uppercase string (Subject Name)
                is_subject_code = re.match(r'^\d*[A-Z]+\d+[A-Z0-9]*$', line)
                is_subject_name = (line.isupper() and len(line) > 5 and not re.search(r'\d', line[:5]))
                # Filter out labels and headers
                exclude_keywords = ["TOTAL", "ATTENDANCE", "SUBJECT", "CLASSES", "CONDUCTED", "S.NO", "SERIAL"]
                if (is_subject_code or is_subject_name) and not any(kw in line.upper() for kw in exclude_keywords):
                    try:
                        # Look at the next 10 lines for attendance numbers
                        # We expect Attended, Total, and Percentage in sequence
                        lookahead = lines[i+1 : i+12]
                        numbers = []
                        for sub_line in lookahead:
                            # Extract numbers or percentages
                            # Matches "25", "25.0", "83.33%", "83.33"
                            match = re.search(r'(\d+\.?\d*)%?', sub_line)
                            if match:
                                numbers.append(match.group(1))
                            
                            if len(numbers) >= 3:
                                break
                        
                        if len(numbers) >= 3:
                            attendance_list.append({
                                "subject": line,
                                "attended": numbers[0],
                                "total": numbers[1],
                                "percentage": numbers[2]
                            })
                    except:
                        continue

            # Fallback Strategy: Fieldset card scanning if text analysis was too sparse
            if len(attendance_list) < 3:
                fieldsets = await page.locator("fieldset").all()
                for fs in fieldsets:
                    text = await fs.inner_text()
                    if "%" in text:
                        # Extract components
                        subj_match = re.search(r"Subject Name\s*:?\s*(.*)", text, re.I)
                        att_match = re.search(r"Classes Attended\s*:?\s*(\d+)", text, re.I)
                        tot_match = re.search(r"Total Conducted\s*:?\s*(\d+)", text, re.I)
                        perc_match = re.search(r"Attendance\s*%\s*:?\s*(\d+\.?\d*)", text, re.I)
                        
                        if subj_match and (att_match or perc_match):
                            attendance_list.append({
                                "subject": subj_match.group(1).strip().split('\n')[0],
                                "attended": att_match.group(1) if att_match else "0",
                                "total": tot_match.group(1) if tot_match else "0",
                                "percentage": perc_match.group(1) if perc_match else "0"
                            })

            # Cleanup and Uniqueness
            unique_attendance = []
            seen_subjects = set()
            for item in attendance_list:
                # Basic cleaning of subject names
                clean_name = item["subject"].replace(":", "").strip()
                exclude_keywords = ["SUBJECT CODE", "CLASSES ATTENDED", "TOTAL CONDUCTED", "ATTENDANCE %", "S.NO"]
                if clean_name not in seen_subjects and len(clean_name) > 2 and not any(kw in clean_name.upper() for kw in exclude_keywords):
                    unique_attendance.append({
                        "subject": clean_name,
                        "attended": item["attended"],
                        "total": item["total"],
                        "percentage": item["percentage"]
                    })
                    seen_subjects.add(clean_name)

            if not unique_attendance:
                return {"error": "Attendance data not found. Please ensure you have access to the dashboard and try again."}

            return unique_attendance

        except Exception as e:
            return {"error": f"Scraping error: {str(e)}"}
        finally:
            await browser.close()
