import pickle

with open(f'model/trained_model/trained_model_100.pkl', 'rb') as file:
       

        model= pickle.load(file)
        