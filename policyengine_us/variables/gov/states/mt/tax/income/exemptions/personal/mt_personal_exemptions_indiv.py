from policyengine_us.model_api import *


class mt_personal_exemptions_indiv(Variable):
    value_type = float
    entity = Person
    label = "Montana exemptions when married couples file separately"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(person, period, parameters):
        p = parameters(period).gov.states.mt.tax.income.exemptions

        if p.applies:
            head_or_spouse = person("is_tax_unit_head_or_spouse", period)
            blind = person("is_blind", period)
            blind_head_or_spouse = blind * head_or_spouse
            # Allocate the dependent exemption to the head
            head = person("is_tax_unit_head", period)
            aged_exemption = person(
                "mt_aged_exemption_eligible_person", period
            )
            exemption_count = (
                head_or_spouse.astype(int)
                + blind_head_or_spouse.astype(int)
                + aged_exemption.astype(int)
            )
            return exemption_count * p.amount

        return 0
