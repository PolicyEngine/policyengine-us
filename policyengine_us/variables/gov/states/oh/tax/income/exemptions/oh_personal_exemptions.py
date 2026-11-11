from policyengine_us.model_api import *


class oh_personal_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio personal exemptions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=14",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.025",
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.oh.tax.income.exemptions.personal

        eligible_exemptions = add(
            tax_unit, period, ["oh_personal_exemptions_eligible_person"]
        )

        # R.C. 5747.025(A) sets the exemption by modified adjusted gross income.
        modified_agi = tax_unit("oh_modified_agi", period)
        exemption_amount = p.amount.calc(modified_agi)

        return eligible_exemptions * exemption_amount
