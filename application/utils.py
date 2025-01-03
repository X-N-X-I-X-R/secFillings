import logging
import colorlog
from sec_edgar_downloader import Downloader  # type: ignore
import os
import shutil
from datetime import datetime
import glob
from django.conf import settings
from bs4 import BeautifulSoup 
import time
import re
from typing import Optional, Tuple, Dict

# Configure colorlog
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(levelname)s - %(message)s',
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
        'PROCESS_TIME': 'blue',  # Change 'pink' to 'blue' or any other valid color
    }
))

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Define a custom log level
PROCESS_TIME_LEVEL = 25
logging.addLevelName(PROCESS_TIME_LEVEL, "PROCESS_TIME")

def process_time(self, message, *args, **kws):
    if self.isEnabledFor(PROCESS_TIME_LEVEL):
        self._log(PROCESS_TIME_LEVEL, message, args, **kws)

logging.Logger.process_time = process_time  # type: ignore

HTML_FILES_NAME = ["primary-document.html", "full-submission.txt"]

def find_and_rename_files(folder_path: str):
    """
    פונקציה המחפשת קבצים מסוג primary-document.html או full-submission.txt
    ומחליפה את השם שלהם (למשל מ-primary-document.html ל-AAPL_10-K.html).
    """
    logger.info("Started processing folder: %s", folder_path)
    try:
        for dirpath, _, files in os.walk(folder_path):
            for file in files:
                if file in HTML_FILES_NAME:
                    report_type_dir = os.path.basename(os.path.dirname(dirpath))
                    ticker_dir = os.path.basename(os.path.dirname(os.path.dirname(dirpath)))
                    file_extension = file.split('.')[-1]
                    new_file_name = f"{ticker_dir.upper()}_{report_type_dir}.{file_extension}"
                    source_path = os.path.join(dirpath, file)
                    destination_path = os.path.join(dirpath, new_file_name)
                    logger.info("Renaming file from %s to %s", source_path, destination_path)
                    os.rename(source_path, destination_path)
        logger.info("Finished processing folder: %s", folder_path)
    except Exception as e:
        logger.error("Error during file renaming in folder %s: %s", folder_path, e)
        raise

def move_files_to_parent(folder_path: str):
    """
    Moves HTML/TXT files from subdirectories to their parent directory,
    ensuring existing files are not replaced and maintaining folder structure.
    """
    logger.info("Moving files to parent folder for path: %s", folder_path)
    try:
        for dirpath, _, files in os.walk(folder_path, topdown=False):
            for file in files:
                source_path = os.path.join(dirpath, file)
                parent_dir = os.path.dirname(dirpath)
                destination_path = os.path.join(parent_dir, file)

                if not os.path.exists(destination_path):
                    logger.info(f"Moving {source_path} to {destination_path}")
                    os.rename(source_path, destination_path)
                else:
                    logger.info(f"File already exists, skipping move: {destination_path}")

            # Remove the directory only if it is empty after moving files
            if not os.listdir(dirpath):
                logger.info(f"Removing empty directory: {dirpath}")
                os.rmdir(dirpath)

        logger.info("Finished moving files for path: %s", folder_path)
    except Exception as e:
        logger.error("Error during file moving for path %s: %s", folder_path, e)

from bs4 import BeautifulSoup

from bs4 import BeautifulSoup

import re
from bs4 import BeautifulSoup

