from policyengine_us.model_api import *


class wv_public_pension_subtraction_person(Variable):
    value_type = float
    entity = Person
    label = "West Virginia public pension subtraction for each person"
    defined_for = StateCode.WV
    unit = USD
    definition_period = YEAR
    reference = "https://code.wvlegislature.gov/11-21-12/"

    def formula(person, period, parameters):
        # "benefits received under any federal retirement system to which Title 4 U.S.C. §111 applies"
        # https://www.law.cornell.edu/uscode/text/4/111
        federal_pension_income = person(
            "taxable_federal_pension_income", period
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.public_pension
        capped = min_(federal_pension_income, p.max_amount)
        return capped * head_or_spouse
