'''
Resume Tailoring Module
Uses career-ops through its intended interface (AI agent workflow).

Flow:
  1. Save job description to career-ops/jds/ directory
  2. Create a prompt file for Kiro/Claude to execute career-ops pdf mode
  3. Call Node.js script that uses career-ops methodology
  4. Copy generated PDF to our output directory
  5. Return the PDF path for upload_resume() in runAiBot.py
'''

import os
import re
import shutil
import subprocess
from datetime import datetime

from modules.helpers import print_lg

# ── Paths ──────────────────────────────────────────────────────────────────────
CAREER_OPS_DIR = "career-ops"
CAREER_OPS_JDS_DIR = os.path.join(CAREER_OPS_DIR, "jds")
CAREER_OPS_OUTPUT = os.path.join(CAREER_OPS_DIR, "output")
CAREER_OPS_SCRIPT = os.path.join(CAREER_OPS_DIR, "generate-tailored-resume.mjs")
OUTPUT_DIR = "all resumes/temp"


def _sanitize_company_name(company_name: str) -> str:
    """Sanitize company name for use in filenames."""
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '-', company_name.lower())
    safe_name = re.sub(r'-+', '-', safe_name).strip('-')[:30]
    return safe_name if safe_name else "company"


def _get_api_key() -> str:
    """Get OpenAI API key from config."""
    try:
        from config.secrets import llm_api_key
        return llm_api_key
    except Exception as e:
        print_lg(f"[TailoredResume] ERROR: Could not get API key: {e}")
        return None


def _call_career_ops_node(api_key: str, job_description: str, company_name: str) -> str | None:
    """
    Call career-ops Node.js script that follows career-ops methodology.
    Returns the path to the generated PDF, or None if failed.
    """
    print_lg("[TailoredResume] Calling career-ops (Node.js) to generate tailored resume...")
    
    try:
        # Check if Node.js script exists
        if not os.path.exists(CAREER_OPS_SCRIPT):
            print_lg(f"[TailoredResume] ERROR: career-ops script not found: {CAREER_OPS_SCRIPT}")
            print_lg(f"[TailoredResume] Please ensure generate-tailored-resume.mjs exists in career-ops/")
            return None
        
        # Save job description to jds directory (career-ops convention)
        safe_company = _sanitize_company_name(company_name)
        os.makedirs(CAREER_OPS_JDS_DIR, exist_ok=True)
        jd_file = os.path.join(CAREER_OPS_JDS_DIR, f"{safe_company}.md")
        
        with open(jd_file, 'w', encoding='utf-8') as f:
            f.write(f"# {company_name}\n\n")
            f.write(job_description)
        
        print_lg(f"[TailoredResume] Saved JD to: {jd_file}")
        print_lg(f"[TailoredResume] Calling: node {CAREER_OPS_SCRIPT}")
        
        # Call Node.js script
        result = subprocess.run(
            ['node', CAREER_OPS_SCRIPT, api_key, job_description, company_name],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.getcwd(),
            encoding='utf-8',
            errors='replace'
        )
        
        print_lg(f"[TailoredResume] career-ops return code: {result.returncode}")
        
        if result.stdout:
            # Look for PDF_PATH in output
            for line in result.stdout.split('\n'):
                if line.startswith('PDF_PATH:'):
                    pdf_path = line.replace('PDF_PATH:', '').strip()
                    print_lg(f"[TailoredResume] ✓ Found generated PDF: {pdf_path}")
                    return pdf_path
            
            print_lg(f"[TailoredResume] career-ops output:\n{result.stdout}")
        
        if result.stderr:
            print_lg(f"[TailoredResume] career-ops errors:\n{result.stderr}")
        
        if result.returncode != 0:
            print_lg(f"[TailoredResume] ERROR: career-ops failed with return code {result.returncode}")
            return None
        
        # Fallback: Find the most recently created PDF
        if not os.path.exists(CAREER_OPS_OUTPUT):
            print_lg(f"[TailoredResume] ERROR: career-ops output directory not found: {CAREER_OPS_OUTPUT}")
            return None
        
        pdf_files = [f for f in os.listdir(CAREER_OPS_OUTPUT) if f.endswith('.pdf') and safe_company in f]
        if not pdf_files:
            print_lg("[TailoredResume] ERROR: No matching PDF files found in career-ops output directory")
            return None
        
        # Get the most recent PDF
        pdf_files_with_time = [(f, os.path.getmtime(os.path.join(CAREER_OPS_OUTPUT, f))) for f in pdf_files]
        latest_pdf = max(pdf_files_with_time, key=lambda x: x[1])[0]
        generated_pdf_path = os.path.join(CAREER_OPS_OUTPUT, latest_pdf)
        
        print_lg(f"[TailoredResume] ✓ Found generated PDF: {generated_pdf_path}")
        return generated_pdf_path
        
    except subprocess.TimeoutExpired:
        print_lg("[TailoredResume] ERROR: career-ops timed out (120s)")
        return None
    except Exception as e:
        print_lg(f"[TailoredResume] ERROR: Failed to call career-ops: {e}")
        import traceback
        print_lg(f"[TailoredResume] Traceback: {traceback.format_exc()}")
        return None


