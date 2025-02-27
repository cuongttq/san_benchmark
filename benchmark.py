import subprocess
import json
import csv
import os
import pandas as pd
import requests
from datetime import datetime

# ==== TELEGRAM BOT CONFIGURATION ====
TELEGRAM_BOT_TOKEN = ""
CHAT_ID = ""

# ==== TEST CASES FOR FIO ====
fio_tests = [
    {"name": "4k-100R", "rwmixread": "100", "bs": "4k", "size": "1G", "iodepth": 64},
    {"name": "4k-100W", "rwmixread": "0", "bs": "4k", "size": "1G", "iodepth": 64},
    {"name": "4k-30R-70W", "rwmixread": "30", "bs": "4k", "size": "1G", "iodepth": 64},
    {"name": "4k-50R-50W", "rwmixread": "50", "bs": "4k", "size": "1G", "iodepth": 64},
    {"name": "4k-70R-30W", "rwmixread": "70", "bs": "4k", "size": "1G", "iodepth": 64},
    {"name": "128k-100R", "rwmixread": "100", "bs": "128k", "size": "1G", "iodepth": 64},
    {"name": "128k-100W", "rwmixread": "0", "bs": "128k", "size": "1G", "iodepth": 64},
    {"name": "128k-30R-70W", "rwmixread": "30", "bs": "128k", "size": "1G", "iodepth": 64},
    {"name": "128k-50R-50W", "rwmixread": "50", "bs": "128k", "size": "1G", "iodepth": 64},
    {"name": "128k-70R-30W", "rwmixread": "70", "bs": "128k", "size": "1G", "iodepth": 64},
    {"name": "1024k-100R", "rwmixread": "100", "bs": "1024k", "size": "1G", "iodepth": 64},
    {"name": "1024k-100W", "rwmixread": "0", "bs": "1024k", "size": "1G", "iodepth": 64},
    {"name": "1024k-30R-70W", "rwmixread": "30", "bs": "1024k", "size": "1G", "iodepth": 64},
    {"name": "1024k-50R-50W", "rwmixread": "50", "bs": "1024k", "size": "1G", "iodepth": 64},
    {"name": "1024k-70R-30W", "rwmixread": "70", "bs": "1024k", "size": "1G", "iodepth": 64},
]

# ==== FILE OUTPUT CONFIGURATION ====
san = ""  # Set your file name prefix here
date_str = datetime.now().strftime("%d%m%y-%H%M%S")
csv_filename = f"Report-{date_str}_Benchmark-{san}.csv"
xlsx_filename = f"Report-{date_str}_Benchmark-{san}.xlsx"
file_exists = os.path.isfile(csv_filename)


# ==== RUN FIO AND SAVE DATA ====
with open(csv_filename, mode="a", newline="") as file:
    writer = csv.writer(file)
    
    # Write header if file does not exist
    if not file_exists:
        writer.writerow(["Test Name", "File Size", "Block Size", "IO Depth", "Read", "Write", "Read IOPS (K)", "Write IOPS (K)", "Read BW (MB/s)", "Write BW (MB/s)"])
    
    # Run each FIO test case
    for test in fio_tests:
        fio_command = [
            "fio",
            "--randrepeat=1",
            "--ioengine=libaio",
            "--direct=1",
            "--gtod_reduce=1",
            f"--name={test['name']}",
            f"--bs={test['bs']}",
            "--numjobs=1",
            f"--iodepth={test['iodepth']}",
            f"--size={test['size']}",
            "--readwrite=randrw",
            f"--rwmixread={test['rwmixread']}",
            "--runtime=30",
            "--time_based",
            "--output-format=json"
        ]


        try:
            result = subprocess.run(fio_command, capture_output=True, text=True, check=True)
            fio_output = json.loads(result.stdout)

            # Extract results from JSON
            job = fio_output["jobs"][0]
            read_iops = round(job["read"]["iops"] / 1000, 2)
            write_iops = round(job["write"]["iops"] / 1000, 2)
            read_bw = round(job["read"]["bw"] / 1024)
            write_bw = round(job["write"]["bw"] / 1024)
            write_percent = 100 - int(test["rwmixread"])

            # Write to CSV file
            writer.writerow([test["name"], "1G", test["bs"], test["iodepth"], test["rwmixread"], write_percent, read_iops, write_iops, read_bw, write_bw])
            print(f"Saved results for {test['name']} in {csv_filename}")

        except subprocess.CalledProcessError as e:
            print(f"Error running fio for {test['name']}: {e}")
        except json.JSONDecodeError:
            print(f"Error parsing JSON output from fio for {test['name']}.")

# ==== CONVERT CSV TO XLSX ====
df = pd.read_csv(csv_filename)
df.to_excel(xlsx_filename)
print(f"Converted {csv_filename} to {xlsx_filename}")

# ==== SEND FILE VIA TELEGRAM ====
url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
files = {"document": open(xlsx_filename, "rb")}
data = {"chat_id": CHAT_ID}

response = requests.post(url, data=data, files=files)

if response.status_code == 200:
    print("File successfully sent via Telegram!")
else:
    print(f"Error sending file: {response.text}")
