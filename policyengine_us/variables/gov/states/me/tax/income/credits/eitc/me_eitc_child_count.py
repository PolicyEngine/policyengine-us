from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import federal_eitc_tax_unit


class me_eitc_child_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "Maine EITC qualifying children"
    documentation = "Qualifying children Maine's earned income tax credit takes into account. From 2021 a child with an ITIN or any Social Security number counts on a return whose filer files a federal income tax return (me_eitc_ssn_limitation_waived)."
    definition_period = YEAR
    reference = (
        # § 5219-S(7): "for an individual who files a federal income tax
        # return", the taxpayer identification number required by IRC
        # 32(c)(3)(D) "means a federal individual taxpayer identification
        # number ... or a social security number".
        "https://legislature.maine.gov/statutes/36/title36sec5219-S.html",
        "https://www.law.cornell.edu/uscode/text/26/32#c_3_D",
        "https://www.law.cornell.edu/uscode/text/26/32#m",
    )
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        federal = federal_eitc_tax_unit(tax_unit, period)
        return federal("eitc_child_count", period)
