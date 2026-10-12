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
        p = parameters(period).gov.states.ar.ade.oec.sra
        # FSU §4.3.2 excludes children's SSI and Social Security; mask by adult status.
        person = spm_unit.members
        is_adult = person("age", period.this_year) >= p.eligibility.adult_age_threshold
        per_person_components = [person(source, period) for source in p.income.sources]
        per_person_income = sum(per_person_components)
        return spm_unit.sum(per_person_income * is_adult)
