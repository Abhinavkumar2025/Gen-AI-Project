"""RentGuard AI - Generative AI Explanation Module

Translates statistical autoencoder reconstruction errors and feature residuals
into plain-language verification guidance for property managers.
Supports Groq API (ultra-fast Llama-3.3 / Llama-3.1) and OpenAI API with
an intelligent deterministic rule-based fallback.
Adheres strictly to fair housing compliance and non-accusatory guidelines.
"""

import os
import json
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()


def generate_rule_based_explanation(
    app_data: Dict[str, Any],
    reconstruction_error: float,
    anomaly_category: str,
    top_contributions: Dict[str, float]
) -> Dict[str, Any]:
    """
    Deterministic rule-based fallback generating actionable verification instructions
    without requiring external LLM API access.
    """
    income = float(app_data.get("monthly_income", 0))
    rent = float(app_data.get("monthly_rent", 0))
    credit = int(app_data.get("credit_score", 0))
    evictions = int(app_data.get("previous_evictions", 0))
    loans = int(app_data.get("existing_loans", 0))
    emp_status = str(app_data.get("employment_status", ""))
    emp_dur = float(app_data.get("employment_duration", 0))
    rent_hist = float(app_data.get("rental_history_duration", 0))
    prev_res = int(app_data.get("previous_residences", 0))
    
    rent_to_income = (rent / income * 100) if income > 0 else 999.0
    
    patterns = []
    fields_to_verify = []
    steps = []
    
    # 1. Rent-to-Income / Affordability checks
    if rent_to_income > 45.0:
        patterns.append(
            f"The requested monthly rent (${rent:,.2f}) accounts for {rent_to_income:.1f}% of stated monthly income (${income:,.2f}), "
            f"which deviates from standard affordability benchmarks (typically ≤ 30-35%)."
        )
        fields_to_verify.append("monthly_income")
        fields_to_verify.append("monthly_rent")
        steps.append("Request the last 3 consecutive months of bank statements or official W-2 tax forms.")
        steps.append("Verify if a co-signer, housing voucher, or guarantor is backing the lease.")
        
    # 2. Credit vs Eviction discordance
    if credit >= 750 and evictions > 0:
        patterns.append(
            f"The application pairs a high credit score ({credit}) with reported prior evictions ({evictions}), "
            f"which represents an uncommon combination in historical reference pools."
        )
        fields_to_verify.append("previous_evictions")
        fields_to_verify.append("credit_score")
        steps.append("Perform a court records check to confirm whether previous eviction proceedings were dismissed, settled, or identity misattributions.")
        
    # 3. Employment vs Tenancy mismatch
    if emp_dur > 15.0 and rent_hist < 1.0:
        patterns.append(
            f"Applicant reports long-standing continuous employment ({emp_dur:.1f} years) alongside very brief independent rental history ({rent_hist:.1f} years). "
            f"This often indicates a transition from homeownership, military service, or familial living."
        )
        fields_to_verify.append("rental_history_duration")
        fields_to_verify.append("employment_duration")
        steps.append("Clarify previous living arrangement (e.g., prior home sale, family residence) and contact current HR department for employment confirmation.")
        
    # 4. Residence density
    if prev_res >= 5 and rent_hist <= 2.5:
        patterns.append(
            f"Reports {prev_res} distinct residences within a span of {rent_hist:.1f} years, indicating elevated residential turnover."
        )
        fields_to_verify.append("previous_residences")
        steps.append("Request landlord references for the two most recent residences to corroborate rental dates.")
        
    # 5. Loan stack
    if loans >= 7:
        patterns.append(
            f"Reports {loans} active loan obligations, which is higher than the baseline average."
        )
        fields_to_verify.append("existing_loans")
        steps.append("Review debt-to-income summary to determine monthly net disposable income.")
        
    # 6. Unemployed with luxury rent
    if emp_status == "Unemployed" and rent > 2500:
        patterns.append(
            f"Current employment status is listed as 'Unemployed' with requested rent of ${rent:,.2f}."
        )
        fields_to_verify.append("employment_status")
        fields_to_verify.append("monthly_income")
        steps.append("Obtain proof of liquid assets, trust funds, severance agreements, or corporate relocation stipend.")

    # Deduplicate fields and steps
    fields_to_verify = list(dict.fromkeys(fields_to_verify))
    steps = list(dict.fromkeys(steps))
    
    # If standard statistical variance
    if not patterns:
        if anomaly_category == "Low anomaly":
            patterns.append("Application aligns closely with historical baseline parameters across all modeled dimensions.")
            fields_to_verify = ["General standard document verification"]
            steps = ["Execute routine identity and proof of income checks according to standard operating policy."]
            summary = "Low statistical deviation. The applicant's profile aligns well with typical tenancy guidelines."
        else:
            top_field = list(top_contributions.keys())[0] if top_contributions else "financial metrics"
            patterns.append(
                f"Statistical variation detected primarily in the distribution of '{top_field}', with a reconstruction error of {reconstruction_error:.4f}."
            )
            fields_to_verify = [top_field]
            steps = [f"Conduct standard documentary verification focused on confirming reported {top_field}."]
            summary = f"{anomaly_category} flagged due to statistical variance in {top_field}. Conduct standard manual verification."
    else:
        summary = (
            f"{anomaly_category} review recommended. Primary statistical variances identified across {', '.join(fields_to_verify[:3])}. "
            f"Follow the verification steps below before making a leasing determination."
        )

    return {
        "explanation": "\n".join(patterns),
        "fields_to_verify": fields_to_verify,
        "suggested_steps": steps,
        "manager_summary": summary,
        "source": "RentGuard Deterministic Engine"
    }


