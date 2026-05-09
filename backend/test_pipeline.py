from ai_pipeline import run_pipeline

# Fake meeting transcript to test with
transcript = """
John: Alright everyone, let's get started. We need to finalize the product launch for next month.

Sarah: I've completed the marketing materials. Just need final approval from John by Wednesday.

Mike: The development team finished the core features. I still need to write the deployment docs though.

Sarah: Who's handling the social media announcements?

John: That'll be me. I'll schedule posts for launch day, which is the 15th.

Mike: I'll also need someone to review the staging environment before we go live. Can we get that done by Friday?

John: Sure, Sarah can you handle that review?

Sarah: Yes, I'll have it done by Thursday actually.

John: Perfect. Let's plan to meet again next Monday to do a final check.
"""

result = run_pipeline(transcript)

print("\n── SUMMARY ──────────────────────────")
print(result["summary"])

print("\n── ACTION ITEMS ─────────────────────")
for item in result["action_items"]:
    print(f"✅ {item['task']} | Owner: {item['owner']} | Due: {item['due_date']}")

print("\n── EMAIL DRAFT ──────────────────────")
print(result["email_draft"])
