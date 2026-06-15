from policyengine_us.model_api import *


class ri_social_security_modification_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Rhode Island Social Security Modification"
    definition_period = YEAR
    reference = [
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/Social%20Security%20Worksheet_w.pdf",
        "https://webserver.rilegislature.gov/BillText/BillText26/HouseText26/H7127Aaa.html#:~:text=For%20the%20tax%20years%20beginning%20on%20or%20after%20January%201%2C%202027",
    ]
    # MODIFICATION FOR TAXABLE SOCIAL SECURITY INCOME WORKSHEET STEP 1: Eligibility
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        birth_year = tax_unit("older_spouse_birth_year", period)

        p = parameters(
            period
        ).gov.states.ri.tax.income.agi.subtractions.social_security.limit

        # The 2027 budget bill removes the age condition for Social Security.
        age_eligible = (birth_year <= p.birth_year) | (period.start.year >= 2027)

        # Income eligibility.
        income_limit = p.income[filing_status]
        income_eligible = income < income_limit

        return age_eligible & income_eligible
