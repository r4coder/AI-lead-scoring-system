# test_scoring.py
# Run with:  python -m unittest test_scoring -v

import unittest
from scoring import score_lead

SAMPLE = {
    "name": "Rahul Sharma", "company": "ABC Technologies",
    "website": "www.abctechnologies.com", "job_title": "Founder",
    "industry": "IT Services", "location": "Bangalore",
    "company_size": "50-100 Employees", "lead_source": "Website",
    "requirement": "Looking for CRM software",
    "email": "rahul@example.com", "phone": "+91 9876543210",
}


class TestLeadScoring(unittest.TestCase):

    def test_sample_lead_is_hot(self):
        result = score_lead(SAMPLE)
        self.assertEqual(result["score"], 95)
        self.assertEqual(result["classification"], "Hot")
        self.assertEqual(result["confidence"], "High")

    def test_same_input_same_score(self):
        first = score_lead(SAMPLE)["score"]
        second = score_lead(SAMPLE)["score"]
        self.assertEqual(first, second)

    def test_warm_lead(self):
        lead = {
            "name": "Anita", "company": "Hotel Sunrise", "website": "",
            "job_title": "Executive", "industry": "Hospitality",
            "location": "Jaipur", "company_size": "8",
            "lead_source": "Cold Call", "requirement": "Need a tool to track customers",
            "email": "anita@gmail.com", "phone": "9123456780",
        }
        result = score_lead(lead)
        self.assertEqual(result["score"], 49)
        self.assertEqual(result["classification"], "Warm")

    def test_cold_lead(self):
        lead = {
            "name": "Ravi", "company": "", "website": "",
            "job_title": "Student", "industry": "Education",
            "location": "Nagpur", "company_size": "1",
            "lead_source": "Purchased List", "requirement": "free project report",
            "email": "ravi@gmail.com", "phone": "",
        }
        result = score_lead(lead)
        self.assertEqual(result["classification"], "Cold")

    def test_empty_lead_does_not_crash(self):
        result = score_lead({})
        self.assertEqual(result["score"], 0)
        self.assertEqual(result["classification"], "Cold")
        self.assertEqual(result["confidence"], "Low")

    def test_invalid_email_gets_zero(self):
        lead = dict(SAMPLE)
        lead["email"] = "not-an-email"
        result = score_lead(lead)
        email_item = [i for i in result["breakdown"] if i["parameter"] == "Email"][0]
        self.assertEqual(email_item["points"], 0)

    def test_free_email_scores_less(self):
        lead = dict(SAMPLE)
        lead["email"] = "rahul@gmail.com"
        self.assertEqual(score_lead(lead)["score"], 91)

    def test_missing_fields_lower_confidence(self):
        lead = dict(SAMPLE)
        lead["phone"] = ""
        lead["website"] = ""
        lead["location"] = ""
        result = score_lead(lead)
        self.assertEqual(result["confidence"], "Low")

    def test_assistant_manager_is_junior(self):
        lead = dict(SAMPLE)
        lead["job_title"] = "Assistant Manager"
        title_item = score_lead(lead)["breakdown"][0]
        self.assertEqual(title_item["points"], 2)

    def test_score_is_between_0_and_100(self):
        result = score_lead(SAMPLE)
        self.assertTrue(0 <= result["score"] <= 100)


if __name__ == "__main__":
    unittest.main()
