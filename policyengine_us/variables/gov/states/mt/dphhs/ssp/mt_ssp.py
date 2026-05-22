from policyengine_us.model_api import *


class mt_ssp(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana State Supplementation"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MT
    reference = (
        "https://www.law.cornell.edu/regulations/montana/ARM-37-43-101",
        "https://www.law.cornell.edu/regulations/montana/ARM-37-43-102",
        "https://www.law.cornell.edu/regulations/montana/ARM-37-43-103",
        "https://www.law.cornell.edu/regulations/montana/ARM-37-43-104",
        "https://secure.ssa.gov/poms.nsf/lnx/0501415010DEN",
        "https://www.ssa.gov/policy/docs/progdesc/ssi_st_asst/2011/mt.html",
        "https://leg.mt.gov/bills/mca/title_0520/chapter_0010/part_0010/section_0040/0520-0010-0010-0040.html",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members
        eligible = person("mt_ssp_eligible", period)
        couple_per_spouse = person("mt_ssp_couple_per_spouse", period)
        individual = person("mt_ssp_individual", period)
        couple_active = couple_per_spouse > 0
        base_amount = where(couple_active, couple_per_spouse, individual)
        # Residual countable income (federal SSI exhausted) spills onto
        # the state supplement.
        uncapped_ssi = person("uncapped_ssi", period)
        reduction = max_(0, -uncapped_ssi)
        per_person = max_(0, base_amount - reduction) * eligible
        return spm_unit.sum(per_person)
