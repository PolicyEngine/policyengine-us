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
        # Allocate the business income deduction to each person in the tax unit
        # based on their share of per cap qualified business income deduction amount
        qbid_amt = person("qbid_amount", period)
        total_qbid_amount = person.tax_unit.sum(qbid_amt)
        total_deduction_amount = person.tax_unit(
            "qualified_business_income_deduction", period
        )
        deduction_fraction = np.zeros_like(total_qbid_amount)
        qbid_mask = total_qbid_amount != 0
        deduction_fraction[qbid_mask] = (
            qbid_amt[qbid_mask] / total_qbid_amount[qbid_mask]
        )

        # A floor-only deduction can have no ordinary per-person QBID amount.
        # In that case, allocate the §199A(i) floor by active-QBI shares.
        active_qbi = person("active_qualified_business_income", period)
        total_active_qbi = person.tax_unit.sum(active_qbi)
        active_qbi_mask = (
            (total_qbid_amount == 0)
            & (total_deduction_amount > 0)
            & (total_active_qbi != 0)
        )
        deduction_fraction[active_qbi_mask] = (
            active_qbi[active_qbi_mask] / total_active_qbi[active_qbi_mask]
        )
        return deduction_fraction * total_deduction_amount
