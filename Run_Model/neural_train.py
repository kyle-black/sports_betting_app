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
# Define helper functions.




def bayesian_network(data,train_cols):
    scaler = StandardScaler()
    #detector = IsolationForest(n_estimators=1000, contamination="auto", random_state=0)
    neg_log_likelihood = lambda x, rv_x: -rv_x.log_prob(x)

    # Load data and keep only first six months due to drift.
   # data = pd.read_excel("data.xlsx")
   # data = data[data["Date"] <= "2004-09-10"]


    # Select columns and remove rows with missing values.
    #columns = ["PT08.S1(CO)", "PT08.S3(NOx)", "PT08.S4(NO2)", "PT08.S5(O3)", "T", "AH", "CO(GT)", "C6H6(GT)", "NOx(GT)", "NO2(GT)"]
    
    columns = data.columns
    
    data = data[columns].dropna(axis=0)
    # Scale data to zero mean and unit variance.
   # X_t = scaler.fit_transform(data)
    X_t = data
    X_t = X_t.astype(float)
    # Remove outliers.
   # is_inlier = detector.fit_predict(X_t)
    #X_t = X_t[(is_inlier > 0),:]
    # Restore frame.
    dataset = pd.DataFrame(X_t, columns=columns)

#    outputs = ['home_is_winner']
    train_cols = ['home_Current_win_pct','home_prev_win_pct','Rolling_10D_win_x','Rolling_30D_win_x', 'away_Current_win_pct', 'away_prev_win_pct', 
         'Rolling_10D_win_y', 'Rolling_30D_win_y', 'home_r_Current','home_r_3', 'home_r_1', 'home_r_Home', 'home_r_Away', 'home_r_prev','Rolling_10D_r_home', 'Rolling_30D_r_home', 'away_r_Current','away_r_3', 'away_r_1', 
         'away_r_Home', 'away_r_Away', 'away_r_prev','Rolling_10D_r_away', 'Rolling_30D_r_away', 'home_opp_Current','home_opp_3', 'home_opp_1', 'home_opp_Home', 'home_opp_Away', 'home_opp_prev','Rolling_10D_opp_home', 
         'Rolling_30D_opp_home','away_opp_Current','away_opp_3', 'away_opp_1', 'away_opp_Home', 'away_opp_Away', 'away_opp_prev','Rolling_10D_opp_away', 'Rolling_30D_opp_away' ]
    inputs = train_cols
    # Select labels for inputs and outputs.
   # inputs = ["PT08.S1(CO)", "PT08.S3(NOx)", "PT08.S4(NO2)", "PT08.S5(O3)", "T", "AH"]
    outputs = ['lowvig_home_vf']
    
  

    # Define some hyperparameters.
    n_epochs = 50
    n_samples = dataset.shape[0]
    n_batches = 10
    batch_size = np.floor(n_samples/n_batches)
    buffer_size = n_samples
    # Define training and test data sizes.
    n_train = int(0.7*dataset.shape[0])
    # Define dataset instance.
    data = tf.data.Dataset.from_tensor_slices((dataset[inputs].values, dataset[outputs].values))
    data = data.shuffle(n_samples, reshuffle_each_iteration=True)
    # Define train and test data instances.
    data_train = data.take(n_train).batch(batch_size).repeat(n_epochs)
    data_test = data.skip(n_train).batch(1)





    # Define prior for regularization.
    prior = tfd.Independent(tfd.Normal(loc=tf.zeros(len(outputs), dtype=tf.float64), scale=1.0), reinterpreted_batch_ndims=1)
    # Define model instance.
    model = tfk.Sequential([
    tfk.layers.InputLayer(input_shape=(len(inputs),), name="input"),
    tfk.layers.Dense(10, activation="relu", name="dense_1"),
    tfk.layers.Dense(tfp.layers.MultivariateNormalTriL.params_size(
    len(outputs)), activation=None, name="distribution_weights"),
    tfp.layers.MultivariateNormalTriL(len(outputs), activity_regularizer=tfp.layers.KLDivergenceRegularizer(prior, weight=1/n_batches), name="output")
    ], name="model")
    # Compile model.
    model.compile(optimizer="adam", loss=neg_log_likelihood)
    # Run training session.
    model.fit(data_train, epochs=n_epochs, validation_data=data_test, verbose=False)
    # Describe model.
    model.summary()

    model.save('bayesian_neural_n.h5')
    model.save_weights('models/bayesian_neural_n.h5')



    tfp.layers.DenseFlipout(10, activation="relu", name="dense_1")



    # Predict.
    samples = len(data_test)
    iterations = 20
    test_iterator = tf.compat.v1.data.make_one_shot_iterator(data_test)
    X_true, Y_true, Y_pred = np.empty(shape=(samples, len(inputs))), np.empty(shape=(samples, len(outputs))), np.empty(shape=(samples, len(outputs), iterations))
    for i in range(samples):
        features, labels = test_iterator.get_next()
        X_true[i,:] = features
        Y_true[i,:] = labels.numpy()
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
    Y_pred_mean = np.mean(Y_pred, axis=-1)

    Y_pred_transformed = 1/(1 + np.exp(-Y_pred))
    Y_pred_mean_transformed = np.mean(Y_pred_transformed, axis=-1)
    Y_pred_mean_flat = Y_pred_mean_transformed.reshape(-1)

    Y_true_flat = Y_true.reshape(-1)

# now calculate Brier score and Log Loss
    brier_score = brier_score_loss(Y_true_flat, Y_pred_mean_flat)
    print(f"Brier Score: {brier_score}")

    logloss = log_loss(Y_true_flat, Y_pred_mean_flat)
    print(f"Log Loss: {logloss}")

    '''

