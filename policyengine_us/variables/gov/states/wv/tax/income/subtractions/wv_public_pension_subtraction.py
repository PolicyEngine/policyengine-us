from policyengine_us.model_api import *


class wv_public_pension_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia public pension subtraction"
    defined_for = StateCode.WV
    unit = USD
    definition_period = YEAR
    reference = "https://code.wvlegislature.gov/11-21-12/"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # "benefits received under any federal retirement system to which Title 4 U.S.C. §111 applies"
        # https://www.law.cornell.edu/uscode/text/4/111
        federal_pension_income = person(
            "taxable_federal_pension_income", period
        )
        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.public_pension
        person_capped = min_(federal_pension_income, p.max_amount)
        # Only applies to head and spouse.
        head_spouse_capped = person_capped * ~person(
            "is_tax_unit_dependent", period
        )
        return tax_unit.sum(head_spouse_capped)
