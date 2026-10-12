from policyengine_us.model_api import *


class me_pro_forma_childless_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine pro forma federal EITC for the childless age expansion"
    unit = USD
    documentation = (
        "Federal earned income credit recomputed for the 18-24 childless "
        "cohort Maine restores under 36 M.R.S. § 5219-S(5)-(6), ignoring the "
        "federal minimum-age floor. All other federal § 32 requirements "
        "(earnings, phase-out, investment income, taxpayer identification) "
        "still apply."
    )
    definition_period = YEAR
    reference = "https://legislature.maine.gov/statutes/36/title36sec5219-S.html"
    defined_for = "me_childless_eitc_age_eligible"

    def formula(tax_unit, period, parameters):
        # § 5219-S(5): the credit "must be calculated in the same manner as it
        # would be calculated if that individual were eligible for a federal
        # earned income credit." The federal phase-in and reduction amounts are
        # age-independent, so the pro forma equals the ordinary federal EITC
        # computation with the demographic (age) gate dropped, retaining the
        # investment-income and identification (SSN) requirements of § 32.
        phased_in = tax_unit("eitc_phased_in", period)
        maximum = tax_unit("eitc_maximum", period)
        reduction = tax_unit("eitc_reduction", period)
        investment_eligible = tax_unit("eitc_investment_income_eligible", period)
        filer_has_ssn = tax_unit("filer_meets_eitc_identification_requirements", period)
        return (
            min_(phased_in, max_(0, maximum - reduction))
            * investment_eligible
            * filer_has_ssn
        )
