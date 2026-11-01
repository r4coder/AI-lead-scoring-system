# scoring.py
# Rule based lead scoring. No AI is used here, so the same input
# will always give the same score.

import re

# Max points for each parameter (total = 100)
WEIGHTS = {
    "job_title": 20,
    "requirement": 20,
    "company_size": 15,
    "lead_source": 10,
    "industry": 10,
    "location": 5,
    "email": 8,
    "phone": 4,
    "website": 8,
}

# Fields we look at to decide how confident we are
SCORED_FIELDS = ["job_title", "requirement", "company_size", "lead_source",
                 "industry", "location", "email", "phone", "website"]

FREE_EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "rediffmail.com"]

TARGET_INDUSTRIES = ["it services", "software", "saas", "fintech", "e-commerce", "ecommerce",
                     "healthcare", "manufacturing", "real estate", "education", "retail",
                     "banking", "finance", "logistics", "consulting"]

METRO_CITIES = ["bangalore", "bengaluru", "mumbai", "delhi", "hyderabad", "pune",
                "chennai", "gurgaon", "gurugram", "noida", "kolkata"]

SOURCE_POINTS = {
    "referral": 10,
    "website": 8,
    "webinar": 7,
    "linkedin": 6,
    "event": 6,
    "email campaign": 5,
    "social media": 4,
    "cold call": 3,
    "purchased list": 2,
}

PRODUCT_WORDS = ["crm", "erp", "software", "automation", "sales", "lead", "customer",
                 "tool", "platform", "dashboard"]
INTENT_WORDS = ["looking for", "need", "want", "require", "urgent", "demo", "pricing",
                "quote", "buy", "implement", "purchase"]
WEAK_WORDS = ["just browsing", "just exploring", "free", "student", "project report",
              "job", "internship", "not sure"]


def clean(value):
    # turns None or extra spaces into a clean string
    if value is None:
        return ""
    return str(value).strip()


def score_job_title(title):
    max_points = WEIGHTS["job_title"]
    if title == "":
        return 0, "Job title is missing"

    t = title.lower()

    # check low level words first, because "assistant manager" has "manager" in it
    for word in ["intern", "student", "trainee", "assistant"]:
        if word in t:
            return 2, "Job title '" + title + "' is a junior role with little buying power"

    for word in ["founder", "owner", "ceo", "cto", "cfo", "coo", "cmo", "director",
                 "president", "managing", "partner", "chief"]:
        if word in t:
            return max_points, "Job title '" + title + "' is a key decision maker"

    for word in ["head", "manager", "vp", "gm"]:
        if re.search(r"\b" + word + r"\b", t):
            return 14, "Job title '" + title + "' can influence the buying decision"

    for word in ["lead", "senior", "architect", "consultant"]:
        if word in t:
            return 8, "Job title '" + title + "' is an influencer, not the final decision maker"

    return 5, "Job title '" + title + "' has unclear buying authority"


def get_numbers(text):
    # finds all numbers in a text like "50-100 Employees"
    found = re.findall(r"\d[\d,]*", text)
    numbers = []
    for item in found:
        numbers.append(int(item.replace(",", "")))
    return numbers


def score_company_size(size):
    if size == "":
        return 0, "Company size is missing"

    numbers = get_numbers(size)
    if len(numbers) == 0:
        return 3, "Company size '" + size + "' could not be understood"

    # use the average if a range is given
    employees = sum(numbers) / len(numbers)

    if employees >= 500:
        points = 15
    elif employees >= 100:
        points = 14
    elif employees >= 50:
        points = 12
    elif employees >= 11:
        points = 8
    elif employees >= 2:
        points = 5
    else:
        points = 2

    return points, "Company size '" + size + "' scored " + str(points) + " out of 15"


def score_requirement(requirement):
    if requirement == "":
        return 0, "Requirement is missing"

    r = requirement.lower()
    points = 0
    notes = []

    # does the requirement match what we sell
    for word in PRODUCT_WORDS:
        if word in r:
            points = points + 10
            notes.append("matches our product ('" + word + "')")
            break

    # does the lead show buying intent
    for word in INTENT_WORDS:
        if word in r:
            points = points + 6
            notes.append("shows buying intent ('" + word + "')")
            break

    # is the requirement detailed
    if len(r.split()) >= 3:
        points = points + 4
        notes.append("is described clearly")

    # weak signals reduce the points
    for word in WEAK_WORDS:
        if word in r:
            points = points - 8
            notes.append("has a weak signal ('" + word + "')")
            break

    if points < 0:
        points = 0
    if points > WEIGHTS["requirement"]:
        points = WEIGHTS["requirement"]

    if len(notes) == 0:
        return points, "Requirement is vague and does not match our product"
    return points, "Requirement " + ", ".join(notes)


