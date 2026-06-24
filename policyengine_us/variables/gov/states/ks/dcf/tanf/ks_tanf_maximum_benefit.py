from policyengine_us.model_api import *


class ks_tanf_maximum_benefit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Kansas TANF maximum benefit amount"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-100",
        "https://www.law.cornell.edu/regulations/kansas/K-A-R-30-4-101",
    )
    defined_for = StateCode.KS

    def formula(spm_unit, period, parameters):
        # Per K.A.R. 30-4-100 and K.A.R. 30-4-101:
        # Payment standard = basic standard (by assistance unit size) + shelter
        # allowance (by county group). The assistance unit size excludes SSI
        # recipients (KEESM 4113). We use the non-shared (F-4) standards; we
        # don't track shared-living arrangements (F-5, lower) at the moment.
        p = parameters(period).gov.states.ks.dcf.tanf
        unit_size = spm_unit("ks_tanf_assistance_unit_size", period.this_year)
        capped_size = min_(unit_size, p.max_family_size_in_table)
        additional_people = max_(unit_size - p.max_family_size_in_table, 0)
        basic_standard = (
            p.payment_standard.basic_standard[capped_size]
            + additional_people * p.payment_standard.additional_person_amount
        )
        county_group = spm_unit("ks_tanf_county_group", period.this_year)
        shelter_allowance = p.payment_standard.shelter_allowance[county_group]
        return basic_standard + shelter_allowance
