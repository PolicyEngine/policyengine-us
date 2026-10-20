from policyengine_us.model_api import *


class oh_other_subtractions(Variable):
    value_type = float
    entity = Person
    label = "Ohio other deductions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.OH
    documentation = (
        "Ohio other deductions reported on Ohio Schedule of Adjustments, "
        "line 38 (Other deductions), entered as a positive amount. Do not include "
        "Social Security, military retirement, 529 deductions, Pell grants, educator "
        "expenses, disability benefits, medical expenses, U.S. government interest, "
        "state tax refunds, business income deductions, or capital gain deductions, "
        "which PolicyEngine computes separately."
    )
    reference = "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=20"
