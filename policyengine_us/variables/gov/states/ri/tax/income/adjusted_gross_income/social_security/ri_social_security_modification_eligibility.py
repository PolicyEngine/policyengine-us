from policyengine_us.model_api import *


class ri_social_security_modification_eligibility(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island Social Security Modification Eligibility"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/Social%20Security%20Worksheet_w.pdf"
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        age = person("age", period)
        birth_year = period.start.year - age

        p = parameters(
            period
        ).gov.states.ri.tax.income.adjusted_gross_income.subtractions.social_security

        # Age-based eligibility.
        age_conditions = birth_year <= p.birth_date_limit
        head_eligible = age_conditions & is_head
        spouse_eligible = age_conditions & is_spouse
        age_is_eligible = head_eligible | spouse_eligible

        # Status eligibility.
        status_is_eligible = income < p.income_amount[filing_status]

        return tax_unit.max(age_is_eligible & status_is_eligible)
