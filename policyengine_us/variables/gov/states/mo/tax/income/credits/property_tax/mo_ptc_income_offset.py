from policyengine_us.model_api import *


class mo_ptc_income_offset(Variable):
    value_type = float
    entity = TaxUnit
    label = "MO property tax credit gross income offset amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.mo.gov/forms/MO-PTS_2021.pdf",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.025&bid=6438",
        "https://revisor.mo.gov/main/OneSection.aspx?section=135.030&bid=6439",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        rents = tax_unit("rents", period)
        p = parameters(period).gov.states.mo.tax.income.credits.property_tax
        return where(
            ~joint,
            p.income_offset.non_joint,
            where(
                rents,
                p.income_offset.joint_renter,
                p.income_offset.joint_owner,
            ),
        )
