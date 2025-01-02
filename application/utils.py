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
    }
))

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

HTML_FILES_NAME = ["primary-document.html", "full-submission.txt"]


start = time.time()
def find_and_rename_files(folder_path):
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
                    ticker_dir = os.path.basename(
                        os.path.dirname(
                            os.path.dirname(dirpath)
                        )
                    )
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

def move_files_to_parent(folder_path):
    """
    פונקציה המעבירה קבצי html/txt מתתי־תיקיות אל התיקייה שמעליהם,
    ואז מוחקת תתי־תיקיות ריקות.
    """
    logger.info("Moving files to parent folder for path: %s", folder_path)
    try:
        for dirpath, _, files in os.walk(folder_path, topdown=False):
            for file in files:
                if any(file.endswith(ext) for ext in ["html", "txt"]):
                    source_path = os.path.join(dirpath, file)
                    destination_path = os.path.join(os.path.dirname(dirpath), file)
                    logger.info("Moving file from %s to %s", source_path, destination_path)
                    os.rename(source_path, destination_path)

                    # אם התיקייה התרוקנה בסיום - מוחקים אותה
                    if not os.listdir(dirpath):
                        logger.info("Removing empty directory: %s", dirpath)
                        os.rmdir(dirpath)
        logger.info("Finished moving files for path: %s", folder_path)
    except Exception as e:
        logger.error("Error during file moving for path %s: %s", folder_path, e)
        raise


def _insert_custom_style(soup: BeautifulSoup):
    """
    פונקציה עזר להוספת בלוק עיצוב (CSS) אל ה-HTML, 
    בכדי להמחיש שינוי ויזואלי לעומת התוכן המקורי.
    """
    style_content = """
    <style>
    body {
        background-color: #f9f9f9;
        color: #333;
        font-family: Arial, sans-serif;
        margin: 20px;
    }
    h1, h2, h3 {
        color: #4b75c9; /* כחול נעים */
        font-weight: bold;
    }
    p {
        line-height: 1.6;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        margin: 15px 0;
    }
    th, td {
        border: 1px solid #ccc;
        padding: 8px;
    }
    th {
        background-color: #ddd;
    }
    .custom-header {
        background-color: #4b75c9;
        color: #fff;
        padding: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .custom-header h1 {
        margin: 0;
    }
    </style>
    """

    # נוודא שיש תגית <head>, ואם לא - ניצור אותה
    if not soup.head:
        # אם אין head בכלל, ניצור חדש כילד ראשון ב-html
        if soup.html:
            head_tag = soup.new_tag("head")
            soup.html.insert(0, head_tag)
        else:
            # אם אין גם <html>, ניצור אחד
            html_tag = soup.new_tag("html")
            soup.insert(0, html_tag)
            head_tag = soup.new_tag("head")
            html_tag.insert(0, head_tag)
    else:
        head_tag = soup.head

    # נוסיף את ה-style לתגית head
    head_tag.append(BeautifulSoup(style_content, "html.parser"))

    # כדוגמה, נוסיף כותרת עליונה (דיוויד) בגוף הדף
    # אפשר לשפר ולעצב לפי רצונך
    if soup.body:
        header_div = soup.new_tag("div", **{"class": "custom-header"})
        header_h1 = soup.new_tag("h1")
        header_h1.string = "מסמך מעוצב לדוגמה"
        header_div.append(header_h1)
        # נכניס את ה-div לפני כל תוכן אחר שב-body
        soup.body.insert(0, header_div)
    else:
        # אם אין body, ניצור תגית body
        body_tag = soup.new_tag("body")
        soup.append(body_tag)
        header_div = soup.new_tag("div", **{"class": "custom-header"})
        header_h1 = soup.new_tag("h1")
        header_h1.string = "מסמך מעוצב לדוגמה"
        header_div.append(header_h1)
        body_tag.insert(0, header_div)


