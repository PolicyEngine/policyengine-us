from policyengine_us.model_api import *
from numpy import ceil


class mn_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota exemptions amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2023-12/m1_21_0.pdf",
        "https://www.revenue.state.mn.us/sites/default/files/2023-12/m1_inst_21.pdf",
        "https://www.revenue.state.mn.us/sites/default/files/2023-12/m1_22.pdf",
        "https://www.revenue.state.mn.us/sites/default/files/2024-02/m1-inst-22.pdf",
        "https://www.revisor.mn.gov/statutes/cite/290.0121",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        # Minn. Stat. 290.0121 allows an exemption for each dependent "as
        # defined in sections 151 and 152 of the Internal Revenue Code".
        # Under IRC 152(b)(1) a return on which the filer, or on a joint
        # return either spouse, can be claimed as a dependent has none (the
        # Form M1 instructions say to leave line 5 blank).
        dependents = tax_unit("tax_unit_dependents", period)
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        allowed_dependents = where(filer_is_dependent, 0, dependents)
        p = parameters(period).gov.states.mn.tax.income.exemptions
        exemptions = p.amount * allowed_dependents
        # limit exemptions if federal AGI is above a threshold
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        excess_agi = max_(0, agi - p.agi_threshold[filing_status])
        steps = ceil(excess_agi / p.agi_step_size[filing_status])
        offset_fraction = p.agi_step_fraction * steps
        offset = offset_fraction * exemptions
        return max_(0, exemptions - offset)
