import re
s = "Reports on post-exploitation on honeypot exploiting vulnerable wu-ftpd (CVE-2001-0550)"
print(re.findall(r"([cC][vV][eE])[-_ ]?([0-9]{4})[-_ ]?([0-9]+)",s))