def score_source(source):
    if source == "":
        return 0, "Lead source is missing"
    points = SOURCE_POINTS.get(source.lower(), 3)
    return points, "Lead source '" + source + "' scored " + str(points) + " out of 10"


def score_industry(industry):
    if industry == "":
        return 0, "Industry is missing"
    i = industry.lower()
    for name in TARGET_INDUSTRIES:
        if name in i:
            return 10, "Industry '" + industry + "' is one of our target industries"
    return 5, "Industry '" + industry + "' is not a main target industry"


def score_location(location):
    if location == "":
        return 0, "Location is missing"
    l = location.lower()
    for city in METRO_CITIES:
        if city in l:
            return 5, "Location '" + location + "' is a major business hub"
    return 3, "Location '" + location + "' is outside our main business hubs"


def score_email(email):
    if email == "":
        return 0, "Email is missing"
    pattern = r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$"
    if re.match(pattern, email) is None:
        return 0, "Email '" + email + "' is not a valid format"
    domain = email.split("@")[1].lower()
    if domain in FREE_EMAIL_DOMAINS:
        return 4, "Email uses a free provider (" + domain + ")"
    return 8, "Email uses a company domain (" + domain + ")"


def score_phone(phone):
    if phone == "":
        return 0, "Phone number is missing"
    digits = re.sub(r"\D", "", phone)
    if len(digits) >= 10 and len(digits) <= 13:
        return 4, "Phone number looks valid"
    return 0, "Phone number '" + phone + "' looks invalid"


def score_website(website):
    if website == "":
        return 0, "Website is missing"
    w = website.lower()
    if "." in w and " " not in w:
        return 8, "Company website is provided"
    return 0, "Website '" + website + "' looks invalid"


def get_classification(score):
    if score >= 70:
        return "Hot"
    if score >= 40:
        return "Warm"
    return "Cold"


def get_quality(score):
    if score >= 80:
        return "Excellent - strong fit and a real decision maker"
    if score >= 60:
        return "Good - worth an active follow-up"
    if score >= 40:
        return "Average - needs more nurturing before a sales push"
    return "Poor - low fit or very little information"


def get_confidence(lead):
    filled = 0
    for field in SCORED_FIELDS:
        if clean(lead.get(field)) != "":
            filled = filled + 1
    percent = filled * 100 / len(SCORED_FIELDS)

    if percent >= 90:
        level = "High"
    elif percent >= 70:
        level = "Medium"
    else:
        level = "Low"
    return level, filled


def get_next_action(classification, lead):
    has_phone = clean(lead.get("phone")) != ""
    if classification == "Hot":
        if has_phone:
            return "Call the lead within 24 hours and book a product demo."
        return "Email the lead within 24 hours and ask for a demo call."
    if classification == "Warm":
        return "Send a personalised email with case studies and follow up in 3 days."
    return "Add to the email newsletter list and review again after 30 days."


def score_lead(lead):
    # clean all the values first
    data = {}
    for key in lead:
        data[key] = clean(lead[key])

    results = {
        "job_title": score_job_title(data.get("job_title", "")),
        "requirement": score_requirement(data.get("requirement", "")),
        "company_size": score_company_size(data.get("company_size", "")),
        "lead_source": score_source(data.get("lead_source", "")),
        "industry": score_industry(data.get("industry", "")),
        "location": score_location(data.get("location", "")),
        "email": score_email(data.get("email", "")),
        "phone": score_phone(data.get("phone", "")),
        "website": score_website(data.get("website", "")),
    }

    total = 0
    breakdown = []
    positives = []
    negatives = []

    for name in SCORED_FIELDS:
        points, note = results[name]
        max_points = WEIGHTS[name]
        total = total + points

        item = {"parameter": name.replace("_", " ").title(),
                "points": points, "max": max_points, "note": note}
        breakdown.append(item)

        # half or more of the max points is positive, otherwise negative
        if points * 2 >= max_points:
            positives.append(item)
        else:
            negatives.append(item)

    classification = get_classification(total)
    confidence, filled = get_confidence(data)

    return {
        "name": data.get("name", ""),
        "company": data.get("company", ""),
        "score": total,
        "classification": classification,
        "quality": get_quality(total),
        "positives": positives,
        "negatives": negatives,
        "breakdown": breakdown,
        "confidence": confidence,
        "fields_filled": str(filled) + " of " + str(len(SCORED_FIELDS)),
        "next_action": get_next_action(classification, data),
    }