def _copy_to_output(source_pdf: str, company_name: str) -> str | None:
    """
    Copy the generated PDF to our output directory with proper naming.
    Returns the final PDF path.
    """
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        safe_company = _sanitize_company_name(company_name)
        pdf_filename = f"{safe_company}_tailored_resume.pdf"
        destination_path = os.path.join(OUTPUT_DIR, pdf_filename)
        
        print_lg(f"[TailoredResume] Copying PDF to: {destination_path}")
        shutil.copy2(source_pdf, destination_path)
        
        if os.path.exists(destination_path):
            file_size = os.path.getsize(destination_path)
            print_lg(f"[TailoredResume] ✓ PDF copied successfully ({file_size} bytes)")
            return destination_path
        else:
            print_lg(f"[TailoredResume] ERROR: PDF not found after copy: {destination_path}")
            return None
            
    except Exception as e:
        print_lg(f"[TailoredResume] ERROR: Failed to copy PDF: {e}")
        import traceback
        print_lg(f"[TailoredResume] Traceback: {traceback.format_exc()}")
        return None


# ── Public entry point ─────────────────────────────────────────────────────────
def generate_tailored_resume(ai_client, ai_provider: str, job_description: str, company_name: str = "company") -> str | None:
    """
    Main function called by runAiBot.py.
    
    This function calls career-ops through its Node.js interface to generate a tailored resume.
    career-ops handles all the AI logic, HTML templating, and PDF generation following its methodology.

    Args:
        ai_client:       Not used (career-ops uses its own OpenAI client)
        ai_provider:     Not used (career-ops uses OpenAI)
        job_description: Full text of the job description from LinkedIn
        company_name:    Company name for the PDF filename

    Returns:
        Path to the generated PDF, or None if generation failed.
        On failure, the bot will SKIP the job (no default resume fallback).
    """
    try:
        print_lg(f"\n{'='*80}")
        print_lg(f"[TailoredResume] Starting resume generation for: {company_name}")
        print_lg(f"[TailoredResume] Job description length: {len(job_description)} chars")
        print_lg(f"[TailoredResume] Using career-ops methodology")
        print_lg(f"{'='*80}\n")

        # Get API key
        api_key = _get_api_key()
        if not api_key:
            print_lg("[TailoredResume] ERROR: No API key found, skipping tailoring.")
            return None
        
        # Call career-ops Node.js script
        generated_pdf = _call_career_ops_node(api_key, job_description, company_name)
        
        if not generated_pdf:
            print_lg("[TailoredResume] ERROR: career-ops did not generate a PDF")
            return None
        
        # Copy PDF to our output directory with proper naming
        final_pdf_path = _copy_to_output(generated_pdf, company_name)
        
        if final_pdf_path and os.path.exists(final_pdf_path):
            print_lg(f"\n{'='*80}")
            print_lg(f"[TailoredResume] ✅ SUCCESS! Tailored resume generated:")
            print_lg(f"[TailoredResume] 📄 File: {final_pdf_path}")
            print_lg(f"[TailoredResume] 📦 Size: {os.path.getsize(final_pdf_path)} bytes")
            print_lg(f"{'='*80}\n")
            return final_pdf_path
        
        print_lg(f"\n{'='*80}")
        print_lg("[TailoredResume] ❌ FAILED: PDF not found after generation.")
        print_lg(f"{'='*80}\n")
        return None
        
    except Exception as e:
        print_lg(f"[TailoredResume] CRITICAL ERROR in generate_tailored_resume: {type(e).__name__}: {e}")
        import traceback
        print_lg(f"[TailoredResume] Full traceback:\n{traceback.format_exc()}")
        return None
