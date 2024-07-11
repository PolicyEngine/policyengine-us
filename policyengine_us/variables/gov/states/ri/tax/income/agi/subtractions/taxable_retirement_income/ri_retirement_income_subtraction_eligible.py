from policyengine_us.model_api import *


class ri_retirement_income_subtraction_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Rhode Island retirement income subtraction"
    definition_period = YEAR
    reference = "http://webserver.rilin.state.ri.us/Statutes/title44/44-30/44-30-12.HTM"
    # Eligibility is the same as Social Security's eligibility
    # https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/Social%20Security%20Worksheet_w.pdf
    # STEP 1: Eligibility
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        older_spouse_birth_year = tax_unit("older_spouse_birth_year", period)

        p_ss = parameters(
            period
        ).gov.states.ri.tax.income.agi.subtractions.social_security.limit
        age_eligible = older_spouse_birth_year <= p_ss.birth_year

        # Income eligibility.
        p_tri = parameters(
            period
        ).gov.states.ri.tax.income.agi.subtractions.taxable_retirement_income
        income_eligible = income < p_tri.income_limit[filing_status]

        return age_eligible & income_eligible
