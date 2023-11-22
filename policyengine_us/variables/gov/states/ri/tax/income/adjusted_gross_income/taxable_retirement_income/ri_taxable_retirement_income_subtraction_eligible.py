from policyengine_us.model_api import *


class ri_taxable_retirement_income_subtraction_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = (
        "Eligible for the Rhode Island taxable retirement income subtraction"
    )
    definition_period = YEAR
    reference = "http://webserver.rilin.state.ri.us/Statutes/title44/44-30/44-30-12.HTM"
    # Eligibility is the same as Social Security's eligibility https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/Social%20Security%20Worksheet_w.pdf STEP 1: Eligibility
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        age = tax_unit.members("age", period)
        birth_year = -(age - period.start.year)

        p = parameters(
            period
        ).gov.states.ri.tax.income.adjusted_gross_income.subtractions.social_security.threshold

        # Age-based eligibility.
        age_conditions = birth_year <= p.birth_year
        age_is_eligible = tax_unit.any(age_conditions & head_or_spouse)

        # Status eligibility.
        status_is_eligible = income < p.income[filing_status]

        return age_is_eligible & status_is_eligible