def _insert_custom_style(soup: BeautifulSoup):
    """
    פונקציה לעיצוב הדוח בסגנון המזכיר עיתון (דו-עמודי),
    תוך מיון דפים לפי מספר העמוד המופיע בכותרת.
    """

    style_content = """
    <style>
    /* גוף הדף */
    body {
        background-color: #f8f8f2;
        color: #333333;
        font-family: 'Times New Roman', Times, serif;
        margin: 0;
        padding: 20px;
        line-height: 1.6;
    }
    /* עיצוב הכותרות */
    h1, h2, h3 {
        font-family: 'Times New Roman', Times, serif;
        color: #111111;
        margin-bottom: 0.5em;
    }
    /* טקסט כללי */
    p {
        margin-bottom: 1em;
        text-align: justify;
    }
    /* תמונות */
    .content img {
        max-width: 100%;
        height: auto;
        margin: 10px 0;
    }
    /* ציטוטים */
    blockquote {
        border-left: 3px solid #cccccc;
        padding-left: 15px;
        color: #555555;
        font-style: italic;
        margin: 20px 0;
    }
    /* טבלאות */
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }
    th, td {
        border: 1px solid #cccccc;
        padding: 8px;
        text-align: left;
    }
    th {
        background-color: #eee;
    }
    /* אזור תחתון (footer) */
    .footer {
        text-align: center;
        margin-top: 40px;
        font-size: 0.9em;
        color: #777777;
    }
    /* פריסת "עיתון": שתי עמודות זו לצד זו */
    .content-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        grid-gap: 30px;
        margin-bottom: 40px;
    }
    /* כל "עמוד" בנפרד */
    .page {
        background-color: #ffffff;
        padding: 15px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        border: 1px solid #ddd;
        margin-bottom: 20px;
    }
    /* הסתרת תגים ייחודיים של XBRL */
    ix\\:header, ix\\:references, xbrli\\:context, xbrli\\:period,
    xbrli\\:startDate, xbrli\\:endDate, xbrli\\:segment,
    xbrli\\:unitNumerator, xbrli\\:divide {
        display: none;
    }
    </style>
    """

    # 1) יצירת head אם לא קיים
    if not soup.head:
        if not soup.html:
            html_tag = soup.new_tag("html")
            soup.insert(0, html_tag)
        else:
            html_tag = soup.html
        head_tag = soup.new_tag("head")
        html_tag.insert(0, head_tag)
    else:
        head_tag = soup.head

    # הוספת ה-style ל-head
    head_tag.append(BeautifulSoup(style_content, "html.parser"))

    # 2) יצירת body אם לא קיים
    if not soup.body:
        if not soup.html:
            html_tag = soup.new_tag("html")
            soup.insert(0, html_tag)
        else:
            html_tag = soup.html
        body_tag = soup.new_tag("body")
        html_tag.append(body_tag)
    else:
        body_tag = soup.body

    # הסרת אלמנטים לא רצויים
    for unwanted_class in ['button', 'card', 'custom-header']:
        for tag in soup.find_all(class_=unwanted_class):
            tag.decompose()

    # 3) יצירת Grid של עמודים
    grid_container = soup.new_tag("div", **{"class": "content-grid"})
    pages = []

    # מוצאים כל כותרת (h2/h3) וכל התוכן ששייך אליה עד הכותרת הבאה
    headings = soup.find_all(['h2', 'h3'])
    for heading in headings:
        page_div = soup.new_tag("div", **{"class": "page"})
        page_div.append(heading.extract())
        # אוספים את האחים (siblings) עד כותרת חדשה
        for sibling in heading.find_next_siblings():
            if sibling.name in ['h2', 'h3']:
                break
            page_div.append(sibling.extract())
        pages.append(page_div)

    # הוספת העמודים ל־Grid לפי הסדר
    for page_div in pages:
        grid_container.append(page_div)

    body_tag.append(grid_container)

    # 4) הוספת footer אם אין
    if not soup.find("div", {"class": "footer"}):
        footer_div = soup.new_tag("div", **{"class": "footer"})
        footer_div.string = "דוח זה נוצר באמצעות מערכת ניתוח SEC Filings."
        body_tag.append(footer_div)

    # 5) הסרת/עטיפת תגים ייחודיים של XBRL
    xbrl_tags = [
        'ix:header', 'ix:references', 'xbrli:context', 'xbrli:period',
        'xbrli:startDate', 'xbrli:endDate', 'xbrli:segment',
        'xbrli:unitNumerator', 'xbrli:divide'
    ]
    for tag_name in xbrl_tags:
        for el in soup.find_all(tag_name):
            el.unwrap()

    return

