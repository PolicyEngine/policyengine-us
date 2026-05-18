from policyengine_us.model_api import *


class ar_sra_gross_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Arkansas SRA gross income for the per-family copay ceiling"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.AR
    reference = (
        "https://dese.ade.arkansas.gov/Files/2025-2027_CCDF_State_Plan_Final_4.26.24.1REV_OEC.pdf#page=39",
        "https://dese.ade.arkansas.gov/Files/FSU-Procedural-Manual-June-2023_UPDATED_20230629075344.pdf#page=19",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ar.ade.oec.sra.income
        # CCDF State Plan §3.1.1 caps the family copay at 4% of gross income,
        # which includes all members (children's SSI and SS included).
        person = spm_unit.members
        per_person_income = sum(person(source, period) for source in p.sources)
        return spm_unit.sum(per_person_income)
