from policyengine_us.model_api import *


class qualified_business_income_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Qualified business income deduction for each person"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/199A#b_1"
        "https://www.irs.gov/pub/irs-prior/p535--2018.pdf"
    )

    def formula(person, period, parameters):
        business_income = person("qualified_business_income", period)
        total_business_income = person.tax_unit.sum(business_income)
        deduction_amount = person.tax_unit(
            "qualified_business_income_deduction", period
        )
        ded_fraction = np.zeros_like(total_business_income)
        mask = total_business_income != 0
        ded_fraction[mask] = (
            business_income[mask] / total_business_income[mask]
        )
        return deduction_amount * ded_fraction
