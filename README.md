# AI-Based Lead Scoring System

A small web app that scores sales leads from 0 to 100 using a fixed, weighted rule set.
An LLM (Claude) is used **only to write the explanation**. It never decides the score.

## How to run

```
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

Optional: for AI written explanations set your key first.
Without a key the app still works and shows a rule-based summary.
```
export ANTHROPIC_API_KEY=your_key_here      (Windows: set ANTHROPIC_API_KEY=your_key_here)
```

Run the tests: `python -m unittest test_scoring -v`

## Project files

| File | Purpose |
|------|---------|
| scoring.py | All scoring rules and weights |
| explainer.py | Explanation text (LLM with a no-AI fallback) |
| app.py | Flask web app and JSON API |
| templates/index.html | User interface |
| test_scoring.py | Test cases |

## Scoring methodology

Every lead is scored on 9 parameters. The weights add up to 100.

| Parameter | Weight | How it is scored |
|-----------|--------|------------------|
| Job title | 20 | Founder/CEO/Director = 20, Head/Manager/VP = 14, Lead/Senior = 8, Other = 5, Junior/Intern/Student = 2 |
| Requirement | 20 | Matches our product (+10), shows buying intent (+6), clearly described (+4), weak signal like "free" or "student" (-8) |
| Company size | 15 | 500+ = 15, 100-499 = 14, 50-99 = 12, 11-49 = 8, 2-10 = 5, 1 = 2 (average is used for ranges) |
| Lead source | 10 | Referral 10, Website 8, Webinar 7, LinkedIn/Event 6, Email campaign 5, Social 4, Cold call 3, Purchased list 2, Other 3 |
| Industry | 10 | Target industry = 10, other = 5 |
| Location | 5 | Major business hub = 5, other = 3 |
| Email | 8 | Company domain = 8, free provider (gmail etc.) = 4, invalid = 0 |
| Phone | 4 | Valid length (10-13 digits) = 4, invalid = 0 |
| Website | 8 | Provided and valid = 8, invalid = 0 |

### Classification
- **Hot**: 70 and above
- **Warm**: 40 to 69
- **Cold**: below 40

### Lead quality
80+ Excellent, 60-79 Good, 40-59 Average, below 40 Poor.

### Handling missing information
- A missing field scores **0** for that parameter and is listed as a negative factor.
- The app never crashes on empty input.
- **Confidence** depends on how many of the 9 scoring fields are filled:
  High = 8 or 9 fields, Medium = 7 fields, Low = 6 or fewer.

### Consistency
The score comes only from fixed rules in `scoring.py`, so the same input always gives the same score.
The LLM receives the finished score and breakdown and is told not to change them.

### Recommended next action
- Hot: call within 24 hours and book a demo (email if there is no phone number)
- Warm: personalised email, follow up in 3 days
- Cold: add to newsletter, review after 30 days

## Sample test cases

| # | Lead | Score | Class | Confidence |
|---|------|-------|-------|------------|
| 1 | Rahul Sharma, Founder, IT Services, Bangalore, 50-100, Website, "Looking for CRM software" | 95 | Hot | High |
| 2 | Anita, Executive, Hospitality, Jaipur, 8, Cold Call, gmail, no website, "Need a tool to track customers" | 49 | Warm | Medium |
| 3 | Ravi, Student, Education, Nagpur, 1, Purchased List, "free project report", no phone or website | 23 | Cold | Medium |
| 4 | Empty lead | 0 | Cold | Low |
| 5 | Sample lead with email "not-an-email" | email = 0 points | - | - |
| 6 | Sample lead with gmail address | 91 | Hot | High |

## API

`POST /api/score` with JSON like the sample lead (keys: name, company, website, job_title,
industry, location, company_size, lead_source, requirement, email, phone). Returns score,
classification, quality, positives, negatives, explanation, confidence and next_action.

## Demo steps
1. Start the app and press **Use sample lead**. It scores 95 (Hot).
2. Change job title to "Student" and requirement to "free project report". The score drops.
3. Clear phone, website and location. Confidence drops to Low.
4. Press **Score lead** twice with the same data. The score is identical.

## Possible improvements
- Save leads in a database and show a ranked list
- Let the sales team edit weights from a settings page
- Upload leads from a CSV file
