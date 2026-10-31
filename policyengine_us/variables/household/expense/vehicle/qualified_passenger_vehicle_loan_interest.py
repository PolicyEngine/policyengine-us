from policyengine_us.model_api import *


class qualified_passenger_vehicle_loan_interest(Variable):
    value_type = float
    entity = Household
    label = "qualified passenger vehicle loan interest"
    unit = USD
    documentation = (
        "Interest on loans that meet the federal qualified passenger "
        "vehicle loan interest requirements, including qualifying vehicle "
        "and loan requirements, entered for the household as a whole. The "
        "whole amount counts on the return of the tax unit that includes the "
        "household head: the oldest flagged head when several are flagged, "
        "and the oldest member when none is. A head claimed as a dependent "
        "puts it on the claiming filer's return. To count a loan on the "
        "return of the person who incurred it, enter it in "
        "qualified_passenger_vehicle_loan_interest_person instead."
    )
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/taxtopics/tc505",
        "https://www.irs.gov/pub/irs-pdf/p6126.pdf",
        "https://www.irs.gov/irb/2026-05_IRB",
    )
    uprating = "gov.bls.cpi.cpi_u"
