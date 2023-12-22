from policyengine_us.model_api import *


class hi_disabled_exemptions_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii disabled exemptions eligible"
    unit = USD
    documentation = (
        "https://files.hawaii.gov/tax/forms/2022/n11ins.pdf#page=20"
    )
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        is_head = person("is_tax_unit_head", period)
        is_spouse = person("is_tax_unit_spouse", period)
        disabled = person("is_disabled", period)
        # if filing status is not joint, the disabled_exemption_spouse should be zero
        # The taxpayer shall not take additional exemptions with regard to spouse disability.
        filing_status = tax_unit("filing_status", period)
        joint_filing = (
            filing_status == filing_status.possible_values.JOINT
        )
        return (is_head & disabled) | (is_spouse & disabled & joint_filing)
        
