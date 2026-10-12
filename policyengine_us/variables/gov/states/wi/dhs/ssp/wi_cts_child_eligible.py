from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wi.dhs.ssp._wi_cts import cts_relationships


class wi_cts_child_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Wisconsin CTS nonfinancially eligible child"
    definition_period = MONTH
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf"
    documentation = "Override for verified PRUCOL or other lawful statuses absent from the immigration enum, and certified Huber Law childcare release. Both co-resident natural/adoptive parents must receive Wisconsin state SSI."

    def formula(person, period, parameters):
        _, _, _, _, parents, ssi_parents = cts_relationships(person, period)
        status = person("immigration_status", period.this_year)
        s = status.possible_values
        immigration = (
            (status == s.CITIZEN)
            | (status == s.LEGAL_PERMANENT_RESIDENT)
            | (status == s.REFUGEE)
            | (status == s.ASYLEE)
            | (status == s.CUBAN_HAITIAN_ENTRANT)
            | (status == s.DEPORTATION_WITHHELD)
            | (status == s.CONDITIONAL_ENTRANT)
        )
        return (
            person("wi_cts_dependent_child", period)
            & (person("ssi", period) == 0)
            & (ssi_parents > 0)
            & (parents == ssi_parents)
            & immigration
            & ~person("is_incarcerated", period)
        )
