"""
LinkedIn Auto-Post Generator with Images
Generates recruiter-targeted posts using Claude API,
fetches a relevant image from Unsplash,
then publishes to LinkedIn with the image attached.
"""

import os
import random
import requests
from datetime import date
import anthropic

TOPICS = [
    {
        "theme": "Healthcare data analytics",
        "prompt_hint": "Share a real trend, challenge, or insight in healthcare claims analytics, "
                       "EHR data, or population health management. Use a specific example or stat.",
        "image_query": "healthcare data analytics"
    },
    {
        "theme": "X12 EDI / HIPAA / ICD-10",
        "prompt_hint": "Write about something specific to EDI 837/835 transactions, HIPAA compliance, "
                       "ICD-10 coding, or CMS regulations. Make it practical for a data analyst.",
        "image_query": "medical coding healthcare technology"
    },
    {
        "theme": "Python / SQL tips for data professionals",
        "prompt_hint": "Share a concrete Python or SQL tip or pattern that applies to healthcare "
                       "or data analytics work. Keep it technical but accessible.",
        "image_query": "python programming data science"
    },
    {
        "theme": "AI & data engineering trends",
        "prompt_hint": "Write about a notable trend in AI, LLMs, data engineering, or MLOps and "
                       "how it impacts healthcare data or analytics work specifically.",
        "image_query": "artificial intelligence machine learning"
    },
    {
        "theme": "Career insights for data professionals",
        "prompt_hint": "Write about a job search lesson, career tip, or observation about the data "
                       "analyst / ML / analytics engineering job market. Make it real and specific.",
        "image_query": "professional career growth technology"
    },
]


def generate_post(topic: dict) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    today = date.today().strftime("%B %d, %Y")

    system_prompt = """You are a LinkedIn ghostwriter for Rakshith Chandupatla, a Healthcare Data Analyst 
based in New Jersey. His expertise: Python, SQL, X12 EDI 837/835, HIPAA, ICD-10, CPT, 
TensorFlow, Tableau, Power BI, AWS (S3/EC2), MongoDB, Docker. He works with Change Healthcare 
and Optum/UnitedHealth Group data. His goal is to attract recruiter attention and land interviews 
for Healthcare Data Analyst, ML Engineer, Analytics Engineer, BI Analyst, or Data Analyst roles.

WRITING RULES — follow strictly:
- Write in first person as Rakshith
- First line must be a strong specific hook — no generic openers
- 150–220 words total
- Include 1-2 specific data points, tools, or real examples
- End with a question or CTA that invites engagement
- 5–8 hashtags at the very end using # symbol (e.g. #HealthcareAI)
- Max 2 emojis total
- Tone: confident, knowledgeable, conversational — not corporate
- Return ONLY the final post text. No preamble, no explanation, no thinking out loud, no dashes or separators."""

    user_prompt = f"""Today is {today}.

Topic: {topic['theme']}
Direction: {topic['prompt_hint']}

Write the LinkedIn post now. Return ONLY the post text."""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )
    return response.content[0].text.strip()


def get_unsplash_image(query: str) -> tuple[bytes, str]:
    """Fetch a relevant image from Unsplash. Returns (image_bytes, media_type)."""
    access_key = os.environ["UNSPLASH_ACCESS_KEY"]
    r = requests.get(
        "https://api.unsplash.com/photos/random",
        params={"query": query, "orientation": "landscape"},
        headers={"Authorization": f"Client-ID {access_key}"}
    )
    if r.status_code != 200:
        raise RuntimeError(f"Unsplash error {r.status_code}: {r.text}")

    data = r.json()
    image_url = data["urls"]["regular"]
    # Trigger Unsplash download tracking (required by API guidelines)
    requests.get(data["links"]["download_location"],
                 headers={"Authorization": f"Client-ID {access_key}"})

    img_response = requests.get(image_url)
    return img_response.content, "image/jpeg"


def upload_image_to_linkedin(image_bytes: bytes, media_type: str, user_urn: str, access_token: str) -> str:
    """Upload image to LinkedIn and return the asset URN."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    # Step 1: Register upload
    register_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": user_urn,
            "serviceRelationships": [{
                "relationshipType": "OWNER",
                "identifier": "urn:li:userGeneratedContent"
            }]
        }
    }
    r = requests.post(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        headers=headers,
        json=register_payload
    )
    if r.status_code != 200:
        raise RuntimeError(f"LinkedIn register upload failed: {r.status_code} {r.text}")

    upload_data = r.json()
    upload_url = upload_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset_urn = upload_data["value"]["asset"]

    # Step 2: Upload image bytes
    upload_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": media_type
    }
    r2 = requests.put(upload_url, headers=upload_headers, data=image_bytes)
    if r2.status_code not in (200, 201):
        raise RuntimeError(f"LinkedIn image upload failed: {r2.status_code} {r2.text}")

    print(f"✅ Image uploaded: {asset_urn}")
    return asset_urn


def post_to_linkedin(post_text: str, asset_urn: str = None) -> None:
    access_token = os.environ["LINKEDIN_ACCESS_TOKEN"]
    user_urn = os.environ["LINKEDIN_USER_URN"]

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    if asset_urn:
        payload = {
            "author": user_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": post_text},
                    "shareMediaCategory": "IMAGE",
                    "media": [{
                        "status": "READY",
                        "description": {"text": "Healthcare Data Analytics"},
                        "media": asset_urn,
                        "title": {"text": ""}
                    }]
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }
    else:
        payload = {
            "author": user_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": post_text},
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
        }

    r = requests.post("https://api.linkedin.com/v2/ugcPosts", headers=headers, json=payload)
    if r.status_code == 201:
        print("✅ Post published to LinkedIn!")
    else:
        print(f"❌ LinkedIn API error {r.status_code}: {r.text}")
        raise RuntimeError("LinkedIn posting failed")


if __name__ == "__main__":
    topic = random.choice(TOPICS)
    print(f"📝 Topic: {topic['theme']}\n")

    print("🤖 Generating post with Claude...")
    post = generate_post(topic)
    print("=" * 60)
    print(post)
    print("=" * 60)
    print(f"📊 Word count: {len(post.split())}\n")

    asset_urn = None
    try:
        print(f"🖼️  Fetching image for: {topic['image_query']}")
        image_bytes, media_type = get_unsplash_image(topic["image_query"])
        access_token = os.environ["LINKEDIN_ACCESS_TOKEN"]
        user_urn = os.environ["LINKEDIN_USER_URN"]
        asset_urn = upload_image_to_linkedin(image_bytes, media_type, user_urn, access_token)
    except Exception as e:
        print(f"⚠️  Image upload failed ({e}) — posting without image")

    print("📤 Publishing to LinkedIn...")
    post_to_linkedin(post, asset_urn)
    print("✅ Done!")