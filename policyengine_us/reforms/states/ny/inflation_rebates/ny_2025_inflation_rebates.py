from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant


def create_ny_2025_inflation_rebates() -> Reform:
    class ny_2025_inflation_rebates(Variable):
        value_type = float
        entity = TaxUnit
        label = "New York 2025 inflation rebates"
        unit = USD
        definition_period = YEAR
        reference = "https://www.governor.ny.gov/news/money-your-pockets-governor-hochul-proposes-sending-86-million-new-yorkers-inflation-refund"
        defined_for = StateCode.NY

        def formula(tax_unit, period, parameters):
            p = parameters(period).gov.contrib.states.ny.inflation_rebates
            agi = tax_unit("ny_agi", period)
            filing_status = tax_unit("filing_status", period)
            filing_statuses = filing_status.possible_values
            return select(
                [
                    filing_status == filing_statuses.SINGLE,
                    filing_status == filing_statuses.JOINT,
                    filing_status == filing_statuses.HEAD_OF_HOUSEHOLD,
                    filing_status == filing_statuses.SEPARATE,
                    filing_status == filing_statuses.SURVIVING_SPOUSE,
                ],
                [
                    p.single.calc(agi, right=True),
                    p.joint.calc(agi, right=True),
                    p.head_of_household.calc(agi, right=True),
                    p.separate.calc(agi, right=True),
                    p.surviving_spouse.calc(agi, right=True),
                ],
            )

    def modify_parameters(parameters):
        parameters.gov.states.ny.tax.income.credits.refundable.update(
            start=instant("2025-01-01"),
            stop=instant("2025-12-31"),
            value=[
                "ny_eitc",
                "ny_supplemental_eitc",
                "ny_ctc",
                "ny_cdcc",
                "ny_real_property_tax_credit",
                "ny_college_tuition_credit",
                "ny_2025_inflation_rebates",
            ],
        )
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(ny_2025_inflation_rebates)
            self.modify_parameters(modify_parameters)

    return reform


def create_ny_2025_inflation_rebates_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_ny_2025_inflation_rebates()

    p = parameters.gov.contrib.states.ny.inflation_rebates

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_ny_2025_inflation_rebates()
    else:
        return None


ny_2025_inflation_rebates = create_ny_2025_inflation_rebates_reform(
    None, None, bypass=True
)
