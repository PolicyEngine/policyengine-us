from policyengine_us.model_api import *


class ks_tanf_max_benefit_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kansas TANF maximum benefit standard (CBPP convention)"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-100",
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-101",
        "https://www.cbpp.org/research/family-income-support/tanf-benefits-remain-low-despite-recent-increases-in-some-states",
    )
    defined_for = StateCode.KS
    documentation = """
    Returns the Group IV non-shared-living payment standard (basic standard +
    $135 shelter), matching the CBPP and Welfare Rules Database convention for
    cross-state comparison. Group IV covers Johnson County, the most populous in
    Kansas. Unlike ks_tanf_maximum_benefit, this figure always uses the Group IV
    shelter allowance and the full household size, independent of the
    household's actual county or SSI status.
    """

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ks.dcf.tanf
        unit_size = spm_unit("spm_unit_size", period.this_year)
        capped_size = min_(unit_size, p.max_family_size_in_table)
        additional_people = max_(unit_size - p.max_family_size_in_table, 0)
        basic_standard = (
            p.payment_standard.basic_standard[capped_size]
            + additional_people * p.payment_standard.additional_person_amount
        )
        # CBPP convention: most populous county (Group IV) shelter allowance.
        shelter_allowance = p.payment_standard.shelter_allowance.GROUP_IV
        return basic_standard + shelter_allowance
