from policyengine_us.model_api import *


class qualified_business_income_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Qualified business income deduction for each person"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/199A#b_1",
        "https://www.irs.gov/pub/irs-prior/p535--2018.pdf",
    )

    def formula(person, period, parameters):
        # Allocate the business income deduction to the head and spouse
        # based on their share of per cap qualified business income deduction
        # amount. The deduction is theirs alone, so a tax unit dependent's
        # share is zero.
        filer = ~person("is_tax_unit_dependent", period)
        qbid_amt = person("qbid_amount", period) * filer
        total_qbid_amount = person.tax_unit.sum(qbid_amt)
        total_deduction_amount = person.tax_unit(
            "qualified_business_income_deduction", period
        )
        deduction_fraction = np.zeros_like(total_qbid_amount)
        mask = total_qbid_amount != 0
        deduction_fraction[mask] = qbid_amt[mask] / total_qbid_amount[mask]
        return deduction_fraction * total_deduction_amount
