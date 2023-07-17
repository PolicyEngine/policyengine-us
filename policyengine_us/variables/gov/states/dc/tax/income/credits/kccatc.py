from policyengine_us.model_api import *


class dc_kccatc(Variable):
    value_type = float
    entity = TaxUnit
    label = "DC keep child care affordable tax credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/52926_D-40_12.21.21_Final_Rev011122.pdf#page=67"
        "https://otr.cfo.dc.gov/sites/default/files/dc/sites/otr/publication/attachments/2022_D-40_Booklet_Final_blk_01_23_23_Ordc.pdf#page=59"
    )
    defined_for = StateCode.DC

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.dc.tax.income.credits
        # determine tax unit's income eligibility status
        taxinc = tax_unit("dc_taxable_income_joint", period)
        filing_status = tax_unit("filing_status", period)
        income_eligible = taxinc <= p.kccatc.income_limit[filing_status]
        # determine count of age eligible children
        person = tax_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        age_eligible = is_dependent & (age <= p.kccatc.max_age)
        eligible_child_count = tax_unit.sum(age_eligible)
        # calculate KCCATC amount
        max_kccatc = eligible_child_count * p.kccatc.max_amount
        total_care_expenses = tax_unit("tax_unit_childcare_expenses", period)
        kccatc = min_(total_care_expenses, max_kccatc)
        # return calculated kccatc amount if income eligible
        return income_eligible * kccatc
