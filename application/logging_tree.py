# logging_tree.py

import pandas as pd
import re
from datetime import datetime
import networkx as nx

# נתיב לקובץ הלוגים שלך
LOG_FILE_PATH ='/Users/elmaliahmac/Documents/secFilling_API/logfile.log'

# תבנית לפריסת הלוגים
log_pattern = re.compile(
    r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+) - (?P<level>\w+) - (?P<message>.*)'
)

# פונקציה לקריאת הלוגים ופריסתם
def parse_logs(log_file):
    logs = []
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            match = log_pattern.match(line)
            if match:
                log_entry = match.groupdict()
                # המרת מחרוזת התאריך לאובייקט datetime
                log_entry['timestamp'] = datetime.strptime(log_entry['timestamp'], '%Y-%m-%d %H:%M:%S,%f')
                logs.append(log_entry)
    df = pd.DataFrame(logs)
    return df

# פונקציה לבניית העץ מהלוגים
def build_tree(df):
    G = nx.DiGraph()
    parent_stack = []
    
    for index, row in df.iterrows():
        message = row['message']
        timestamp = row['timestamp']
        level = row['level']
        
        # זיהוי התחלת תהליך
        if 'Fetching SEC filings' in message:
            current_step = 'Fetch SEC filings'
            G.add_node(current_step, timestamp=timestamp, level=level)
            parent_stack = [current_step]
        
        elif 'Save directory' in message:
            current_step = 'Save directory'
            G.add_node(current_step, timestamp=timestamp, level=level)
            if parent_stack:
                G.add_edge(parent_stack[-1], current_step)
                parent_stack.append(current_step)
        
        elif 'Checking existing files' in message:
            current_step = 'Check existing files'
            G.add_node(current_step, timestamp=timestamp, level=level)
            if parent_stack:
                G.add_edge(parent_stack[-1], current_step)
                parent_stack.append(current_step)
        
        elif 'Downloader initialized successfully' in message:
            current_step = 'Initialize Downloader'
            G.add_node(current_step, timestamp=timestamp, level=level)
            if parent_stack:
                G.add_edge(parent_stack[-1], current_step)
                parent_stack.append(current_step)
        
        elif 'Number of filings downloaded' in message:
            current_step = 'Download Filings'
            G.add_node(current_step, timestamp=timestamp, level=level)
            if parent_stack:
                G.add_edge(parent_stack[-1], current_step)
                parent_stack.append(current_step)
        
        elif 'Filing paths found' in message:
            current_step = 'Find Filing Paths'
            G.add_node(current_step, timestamp=timestamp, level=level)
            if parent_stack:
                G.add_edge(parent_stack[-1], current_step)
                parent_stack.append(current_step)
        
        elif 'Processing filing path' in message:
            current_step = 'Process Filing Path'
            G.add_node(current_step, timestamp=timestamp, level=level)
            if parent_stack:
                G.add_edge(parent_stack[-1], current_step)
                parent_stack.append(current_step)
        
        elif 'Started processing folder' in message:
            current_step = 'Start Processing Folder'
            G.add_node(current_step, timestamp=timestamp, level=level)
            if parent_stack:
                G.add_edge(parent_stack[-1], current_step)
                parent_stack.append(current_step)
        
        elif 'Finished processing folder' in message:
            current_step = 'Finish Processing Folder'
            G.add_node(current_step, timestamp=timestamp, level=level)
            if len(parent_stack) > 1:
                parent_stack.pop()
                G.add_edge(parent_stack[-1], current_step)
                parent_stack.append(current_step)
        
        elif 'Moving files to parent folder' in message:
            current_step = 'Move Files to Parent Folder'
            G.add_node(current_step, timestamp=timestamp, level=level)
            if parent_stack:
                G.add_edge(parent_stack[-1], current_step)
                parent_stack.append(current_step)
        
        elif 'Processing final HTML file' in message:
            current_step = 'Process Final HTML File'
            G.add_node(current_step, timestamp=timestamp, level=level)
            if parent_stack:
                G.add_edge(parent_stack[-1], current_step)
                parent_stack.append(current_step)
        
        elif 'Runtime of the fetch_sec_fillings function' in message:
            current_step = 'Log Runtime'
            G.add_node(current_step, timestamp=timestamp, level=level)
            if parent_stack:
                G.add_edge(parent_stack[-1], current_step)
                parent_stack.append(current_step)
        
        # ניתן להוסיף תנאים נוספים לפי הצורך
    
    return G

# פונקציה ליצירת DataFrame
def get_log_dataframe():
    df = parse_logs(LOG_FILE_PATH)
    return df

# פונקציה לבניית העץ
def get_graph():
    df = get_log_dataframe()
    G = build_tree(df)
    return G

# פונקציה לדוגמה להדפסת העץ
def print_tree(G):
    for edge in G.edges():
        print(f"{edge[0]} -> {edge[1]}")

# אם תרצה לבדוק את הקוד:
if __name__ == "__main__":
    G = get_graph()
    print_tree(G)
