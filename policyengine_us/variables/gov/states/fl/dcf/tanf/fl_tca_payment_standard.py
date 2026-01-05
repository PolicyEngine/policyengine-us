from policyengine_us.model_api import *


class fl_tca_payment_standard(Variable):
    value_type = float
    entity = SPMUnit
    label = "Florida TCA payment standard"
    unit = USD
    definition_period = MONTH
    reference = (
        "https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0400-0499/0414/Sections/0414.095.html",
        "https://flrules.org/gateway/RuleNo.asp?id=65A-4.220",
    )
    defined_for = StateCode.FL

    def formula(spm_unit, period, parameters):
        # Per Florida Statutes 414.095(10): Payment based on shelter tier
        p = parameters(period).gov.states.fl.dcf.tanf
        payment = p.payment_standard
        threshold = p.shelter_cost_threshold

        # Get monthly shelter cost (housing_cost is annual)
        monthly_shelter = (
            spm_unit("housing_cost", period.this_year) / MONTHS_IN_YEAR
        )

        # Determine unit size, capped at max in parameter table
        size = spm_unit("spm_unit_size", period.this_year)
        max_size = p.max_family_size
        capped_size = min_(size, max_size)

        # Determine payment standard based on shelter tier
        zero_shelter = monthly_shelter == 0
        low_shelter = (monthly_shelter > 0) & (monthly_shelter <= threshold)

        zero_shelter_amount = payment.zero_shelter[capped_size]
        low_shelter_amount = payment.low_shelter[capped_size]
        high_shelter_amount = payment.high_shelter[capped_size]

        return select(
            [zero_shelter, low_shelter],
            [zero_shelter_amount, low_shelter_amount],
            default=high_shelter_amount,
        )
