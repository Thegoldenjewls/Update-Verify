from datetime import datetime, timedelta
from collections import defaultdict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Read the content of message.txt
file_path = 'message.txt'  
with open(file_path, 'r') as file:
    lines = file.readlines()

# Parse entries to extract dates and image identifiers
backups = defaultdict(list)
for line in lines:
    line = line.strip()
    if not line:  # Skip blank lines
        continue
    parts = line.split('/')
    if len(parts) > 1:
        image_info = parts[-1]
        date_part = image_info[:6]
        if date_part.isdigit() and len(date_part) == 6:  # Check for valid date format
            try:
                date = datetime.strptime(date_part, "%y%m%d")  # Parse the date
                image_id = image_info.split('_')[-1]  # Extract image identifier
                backups[image_id].append(date_part)
            except ValueError as e:
                print(f"Invalid date format: {date_part} in line {line}")
        else:
            print(f"Skipping invalid date: {date_part} in line {line}")

# Convert dates to datetime objects and sort for each image
for image_id in backups:
    backups[image_id] = sorted([datetime.strptime(date, "%y%m%d") for date in backups[image_id]])

# Analyze last updates for each image
backup_analysis = {}
current_date = datetime.now()
for image_id, dates in backups.items():
    if dates:
        last_update = dates[-1]  # Last update date
        days_since_last_backup = (current_date - last_update).days
        backup_analysis[image_id] = {
            "last_update": last_update.strftime("%y%m%d"),
            "days_since_last_backup": days_since_last_backup,
        }

# Generate the email body HTML 
email_body = """
<html>
<head>
    <style>
        .highlight { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Backup Verification Report</h1>
    <p>Below is the analysis of backups:</p>
    <ul>
"""

for image_id, info in backup_analysis.items():
    email_body += f"<li><strong>Image:</strong> {image_id}<br>"
    email_body += f"  <strong>Last Update:</strong> {info['last_update']}<br>"
    
    # Highlight in red if last backup exceeds 2 days
    if info['days_since_last_backup'] > 2:
        email_body += f"  <strong>Days Since Last Backup:</strong> <span class='highlight'>{info['days_since_last_backup']} days</span><br>"
    else:
        email_body += f"  <strong>Days Since Last Backup:</strong> {info['days_since_last_backup']} days<br>"


email_body += """
    </ul>
</body>
</html>
"""

# Email configuration
sender_email = "Bfalerts2024@gmail.com"  
receiver_email = "julianlucoronado@gmail.com"
email_password = "wjsg nfjh yiej jdcz" 

# Compose the email
subject = "Backup Verification Report"
msg = MIMEMultipart("alternative")
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = subject

# Attach the HTML content
msg.attach(MIMEText(email_body, 'html'))

# Send the email
try:
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, email_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
    print("Email sent successfully!")
except Exception as e:
    print(f"Error sending email: {e}")
