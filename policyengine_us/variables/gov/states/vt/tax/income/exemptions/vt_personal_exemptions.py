from policyengine_us.model_api import *


class vt_personal_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont personal exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VT
    reference = (
        "https://tax.vermont.gov/sites/tax/files/documents/IN-111-2022.pdf"
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.vt.tax.income.exemption
        is_joint = tax_unit("tax_unit_is_joint", period)
        elsewhere_head = tax_unit("head_is_dependent_elsewhere", period)
        elsewhere_spouse = tax_unit("spouse_is_dependent_elsewhere", period)
        eligible_head = (~elsewhere_head).astype(int)
        eligible_spouse = (~elsewhere_spouse).astype(int)
        eligible_count = eligible_head + (eligible_spouse * is_joint)
        # add number of other dependents claimed on federal Form 1040 (line 5c)
        dependents = tax_unit("tax_unit_count_dependents", period)
        total_exemption_count = eligible_count + dependents
        return total_exemption_count * p.personal