def explain_anomaly(
    app_data: Dict[str, Any],
    reconstruction_error: float,
    anomaly_category: str,
    top_contributions: Dict[str, float],
    api_key: Optional[str] = None,
    provider: str = "groq",
    model_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate plain-language explanation and verification checklist using Groq API
    (or OpenAI API), with automatic graceful fallback to the deterministic engine.
    """
    # 1. Resolve credentials & provider
    groq_key = api_key if (provider == "groq" and api_key) else os.getenv("GROQ_API_KEY", "")
    openai_key = api_key if (provider == "openai" and api_key) else os.getenv("OPENAI_API_KEY", "")
    
    # Clean default placeholders
    if groq_key and (groq_key.startswith("gsk_your_groq") or groq_key.strip() == ""):
        groq_key = ""
    if openai_key and (openai_key.startswith("your_openai") or openai_key.strip() == ""):
        openai_key = ""
        
    # Determine active provider
    active_provider = provider
    if provider == "groq" and not groq_key and openai_key:
        active_provider = "openai"
    elif provider == "openai" and not openai_key and groq_key:
        active_provider = "groq"
        
    # If no key available for either, fallback immediately
    if (active_provider == "groq" and not groq_key) or (active_provider == "openai" and not openai_key):
        return generate_rule_based_explanation(app_data, reconstruction_error, anomaly_category, top_contributions)

    # Craft sanitized, minimal payload containing ONLY necessary metrics
    safe_payload = {
        "monthly_income": app_data.get("monthly_income"),
        "monthly_rent": app_data.get("monthly_rent"),
        "credit_score": app_data.get("credit_score"),
        "employment_status": app_data.get("employment_status"),
        "employment_duration_years": app_data.get("employment_duration"),
        "previous_evictions": app_data.get("previous_evictions"),
        "existing_loans": app_data.get("existing_loans"),
        "rental_history_duration_years": app_data.get("rental_history_duration"),
        "previous_residences_count": app_data.get("previous_residences"),
        "model_reconstruction_error": round(float(reconstruction_error), 4),
        "anomaly_category": anomaly_category,
        "feature_contributions_pct": {k: round(v, 2) for k, v in top_contributions.items()}
    }
    
    system_prompt = (
        "You are RentGuard AI's senior real estate underwriting assistant. "
        "Your role is to help property managers understand statistical anomalies in rental applications. "
        "\nCRITICAL COMPLIANCE RULES:\n"
        "1. NEVER state, imply, or accuse an applicant of fraud, dishonesty, or misrepresentation.\n"
        "2. NEVER recommend automatic rejection or denial.\n"
        "3. Clearly state that anomalies represent statistical deviations from a baseline model, not confirmed issues.\n"
        "4. NEVER invent or extrapolate missing facts.\n"
        "5. Provide constructive, practical verification steps (e.g., specific documents to request).\n"
        "6. Return ONLY valid JSON matching this exact schema:\n"
        "{\n"
        '  "explanation": "concise description of why the metrics diverge from baseline",\n'
        '  "fields_to_verify": ["list", "of", "field", "names"],\n'
        '  "suggested_steps": ["actionable", "step", "for", "leasing", "agent"],\n'
        '  "manager_summary": "one-sentence objective summary"\n'
        "}"
    )
    user_prompt = f"Analyze this rental application evaluation:\n{json.dumps(safe_payload, indent=2)}"

    # 2. Try Groq API
    if active_provider == "groq":
        target_model = model_name or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            
            chat_completion = client.chat.completions.create(
                model=target_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=650
            )
            content = chat_completion.choices[0].message.content
            parsed = json.loads(content)
            parsed["source"] = f"Groq ({target_model})"
            return parsed
        except Exception as e:
            print(f"[Explanation Engine] Groq API call failed: {e}. Falling back to deterministic engine.")
            fallback = generate_rule_based_explanation(app_data, reconstruction_error, anomaly_category, top_contributions)
            fallback["source"] = f"RentGuard Deterministic Engine (Fallback: {type(e).__name__})"
            return fallback

    # 3. Try OpenAI API
    if active_provider == "openai":
        target_model = model_name or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_key)
            
            response = client.chat.completions.create(
                model=target_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=650
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            parsed["source"] = f"OpenAI ({target_model})"
            return parsed
        except Exception as e:
            print(f"[Explanation Engine] OpenAI call failed: {e}. Falling back to deterministic engine.")
            fallback = generate_rule_based_explanation(app_data, reconstruction_error, anomaly_category, top_contributions)
            fallback["source"] = f"RentGuard Deterministic Engine (Fallback: {type(e).__name__})"
            return fallback

    return generate_rule_based_explanation(app_data, reconstruction_error, anomaly_category, top_contributions)
