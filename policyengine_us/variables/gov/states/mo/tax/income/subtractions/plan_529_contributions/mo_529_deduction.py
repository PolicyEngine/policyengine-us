from policyengine_us.model_api import *


class mo_529_deduction(Variable):
    value_type = float
    entity = Person
    label = "Missouri 529 plan contribution subtraction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revisor.mo.gov/main/OneSection.aspx?section=143.121",
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2025.pdf#page=12",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.mo.tax.income.subtractions.plan_529_contributions
        # Get the TaxUnit-level deduction cap
        filing_status = person.tax_unit("filing_status", period)
        cap = p.cap[filing_status]
        total_contributions = person.tax_unit("investment_in_529_plan", period)
        unit_deduction = min_(total_contributions, cap)
        # Allocate proportionally to each person
        person_contributions = person("investment_in_529_plan_indv", period)
        total = person.tax_unit.sum(person_contributions)
        share = np.zeros_like(total)
        mask = total != 0
        share[mask] = person_contributions[mask] / total[mask]
        return share * unit_deduction