def process_final_html(html_file_path):
    """
    מעבד קובץ HTML סופי: 
    1. מעביר את הקובץ המקורי לתיקיית ארכיון (archived_html).
    2. פותח אותו משם, מסיר תמונות, מוסיף עיצוב מותאם, ומייצר קובץ באותו השם במיקומו המקורי.
    3. מחזיר את המסלול של הקובץ החדש (אותו שם), וכן נתונים שהוצאו (אופציונלי).
    """
    try:
        logger.info("Processing final HTML file: %s", html_file_path)

        # 1) הגדרת תיקיית ארכיון (ניתן להתאים לפי הצורך)
        archive_dir = os.path.join(settings.BASE_DIR, 'scraper', 'saved_data', 'archived_html')
        os.makedirs(archive_dir, exist_ok=True)

        # בניית נתיב גיבוי
        backup_file_path = os.path.join(archive_dir, os.path.basename(html_file_path))

        # העברת הקובץ הנוכחי לארכיון
        shutil.move(html_file_path, backup_file_path)
        logger.info("Original HTML file moved to archive: %s", backup_file_path)

        # 2) קריאת הקובץ מהארכיון
        with open(backup_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, 'html.parser')
        logger.debug("HTML content loaded and parsed successfully.")

        # הסרת תגיות <img>
        for img_tag in soup.find_all('img'):
            logger.debug("Removing <img> tag: %s", img_tag)
            img_tag.decompose()

        # הוספת עיצוב מותאם משלך
        _insert_custom_style(soup)

        # דוגמה: שליפת כותרות וטבלאות (אופציונלי)
        extracted_data = {
            "headings": [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])],
            "tables": [str(table) for table in soup.find_all('table')],
        }
        logger.debug("Extracted data: %s", extracted_data)

        # 3) יצירת קובץ חדש באותו שם ומיקום מקורי (html_file_path)
        with open(html_file_path, 'w', encoding='utf-8') as out_file:
            out_file.write(str(soup))
        logger.info("New styled HTML file created with the same name: %s", html_file_path)

        return html_file_path, extracted_data

    except Exception as e:
        logger.error("Error processing final HTML file: %s", e)
        raise


def create_html_without_images(final_html_file_path):
    """
    פונקציה שיוצרת קובץ HTML "נקי מתמונות" (וללא alt) **באותו השם**
    + מוסיפה לו עיצוב מותאם.
    תוך העברה של הקובץ הקיים לארכיון.
    """
    logger.info("יוצר קובץ חדש ללא תמונות מתוך: %s", final_html_file_path)
    try:
        # הגדרת תיקיית ארכיון
        archive_dir = os.path.join(settings.BASE_DIR, 'scraper', 'saved_data', 'archived_html')
        os.makedirs(archive_dir, exist_ok=True)

        # בניית נתיב גיבוי
        backup_file_path = os.path.join(archive_dir, os.path.basename(final_html_file_path))

        # העברת הקובץ הנוכחי לארכיון
        shutil.move(final_html_file_path, backup_file_path)
        logger.info("Moved original file to archive: %s", backup_file_path)

        # קריאת הקובץ מהארכיון
        with open(backup_file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, 'html.parser')
        
        # הסרת כל תגיות <img>
        img_tags = soup.find_all('img')
        for img_tag in img_tags:
            logger.debug("מסיר תגית img: %s", img_tag)
            img_tag.decompose()

        # הסרת מאפיין alt מכל התגיות
        for tag in soup.find_all():
            if tag.has_attr('alt'):
                logger.debug("מסיר את מאפיין 'alt' מתוך התגית: %s", tag)
                del tag['alt']

        # הוספת עיצוב מותאם
        _insert_custom_style(soup)

        # כתיבה של ה-HTML הנקי לאותו שם וקובץ
        with open(final_html_file_path, 'w', encoding='utf-8') as out_file:
            out_file.write(str(soup))
        
        logger.info("קובץ חדש (אותו שם) נוצר ללא תמונות ו-alt, כולל עיצוב: %s", final_html_file_path)
        return final_html_file_path

    except Exception as e:
        logger.error("שגיאה בעת הסרת תמונות מהקובץ %s: %s", final_html_file_path, e)
        raise


