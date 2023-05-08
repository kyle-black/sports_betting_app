import pickle
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sql_output import data_pull



#print(data_pull)

class Prediction:

    def __init__(self, data):
        self.data =data
        self.transformed_data =None
        self.predictions =None

        with open('trained_model.pkl', 'rb') as f:
            self.model = pickle.load(f)

        with open('pca.pkl', 'rb') as f:
            self.pca = pickle.load(f)

    def get_data(self):

        columns_to_add =  ["home_bat_age",
        "home_bat_R_G",
        "home_bat_G",
        "home_bat_PA",
        "home_bat_AB",
        "home_bat_R",
        "home_bat_H",
        "home_bat_2B",
        "home_bat_3B",
        "home_bat_HR",
        "home_bat_RBI",
        "home_bat_SB",
        "home_bat_CS",
        "home_bat_BB",
        "home_bat_SO",
        "home_bat_BA",
        "home_bat_OBP",
        "home_bat_SLG",
        "home_bat_OPS",
        "home_bat_OPS_plus",
        "home_bat_TB",
        "home_bat_GDP",
        "home_bat_HBP",
        "home_bat_SH",
        "home_bat_SF",
        "home_bat_IBB",
        "home_bat_LOB",
        "away_bat",
        "away_bat_age",
        "away_bat_R_G",
        "away_bat_G",
        "away_bat_PA",
        "away_bat_AB",
        "away_bat_R",
        "away_bat_H",
        "away_bat_2B",
        "away_bat_3B",
        "away_bat_HR",
        "away_bat_RBI",
        "away_bat_SB",
        "away_bat_CS",
        "away_bat_BB",
        "away_bat_SO",
        "away_bat_BA",
        "away_bat_OBP",
        "away_bat_SLG",
        "away_bat_OPS",
        "away_bat_OPS_plus",
        "away_bat_TB",
        "away_bat_GDP",
        "away_bat_HBP",
        "away_bat_SH",
        "away_bat_SF",
        "away_bat_IBB",
        "away_bat_LOB",
        "home_fld_RA_G",
        "home_fld_DefEff",
        "home_fld_G",
        "home_fld_GS",
        "home_fld_CG",
        "home_fld_INN",
        "home_fld_CH",
        "home_fld_PO",
        "home_fld_A",
        "home_fld_E",
        "home_fld_DP",
        "home_fld_FLD_PCT",
        "home_fld_Rtot_yr",
        "home_fld_Rdrs",
        "home_fld_Rdrs_yrs",
        "home_fld_Rgood",
        "away_fld_RA_G",
        "away_fld_DefEff",
        "away_fld_G",
        "away_fld_GS",
        "away_fld_CG",
        "away_fld_INN",
        "away_fld_CH",
        "away_fld_PO",
        "away_fld_A",
        "away_fld_E",
        "away_fld_DP",
        "away_fld_FLD_PCT",
        "away_fld_Rtot_yr",
        "away_fld_Rdrs",
        "away_fld_Rdrs_yrs",
        "away_fld_Rgood",
        "home_pitch_RA_G",
        "home_pitch_W",
        "home_pitch_L",
        "home_pitch_W_L_pct",
        "home_pitch_ERA",
        "home_pitch_G",
        "home_pitch_GS",
        "home_pitch_GF",
        "home_pitch_CG",
        "home_pitch_tSho",
        "home_pitch_cSho",
        "home_pitch_SV",
        "home_pitch_IP",
        "home_pitch_H",
        "home_pitch_R",
        "home_pitch_ER",
        "home_pitch_HR",
        "home_pitch_BB",
        "home_pitch_IBB",
        "home_pitch_SO",
        "home_pitch_HBP",
        "home_pitch_BK",
        "home_pitch_WP",
        "home_pitch_BF",
        "home_pitch_ERA_plus",
        "home_pitch_FIP",
        "home_pitch_WHIP",
        "home_pitch_H9",
        "home_pitch_HR9",
        "home_pitch_BB9",
        "home_pitch_SO9",
        "home_pitch_SO_W",
        "home_pitch_LOB",
        "away_pitch_RA_G",
        "away_pitch_W",
        "away_pitch_L",
        "away_pitch_W_L_pct",
        "away_pitch_ERA",
        "away_pitch_G",
        "away_pitch_GS",
        "away_pitch_GF",
        "away_pitch_CG",
        "away_pitch_tSho",
        "away_pitch_cSho",
        "away_pitch_SV",
        "away_pitch_IP",
        "away_pitch_H",
        "away_pitch_R",
        "away_pitch_ER",
        "away_pitch_HR",
        "away_pitch_BB",
        "away_pitch_IBB",
        "away_pitch_SO",
        "away_pitch_HBP",
        "away_pitch_BK",
        "away_pitch_WP",
        "away_pitch_BF",
        "away_pitch_ERA_plus",
        "away_pitch_FIP",
        "away_pitch_WHIP",
        "away_pitch_H9",
        "away_pitch_HR9",
        "away_pitch_BB9",
        "away_pitch_SO9",
        "away_pitch_SO_W",
        "away_pitch_LOB"]


        

        return self.data


        

    def preprocess_data(self):
        # Apply the same preprocessing steps as used during model training
        # (e.g., feature scaling, encoding categorical variables, etc.)
        
        self.transformed_data = self.pca.transform(self.data.drop([ 'game_date', 'home_tm', 'away_tm'], axis=1))

        return self.transformed_data
        
        

    def make_predictions(self):
        # Apply PCA transformation
        
        
        # Make predictions using the trained model
        self.predictions = self.model.predict(self.transformed_data)

        return self.predictions

    # Main script
if __name__ == "__main__":

    predict = Prediction(data_pull)
    data = predict.get_data()
    data.to_csv('tester.csv')
    #print(data)
    
    predict.preprocess_data()
    predictions = predict.make_predictions()

    #for i in predictions:
     #   print(i)
    print(predictions)
    

