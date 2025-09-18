import json
import boto3
import os
import re
import urllib.request
import urllib.error

# AWS SNS client and topic
sns = boto3.client("sns")
TOPIC_ARN = "arn:aws:sns:us-east-2:823741290812:valorem-contact-form"

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
                "expectedAction": "contact"
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

        if token_properties.get('action') != 'contact':
            print(f"reCAPTCHA action mismatch: expected 'contact', got '{token_properties.get('action')}'")
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
    """Main Lambda handler."""
    # Handle CORS preflight requests for both REST and HTTP APIs
    if event.get('httpMethod') == 'OPTIONS' or event.get("requestContext", {}).get("http", {}).get("method") == "OPTIONS":
        return {"statusCode": 204, "headers": _cors(), "body": ""}
    
    try:
        data = json.loads(event.get("body") or "{}")
    except Exception:
        return {"statusCode": 400, "headers": _cors(), "body": json.dumps({"error": "Invalid JSON"})}

    # --- reCAPTCHA Enterprise Assessment ---
    recaptcha_token = data.get('recaptcha_token')
    if not recaptcha_token:
        return {"statusCode": 400, "headers": _cors(), "body": json.dumps({"error": "Missing reCAPTCHA token."})}

    is_human, error_message = _verify_recaptcha(recaptcha_token)
    if not is_human:
        return {"statusCode": 400, "headers": _cors(), "body": json.dumps({"error": error_message})}
    
    # --- Process Form Data ---
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    company = (data.get("company") or "").strip()
    service = (data.get("service") or "").strip()
    message = (data.get("message") or "").strip()

    # Validate required fields
    if not (1 <= len(name) <= 200):
        return {"statusCode": 400, "headers": _cors(), "body": json.dumps({"error": "Invalid name"})}
    if not EMAIL_RE.match(email):
        return {"statusCode": 400, "headers": _cors(), "body": json.dumps({"error": "Invalid email"})}
    if not (0 <= len(message) <= 5000):
        return {"statusCode": 400, "headers": _cors(), "body": json.dumps({"error": "Invalid message"})}
    if len(company) > 200:
        return {"statusCode": 400, "headers": _cors(), "body": json.dumps({"error": "Invalid company"})}
    if len(service) > 100:
        return {"statusCode": 400, "headers": _cors(), "body": json.dumps({"error": "Invalid service"})}

    # --- Send Notification ---
    subject = f"New Contact Form Submission from {name}"[:100]
    body = f"""You are receiving this email because a new message has been submitted through the contact form on the Valorem Global Partners website (valoremgp.com).\n\nHere are the details:\n\nName: {name}\nEmail: {email}\nCompany: {company}\nService of Interest: {service}\n\nMessage:\n{message}"""

    sns.publish(TopicArn=TOPIC_ARN, Subject=subject, Message=body)
    
    return {"statusCode": 200, "headers": _cors(), "body": json.dumps({"ok": True})}
