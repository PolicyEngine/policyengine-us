from policyengine_us.model_api import *
from policyengine_us.tools.state_eitc_helpers import eitc_filing_status_eligible


class eitc_marital_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Meets EITC marital eligibility requirements"
    definition_period = YEAR
    reference = (
        "https://www.govinfo.gov/content/pkg/USCODE-2023-title26/pdf/USCODE-2023-title26-subtitleA-chap1-subchapA-partIV-subpartC-sec32.pdf#page=3",
        "https://www.congress.gov/117/bills/hr1319/BILLS-117hr1319enr.pdf#page=151",
    )
    documentation = """
    Married separate filers must have a qualifying child residing with them
    for more than half the year and satisfy either statutory separation
    route. The exception is enabled from 2021. Child identification rules
    do not determine whether the marital exception applies.
    """

    def formula(tax_unit, period, parameters):
        return eitc_filing_status_eligible(tax_unit, period, parameters)
