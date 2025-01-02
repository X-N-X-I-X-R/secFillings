## README – A Full Process for Fetching and Processing SEC Filings

### General Background
When downloading filings from the U.S. Securities and Exchange Commission (SEC) via the EDGAR system, one typically ends up with a complex hierarchy of folders. These often have serial-like identifiers (e.g., `0000320193-20-000096`), and the main files might have generic names (such as `primary-document.html`). This structure complicates integration with external tools—especially on the Front-End or within data analytics systems, which expect a consistent and uniform file layout.

This project provides an end-to-end solution: from fetching SEC filings to transforming the raw files into readable, clean, and styled documents—all in **2.5 to 3.3 seconds** (in most cases). The resulting output is easily integrated and displayed in any system or application.

---

## Main Components and Workflow

### 1. Fetching Step: `fetch_sec_fillings`
This function is the **central entry point** of the entire process:

1. It uses the `sec_edgar_downloader` library (via a call to `dl.get(...)`) to download filings based on the specified parameters (ticker, report type, date range, etc.).  
2. The downloaded files are then stored in a folder structure similar to:
   ```
   /scraper/saved_data/sec-edgar-filings/<TICKER>/<REPORT_TYPE>/<SERIAL>/
   ```
   where `<SERIAL>` is a unique identifier (UUID/Serial) provided by EDGAR.  
3. Once the download finishes, the function calls `process_downloaded_files()`, which organizes, renames, and prepares the files for readability.  
4. Finally, `fetch_sec_fillings` locates the processed HTML file and returns its path so it can be displayed or further analyzed.

### 2. Renaming Step: `find_and_rename_files`
- **Challenge**: Within each `<SERIAL>` folder, files like `primary-document.html` and `full-submission.txt` might not indicate which ticker or filing type they belong to.  
- **Solution**: This function scans all subfolders recursively and:
  - Identifies files named `primary-document.html` or `full-submission.txt`.  
  - Extracts the ticker (e.g., `AAPL`) and the report type (e.g., `10-K`) from the folder path.  
  - Renames the file to a standardized format, such as `AAPL_10-K.html` (instead of `primary-document.html`), immediately clarifying its content.

### 3. Moving Files Upward: `move_files_to_parent`
- **Problem**: After renaming, files are still “buried” within subfolders (e.g., `0000320193-20-000096`).  
- **Mechanism**:  
  - This function traverses folders with `topdown=False` and moves all `.html` or `.txt` files to the parent folder (e.g., `AAPL/10-K`).  
  - If the subfolder becomes empty, it is deleted—leading to a simpler, more accessible structure:
    ```
    /scraper/saved_data/sec-edgar-filings/AAPL/10-K/AAPL_10-K.html
    /scraper/saved_data/sec-edgar-filings/AAPL/10-K/AAPL_10-K.txt
    ```

### 4. Final Processing Stage: `process_final_html`
1. **Archiving the File**: Before processing the main HTML file, it’s automatically moved to an `archived_html` directory to preserve a raw copy.  
2. **Handling with BeautifulSoup**: After loading the file with `BeautifulSoup`, the following actions take place:
   - **Removing Images**: All `<img>` tags are removed as needed.  
   - **Adding Custom Styling**: The `_insert_custom_style` function embeds basic CSS for improved appearance (background color, highlighted headings, table formatting, etc.).  
   - **Writing Back**: The result is saved under the same original path (e.g., `AAPL_10-K.html`), allowing users to retain both clarity and consistent naming.  
3. **Returning Data**: This function also returns an `extracted_data` object (e.g., a list of headings, tables) should you need further analysis.

### 5. Additional Processing – `create_html_without_images` (Optional)
This extended version removes all `alt` attributes and other visual elements for maximum cleanliness:
- Similar to `process_final_html`, it uses `BeautifulSoup` to remove undesired tags and attributes, then writes the styled document back under the same name.

### 6. Orchestrating the Entire Process: `process_downloaded_files`
- This **master** function calls, in sequence:
  1. `find_and_rename_files` – to rename the files.  
  2. `move_files_to_parent` – to move them out of the deeper folders.  
  3. A loop over all resulting `.html` files, calling `process_final_html` for each.  
- As a result, every SEC folder that was downloaded is fully processed and ready for end users.

---

## Key Advantages

- **Consistency and Transparency**: Instead of dealing with serial folder names and generic file titles, you get structured naming (`<TICKER>_<REPORT_TYPE>.html`).  
- **Time Efficiency**: Thanks to an automated mechanism and effective cleaning, you get a file ready for immediate use in about **2.5 to 3.3 seconds** (depending on network load and file size).  
- **Archiving the Original**: Every raw file is archived before modification, ensuring a pristine backup for audits or further processing.  
- **Full Front-End Compatibility**: At the end, you can embed the file in an `<iframe>`, serve it via an API, or convert it to PDF. Since the file name and location are consistent, the client/Front-End does not need to guess the content’s path.

---

## Simple Flowchart

```
fetch_sec_fillings
  │
  ├── Downloader.get(...)      → Download from EDGAR (SEC)
  ├── process_downloaded_files → End-to-end file processing
  │      ├── find_and_rename_files  
  │      ├── move_files_to_parent
  │      └── for each *.html → process_final_html
  └── Locate and return the relative path of the final file
```

---

## Summary
This system resolves the inherent complexity of SEC download structures—generic file names, serial folder identifiers, and deep directory layers—turning them into a clear, accessible, and readable set of files. Within a few seconds, any “noise” (e.g., unnecessary images) is removed and basic styling is applied, producing a well-structured document ready for analysis, display, or internal archiving.

If you need a reliable and fast mechanism for managing and distributing SEC filings, this solution provides an entire processing chain—from initial download through presentation. It **significantly reduces** the time and complexity involved in EDGAR integration and **delivers** clean, styled documents suitable for any work environment.