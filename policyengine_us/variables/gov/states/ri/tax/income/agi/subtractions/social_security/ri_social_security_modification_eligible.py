from policyengine_us.model_api import *


class ri_social_security_modification_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Rhode Island Social Security Modification"
    definition_period = YEAR
    reference = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/Social%20Security%20Worksheet_w.pdf"
    # MODIFICATION FOR TAXABLE SOCIAL SECURITY INCOME WORKSHEET STEP 1: Eligibility
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        birth_year = tax_unit("older_spouse_birth_year", period)

        p = parameters(
            period
        ).gov.states.ri.tax.income.agi.subtractions.social_security.limit

        # Age eligibility.
        aged = birth_year <= p.birth_year
        head_or_spouse = tax_unit.any(person("is_tax_unit_head_or_spouse", period))
        aged_head_or_spouse = (aged & head_or_spouse)

        # Income eligibility.
        income_limit = p.income[filing_status]
        income_eligible = income < income_limit

        return aged_head_or_spouse & income_eligible
