from policyengine_us.model_api import *
from policyengine_us.reforms.utils import create_reform_if_active


def create_family_security_act_2024_eitc() -> Reform:

    class eitc_maximum(Variable):
        value_type = float
        entity = TaxUnit
        label = "Maximum EITC"
        definition_period = YEAR
        reference = "https://www.law.cornell.edu/uscode/text/26/32#a"
        unit = USD

        def formula(tax_unit, period, parameters):
            child_count = tax_unit("eitc_child_count", period)
            p = parameters(
                period
            ).gov.contrib.congress.romney.family_security_act_2_0.eitc.amount
            filing_status = tax_unit("filing_status", period)
            joint = filing_status == filing_status.possible_values.JOINT
            return where(
                joint, p.joint.calc(child_count), p.single.calc(child_count)
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(eitc_maximum)

    return reform


def create_family_security_act_2024_eitc_reform(
    parameters, period, bypass: bool = False
):
    return create_reform_if_active(
        parameters,
        period,
        "gov.contrib.congress.romney.family_security_act_2_0.eitc",
        "apply_eitc_structure",
        create_family_security_act_2024_eitc,
        bypass,
    )


family_security_act_2024_eitc = create_family_security_act_2024_eitc_reform(
    None, None, bypass=True
)
