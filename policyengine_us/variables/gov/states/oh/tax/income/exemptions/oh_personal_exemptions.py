from policyengine_us.model_api import *


class oh_personal_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio personal exemptions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=14",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.exemptions.personal

        eligible_exemptions = add(
            tax_unit, period, ["oh_personal_exemptions_eligible_person"]
        )

        agi = tax_unit("oh_agi", period)
        exemption_amount = p.amount.calc(agi, right=True)

        return eligible_exemptions * exemption_amount
