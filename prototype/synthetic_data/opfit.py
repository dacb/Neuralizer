# Importing necessary package
import pandas as pd
import numpy as np
import os
import sklearn
from sklearn.model_selection import train_test_split
import keras
import keras.backened as K
from keras import *

def read_file(filename,X_var,Y_var):
    '''The function takes name of datafile, list of predictors and response'''
    ''' it returns array_like X and Y for data fitting'''
    location = os.path.abspath(filename)
    df = pd.read_csv('%s'%location,sep='\t')
    X = np.array(df[X_var].values)
    Y = np.array(df[Y_var].values)
    return X,Y

def split_train_test(X,Y,test_fraction,random_state):
    '''This function takes X,Y,test_fraction and random_state number'''
    '''It returns training and test sets with desired seperated size'''
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=test_fraction, random_state=random_state)
    return X_train, X_test, Y_train, Y_test


def R_squared(y_true,y_pred):
    u = K.sum(K.square(y_true - y_pred))
    v = K.sum(K.square(y_true - K.mean(y_true)))
    return (1 - u/(v + K.epsilon()))

def make_combo(option1=['tanh','relu','linear'],option2=['0.1','0.01','0.001']):
    parameter_combo = []
    for i in option1:
        for j in option2:
            combo = []
            combo.append(i)
            combo.append(j)
            parameter_combo.append(combo)
            
    return parameter_combo

def make_pairwise_list(max_depth=2, options=['tanh', 'softmax', 'relu']):
    combinations = []
    for i in range(len(options)**max_depth):
        state = []
        for depth in range(max_depth):
            if depth == 0:
                #print(f"{i:4}:  {options[i // len(options)**(max_depth-1)]}", end='  ')
                state.append(options[i // len(options)**(max_depth-1)])
            elif depth == max_depth - 1:
                #print(f"{options[i % len(options)]}", end='  ')
                state.append(options[i % len(options)])
            else:
                #print(f"{options[i // len(options)**(depth) % len(options)]}", end='  ')
                state.append(options[i // len(options)**(depth) % len(options)])
        #print("")
        combinations.append(state)
    return combinations

def model_search(X_train,Y_train,X_test,Y_test,
    input_dim,output_dim,layers,activation_functions=['tanh','softmax','linear']):
    iterations = len(activation_functions)**(layers + 2)
    inner_iterations = len(activation_functions)**layers
    af_combs = make_pairwise_list(max_depth=layers, options=activation_functions)
    print(f'{layers}\t{activation_functions}\t{iterations} iterations required')
    best_R = 0.0
    best_activation = []
    iteration_n = 1
    for n in range(layers):
        best_activation.append('none')
    best_activation = []
    for inner_iteration in range(inner_iterations):
        for activation_in in activation_functions:
            inner_list = []
            for k in range(layers):
                inner_list.append(af_combs[inner_iteration][k])
            for layer in range(layers):
                for activation_out in activation_functions:
                    print(f"running iteration {iteration_n}")
                    parameter_list = []
                    parameter_list.append(activation_in)
                    parameter_list.extend(inner_list)
                    parameter_list.append(activation_out)
                    print(f"create input layer with activation of {activation_in}")
                    
                    model = keras.Sequential()
                    model.add(keras.layers.Dense(10,input_dim = input_dim,activation=activation_in))
                    for i in range(len(inner_list)):
                        print(f"create hidden layer {layer+1} of type {inner_list[i]}")
                        model.add(keras.layers.Dense(20,activation = inner_list[i]))
                    print(f"create output layer with activation of {activation_out}")
                    model.add(keras.layers.Dense(output_dim,activation=activation_out))
                    model.compile(loss='mean_squared_error', optimizer='adam', 
                                  metrics=[R_squared])
                    history = model.fit(X_train,Y_train,epochs=50, batch_size=10,validation_split=0.33)
                    scores = model.evaluate(X_test,Y_test)
                    print(scores[1])
                    iteration_n += 1 
                    if scores[1]>best_R:
                        best_activation = parameter_list
                        best_R = scores[1]
                    else:
                        pass
        print("")
    print(best_activation)
    print(best_R)
    
    return best_activation
 
def model_multi_search(X_train,Y_train,X_test,Y_test,input_dim,output_dim,layers,
                        activation_functions=['tanh', 'softmax', 'relu'],units=[5,10,20]):
    iterations = (len(units)*len(activation_functions))**(layers+1)*len(activation_functions)
    inner_iterations = (len(units)*len(activation_functions))**layers
    options= make_combo(option1=activation_functions,option2=units)
    af_combs = make_pairwise_list(max_depth=layers, options=options)
    print(f'{layers}\t{activation_functions}\t{iterations} iterations required')
    best_R = 0.0
    best_param = []
    iteration_n = 1
    for n in range(layers):
        best_param.append(['none','none'])
    best_activation = []
    for inner_iteration in range(inner_iterations):
        for option_in in options:
            inner_list=[]
            for k in range(layers):
                inner_list.append(af_combs[inner_iteration][k])
            for layer in range(layers):
                for activation_out in activation_functions:
                    print(inner_list)
                    print(f"running iteration {iteration_n}")
                    parameter_list = []
                    parameter_list.append(option_in)
                    parameter_list.extend(inner_list)
                    parameter_list.append(activation_out)
                    print(f"create input layer with activation of {option_in[0]} and units of {option_in[1]}")
                    
                    model = keras.Sequential()
                    model.add(keras.layers.Dense(option_in[1],input_dim = input_dim,activation=option_in[0]))
                    for i in range(len(inner_list)):
                        print(f"create hidden layer {i+1} of activation {inner_list[i][0]} and units {inner_list[i][1]}")
                        model.add(keras.layers.Dense(inner_list[i][1],activation = inner_list[i][0]))
                    print(f"create output layer with activation of {activation_out} and units of {output_dim}")
                    model.add(keras.layers.Dense(output_dim,activation=activation_out))
                    model.compile(loss='mean_squared_error', optimizer='adam', 
                                  metrics=[R_squared])
                    history = model.fit(X_train,Y_train,epochs=50, batch_size=10,validation_split=0.33)
                    scores = model.evaluate(X_test,Y_test)
                    
                    iteration_n += 1 
                    if scores[1]>best_R:
                        best_param = parameter_list
                        best_R = scores[1]
                    else:
                        pass
        print("")
    print(best_param)
    print(best_R)
    return best_param

def layer_search(X_train,Y_train,X_test,Y_test,
                 input_dim,output_dims,
                 activation_functions,units,hidden_layers=[1,3,5]):
    best_list = []
    
    for layer_count in hidden_layers:
        best_param = model_multi_search(X_train=X_train,Y_train=Y_train,
                                        X_test=X_test,Y_test=Y_test,
                                        input_dim=input_dim,output_dim=output_dims,
                                        layers=layer_count,
                                        activation_functions=activation_functions,units=units)
        best_list.append(best_param)
        
    print(best_list)
    
                                                          