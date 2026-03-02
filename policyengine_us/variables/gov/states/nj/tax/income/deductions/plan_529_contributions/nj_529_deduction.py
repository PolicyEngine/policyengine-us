from policyengine_us.model_api import *


class nj_529_deduction(Variable):
    value_type = float
    entity = Person
    label = "New Jersey 529 plan contribution deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.njleg.state.nj.us/bill-search/2020/A5535",
        "https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.nj.tax.income.deductions.plan_529_contributions
        # Check AGI income limit
        agi = person.tax_unit("adjusted_gross_income", period)
        income_eligible = agi <= p.income_limit
        # Get the TaxUnit-level deduction cap
        total_contributions = person.tax_unit("investment_in_529_plan", period)
        unit_deduction = min_(total_contributions, p.cap)
        # Allocate proportionally to each person
        person_contributions = person("investment_in_529_plan_indv", period)
        total = person.tax_unit.sum(person_contributions)
        share = np.zeros_like(total)
        mask = total != 0
        share[mask] = person_contributions[mask] / total[mask]
        return where(income_eligible, share * unit_deduction, 0)
