from scf import SCF, SCF_2022
from policyengine_us.data.datasets.cps import CPS_2022
from survey_enhance import Imputation
import pandas


def makeSCFPredictor( scf : SCF, cps : CPS_2022 ) :
    
    scf_data = scf.load()
    SCF_VARS = [    'assets_financial'
                ,   'assets_value_primary_residence'
                ]
    CPS_VARS = [    'age'
                ,   'employment_income_last_year'
                #,   'household_net_income'  == not in CPS
                #,   'household_vehicles_owned'  -- not in CPS
                #,   'household_vehicles_value'  -- not in CPS
                #,   'is_female'  -- category
                #,   'is_married' -- category
                # ,   'race'   -- convert to numeric ... also only cps_race is in CPS
                #,   'spm_unit_assets' -- not in CPS
                #,   'spm_unit_count_children' -- not in CPS
                ]

    df_train = pandas.DataFrame()
    for v in scf.variables :
        df_train[v] = scf_data[v]

    assets  = Imputation()
    # TBD: Need to identify categorical variables
    X       = df_train[CPS_VARS]
    y       = df_train[SCF_VARS]
    assets.train(X, y)

    cps_data = cps.load()
    
    df_predict = pandas.DataFrame()
    for v in CPS_VARS :
        df_predict[v] = cps_data[v]

    df_cps = assets.predict( df_predict )

    print( scf_data )


if( __name__ == "__main__" )  :
    scf = SCF_2022(require = True)
    cps = CPS_2022(require = True)
    # cps.generate()
    # scf.generate( )
    makeSCFPredictor( scf, cps )