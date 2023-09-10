'''
RB Created Jan 30, 2021.

Ensure to look at this file for a lot of the initial work

Module to set up and run the Active learning/optimization
'''

import csv, json, time
from datetime import date
#import matplotlib.pyplot as plt
import numpy as np
import pickle
import matplotlib.pyplot as plt

# -*- coding: utf-8 -*-
# Author: Erfan Fatehi
# Created on Auguest 2021
# first trial bayesian optimization
# Pytorch Bayesian Optimization Example
# Importing all possible modules
import os
import torch
import gpytorch
import json
import pandas as pd
import seaborn as sns
from scipy import stats
import pandas as pd
from botorch.models import SingleTaskGP ,ModelListGP, FixedNoiseGP
from botorch.fit import fit_gpytorch_model
from gpytorch.mlls import ExactMarginalLogLikelihood
from botorch.models.gpytorch import GPyTorchModel
from gpytorch.distributions import MultivariateNormal
from gpytorch.means import ConstantMean
from gpytorch.models import ExactGP
from gpytorch.kernels import RBFKernel, ScaleKernel, MaternKernel
from gpytorch.likelihoods import GaussianLikelihood
from gpytorch.mlls import ExactMarginalLogLikelihood
from gpytorch.priors import GammaPrior
from botorch.optim import optimize_acqf_discrete
from botorch.acquisition.monte_carlo import qExpectedImprovement, qUpperConfidenceBound, qNoisyExpectedImprovement
from botorch.acquisition.analytic import NoisyExpectedImprovement


