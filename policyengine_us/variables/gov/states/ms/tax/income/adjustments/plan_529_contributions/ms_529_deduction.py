from policyengine_us.model_api import *


class ms_529_deduction(Variable):
    value_type = float
    entity = Person
    label = "Mississippi 529 plan contribution adjustment"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/mississippi/2022/title-27/chapter-7/article-1/section-27-7-18/",
        "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100251%202.pdf#page=12",
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ms.tax.income.adjustments.plan_529_contributions
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
