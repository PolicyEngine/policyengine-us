from policyengine_us.model_api import *


class ri_taxable_retirement_income_subtraction_eligibility(Variable):
    value_type = bool
    entity = TaxUnit
    label = (
        "Eligible for the Rhode Island taxable retirement income subtraction"
    )
    definition_period = YEAR
    reference = "http://webserver.rilin.state.ri.us/Statutes/title44/44-30/44-30-12.HTM"
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        age = tax_unit.members("age", period)
        birth_year = -(age - period.start.year)

        p = parameters(
            period
        ).gov.states.ri.tax.income.adjusted_gross_income.subtractions

        # Age-based eligibility.
        age_conditions = birth_year <= p.social_security.birth_date_limit
        # Status eligibility.
        status_is_eligible = (
            income < p.social_security.income_threshold[filing_status]
        )

        return age_conditions & status_is_eligible
