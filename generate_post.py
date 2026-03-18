"""
LinkedIn Auto-Post Generator
Generates recruiter-targeted posts using Claude API,
then publishes them directly to LinkedIn.
"""

import os
import random
import anthropic
import requests
from datetime import date

TOPICS = [
    {
        "theme": "Healthcare data analytics",
        "prompt_hint": "Share a real trend, challenge, or insight in healthcare claims analytics, "
                       "EHR data, or population health management. Use a specific example or stat."
    },
    {
        "theme": "X12 EDI / HIPAA / ICD-10",
        "prompt_hint": "Write about something specific to EDI 837/835 transactions, HIPAA compliance, "
                       "ICD-10 coding, or CMS regulations. Make it practical for a data analyst."
    },
    {
        "theme": "Python / SQL tips for data professionals",
        "prompt_hint": "Share a concrete Python or SQL tip or pattern that applies to healthcare "
                       "or data analytics work. Keep it technical but accessible."
    },
    {
        "theme": "AI & data engineering trends",
        "prompt_hint": "Write about a notable trend in AI, LLMs, data engineering, or MLOps and "
                       "how it impacts healthcare data or analytics work specifically."
    },
    {
        "theme": "Career insights for data professionals",
        "prompt_hint": "Write about a job search lesson, career tip, or observation about the data "
                       "analyst / ML / analytics engineering job market. Make it real and specific."
    },
]


def generate_post() -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    topic = random.choice(TOPICS)
    today = date.today().strftime("%B %d, %Y")

    system_prompt = """You are a LinkedIn ghostwriter for Rakshith Chandupatla, a Healthcare Data Analyst 
based in New Jersey. His expertise: Python, SQL, X12 EDI 837/835, HIPAA, ICD-10, CPT, 
TensorFlow, Tableau, Power BI, AWS (S3/EC2), MongoDB, Docker. He works with Change Healthcare 
and Optum/UnitedHealth Group data. His goal is to attract recruiter attention and land interviews 
for Healthcare Data Analyst, ML Engineer, Analytics Engineer, BI Analyst, or Data Analyst roles.

WRITING RULES — follow strictly:
- Write in first person as Rakshith
- First line must be a strong, specific hook — NO generic openers
- 150–220 words total
- Include 1-2 specific data points, tools, or real examples from your knowledge
- End with a question or CTA that invites engagement
- 5–8 hashtags at the very end using # symbol (e.g. #HealthcareAI — NOT hashtag#HealthcareAI)
- Max 2 emojis total
- Tone: confident, knowledgeable, conversational — not corporate
- Return ONLY the final post text. No preamble, no explanation, no thinking out loud, no dashes or separators."""

    user_prompt = f"""Today is {today}.

Topic: {topic['theme']}
Direction: {topic['prompt_hint']}

Write the LinkedIn post now. Return ONLY the post text — no intro, no commentary."""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1000,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}]
    )

    return response.content[0].text.strip()


def post_to_linkedin(post_text: str) -> None:
    access_token = os.environ["LINKEDIN_ACCESS_TOKEN"]
    user_urn = os.environ["LINKEDIN_USER_URN"]

    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    payload = {
        "author": user_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        print(f"✅ Post published to LinkedIn!")
    else:
        print(f"❌ LinkedIn API error {response.status_code}: {response.text}")
        raise RuntimeError("LinkedIn posting failed")


if __name__ == "__main__":
    print("🤖 Generating LinkedIn post...\n")
    post = generate_post()

    print("=" * 60)
    print(post)
    print("=" * 60)
    print(f"\n📊 Word count: {len(post.split())}")

    print("\n📤 Publishing to LinkedIn...")
    post_to_linkedin(post)
    print("\n✅ Done!")
