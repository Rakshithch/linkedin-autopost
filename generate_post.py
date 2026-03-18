"""
LinkedIn Auto-Post Generator
Generates recruiter-targeted posts using Claude API + web search,
then queues them to Buffer for auto-publishing to LinkedIn.
"""

import os
import random
import anthropic
import requests
from datetime import date

# ─────────────────────────────────────────────
# Topic rotation — picks one randomly each run
# ─────────────────────────────────────────────
TOPICS = [
    {
        "theme": "Healthcare data analytics",
        "prompt_hint": "Focus on a real trend, challenge, or insight in healthcare claims analytics, "
                       "EHR data, or population health management. Reference a recent development if possible."
    },
    {
        "theme": "X12 EDI / HIPAA / ICD-10",
        "prompt_hint": "Write about something specific to EDI 837/835 transactions, HIPAA compliance, "
                       "ICD-10 coding changes, or CMS regulations. Make it practical — something a "
                       "data analyst or engineer would find useful."
    },
    {
        "theme": "Python / SQL tips for data professionals",
        "prompt_hint": "Share a concrete Python or SQL tip, pattern, or lesson learned that applies "
                       "to healthcare or data analytics work. Keep it technical but accessible."
    },
    {
        "theme": "AI & data engineering news",
        "prompt_hint": "Search for the latest news in AI, LLMs, data engineering, or MLOps from the "
                       "past week. Summarize the most interesting development and share a take on how "
                       "it impacts healthcare data or analytics work."
    },
    {
        "theme": "Career insights for data professionals",
        "prompt_hint": "Write about a job search lesson, career tip, or observation about the data "
                       "analyst / ML / analytics engineering job market. Make it real and specific, "
                       "not generic career advice."
    },
]

# ─────────────────────────────────────────────
# Generate post using Claude API + web search
# ─────────────────────────────────────────────
def generate_post() -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    topic = random.choice(TOPICS)
    today = date.today().strftime("%B %d, %Y")

    system_prompt = """You are a LinkedIn ghostwriter for Rakshith Chandupatla, a Healthcare Data Analyst 
based in the New Jersey area. His expertise: Python, SQL, X12 EDI 837/835, HIPAA, ICD-10, CPT, 
TensorFlow, Tableau, Power BI, AWS (S3/EC2), MongoDB, Docker. He works with Change Healthcare 
and Optum/UnitedHealth Group data. His goal is to attract recruiter attention and land interviews 
for Healthcare Data Analyst, ML Engineer, Analytics Engineer, BI Analyst, or Data Analyst roles.

WRITING RULES — follow strictly:
- Write in first person as Rakshith
- First line must be a strong, specific hook — NO generic openers like "I'm excited to share..."
- 150–220 words total
- Include 1-2 specific data points, tools, or real examples
- End with a question or CTA that invites engagement
- 5–8 hashtags at the very end (no hashtags in the body)
- Max 2 emojis total
- Tone: confident, knowledgeable, conversational — not corporate
- Return ONLY the post text. No preamble, no explanation."""

    user_prompt = f"""Today is {today}.

Topic area: {topic['theme']}
Direction: {topic['prompt_hint']}

Use your web search tool to find one relevant, recent (last 2 weeks if possible) news item, 
stat, or development to ground the post in something real and timely. Then write the LinkedIn post."""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1000,
        system=system_prompt,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{"role": "user", "content": user_prompt}]
    )

    # Extract final text block (after tool use)
    post_text = ""
    for block in response.content:
        if block.type == "text":
            post_text = block.text  # Take the last text block

    return post_text.strip()


# ─────────────────────────────────────────────
# Post directly to LinkedIn API
# ─────────────────────────────────────────────
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
                "shareCommentary": {
                    "text": post_text
                },
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        post_id = response.headers.get("X-RestLi-Id", "unknown")
        print(f"✅ Post published to LinkedIn!")
        print(f"🔗 Post ID: {post_id}")
    else:
        print(f"❌ LinkedIn API error {response.status_code}: {response.text}")
        raise RuntimeError("LinkedIn posting failed")


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("🤖 Generating LinkedIn post with Claude...\n")
    post = generate_post()

    print("=" * 60)
    print(post)
    print("=" * 60)
    print(f"\n📊 Word count: {len(post.split())}")

    print("\n📤 Publishing to LinkedIn...")
    post_to_linkedin(post)
    print("\n✅ Done! Check your LinkedIn profile — post is live.")
