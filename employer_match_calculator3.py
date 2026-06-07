def get_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("  Please enter a number (e.g. 60000 or 4.5)")

def get_int(prompt, options):
    while True:
        try:
            val = int(input(prompt))
            if val in options:
                return val
            print(f"  Please enter one of: {options}")
        except ValueError:
            print(f"  Please enter one of: {options}")

IRS_LIMIT_2025 = 23500

print("=" * 55)
print("       EMPLOYER 401(k) MATCH CALCULATOR")
print("=" * 55)
print()

# ── INPUTS ──────────────────────────────────────────────
print("-- Your Information --")
salary = get_float("Annual salary ($): ")

print()
print("-- Pay Schedule --")
print("  1 = Weekly (52 paychecks/year)")
print("  2 = Bi-weekly (26 paychecks/year)")
print("  3 = Semi-monthly (24 paychecks/year)")
print("  4 = Monthly (12 paychecks/year)")
freq_choice = get_int("Pay frequency (1/2/3/4): ", [1, 2, 3, 4])
freq_map = {1: 52, 2: 26, 3: 24, 4: 12}
freq_label = {1: "weekly", 2: "bi-weekly", 3: "semi-monthly", 4: "monthly"}
paychecks_per_year = freq_map[freq_choice]

# ── TAX ─────────────────────────────────────────────────
print()
print("-- Tax Information --")
print("  Your 401(k) contribution is pre-tax, meaning it")
print("  reduces your taxable income each paycheck.")
print("  Enter your combined tax rate (federal + state).")
print("  Not sure? A common estimate is 22-30%.")
tax_rate = get_float("Your combined tax rate (%): ")

# ── MATCH TYPE ───────────────────────────────────────────
print()
print("-- Employer Match Type --")
print("  1 = Straight match  (e.g. 100% up to 4% of salary)")
print("  2 = Tiered match    (e.g. 100% on first 3%, then 50% on next 2%)")
match_type = get_int("Match type (1/2): ", [1, 2])

tiers = []

if match_type == 1:
    print()
    print("  Example: employer matches 100% of your contribution")
    print("  up to 4% of your salary.")
    match_rate = get_float("  Employer match rate (e.g. 100 for 100%, 50 for 50%): ")
    cap = get_float("  Up to what % of your salary? (e.g. 4): ")
    tiers.append((match_rate, cap))

else:
    print()
    print("  Enter each tier one at a time.")
    print("  Example tier 1: 100% match on first 3% of salary")
    print("  Example tier 2:  50% match on next  2% of salary")
    print()
    while True:
        tier_num = len(tiers) + 1
        print(f"  -- Tier {tier_num} --")
        match_rate = get_float(f"  Match rate for tier {tier_num} (e.g. 100 or 50): ")
        cap = get_float(f"  Applies to the next __% of your salary (e.g. 3): ")
        tiers.append((match_rate, cap))
        print()
        another = input("  Add another tier? (yes/no): ").strip().lower()
        if another not in ("yes", "y"):
            break
        print()

# ── CALCULATIONS ─────────────────────────────────────────

required_contribution_pct    = sum(cap for _, cap in tiers)
required_contribution_annual = salary * (required_contribution_pct / 100)

total_employer_annual = sum(
    salary * (cap / 100) * (rate / 100)
    for rate, cap in tiers
)

required_per_check = required_contribution_annual / paychecks_per_year
employer_per_check = total_employer_annual / paychecks_per_year
total_per_check    = required_per_check + employer_per_check

# Tax impact
# 401(k) contributions are pre-tax, so they reduce taxable income
# Tax saved = contribution * tax rate (you don't pay tax on that money now)
tax_saved_per_check    = required_per_check * (tax_rate / 100)
# True out-of-pocket cost = contribution minus the tax you save
actual_cost_per_check  = required_per_check - tax_saved_per_check
tax_saved_annual       = required_contribution_annual * (tax_rate / 100)
actual_cost_annual     = required_contribution_annual - tax_saved_annual

irs_warning = required_contribution_annual > IRS_LIMIT_2025

# ── OUTPUT ───────────────────────────────────────────────
print()
print("=" * 55)
print("       RESULTS")
print("=" * 55)

print()
print("-- What You Need to Contribute --")
print(f"  To receive the full employer match,")
print(f"  you must contribute {required_contribution_pct:.2f}% of your salary.")
print()
print(f"  Required annual contribution:          ${required_contribution_annual:>12,.2f}")
print(f"  Required per {freq_label[freq_choice]} paycheck:         ${required_per_check:>12,.2f}")

print()
print("-- What You Will Receive --")
if match_type == 2:
    print("  Tier breakdown:")
    for i, (rate, cap) in enumerate(tiers, 1):
        tier_employer = salary * (cap / 100) * (rate / 100)
        print(f"    Tier {i}: {rate:.0f}% match on {cap:.1f}% of salary  ->  ${tier_employer:,.2f}/yr")
    print()
print(f"  Total employer match per year:         ${total_employer_annual:>12,.2f}")
print(f"  Employer match per {freq_label[freq_choice]} paycheck:   ${employer_per_check:>12,.2f}")

print()
print("-- Combined Total (before tax) --")
print(f"  Your contribution + employer match:")
print(f"  Per {freq_label[freq_choice]} paycheck:                  ${total_per_check:>12,.2f}")
print(f"  Per year:                              ${required_contribution_annual + total_employer_annual:>12,.2f}")

print()
print(f"-- Paycheck Impact After Tax ({tax_rate:.0f}% rate) --")
print(f"  Because 401(k) contributions are pre-tax,")
print(f"  you avoid paying tax on that money now.")
print()
print(f"  Gross contribution per {freq_label[freq_choice]} check:  ${required_per_check:>12,.2f}")
print(f"  Tax saved per {freq_label[freq_choice]} check:           ${tax_saved_per_check:>12,.2f}")
print(f"  -----------------------------------------------")
print(f"  Actual paycheck reduction:             ${actual_cost_per_check:>12,.2f}")
print()
print(f"  In other words: contributing ${required_per_check:,.2f}")
print(f"  per {freq_label[freq_choice]} check only costs you ${actual_cost_per_check:,.2f}")
print(f"  out of pocket after the tax benefit.")
print()
print(f"  Annual tax saved:                      ${tax_saved_annual:>12,.2f}")
print(f"  Actual annual out-of-pocket cost:      ${actual_cost_annual:>12,.2f}")

if irs_warning:
    print()
    print("  WARNING: The required contribution of")
    print(f"  ${required_contribution_annual:,.2f} exceeds the 2025 IRS 401(k)")
    print(f"  annual limit of ${IRS_LIMIT_2025:,}. Verify with your")
    print("  plan administrator.")

print()
print("=" * 55)
print("  Note: This calculator assumes you are starting")
print("  with a $0 balance and shows only what is needed")
print("  to receive the full employer match.")
print("  Tax savings shown are estimates. Consult a tax")
print("  professional for personalized advice.")
print("=" * 55)
print()
