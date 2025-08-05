from flask import Flask, render_template, request, send_from_directory, flash
from docxtpl import DocxTemplate
import os
from datetime import datetime, timedelta

app = Flask(__name__)
UPLOAD_FOLDER = "generated"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.secret_key = "change_this_to_a_secure_random_key"  # Required for flashing messages

@app.route("/", methods=["GET", "POST"])
def generate_proposal():
    success = False
    download_link = None

    firm_types = [
        "Investment Fund", "Broker", "Investment Advisor",
        "Corporate Finance/Investment Bank", "EMI Firm"
    ]
    single_services = [
        "Governance and SMCR Review",
        "Compliance Monitoring Programme Review",
        "Policies and Procedures Gap Analysis",
        "Attestations and Training Records Check",
        "Financial Promotions Compliance Review",
        "Market Abuse and Personal Account Dealing Controls Review",
        "Regulatory Filings and Reporting Check",
        "Client Onboarding and Anti-Money Laundering Review",
        "Regulatory Change Management Assessment",
        "Breach, Complaints, and Incident Management Review"
    ]
    bundled_services = ["Compliance Healthcheck"]
    firm_specific_services = ["FCA EMI Authorisation"]

    if request.method == "POST":
        # Core fields
        client_name = request.form.get("client_name") or request.form.get("clientName") or "N/A"
        firm_type = request.form.get("firm_type") or request.form.get("firmType") or "N/A"
        jurisdiction = request.form.get("jurisdiction") or "N/A"
        primary_contact_name = request.form.get("primary_contact_name") or request.form.get("clientRep") or "N/A"
        proposal_reference = request.form.get("proposal_reference") or "N/A"

        single_service = request.form.get("single_service") or request.form.get("individualServices") or "N/A"
        bundled_service = request.form.get("bundled_service") or request.form.get("bundleServices") or "N/A"
        firm_specific_service = request.form.get("firm_specific_service") or request.form.get("firmSpecificServices") or "N/A"

        today = datetime.today().strftime("%d/%m/%Y")
        expiry = (datetime.today() + timedelta(days=30)).strftime("%d/%m/%Y")

        context = {
            "client_name": client_name,
            "firm_type": firm_type,
            "jurisdiction": jurisdiction,
            "primary_contact_name": primary_contact_name,
            "proposal_date": today,
            "proposal_expiry_date": expiry,
            "proposal_reference": proposal_reference,
            "service_provider_name": "IQ-EQ",
            "proposal_validity_period": "30 days",
            "single_service": single_service,
            "bundled_service": bundled_service,
            "firm_specific_service": firm_specific_service
        }

        # Only generate for known bundles/services
        template_file = None
        filename = None

        # --- HEALTHCHECK BUNDLE ---
        if bundled_service == "Compliance Healthcheck":
            context.update({
                "phase_1_duration": request.form.get("phase_1_duration") or "N/A",
                "phase_2_duration": request.form.get("phase_2_duration") or "N/A",
                "phase_3_duration": request.form.get("phase_3_duration") or "N/A",
                "phase_4_duration": request.form.get("phase_4_duration") or "N/A",
                "total_duration": request.form.get("total_duration") or "N/A",

                "project_lead_name": request.form.get("project_lead_name") or "N/A",
                "project_lead_credentials": request.form.get("project_lead_credentials") or "N/A",
                "project_lead_experience": request.form.get("project_lead_experience") or "N/A",
                "senior_consultant_name": request.form.get("senior_consultant_name") or "N/A",
                "senior_consultant_credentials": request.form.get("senior_consultant_credentials") or "N/A",
                "senior_consultant_experience": request.form.get("senior_consultant_experience") or "N/A",
                "additional_team_members": request.form.get("additional_team_members") or "N/A",

                "service_charge": request.form.get("service_charge") or "N/A",
                "hourly_rate": request.form.get("hourly_rate") or "N/A",
                "total_fee": request.form.get("total_fee") or "N/A",
                "payment_terms": request.form.get("payment_terms") or "N/A",

                "primary_contact_title": request.form.get("primary_contact_title") or "N/A",
                "contact_phone": request.form.get("contact_phone") or "N/A",
                "contact_email": request.form.get("contact_email") or "N/A",
                "office_address": request.form.get("office_address") or "N/A",

                "prepared_by_name": request.form.get("prepared_by_name") or "N/A",
                "electronic_signature": request.form.get("electronic_signature") or "N/A",
            })
            template_file = "templates/healthcheck_template.docx"
            filename = f"{client_name} Healthcheck Proposal.docx"

        # --- FCA EMI AUTHORISATION (AEMI) ---
        elif firm_specific_service == "FCA EMI Authorisation":
            context.update({
                "total_indicative_price_range": request.form.get("total_indicative_price_range") or "N/A",
                "stage_1_price": request.form.get("stage_1_price") or "N/A",
                "stage_2_price_range": request.form.get("stage_2_price_range") or "N/A",
                "stage_3_price": request.form.get("stage_3_price") or "N/A",
            })
            template_file = "templates/AEMI_PROPOSAL_TEMPLATE.docx"
            filename = f"{client_name} EMI Authorisation Proposal.docx"

        # No known service selected
        if template_file is None:
            flash("Please select either 'Compliance Healthcheck' or 'FCA EMI Authorisation' to generate a proposal.")
            return render_template(
                "proposal_engine_mixed.html",
                success=success,
                download_link=download_link,
                firm_types=firm_types,
                single_services=single_services,
                bundled_services=bundled_services,
                firm_specific_services=firm_specific_services,
                selected_firm=firm_type
            )

        # Document Generation
        try:
            doc = DocxTemplate(template_file)
            doc.render(context)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            doc.save(filepath)

            success = True
            download_link = f"/download/{filename}"
        except Exception as e:
            flash(f"Error generating document: {e}")
            success = False

        return render_template(
            "proposal_engine_mixed.html",
            success=success,
            download_link=download_link,
            firm_types=firm_types,
            single_services=single_services,
            bundled_services=bundled_services,
            firm_specific_services=firm_specific_services,
            selected_firm=firm_type
        )

    # GET request
    return render_template(
        "proposal_engine_mixed.html",
        success=success,
        download_link=download_link,
        firm_types=firm_types,
        single_services=single_services,
        bundled_services=bundled_services,
        firm_specific_services=firm_specific_services,
        selected_firm=None
    )

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)