from policyengine_us.model_api import *


class ct_child_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut child tax rebate"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CT
    reference = (
        "https://cga.ct.gov/2022/ACT/PA/PDF/2022PA-00118-R00HB-05506-PA.PDF#page=549",
        "https://portal.ct.gov/-/media/drs/publications/tssb/2022/tssb-2022-5.pdf",
    )

    def formula(tax_unit, period, parameters):
        income = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ct.tax.income.rebate

        reduction_start = p.reduction.start[filing_status]

        person = tax_unit.members
        age = person("age", period)
        dependent = person("is_tax_unit_dependent", period)
        eligible_child = (age <= p.age_limit) & dependent
        count_children = tax_unit.sum(eligible_child)
        capped_children = min_(count_children, p.child_cap)
        total_rebate = capped_children * p.amount

        excess = max_(income - reduction_start, 0)
        increments = np.ceil(excess / p.reduction.increment)
        reduction_share = min_(increments * p.reduction.rate, 1)

        return total_rebate * (1 - reduction_share)
