from flask import Flask, render_template, request

app = Flask(__name__)

IRS_LIMIT_2025 = 23500

@app.route("/", methods=["GET", "POST"])
def index():
    results = None
    error = None

    if request.method == "POST":
        try:
            salary        = float(request.form["salary"])
            freq          = int(request.form["freq"])
            tax_rate      = float(request.form["tax_rate"])
            match_type    = request.form["match_type"]

            freq_map   = {52: "weekly", 26: "bi-weekly", 24: "semi-monthly", 12: "monthly"}
            paychecks  = freq

            # Build tiers
            tiers = []
            if match_type == "straight":
                match_rate = float(request.form["match_rate"])
                match_cap  = float(request.form["match_cap"])
                tiers.append((match_rate, match_cap))
            else:
                rates = request.form.getlist("tier_rate[]")
                caps  = request.form.getlist("tier_cap[]")
                for r, c in zip(rates, caps):
                    if r and c:
                        tiers.append((float(r), float(c)))

            if not tiers:
                raise ValueError("Please enter at least one match tier.")

            # Core calculations
            required_pct    = sum(cap for _, cap in tiers)
            required_annual = salary * (required_pct / 100)
            employer_annual = sum(salary * (cap / 100) * (rate / 100) for rate, cap in tiers)

            required_per_check = required_annual / paychecks
            employer_per_check = employer_annual / paychecks
            total_per_check    = required_per_check + employer_per_check

            # Tax
            tax_saved_per_check   = required_per_check * (tax_rate / 100)
            actual_cost_per_check = required_per_check - tax_saved_per_check
            tax_saved_annual      = required_annual * (tax_rate / 100)
            actual_cost_annual    = required_annual - tax_saved_annual

            irs_warning = required_annual > IRS_LIMIT_2025

            # Tier breakdown for display
            tier_breakdown = []
            for i, (rate, cap) in enumerate(tiers, 1):
                tier_employer = salary * (cap / 100) * (rate / 100)
                tier_breakdown.append({
                    "num": i,
                    "rate": rate,
                    "cap": cap,
                    "employer_annual": tier_employer,
                })

            results = {
                "freq_label":           freq_map.get(paychecks, "per paycheck"),
                "required_pct":         round(required_pct, 2),
                "required_annual":      round(required_annual, 2),
                "required_per_check":   round(required_per_check, 2),
                "employer_annual":      round(employer_annual, 2),
                "employer_per_check":   round(employer_per_check, 2),
                "total_per_check":      round(total_per_check, 2),
                "total_annual":         round(required_annual + employer_annual, 2),
                "tax_rate":             tax_rate,
                "tax_saved_per_check":  round(tax_saved_per_check, 2),
                "actual_cost_per_check":round(actual_cost_per_check, 2),
                "tax_saved_annual":     round(tax_saved_annual, 2),
                "actual_cost_annual":   round(actual_cost_annual, 2),
                "irs_warning":          irs_warning,
                "match_type":           match_type,
                "tier_breakdown":       tier_breakdown,
            }

        except ValueError as e:
            error = str(e) if str(e) else "Please check your inputs and try again."

    return render_template("index.html", results=results, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
