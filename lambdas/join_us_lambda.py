import json
import boto3
import os
import re
import urllib.request
import urllib.error

# AWS SNS client and topic for talent applications (from environment variable)
sns = boto3.client("sns")
TOPIC_ARN = os.environ.get('TOPIC_ARN')

# Email validation regex
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Environment variables for reCAPTCHA Enterprise REST API
RECAPTCHA_API_KEY = os.environ.get('RECAPTCHA_API_KEY')
RECAPTCHA_SITE_KEY = os.environ.get('RECAPTCHA_SITE_KEY')
GOOGLE_CLOUD_PROJECT_ID = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')

def _cors():
    """Returns CORS headers."""
    return {
        "Access-Control-Allow-Origin": "https://www.valoremgp.com",
        "Access-Control-Allow-Methods": "POST,OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type,Accept"
    }

def _verify_recaptcha(token):
    """Verifies a reCAPTCHA token with the REST API using urllib."""
    if not all([RECAPTCHA_API_KEY, RECAPTCHA_SITE_KEY, GOOGLE_CLOUD_PROJECT_ID]):
        print("ERROR: Missing environment variables for reCAPTCHA (API_KEY, SITE_KEY, or PROJECT_ID).")
        return False, "Configuration error."

    try:
        url = f"https://recaptchaenterprise.googleapis.com/v1/projects/{GOOGLE_CLOUD_PROJECT_ID}/assessments?key={RECAPTCHA_API_KEY}"
        
        payload = {
            "event": {
                "token": token,
                "siteKey": RECAPTCHA_SITE_KEY,
                "expectedAction": "join_us"  # Action for the talent form
            }
        }
        
        data = json.dumps(payload).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        
        req = urllib.request.Request(url, data=data, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())

        token_properties = result.get('tokenProperties', {})
        risk_analysis = result.get('riskAnalysis', {})

        if not token_properties.get('valid'):
            print(f"The CreateAssessment call failed: {token_properties.get('invalidReason')}")
            return False, "Invalid reCAPTCHA token."

        if token_properties.get('action') != 'join_us':
            print(f"reCAPTCHA action mismatch: expected 'join_us', got '{token_properties.get('action')}'")
            return False, "reCAPTCHA action mismatch."

        if risk_analysis.get('score', 0) < 0.5:
            print(f"Low reCAPTCHA score: {risk_analysis.get('score')}")
            return False, "Bot-like behavior detected."

        return True, ""

    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"HTTP Error calling reCAPTCHA REST API: {e} - {error_body}")
        return False, "Could not verify CAPTCHA."
    except Exception as e:
        print(f"An unexpected error occurred during reCAPTCHA verification: {e}")
        return False, "Could not verify CAPTCHA."

def lambda_handler(event, context):
    """Main Lambda handler for talent applications."""
    if event.get('httpMethod') == 'OPTIONS' or event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return {"statusCode": 204, "headers": _cors(), "body": ""}
    
    try:
        data = json.loads(event.get("body") or "{}")
    except Exception:
        return {"statusCode": 400, "headers": _cors(), "body": json.dumps({"error": "Invalid JSON"})}

    recaptcha_token = data.get('recaptcha_token')
    if not recaptcha_token:
        return {"statusCode": 400, "headers": _cors(), "body": json.dumps({"error": "Missing reCAPTCHA token."})}

    is_human, error_message = _verify_recaptcha(recaptcha_token)
    if not is_human:
        return {"statusCode": 400, "headers": _cors(), "body": json.dumps({"error": error_message})}
    
    # --- Process Talent Form Data ---
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    country = (data.get("country") or "").strip()
    linkedin = (data.get("linkedin") or "").strip()
    expertise = (data.get("expertise") or "").strip()
    resume = (data.get("resume") or "").strip()

    # Validate required fields
    if not all([name, email, country, linkedin, expertise, resume]):
        return {"statusCode": 400, "headers": _cors(), "body": json.dumps({"error": "All fields are required."})}
    if not EMAIL_RE.match(email):
        return {"statusCode": 400, "headers": _cors(), "body": json.dumps({"error": "Invalid email format."})}

    # --- Send Notification ---
    subject = f"New Talent Application from {name}"[:100]
    body = f"""New application received from the Valorem Global Talent Network page.

Applicant Details:

Name: {name}
Email: {email}
Country & Time Zone: {country}
LinkedIn Profile: {linkedin}
Resume/CV Link: {resume}
Areas of Expertise: {expertise}
"""
    
    if not TOPIC_ARN:
        print("ERROR: TALENT_TOPIC_ARN environment variable not set.")
        return {"statusCode": 500, "headers": _cors(), "body": json.dumps({"error": "Server configuration error."})}

    sns.publish(TopicArn=TOPIC_ARN, Subject=subject, Message=body)
    
    return {"statusCode": 200, "headers": _cors(), "body": json.dumps({"ok": True})}