def extract_filing_date(soup: BeautifulSoup) -> Optional[str]:
    """
    Extracts the filing date from the HTML content.
    Looks for the pattern "For the Fiscal Year Ended <Month> <Day>, <Year>" or
    "For the quarterly period ended <Month> <Day>, <Year>".
    Returns the date string or None if not found.
    """
    patterns = [
    r"For the Fiscal Year Ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"For the quarterly period ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"For the Quarter Ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"For the period ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"For the year ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"As of\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"As of and for the year ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"As of and for the quarter ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Reported for the period ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Filed for the period ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Effective for the period ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"For the twelve months ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"For the three months ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"For the six months ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Ending on\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Commencing on\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Ending\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Starting\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"As at\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"As of\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"For the reporting period ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"For the month ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"For the calendar year ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"For the fiscal quarter ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"As of the end of the period\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"For the annual period ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"For the semiannual period ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"As of\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Through\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Date of earliest event reported\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Date of Report\s+\(Date of earliest event reported\)\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Period Covered\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"From\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})\s+to\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"As of\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"For the interim period ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"For the period from\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Reported on\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"For the transition period ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Date of issuance\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Filed on\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"For the period beginning\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Commencement date\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Expiration date\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Termination date\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Effective date\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"For the biennial period ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Period ending\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})",
    r"Filing date\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})"
]


    text = soup.get_text(" ", strip=True)
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return None

def extract_fiscal_year_ended(soup: BeautifulSoup) -> Optional[str]:
    """
    Extracts the fiscal year ended date from the HTML content.
    Looks for the pattern "For the Fiscal Year Ended <Month> <Day>, <Year>".
    Returns the date string or None if not found.
    """
    pattern = r"For the Fiscal Year Ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})"
    text = soup.get_text(" ", strip=True)
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return None

