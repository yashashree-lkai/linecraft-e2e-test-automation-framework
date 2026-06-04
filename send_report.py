"""
send_report.py — Sends the latest HTML report via Outlook desktop app.
"""

import os
import re
import glob
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# ── Recipients — update with real email addresses ─────────────────────────────
TO_EMAILS = [
    "yashashreek@linecraft.ai",       # ← your email
    #"mithuls@linecraft.ai",           # ← replace with real second email
]
# ─────────────────────────────────────────────────────────────────────────────


def get_latest_report():
    reports = glob.glob("reports/*.html")
    if not reports:
        return None
    return os.path.abspath(max(reports, key=os.path.getctime))


def get_test_summary(report_path):
    """Extract pass/fail counts using regex on pytest-html report."""
    try:
        with open(report_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # pytest-html stores counts like: "2 passed, 1 failed"
        passed = 0
        failed = 0

        passed_match = re.search(r'(\d+)\s+passed', content)
        failed_match = re.search(r'(\d+)\s+failed', content)

        if passed_match:
            passed = int(passed_match.group(1))
        if failed_match:
            failed = int(failed_match.group(1))

        return passed, failed
    except Exception:
        return 0, 0


def send_via_outlook():
    report_path = get_latest_report()
    if not report_path:
        print("✗ No report found in reports/ folder!")
        return

    passed, failed = get_test_summary(report_path)
    status   = "PASSED ✅" if failed == 0 else "FAILED ❌"
    date_str = datetime.now().strftime("%d-%b-%Y %H:%M")

    body = f"""Hi Team,

Playwright regression run completed on {date_str}.

Result      : {status}
Environment : http://wks1103
Passed      : {passed}
Failed      : {failed}

Please find the detailed HTML report attached.
Open it in your browser to see full results with screenshots.

--
QA Automation | Linecraft AI
"""

    try:
        import win32com.client

        # Force desktop Outlook app (not web)
        outlook = win32com.client.gencache.EnsureDispatch("Outlook.Application")
        mail = outlook.CreateItem(0)
        mail.To = "; ".join(TO_EMAILS)
        mail.Subject = f"[Linecraft QA] Regression {status} — {date_str}"
        mail.Body = body
        mail.Attachments.Add(report_path)
        mail.Send()
        print(f"✓ Report emailed via Outlook to: {', '.join(TO_EMAILS)}")

    except ImportError:
        print("✗ pywin32 not installed. Run: pip install pywin32")
    except Exception as e:
        print(f"✗ Failed to send email: {e}")


if __name__ == "__main__":
    send_via_outlook()