def process_downloaded_files():
    """
    עיבוד כל הקבצים שהורדו: שינוי שמות, העברה, ועיבוד/ניקוי קבצי HTML.
    """
    base_path = os.path.join(settings.BASE_DIR, 'scraper', 'saved_data', 'sec-edgar-filings')
    # אוספים את כל התיקיות ברמה העליונה
    folders = glob.glob(f"{base_path}/*")
    # הופכים את הסדר לפי הצורך
    folders.reverse()
    logger.info("Starting to process downloaded files.")

    if folders:
        # תחילה: שינוי שמות הקבצים בכל תיקייה
        for folder in folders:
            logger.info("Processing folder: %s", folder)
            find_and_rename_files(folder)

        # לאחר ששינינו שמות, מזיזים את הקבצים למעלה
        move_files_to_parent(base_path)

        # עכשיו מחפשים קבצי HTML באופן רקורסיבי בכל תיקייה, ומעבדים אותם
        for folder in folders:
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.endswith('.html'):
                        html_file_path = os.path.join(root, file)
                        logger.info("Processing final HTML file: %s", html_file_path)
                        
                        # שלב ראשון: עיבוד רגיל (הסרת img + עיצוב) + יצירת קובץ חדש זהה בשם
                        new_html_file, extracted_data = process_final_html(html_file_path)
                        logger.info("Processed HTML file: %s", new_html_file)
                        logger.debug("Extracted data: %s", extracted_data)

                        # אם תרצה בנוסף ליצור גירסה ללא alt (לגמרי "נקייה"), הסר את הסימון:
                        # new_html_no_imgs = create_html_without_images(new_html_file)
                        # logger.info("New HTML file without images/alt created: %s", new_html_no_imgs)

    logger.info("Finished processing all downloaded files.")


def fetch_sec_fillings(ticker: str, report_type: str, after_date: str, before_date: str):
    """
    הורדת דיווחים (filings) ל-SEC עבור ticker מסוים וטווח תאריכים.
    """
    start = time.time()  # Start time measurement
    try:
        logger.info("Fetching SEC filings for ticker: %s and report_type: %s", ticker, report_type)

        # המרת המחרוזות של התאריכים לאובייקטים של datetime
        after_date_obj = datetime.strptime(after_date, "%Y-%m-%d")
        before_date_obj = datetime.strptime(before_date, "%Y-%m-%d")

        # הגדרת תיקיית השמירה
        save_dir = os.path.join(settings.BASE_DIR, 'scraper', 'saved_data')
        logger.info("Save directory: %s", save_dir)

        # אתחול ה-Downloader
        try:
            dl = Downloader("LL", "news@gmail.com", save_dir)
            logger.info("Downloader initialized successfully.")
        except Exception as e:
            logger.error("Downloader initialization failed: %s", e)
            raise

        # הורדת הקבצים בפועל
        try:
            num_filings = dl.get(
                report_type,
                ticker,
                limit=1,
                include_amends=True,
                after=after_date_obj.strftime("%Y-%m-%d"),
                before=before_date_obj.strftime("%Y-%m-%d"),
                download_details=True
            )
            logger.info("Number of filings downloaded: %s", num_filings)
        except Exception as e:
            logger.error("Downloading filings failed: %s", e)
            raise

        # מציאת הנתיבים של התיקיות שהורדו
        filing_paths = glob.glob(
            os.path.join(save_dir, 'sec-edgar-filings', ticker, report_type)
        )
        logger.info("Filing paths found: %s", filing_paths)

        if filing_paths:
            filing_path = filing_paths[0]
            logger.info("Processing filing path: %s", filing_path)

            # עיבוד כל הקבצים שהורדו (כולל יצירת HTML מעובד)
            process_downloaded_files()

            # בדיקה האם יש עדיין קבצי HTML בתיקייה (החדשים שנוצרו)
            html_files = glob.glob(os.path.join(filing_path, '*.html'))
            logger.info("HTML files found: %s", html_files)

            if html_files:
                html_file_path = html_files[0]
                logger.info("HTML file path: %s", html_file_path)
                return os.path.relpath(html_file_path, settings.BASE_DIR)
            else:
                logger.error("No HTML file found in the report.")
                raise FileNotFoundError("No HTML file found in the report.")

        else:
            logger.error("No report found.")
            raise FileNotFoundError("No report found.")

    except Exception as e:
        logger.error("An error occurred in fetch_sec_fillings: %s", e)
        raise
    finally:
        end = time.time()  # End time measurement
        logger.warning(f"Runtime of the fetch_sec_fillings function is {end - start} seconds")

end = time.time()   

logger.warning(f"Runtime of the program is {end - start}")

