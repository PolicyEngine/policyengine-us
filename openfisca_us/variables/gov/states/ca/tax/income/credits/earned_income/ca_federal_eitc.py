from openfisca_us.model_api import *


class ca_federal_eitc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Modified federal EITC for computing CalEITC"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/file/personal/credits/california-earned-income-tax-credit.html#What-you-ll-get"
    defined_for = "ca_eitc_eligible"

    # Formula will include:
    # phase_in = adj_federal_eitc * p.phase_in_rate[qualifying_children]
    # Or adjust federal EITC variable via a branched simulation.
