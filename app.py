# app.py
# Run with:  python app.py   then open http://127.0.0.1:5000

from flask import Flask, render_template, request, jsonify
from scoring import score_lead
from explainer import get_explanation

app = Flask(__name__)

FIELDS = ["name", "company", "website", "job_title", "industry", "location",
          "company_size", "lead_source", "requirement", "email", "phone"]

SAMPLE_LEAD = {
    "name": "Rahul Sharma",
    "company": "ABC Technologies",
    "website": "www.abctechnologies.com",
    "job_title": "Founder",
    "industry": "IT Services",
    "location": "Bangalore",
    "company_size": "50-100 Employees",
    "lead_source": "Website",
    "requirement": "Looking for CRM software",
    "email": "rahul@example.com",
    "phone": "+91 9876543210",
}


@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    explanation = None
    explanation_type = None
    form_data = {}

    if request.method == "POST":
        if request.form.get("use_sample"):
            form_data = SAMPLE_LEAD
        else:
            for field in FIELDS:
                form_data[field] = request.form.get(field, "")

        result = score_lead(form_data)
        explanation, explanation_type = get_explanation(result)

    return render_template("index.html", result=result, form=form_data,
                           explanation=explanation, explanation_type=explanation_type)


@app.route("/api/score", methods=["POST"])
def api_score():
    lead = request.get_json()
    if lead is None:
        return jsonify({"error": "Please send lead data as JSON"}), 400

    result = score_lead(lead)
    result["explanation"], result["explanation_type"] = get_explanation(result)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
