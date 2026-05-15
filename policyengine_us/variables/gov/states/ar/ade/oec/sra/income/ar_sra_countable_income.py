from policyengine_us.model_api import *


class ar_sra_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arkansas SRA countable income"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.AR
    reference = (
        "https://dese.ade.arkansas.gov/Files/FSU-Procedural-Manual-June-2023_UPDATED_20230629075344.pdf#page=19",
        "https://dese.ade.arkansas.gov/Files/FSU-Procedural-Manual-June-2023_UPDATED_20230629075344.pdf#page=20",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ar.ade.oec.sra.income
        # FSU Manual Section 4.3.2: SSI and Social Security of children under
        # 18 are excluded from countable income. Sum each listed source per
        # person and mask out child contributions before aggregating to the
        # SPM unit.
        person = spm_unit.members
        # `age` is YEAR-defined; period.this_year reverses auto-division so
        # this returns age in years for monthly periods.
        is_adult = person("age", period.this_year) >= 18
        per_person_income = sum(person(source, period) for source in p.sources)
        return spm_unit.sum(per_person_income * is_adult)
