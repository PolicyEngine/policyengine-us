from policyengine_us.model_api import *


class ca_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "California CalWORKs Cash Benefit"
    unit = USD
    definition_period = YEAR
    defined_for = "ca_tanf_eligible"

    def formula(spm_unit, period, parameters):
        maximum_payment = spm_unit("ca_tanf_maximum_payment", period)
        countable_income = spm_unit(
            "ca_tanf_countable_income_recipient", period
        )
        person = spm_unit.members
        eligible_people_based_on_immigration_status = spm_unit.sum(
            person("ca_tanf_immigration_status_eligible_person", period)
        )
        spm_unit_size = spm_unit("spm_unit_size", period)
        prorated_fraction = np.zeros_like(spm_unit_size, dtype=float)
        mask = spm_unit_size != 0
        prorated_fraction[mask] = (
            eligible_people_based_on_immigration_status[mask]
            / spm_unit_size[mask]
        )
        return prorated_fraction * max_(maximum_payment - countable_income, 0)
