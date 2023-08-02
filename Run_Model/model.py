import pandas as pd
import numpy as np
import tensorflow as tf
tfk = tf.keras
tf.keras.backend.set_floatx("float64")
import tensorflow_probability as tfp
tfd = tfp.distributions
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import brier_score_loss, log_loss



def model_output(df):

    

    #print(df.columns)
    
    train_cols = ['home_Current_win_pct','home_prev_win_pct','home_Rolling_10D_win','home_Rolling_30D_win', 'away_Current_win_pct', 'away_prev_win_pct', 
         'away_Rolling_10D_win', 'away_Rolling_30D_win', 'home_r_Current','home_r_3', 'home_r_1', 'home_r_Home', 'home_r_Away', 'home_r_prev','Rolling_10D_r_home', 'Rolling_30D_r_home', 'away_r_Current','away_r_3', 'away_r_1', 
         'away_r_Home', 'away_r_Away', 'away_r_prev','Rolling_10D_r_away', 'Rolling_30D_r_away', 'home_opp_Current','home_opp_3', 'home_opp_1', 'home_opp_Home', 'home_opp_Away', 'home_opp_prev','Rolling_10D_opp_home', 
         'Rolling_30D_opp_home','away_opp_Current','away_opp_3', 'away_opp_1', 'away_opp_Home', 'away_opp_Away', 'away_opp_prev','Rolling_10D_opp_away', 'Rolling_30D_opp_away' ]
    
    
   # for i in df.columns:
   # print(df[train_cols])
    #print(df.columns)
    
    
    inputs = train_cols
    outputs = ['lowvig_home_vf']
    df = df.dropna()
    ############################## Model Archetecture
    n_batches = 10
    custom_objects = {"KLDivergenceRegularizer": tfp.layers.KLDivergenceRegularizer, "tfdNormal": tfd.Normal,"MultivariateNormalTriL": tfp.layers.MultivariateNormalTriL }
    neg_log_likelihood = lambda x, rv_x: -rv_x.log_prob(x)
    prior = tfd.Independent(tfd.Normal(loc=tf.zeros(len(outputs), dtype=tf.float64), scale=1.0), reinterpreted_batch_ndims=1)
    model = tfk.Sequential([
    tfk.layers.InputLayer(input_shape=(len(inputs),), name="input"),
    tfk.layers.Dense(10, activation="relu", name="dense_1"),
    tfk.layers.Dense(tfp.layers.MultivariateNormalTriL.params_size(len(outputs)), 
                     activation=None, name="distribution_weights"),
    tfp.layers.MultivariateNormalTriL(len(outputs), 
                                      activity_regularizer=tfp.layers.KLDivergenceRegularizer(prior, weight=1/n_batches), 
                                      name="output")
], name="model")

    model.compile(optimizer="adam", loss=neg_log_likelihood)
    model.load_weights('models/bayesian_neural_n.h5')
    
    
    #weights = tf.keras.models.load_weights('models/bayesian_neural_n_weights_01.h5', custom_objects=custom_objects)
    ##############################################################
    ################################################################
    ##################################################################

    
###################Prediction Sequence on Live Data  ##############
    prediction_dict ={}
    
    samples = len(df)
    df_new =df.copy()
    df_new['home_prediction_mean'] = np.nan

    dataset = tf.data.Dataset.from_tensor_slices((df[train_cols].values))
    iterations = 20
    predictions_list =[]
    data_iterator = tf.compat.v1.data.make_one_shot_iterator(dataset)
    predictions = np.empty(shape=(samples, len(outputs), iterations))
    game_pred =[]
    for i in range(samples):

        
        features = data_iterator.get_next()
        #prediction_dict['game'] = i
        predictions_list = []
       # prediction_dict[i] = None
        for k in range(iterations):
            
            predictions = model.predict(tf.expand_dims(features, 0))
            predictions_list.append(predictions)
        prediction_dict[i] = predictions_list
        #prediction_dict[['home_mean'] = np.mean(predictions_list)
    
    
    for idx, value in prediction_dict.items():
        print(idx, value)
        df_new.loc[idx, 'home_prediction_mean']= np.mean(value)
        df_new.loc[idx, 'home_predictions_sd']= np.std(value)
        #df_new.loc[idx, 'prediction'] = np.array(value)
    print(df_new)

    return df_new
    #df_new.to
   # print(df_new)
                   #prediction_dict['game'][i] = predictions_list
        #    game_pred.append(predictions[0][0])
       # print(f'home_team:{df.iloc[i]["home_team"]} predictions: {game_pred[i:i+iterations]}  ')
       # df_new.loc[i,'prediction'] = game_pred[i:i+iterations]
    
    #print(len(predictions_list[]))
    #for i in range(0,len(predictions_list), iterations):
    #    yield predictions_list[i:i+iterations]
        #df_new.loc[i, "prediction"] = predictions_list[i:i+iterations]
   # print(dl)
   # df_new['prediction'] = game_pred[df_new.index:df_new.index+iterations]

   # print(df_new['prediction'])
        #predictions_list.append(predictions)
    
        #prediction_dict[df.iloc[i]['game_date']]={'home_team':}
        #df.iloc[i]['home_team']
        #preds =predictions_list[
        #mean = np.mean(preds)
    #print(predictions_list)

    #df.index
#    df_new.loc[i,'mean_predictions'] = mean
   # df_new.loc[i,'predictions'] = [predictions_list[i:i+iterations]]
    
    #print(df_new['mean_predictions'])
    #pred_mean = np.mean(predictions, axis=-1)
    #pred_sd = np.std(predictions, axis=-1)

    #return pred_mean, pred_sd


        
    '''
        features, labels = test_iterator.get_next()
            X_true[i,:] = features
      #      Y_true[i,:] = labels.numpy()
            Yt = Y_true[i,:]
            for k in range(iterations):
                Y_pred[i,:,k] = model.predict(features)
                print(f'predictions: {Y_pred[i,:,k]} true: {Yt} ')
           
        # Calculate mean and standard deviation.
        Y_pred_m = np.mean(Y_pred, axis=-1)
        Y_pred_s = np.std(Y_pred, axis=-1)


        print(f'predictions:{Y_pred_m[0]} true:{Y_true[0]} st.dev:{Y_pred_s[0]}')
        print(f'predictions:{Y_pred_m[1]} true:{Y_true[1]} st.dev:{Y_pred_s[1]}')
        print(f'predictions:{Y_pred_m[2]} true:{Y_true[2]} st.dev:{Y_pred_s[2]}')
        print(f'predictions:{Y_pred_m[3]} true:{Y_true[3]} st.dev:{Y_pred_s[3]}')
        print(Y_pred_s[0])
    '''