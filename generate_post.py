import os, random, requests
from datetime import date
import anthropic

TOPICS = [
    {"theme": "Healthcare data analytics", "prompt_hint": "Share a real insight in healthcare claims analytics or population health. Use a specific example.", "image_query": "healthcare data analytics"},
    {"theme": "X12 EDI / HIPAA / ICD-10", "prompt_hint": "Write about EDI 837/835, HIPAA compliance, or ICD-10 coding. Make it practical.", "image_query": "medical coding healthcare technology"},
    {"theme": "Python / SQL tips", "prompt_hint": "Share a concrete Python or SQL tip for healthcare data work.", "image_query": "python programming data science"},
    {"theme": "AI & data engineering", "prompt_hint": "Write about an AI or data engineering trend and its impact on healthcare analytics.", "image_query": "artificial intelligence machine learning"},
    {"theme": "Career insights", "prompt_hint": "Write a specific career tip about the data analyst or ML job market in 2026.", "image_query": "professional career growth technology"},
]

def generate_post(topic):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    system = """You are a LinkedIn ghostwriter for Rakshith Chandupatla, a Healthcare Data Analyst in New Jersey.
Skills: Python, SQL, X12 EDI 837/835, HIPAA, ICD-10, TensorFlow, Tableau, Power BI, AWS, MongoDB, Docker.
Works with Change Healthcare and Optum/UnitedHealth Group data.
Goal: attract recruiters for Healthcare Data Analyst, ML Engineer, Analytics Engineer, BI Analyst roles.

RULES:
- First person, strong specific hook on line 1
- 150-220 words
- 1-2 specific examples or stats
- End with a question or CTA
- 5-8 hashtags at end using # (e.g. #HealthcareAI)
- Max 2 emojis
- NO preamble, NO explanation, NO thinking, NO dashes or separators
- Output ONLY the post text"""
    r = client.messages.create(
        model="claude-opus-4-6", max_tokens=800, system=system,
        messages=[{"role": "user", "content": f"Topic: {topic['theme']}\n{topic['prompt_hint']}\n\nWrite the post now. Post text only."}]
    )
    return r.content[0].text.strip()

def get_image(query):
    r = requests.get("https://api.unsplash.com/photos/random",
        params={"query": query, "orientation": "landscape"},
        headers={"Authorization": f"Client-ID {os.environ['UNSPLASH_ACCESS_KEY']}"})
    data = r.json()
    requests.get(data["links"]["download_location"], headers={"Authorization": f"Client-ID {os.environ['UNSPLASH_ACCESS_KEY']}"})
    return requests.get(data["urls"]["regular"]).content

def upload_image(image_bytes, user_urn, token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "X-Restli-Protocol-Version": "2.0.0"}
    payload = {"registerUploadRequest": {"recipes": ["urn:li:digitalmediaRecipe:feedshare-image"], "owner": user_urn, "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}]}}
    r = requests.post("https://api.linkedin.com/v2/assets?action=registerUpload", headers=headers, json=payload)
    upload_url = r.json()["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset_urn = r.json()["value"]["asset"]
    requests.put(upload_url, headers={"Authorization": f"Bearer {token}", "Content-Type": "image/jpeg"}, data=image_bytes)
    return asset_urn

def post_to_linkedin(text, asset_urn=None):
    token = os.environ["LINKEDIN_ACCESS_TOKEN"]
    urn = os.environ["LINKEDIN_USER_URN"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", "X-Restli-Protocol-Version": "2.0.0"}
    media = "IMAGE" if asset_urn else "NONE"
    content = {"shareCommentary": {"text": text}, "shareMediaCategory": media}
    if asset_urn:
        content["media"] = [{"status": "READY", "media": asset_urn, "title": {"text": ""}}]
    payload = {"author": urn, "lifecycleState": "PUBLISHED",
        "specificContent": {"com.linkedin.ugc.ShareContent": content},
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}}
    r = requests.post("https://api.linkedin.com/v2/ugcPosts", headers=headers, json=payload)
    print("Published!" if r.status_code == 201 else f"Error {r.status_code}: {r.text}")

if __name__ == "__main__":
    topic = random.choice(TOPICS)
    print(f"Topic: {topic['theme']}")
    post = generate_post(topic)
    print(post)
    try:
        img = get_image(topic["image_query"])
        asset = upload_image(img, os.environ["LINKEDIN_USER_URN"], os.environ["LINKEDIN_ACCESS_TOKEN"])
    except Exception as e:
        print(f"Image failed: {e}"); asset = None
    post_to_linkedin(post, asset)