class ActiveLearning:
    def __init__(self,root_path,experiment_name, test, exp_count): # add in the rootpath here
	# variables defined in the original campaign file
    # Note test and exp_count both imported - may take out test later once not needed anymore
    # exp_count is simply the {i} from the experiment number in the campaign
            self.root_path = root_path
            self.experiment_name = experiment_name
            self.test = test
            self.exp_count = exp_count
	
    def determine_first_experiment(self,data):
        # Initialize the X-tensor and determine the first experiment, to be used only for the very first test
        # This is for making the true X_Sample tensor:
        # As is, makes the x-matrix for 4 elements, can easily add more as necessary
        delete_me = np.array([0,0,0]) # Need to just make a dummy matrix first of the row number of columns
        a1 = np.round(np.linspace(0.1,1,num = 5), decimals = 1)
        a2 = np.round(np.linspace(-0.5,0.5,num = 11), decimals = 1)
        a3 = np.round(np.linspace(5,60,num = 11), decimals = 1) 
        for i in a1:
            for j in a2:
                for k in a3:
                    add = np.array([i,j,k])
                    delete_me = np.vstack((delete_me,add))
        X_matrix = np.delete(delete_me, (0), axis=0)
        X_matrix = torch.tensor(X_matrix)
        
        # Pick a random first point from the available matrix and update the dictionary
        random_indices = np.random.choice(X_matrix.shape[0], size=1, replace=False)
        X_samples = X_matrix[random_indices]

        # Update the dictionary with the initial X and total X matrix
        # This one will just always store the total original X_matrix
        data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['X_matrix'] = X_matrix
        # This one will always store the up-to-date chosen X matrix
        data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['X_sample'] = X_samples

        # Need to store the indices as well for easy access
        total_indexes = np.array([i for i in range(X_matrix.shape[0])])
        train_inds= random_indices 
        test_inds = [i for i in total_indexes if not i in train_inds] 
        data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['total_indexes'] = total_indexes
        data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['train_inds'] = train_inds
        data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['test_inds'] = test_inds

        # Save to pickle file:
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'wb') as f:
            pickle.dump(data, f)

    def determine_next_experiment_random(self, data):

        # First import the current indices to be able to use:
        # Note - will need to import the previous test indexes as that is where they are stored from initial
        # determine_first_experiment and then all subsequent experiments index data will be at Test_(n - 1)
        # Note cannot just remake them or will lose all information
        # Want to do something where we populate the correct information first into the correct test?
        
        if self.exp_count == 0:
        
            total_indexes = data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['total_indexes']
            train_inds = data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['train_inds']
            test_inds = data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['test_inds']

        else:

            total_indexes = data[f'{self.experiment_name}'][f'Test_{self.exp_count-1}']['AL']['total_indexes']
            train_inds = data[f'{self.experiment_name}'][f'Test_{self.exp_count-1}']['AL']['train_inds']
            test_inds = data[f'{self.experiment_name}'][f'Test_{self.exp_count-1}']['AL']['test_inds']

        # import the latest X_sample (X_chosen) matrix, note this will also be stored in the previous Test_(n-1)  
        if self.exp_count == 0:

            X_samples = np.array(data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['X_sample'])

        else:

            X_samples = np.array(data[f'{self.experiment_name}'][f'Test_{self.exp_count-1}']['AL']['X_sample'])

        print(f'the previous X_samples matrix imported and is currently active is {X_samples}')

        # Need to convert X_samples into a tensor
        init_x = torch.tensor(X_samples)

        # Now grab a new set of experiments from the available X_matrix, indexed to the available selections remaining from test_inds. Note indexing from original
        # X_Matrix at exp_count = 0
        X_matrix = np.array(data[f'{self.experiment_name}'][f'Test_0']['AL']['X_matrix'])[test_inds]
        X_matrix = torch.tensor(X_matrix)
        random_indices = np.random.choice(X_matrix.shape[0], size=1, replace=False)
        print(f'This is the random index chosen for this run = {random_indices}')
        candidates = X_matrix[random_indices]

        # Update dictionary for newly selected X_samples
        data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['X_sample'] = torch.cat((init_x,candidates),0)

        # Now update all dictionaries and indexes accordingly, storing correctly in the appropriate experimental dictionary 
        print(f"New candidates composition to be added to trainset: {X_matrix[random_indices]}")
       
        #adding the new data point to train set for the next round
        train_inds = np.append(train_inds, random_indices)
        test_inds = [k for k in total_indexes if not k in train_inds]

        # Update the dicitonaries accordingly
        data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['total_indexes']=total_indexes
        data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['train_inds']=train_inds
        data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['test_inds']=test_inds

        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'wb') as f:
            pickle.dump(data, f)

    def determine_next_experiment(self, data):

        # First import the current indices to be able to use:
        # Note - will need to import the previous test indexes as that is where they are stored from initial
        # determine_first_experiment and then all subsequent experiments index data will be at Test_(n - 1)
        # Note cannot just remake them or will lose all information
        # Want to do something where we populate the correct information first into the correct test?
        
        if self.exp_count == 0:
        
            total_indexes = data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['total_indexes']
            train_inds = data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['train_inds']
            test_inds = data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['test_inds']

        else: # exp_counts are - 1 based on way the data is stored

            total_indexes = data[f'{self.experiment_name}'][f'Test_{self.exp_count-1}']['AL']['total_indexes']
            train_inds = data[f'{self.experiment_name}'][f'Test_{self.exp_count-1}']['AL']['train_inds']
            test_inds = data[f'{self.experiment_name}'][f'Test_{self.exp_count-1}']['AL']['test_inds']

        # import the latest overpotential matrix
        # y in this case is correct to have Test = n because updated with post_processing
        
        # Build an array of all the OP data to use as the y array for the active learning
        y = np.zeros(self.exp_count+1) # Make the initial array of zeroes for size of exp_count (note +1 is needed)
        for i in range(self.exp_count+1): # WHY DID I DO IT LIKE THIS, IS THIS NEEDED?
            y[i] = np.array([data[f'{self.experiment_name}'][f'Test_{i}']['Metric']['OP']])

        Y_samples = -y[:, None] # the data object should be in columns
        print(Y_samples)

        # import the latest X_sample (X_chosen) matrix, note this will also be stored in the previous Test_(n-1)  
        if self.exp_count == 0:

            X_samples = np.array(data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['X_sample'])

        else:

            X_samples = np.array(data[f'{self.experiment_name}'][f'Test_{self.exp_count-1}']['AL']['X_sample'])

        # print so can see what composition will be used
        print(f'Experimental Variables = {X_samples}')
        
        #new_candidate_pool is the pool that we pick the new candidate from
        ### Note right now I have this just set to Test_0 since that is where it is originally stored and we do not
        ### delete anything from it. May have to change if we end up doing that (have X_matrix_orig and alter etc.)
        xx = np.array(data[f'{self.experiment_name}'][f'Test_0']['AL']['X_matrix'])
        new_candidate_pool = np.zeros(xx.shape)
        new_candidate_pool = xx.astype(np.float32) 
        
        #initial train set in tensor
        init_x = torch.tensor(X_samples)
        init_y = torch.tensor(Y_samples)

        #maximum of the sampled dataset
        best_init_y = torch.tensor(init_y.max().item()) 
        #best_init_y =torch.tensor(init_y.min().item())
        #xxx = np.delete(xxx, random_indices, 0)
        #%%

        #%% generate next points based on discrete input for acq function (xxx is the pool of choices)
        
        def next_points(init_x , init_y , best_init_y ,new_candidate_pool, n_points):
            with gpytorch.settings.cholesky_jitter(1e-6):
            #Gaussian process surrogate model
                init_var=torch.ones(init_y.shape, dtype=float)*0.005
                single_model = FixedNoiseGP(init_x, init_y ,init_var)
                mll= ExactMarginalLogLikelihood(single_model.likelihood, single_model)
                fit_gpytorch_model(mll)
            #acquisition function
                NEI = NoisyExpectedImprovement(single_model, init_x , num_fantasies=100)
                # EI = qExpectedImprovement (model = single_model, best_f = best_init_y, maximize=True)
                # qNEI = qNoisyExpectedImprovement(model = single_model, X_baseline = init_x)
                # UCB = qUpperConfidenceBound(model = single_model, beta=10)
                #new candidates for the next round of analysis
                candidates , _ = optimize_acqf_discrete(
                            acq_function= NEI, 
                            q=n_points,
                            choices=torch.tensor(new_candidate_pool),
                            max_batch_size=128,
                            unique=1)
            return candidates
        

        # Now run the optimization
        print(f"Optimization of: {self.test}")
        candidates= next_points(init_x, init_y, best_init_y, new_candidate_pool, 1)

        #update the dictionary for the new x selected
        data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['X_sample'] = torch.cat((init_x,candidates),0)
        
        # print the new candidate for person to see
        print(f"New candidate: {candidates}")
        
        # Dump the candidate data so that robot can retrieve the file and information for what X composition to make next run
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'wb') as f:
            pickle.dump(data, f)

        # summation of elements of new candidates should be equal to 1 all the time
        cand=candidates.numpy()
        
        #to find the closest set of input data from our test set
        index= np.where(np.all(new_candidate_pool==cand,axis=1))
    
    # this step is for when the algorithm is stuck to a certain candidate and the new candidate was already studied
    # its like jumping out of a local minimum or maximum
        if (index in train_inds): 
            w=1
        else: w=0
        if (w==1):
            print("Show Must Go On or (We are at the global optimized point)")
            index = np.random.choice(test_inds)
            train_inds = np.append(train_inds, index)
            test_inds = [k for k in total_indexes if not k in train_inds]
            data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['total_indexes']=total_indexes
            data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['train_inds']=train_inds
            data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['test_inds']=test_inds
            #test_inds = np.delete(test_inds, index)
            # X_samples =xx[ train_inds, :]
            # Y_samples =yy[ train_inds]
            # init_x = torch.tensor(X_samples)
            # init_y = torch.tensor(Y_samples)
            # # Again, normally the robot would provide this, but here we are updating based on the new metric y
            # best_init_y =torch.tensor(init_y.max().item())

        else:   
            print(f"New candidates composition to be added to trainset: {xx[index]}")
            #adding the new data point to train set for the next round
            train_inds = np.append(train_inds, index)
            test_inds = [k for k in total_indexes if not k in train_inds]
            #test_inds = np.delete(test_inds, index)
            data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['total_indexes']=total_indexes
            data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['train_inds']=train_inds
            data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['test_inds']=test_inds
            #xxx = xx[test_inds,:]
            #X_samples =xx[ train_inds, :]
            #Y_samples =yy[ train_inds]
            #init_x = torch.tensor(X_samples)
            #init_y = torch.tensor(Y_samples)
            #Again, normally the robot would provide this, but here we are updating based on the new metric y
            #best_init_y =torch.tensor(init_y.max().item())
            #xxx = np.delete(xxx, index, 0)
            #print(f"Best point thus far is this: {best_init_y}")
        
        #dict[f'{experiment_name}'][f'{test_name}']['AL']['y_metric'] = init_y #update the dictionary for the new y
        
        # Need to put the pickle file here to update with each run, this spot represents updating once the experiment is done
        # and the y metric is obtained
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'wb') as f:
            pickle.dump(data, f)