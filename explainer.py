# explainer.py
# Writes the explanation of the score.
# The LLM only explains the score. It never decides it.

import os


def basic_explanation(result):
    # simple explanation without any AI, used when no API key is set
    text = "This lead scored " + str(result["score"]) + " out of 100 and is classified as "
    text = text + result["classification"] + ". "

    if len(result["positives"]) > 0:
        names = []
        for item in result["positives"]:
            names.append(item["parameter"])
        text = text + "The score is helped by: " + ", ".join(names) + ". "

    if len(result["negatives"]) > 0:
        names = []
        for item in result["negatives"]:
            names.append(item["parameter"])
        text = text + "The score is held back by: " + ", ".join(names) + ". "

    text = text + "Confidence is " + result["confidence"].lower() + " because "
    text = text + result["fields_filled"] + " scoring fields were filled in."
    return text


def ai_explanation(result):
    # asks Claude to write a friendly explanation of the finished score
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)

        lines = []
        for item in result["breakdown"]:
            lines.append(item["parameter"] + ": " + str(item["points"]) + "/" + str(item["max"]) + " - " + item["note"])

        prompt = "A rule based system scored a sales lead.\n"
        prompt = prompt + "Final score: " + str(result["score"]) + "/100 (" + result["classification"] + ")\n"
        prompt = prompt + "Breakdown:\n" + "\n".join(lines) + "\n\n"
        prompt = prompt + "Write a short explanation (4 to 5 sentences) for a sales manager. "
        prompt = prompt + "Explain why the lead got this score and what to watch out for. "
        prompt = prompt + "Do not change or question the score and do not invent facts."

        reply = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        return reply.content[0].text
    except Exception as error:
        print("AI explanation failed:", error)
        return None


def get_explanation(result):
    text = ai_explanation(result)
    if text is None:
        return basic_explanation(result), "Rule-based summary"
    return text, "AI generated"
