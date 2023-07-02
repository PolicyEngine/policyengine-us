from policyengine_us.model_api import *
import numpy as np


class nm_aged_blind_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico aged and blind exemption"
    unit = USD
    definition_period = YEAR
    reference = ""
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.tax.income.exemptions.blind_and_aged
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        agi = tax_unit("adjusted_gross_income", period)
        age_threshold = p.age_threshold
        
        # check if taxpayer is blind or aged
        blind_head = tax_unit("blind_head", period).astype(int)
        aged_head = (tax_unit("age_head", period) >= age_threshold).astype(int)
        
        # check if taxpayer is eligible (Taxpayers cannot take exemptions for being both 65 or older and blind.)
        head_eligible = blind_head | aged_head

        # check if spouse is blind or aged
        blind_spouse = tax_unit("blind_spouse", period).astype(int)
        aged_spouse = (tax_unit("age_spouse", period) >= age_threshold).astype(int)
        
        # check if spouse is eligible
        spouse_eligible = blind_spouse | aged_spouse

        eligible_count = head_eligible + spouse_eligible

        # Use `right=True` to reflect "over ... but not over ...".
        amount = select(
            [
                filing_status == statuses.SINGLE,
                filing_status == statuses.JOINT,
                filing_status == statuses.HEAD_OF_HOUSEHOLD,
                filing_status == statuses.SEPARATE,
                filing_status == statuses.WIDOW,
            ],
            [
                p.single.calc(agi, right=True),
                p.joint.calc(agi, right=True),
                p.head_of_household.calc(agi, right=True),
                p.separate.calc(agi, right=True),
                p.widow.calc(agi, right=True),
            ],
        )
        return eligible_count * amount
        