def extract_quarter(soup: BeautifulSoup) -> Optional[Tuple[str, str]]:
    """
    Extracts the quarter from the HTML content if applicable.
    Looks for the pattern "For the quarterly period ended <Month> <Day>, <Year>".
    Returns a tuple (quarter, fiscal_year_date) or None if not found.
    """
    pattern = r"For the quarterly period ended\s+([A-Za-z]+\s+\d{1,2},\s*\d{4})"
    text = soup.get_text(" ", strip=True)
    match = re.search(pattern, text)
    if match:
        quarter = "q" + str((datetime.strptime(match.group(1), "%B %d, %Y").month - 1) // 3 + 1)
        fiscal_year_date = match.group(1).strip()
        return quarter, fiscal_year_date
    return None

def create_unique_path(ticker: str, report_type: str, filing_date: str, quarter: Optional[str] = None) -> Tuple[str, str]:
    """
    יוצר נתיב ייחודי לפי סוג הדוח, שנה ותאריך ההגשה או רבעון (אם קיים).
    לדוגמה: 
    - "AAPL/10-K/2024/annual/AAPL_10-K_2024.html" 
    - "AAPL/10-Q/2024/q1/AAPL_10-Q_q1_2024.html"
    - "AAPL/8-K/2023/2023-06-30/AAPL_8-K_2023-06-30.html"

    :param ticker: סימול הסחר (למשל, "AAPL")
    :param report_type: סוג הדוח (למשל, "10-K", "8-K", "SC 13G", "SD", וכו')
    :param filing_date: תאריך ההגשה של הדוח (למשל, "June 30, 2023")
    :param quarter: רבעון הדוח אם קיים (למשל, "q1")
    :return: tuple של הנתיב לתיקייה והנתיב המלא לקובץ
    """
    try:
        # המרת מחרוזת התאריך לאובייקט datetime
        clean_date = datetime.strptime(filing_date, "%B %d, %Y")
        year = clean_date.year
        date_str = clean_date.strftime("%Y-%m-%d")
    except ValueError as ve:
        logger.error(f"Error parsing filing_date '{filing_date}': {ve}. Using 'Unknown_Date'.")
        year = "Unknown_Year"
        date_str = "Unknown_Date"

    if quarter:
        directory = f"{ticker.upper()}/{report_type.upper()}/{year}/{quarter}"
        filename = f"{ticker.upper()}_{report_type.upper()}_{quarter}_{year}.html"
    else:
        directory = f"{ticker.upper()}/{report_type.upper()}/{year}/{date_str}"
        filename = f"{ticker.upper()}_{report_type.upper()}_{date_str}.html"

    # יצירת הנתיב המלא
    dir_path = os.path.join(settings.BASE_DIR, 'scraper', 'saved_data', 'sec-edgar-filings', directory)
    os.makedirs(dir_path, exist_ok=True)
    full_path = os.path.join(dir_path, filename)

    logger.debug(f"Unique path created: {full_path}")
    return dir_path, full_path

def process_final_html(html_file_path: str, ticker: str, report_type: str) -> Tuple[str, Dict[str, str]]:
    """
    Processes the final HTML file:
    1. Extracts the filing date from the HTML.
    2. Checks if a filing for that date already exists.
    3. If not, archives the original, cleans, styles, and saves with a unique name.
    4. If exists, skips processing to avoid duplication.
    """
    try:
        logger.info("Processing final HTML file: %s", html_file_path)

        # Step 1: Load and parse the original HTML
        with open(html_file_path, 'r', encoding='utf-8') as file:
            original_html_content = file.read()

        soup = BeautifulSoup(original_html_content, 'html.parser')
        logger.debug("HTML content loaded for checking filing date.")

        # Step 2: Extract filing date
        filing_date = extract_filing_date(soup)
        if not filing_date:
            logger.warning("No Filing Date found in file. Using current date for directory structure.")
            filing_date = datetime.now().strftime("%B %d, %Y")

        logger.debug(f"Filing Date extracted: {filing_date}")

        # Step 3: Extract fiscal year ended and quarter if applicable
        fiscal_year_date = extract_fiscal_year_ended(soup)
        quarter_info = extract_quarter(soup) if report_type.lower() == '10-q' else None

        if quarter_info:
            quarter, fiscal_year_date = quarter_info
            logger.debug(f"Quarter extracted: {quarter}, Fiscal Year Ended: {fiscal_year_date}")
        elif fiscal_year_date:
            quarter = None
            logger.debug(f"Fiscal Year Ended extracted: {fiscal_year_date}")
        else:
            quarter = None
            logger.debug("No Fiscal Year Ended information found.")

        # Step 4: Create unique path based on filing date
        dir_path, new_path_full = create_unique_path(ticker, report_type, filing_date, quarter)

        if os.path.exists(new_path_full):
            logger.info(f"Skipping processing as file already exists: {new_path_full}")
            return new_path_full, {"status": "skip", "reason": "File already exists"}

        # Step 5: Archive the original file
        archive_dir = os.path.join(settings.BASE_DIR, 'scraper', 'saved_data', 'archived_html')
        os.makedirs(archive_dir, exist_ok=True)
        backup_file_path = os.path.join(archive_dir, os.path.basename(html_file_path))
        shutil.move(html_file_path, backup_file_path)
        logger.info("Original HTML file moved to archive: %s", backup_file_path)

        # Step 6: Remove images and add custom styling
        for img_tag in soup.find_all('img'):
            logger.debug("Removing <img> tag: %s", img_tag)
            img_tag.decompose()

        _insert_custom_style(soup)

        # Step 7: Save the styled HTML with the unique filename in the new directory
        with open(new_path_full, 'w', encoding='utf-8') as out_file:
            out_file.write(str(soup))
        logger.info("New styled HTML file created with unique name: %s", new_path_full)

        return new_path_full, {"status": "processed", "file": new_path_full}

    except Exception as e:
        logger.error("Error processing final HTML file: %s", e)
        raise
def create_html_without_images(final_html_file_path: str):
    """
    פונקציה שיוצרת קובץ HTML "נקי מתמונות" (ולא alt) **באותו השם**
    + מוסיפה לו עיצוב מותאם.
    תוך העברה של הקובץ הקיים לארכיון.
    """
    logger.info("Creating a new HTML file without images from: %s", final_html_file_path)
    try:
        # Define archive directory
        archive_dir = os.path.join(settings.BASE_DIR, 'scraper', 'saved_data', 'archived_html')
        os.makedirs(archive_dir, exist_ok=True)

        # Build backup file path
        backup_file_path = os.path.join(archive_dir, os.path.basename(final_html_file_path))

        # Move the current file to archive
        shutil.move(final_html_file_path, backup_file_path)
        logger.info("Moved original file to archive: %s", backup_file_path)

        # Read the file from archive
        with open(backup_file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')

        # Remove all <img> tags
        img_tags = soup.find_all('img')
        for img_tag in img_tags:
            logger.debug("Removing <img> tag: %s", img_tag)
            img_tag.decompose()

        # Remove 'alt' attribute from all tags
        for tag in soup.find_all():
            if tag.has_attr('alt'):
                logger.debug("Removing 'alt' attribute from tag: %s", tag)
                del tag['alt']

        # Add custom styling
        _insert_custom_style(soup)

        # Write the cleaned HTML back to the original path
        with open(final_html_file_path, 'w', encoding='utf-8') as out_file:
            out_file.write(str(soup))

        logger.info("New HTML file created without images and 'alt', including styling: %s", final_html_file_path)
        return final_html_file_path

    except Exception as e:
        logger.error("Error removing images from file %s: %s", final_html_file_path, e)
        raise

def process_downloaded_files(ticker: str, report_type: str):
    """
    מעבד את כל הקבצים שהורדו: שינוי שמות, העברה וניקוי קבצי HTML.
    מוודא ששום קובץ קיים לא יוחלף או יוסר במהלך העיבוד.
    """
    base_path = os.path.join(settings.BASE_DIR, 'scraper', 'saved_data', 'sec-edgar-filings', ticker.upper(), report_type.upper())
    filings = glob.glob(os.path.join(base_path, '*'))
    filings.reverse()  # עיבוד התיקיות מהחדשות ליותר ישנות
    logger.info("התחלת עיבוד קבצים שהורדו.")

    if filings:
        for filing_path in filings:
            # לדלג על תיקיות שכבר מתחילות ב-FY או תיקיות סדריות
            report_subdir = os.path.basename(filing_path)
            if report_subdir.startswith('FY') or re.match(r'^\d{9}-\d{2}-\d{6}$', report_subdir):
                logger.info("דלג על תיקיה: %s", filing_path)
                continue

            logger.info("עיבוד תיקיית דוחות: %s", filing_path)

            # שלב 1: שינוי שמות הקבצים בתיקיה
            find_and_rename_files(filing_path)

            # שלב 2: העברת קבצים לתיקיית הדוחות הראשית כדי למנוע תיקיות מקוננות
            move_files_to_parent(filing_path)

            # שלב 3: עיבוד כל קובץ HTML בתיקיית הדוחות
            for root, dirs, files in os.walk(filing_path):
                # להסיר תיקיות שלא רלוונטיות
                dirs[:] = [d for d in dirs if not d.startswith('FY') and not re.match(r'^\d{9}-\d{2}-\d{6}$', d)]
                for file in files:
                    if file.endswith('.html'):
                        html_file_path = os.path.join(root, file)
                        logger.info("עיבוד קובץ HTML: %s", html_file_path)
                        try:
                            # עיבוד קובץ ה-HTML
                            new_html_file, extracted_data = process_final_html(html_file_path, ticker, report_type)
                            logger.info("קובץ HTML עובד: %s", new_html_file)
                            logger.debug("נתונים שהופקו: %s", extracted_data)
                        except Exception as e:
                            logger.error("שגיאה בעיבוד קובץ HTML %s: %s", html_file_path, e)
                            continue

    logger.info("סיום עיבוד כל הקבצים שהורדו.")

def fetch_sec_fillings(ticker: str, report_type: str, after_date: str, before_date: str, include_amends: bool = False) -> Dict[str, str]:
    """
    מוריד דוחות SEC עבור סימול סחר מסוים וטווח תאריכים, מתעלם מקבצים קיימים עבור אותה תאריך הגשה.
    
    :param ticker: סימול הסחר (למשל, "AAPL")
    :param report_type: סוג הדוח (למשל, "10-K", "8-K", "SC 13G", "SD", וכו')
    :param after_date: תאריך התחלה בפורמט "YYYY-MM-DD"
    :param before_date: תאריך סיום בפורמט "YYYY-MM-DD"
    :param include_amends: האם לכלול תיקוני דוחות (למשל, "8-K/A"). ברירת מחדל: False
    :return: מילון עם סטטוס והנתיב לקובץ שהורד או קיים
    """
    start_time = time.time()
    try:
        logger.info("Fetching SEC filings for ticker: %s and report_type: %s", ticker, report_type)

        # המרת מחרוזות התאריך לאובייקטים datetime
        after_date_obj = datetime.strptime(after_date, "%Y-%m-%d")
        before_date_obj = datetime.strptime(before_date, "%Y-%m-%d")

        # הגדרת ספריית השמירה
        save_dir = os.path.join(settings.BASE_DIR, 'scraper', 'saved_data', 'sec-edgar-filings', ticker.upper(), report_type.upper())
        os.makedirs(save_dir, exist_ok=True)
        logger.info("Save directory: %s", save_dir)

        # בדיקת קבצים קיימים בספרייה
        existing_files = glob.glob(os.path.join(save_dir, '*/*.html'))
        logger.info("Checking existing files for %s filings: %s", report_type, existing_files)

        # אימות אם תאריך הגשה מבוקש כבר קיים
        for file_path in existing_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')
                    filing_date = extract_filing_date(soup)
                    if filing_date:
                        filing_date_obj = datetime.strptime(filing_date, "%B %d, %Y")
                        if after_date_obj <= filing_date_obj <= before_date_obj:
                            logger.info("Filing already exists for filing date: %s. Skipping download.", filing_date)
                            return {"status": "exists", "file": file_path}
            except Exception as e:
                logger.error("Error reading file %s: %s", file_path, e)
                continue

        # אתחול Downloader
        try:
            dl = Downloader("LL", "news@gmail.com", save_dir)
            logger.info("Downloader initialized successfully.")
        except Exception as e:
            logger.error("Downloader initialization failed: %s", e)
            raise

        # ביצוע ההורדה בפועל
        try:
            num_filings = dl.get(
                report_type,
                ticker,
                limit=100,  # שנה למספר קבצים שברצונך להוריד. 100 הוא מספר דוגמה.
                include_amends=include_amends,
                after=after_date_obj.strftime("%Y-%m-%d"),
                before=before_date_obj.strftime("%Y-%m-%d"),
                download_details=True
            )
            logger.info("Number of filings downloaded: %s", num_filings)
        except Exception as e:
            logger.error("Downloading filings failed: %s", e)
            raise

        # עיבוד הקבצים שהורדו
        filing_paths = glob.glob(os.path.join(save_dir, '*/*'))
        logger.info("Filing paths found: %s", filing_paths)

        if filing_paths:
            for filing_path in filing_paths:
                logger.info("Processing filing path: %s", filing_path)
                process_downloaded_files(ticker, report_type)

            # בדיקה לקבצי HTML מעובדים
            processed_html_files = glob.glob(os.path.join(save_dir, '*/*/*.html'))
            if processed_html_files:
                # החזרת כל הקבצים המעובדים
                return {"status": "success", "files": processed_html_files}  # type: ignore
            else:
                logger.error("No HTML file found in the processed reports.")
                raise FileNotFoundError("No HTML file found in the processed reports.")
        else:
            logger.error("No reports found after downloading.")
            raise FileNotFoundError("No reports found after downloading.")

    except Exception as e:
        logger.error("An error occurred in fetch_sec_fillings: %s", e)
        raise
    finally:
        end_time = time.time()
        logger.process_time(f"Runtime of the fetch_sec_fillings function is {end_time - start_time} seconds")  # type: ignore
