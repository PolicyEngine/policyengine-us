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
        # determine count of KCCATC age eligible children
        person = tax_unit.members
        is_dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        kccatc_age_eligible = is_dependent & (age <= p.kccatc.max_age)
        kccatc_eligible_count = tax_unit.sum(kccatc_age_eligible)
        # determine count of federal CDCC age eligible children
        cdcc = parameters(period).gov.irs.credits.cdcc.eligibility
        cdcc_age_eligible = is_dependent & (age < cdcc.child_age)
        cdcc_eligible_count = tax_unit.sum(cdcc_age_eligible)
        # calculate KCCATC amount
        max_kccatc = kccatc_eligible_count * p.kccatc.max_amount
        total_care_expenses = tax_unit("tax_unit_childcare_expenses", period)
        ratio = np.zeros_like(cdcc_eligible_count)
        mask = cdcc_eligible_count > 0
        ratio[mask] = kccatc_eligible_count[mask] / cdcc_eligible_count[mask]
        kccatc_care_expenses = total_care_expenses * ratio
        kccatc = min_(kccatc_care_expenses, max_kccatc)
        # return calculated kccatc amount if income eligible
        return income_eligible * kccatc
