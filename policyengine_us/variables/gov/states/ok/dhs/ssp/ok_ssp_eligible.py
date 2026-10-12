from policyengine_us.model_api import *


class ok_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Oklahoma State Supplemental Payment non-income eligibility"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/oklahoma/OAC-340-15-1-5"
    defined_for = StateCode.OK

    def formula(person, period, parameters):
        p = parameters(period).gov.ssa.ssi.eligibility.resources.limit
        couple = person.marital_unit.nb_persons() == 2
        resources = person.marital_unit.sum(
            person("ssi_countable_resources", period.this_year)
        )
        immigration = person("immigration_status", period.this_year)
        citizen = immigration == immigration.possible_values.CITIZEN
        immigrant = person("is_ssi_qualified_noncitizen", period.this_year)
        arrangement = person("ssi_federal_living_arrangement", period)
        medical = arrangement == arrangement.possible_values.MEDICAL_TREATMENT_FACILITY
        return (
            ~medical
            & person("is_ssi_aged_blind_disabled", period.this_year)
            & (resources <= where(couple, p.couple, p.individual))
            & (citizen | immigrant)
            & ~person("ok_ssp_is_excluded", period)
            & ~person("ok_ssp_is_in_tanf_unit", period)
            & ~person("ssi_lives_in_medical_treatment_facility", period)
            & ~person("is_incarcerated", period)
            & person("takes_up_ssi_if_eligible", period)
        )
