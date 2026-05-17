"""
Run this ONCE locally to get the base64 string for your resume.
Copy the output and paste it as the RESUME_BASE64 GitHub secret.

Usage:
    python encode_resume_for_github.py
"""
import base64, os

resume_path = "all resumes/default/resume.pdf"

if not os.path.exists(resume_path):
    print(f"ERROR: Resume not found at: {resume_path}")
    exit(1)

with open(resume_path, "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

print(f"Resume size: {os.path.getsize(resume_path)} bytes")
print(f"\nCopy everything below this line and paste as RESUME_BASE64 secret:\n")
print(encoded)
