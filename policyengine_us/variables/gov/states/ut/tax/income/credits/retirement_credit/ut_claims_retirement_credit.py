from policyengine_us.model_api import *


class ut_claims_retirement_credit(Variable):
    value_type = bool
    entity = TaxUnit
    label = "claims the Utah retirement credit"
    unit = USD
    documentation = (
        "A Utah filer who claims the retirement credit cannot also claim the "
        "Social Security benefits credit or the military retirement credit, "
        "but can claim those two together. We assume the filer takes whichever "
        "option is worth more, and never claims a retirement credit worth "
        "nothing."
    )
    reference = (
        # Each section's subsection (3)(b) bars its credit alongside the
        # retirement credit; nothing bars 59-10-1042 with 59-10-1043.
        "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1019.html",
        "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1042.html",
        "https://le.utah.gov/xcode/Title59/Chapter10/59-10-S1043.html",
        "https://files.tax.utah.gov/tax/forms/2025/tc-40inst.pdf#page=21",
        "https://files.tax.utah.gov/tax/forms/2025/tc-40inst.pdf#page=23",
    )
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        retirement_credit = tax_unit("ut_retirement_credit_max", period)
        # The Social Security benefits credit and the military retirement
        # credit can be claimed together, so the retirement credit competes
        # with their sum.
        alternative_credits = add(
            tax_unit,
            period,
            ["ut_ss_benefits_credit_max", "ut_military_retirement_credit_max"],
        )
        return (retirement_credit > 0) & (retirement_credit >= alternative_credits)
