from policyengine_us.model_api import *


class ar_itemized_deductions_unit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arkansas itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.dfa.arkansas.gov/images/uploads/incomeTaxOffice/2022_AR1000F_and_AR1000NR_Instructions.pdf#page=21"
    defined_for = StateCode.AR

    # Arkansas does not tie itemization choice to federal choice.
    adds = "gov.states.ar.tax.income.deductions.itemized.sources"
