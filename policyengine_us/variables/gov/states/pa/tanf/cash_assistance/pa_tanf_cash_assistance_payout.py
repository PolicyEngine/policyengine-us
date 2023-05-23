from policyengine_us.model_api import *


class pa_tanf_cash_assistance_payout(Variable):
    value_type = float
    entity = SPMUnit
    label = "Penhsylvania TANF cash assistance payout"
    unit = USD
    definition_period = YEAR
    reference = "https://www.compass.state.pa.us/compass.web/menuitems/CashFAQ.aspx?Language=EN"
    defined_for = StateCode.PA

    def formula(spm_unit, period, parameters):
        people = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.pa.dhs.tanf.cash_assistance # not sure
        county = spm_unit.household("county_str", period)

        # Group 1: Bucks, Chester, Lancaster, Montgomery, Pike
        bucks = county == 'BUCKS_COUNTY_PA"
        chester = county == "CHESTER_COUNTY_PA"
        lancaster = county == "LANCASTER_COUNTY_PA"
        montgomery = county == "MONTGOMERY_COUNTY_PA"
        pike = county == "PIKE_COUNTY_PA"
        group1 = [bucks]
        # Group 2: Adams, Allegheny, Berks, Blair, Bradford, Butler, Centre, Columbia, Crawford, Cumberland, Dauphin, Delaware, Erie, Lackawanna, Lebanon, Lehigh, Luzerne, Lycoming, Monroe, Montour, Northampton, Philadelphia, Sullivan, Susquehanna, Union, Warren, Wayne, Westmoreland, Wyoming, York
        adams = county == "ADAMS_COUNTY_PA"
        allegheny = county == "ALLEGHENY_COUNTY_PA"
        berks = county == "BERKS_COUNTY_PA"
        blair = county == "BLAIR_COUNTY_PA"
        bradford = county == "BRADFORD_COUNTY_PA"
        butler = county == "BUTLER_COUNTY_PA"
        centre = county == "CENTRE_COUNTY_PA"
        columbia = county == "COLUMBIA_COUNTY_PA"
        crawford = county == "CRAWFORD_COUNTY_PA"
        cumberland = county == "CUMBERLAND_COUNTY_PA"
        dauphin = county == "DAUPHIN_COUNTY_PA"
        delaware = county == "DELAWARE_COUNTY_PA"
        erie = county == "ERIE_COUNTY_PA"
        lackawanna = county == "LACKAWANNA_COUNTY_PA"
        lebanon = county == "LEBANON_COUNTY_PA"
        lehigh = county == "LEHIGH_COUNTY_PA"
        luzerne = county == "LUZERNE_COUNTY_PA"
        lycoming = county == "LYCOMING_COUNTY_PA"
        monroe = county == "MONROE_COUNTY_PA"
        montour = county == "MONTOUR_COUNTY_PA"
        northampton = county == "NORTHAMPTON_COUNTY_PA"
        philadelphia = county == "PHILADELPHIA_COUNTY_PA"
        sullivan = county == "SULLIVAN_COUNTY_PA"
        susquehanna = county == "SUSQUEHANNA_COUNTY_PA"
        union = county == "UNION_COUNTY_PA"
        warren = county == "WARREN_COUNTY_PA"
        wayne = county == "WAYNE_COUNTY_PA"
        westmoreland = county == "WESTMORELAND_COUNTY_PA"
        wyoming = county == "WYOMING_COUNTY_PA"
        york = county == "YORK_COUNTY_PA"

        # Group 3: Beaver, Cameron, Carbon, Clinton, Elk, Franklin, Indiana, Lawrence, McKean, Mercer, Mifflin, Perry, Potter, Snyder, Tioga, Venango, Washington
        beaver = county == "BEAVER_COUNTY_PA"
        cameron = county == "CAMERON_COUNTY_PA"
        carbon = county == "CARBON_COUNTY_PA"
        clinton = county == "CLINTON_COUNTY_PA"
        elk = county ==  "ELK_COUNTY_PA"
        franklin = county == "FRANKLIN_COUNTY_PA"
        indiana = county == "INDIANA_COUNTY_PA"
        lawrence = county == "LAWRENCE_COUNTY_PA"
        mckean = county == "MCKEAN_COUNTY_PA"
        mercer = county == "MERCER_COUNTY_PA"
        mifflin = county == "MIFFLIN_COUNTY_PA"
        perry = county == "PERRY_COUNTY_PA"
        potter = county == "POTTER_COUNTY_PA"
        snyder = county == "SNYDER_COUNTY_PA"
        tioga = county == "TIOGA_COUNTY_PA"
        venango = county == "VENANGO_COUNTY_PA"
        washington = county == "WASHINGTON_COUNTY_PA"
       
        # Group 4: Armstrong, Bedford, Cambria, Clarion, Clearfield, Fayette, Forest, Fulton, Greene, Huntingdon, Jefferson, Juniata, Northumberland, Schuylkill, Somerset
        armstrong = county == "ARMSTRONG_COUNTY_PA"
        bedford = county == "BEDFORD_COUNTY_VA"
        cambria = county == "CAMBRIA_COUNTY_PA"
        clarion = county == "CLARION_COUNTY_PA"
        clearfield = county == "CLEARFIELD_COUNTY_PA"
        fayette = county == "FAYETTE_COUNTY_PA"
        forest = county == "FOREST_COUNTY_PA"
        fulton = county == "FULTON_COUNTY_PA"
        greene = county == "GREENE_COUNTY_PA"
        huntingdon = county == "HUNTINGDON_COUNTY_PA"
        jefferson = county == "JEFFERSON_COUNTY_PA"
        juniata = county == "JUNIATA_COUNTY_PA"
        northumberland = county == "NORTHUMBERLAND_COUNTY_PA"
        schuylkill = county == "SCHUYLKILL_COUNTY_PA"
        somerset = county == "SOMERSET_COUNTY_PA"


        group_1 = [bucks, chester, lancaster, montgomery, pike]
        group_2 = [adams, allegheny, berks, blair, bradford, butler, centre, columbia, crawford, 
            cumberland, dauphin, delaware, erie, lackawanna, lebanon, lehigh, luzerne,
            lycoming, monroe, montour, northampton, philadelphia, sullivan, susquehanna, 
            union, warren, wayne, westmoreland, wyoming, york]
        group_3 = [beaver, cameron, carbon, clinton, elk, franklin, indiana, lawrence, mckean, 
            mercer, mifflin, perry, potter, snyder, tioga, venango, washington]
        group_4 = [armstrong, bedford, cambria, clarion, clearfield, fayette, forest, fulton, 
            greene, huntingdon, jefferson, juniata, northumberland, schuylkill, somerset]
            
    return
