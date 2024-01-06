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
import os
import torch
import gpytorch
import json
import pandas as pd
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
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from scipy.spatial.distance import euclidean
from scipy.stats.qmc import Sobol


class ActiveLearning:
    def __init__(self,root_path,experiment_name, test, exp_count): # add in the rootpath here
	# variables defined in the original campaign file
    # Note test and exp_count both imported - may take out test later once not needed anymore
    # exp_count is simply the {i} from the experiment number in the campaign
            self.root_path = root_path
            self.experiment_name = experiment_name
            self.test = test
            self.exp_count = exp_count
            self.loaded_data = self.load_data()
	
    def load_data(self):
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'rb') as file:
            loaded_data = pickle.load(file)
            return loaded_data

    def save_data(self):
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'wb') as file:
            pickle.dump(self.loaded_data, file)
	
    def determine_first_experiment(self):
        # Initialize the X-tensor and determine the first experiment, to be used only for the very first test
        # This is for making the true X_Sample tensor:
        # As is, makes the x-matrix for 4 elements, can easily add more as necessary
        a1 = np.round(np.linspace(0.1, 1, num=5), decimals=1)
        a2 = np.round(np.linspace(-0.5, 0.5, num=11), decimals=1)
        a3 = np.round(np.linspace(5, 60, num=11), decimals=1)

        # Use meshgrid to create all combinations of values from a1, a2, and a3
        a1, a2, a3 = np.meshgrid(a1, a2, a3, indexing='ij')
        X_matrix = np.column_stack((a1.ravel(), a2.ravel(), a3.ravel()))

        X_matrix = torch.tensor(X_matrix, dtype=torch.float64)
        
        # Pick a random first point from the available matrix and update the dictionary
        random_indices = np.random.choice(X_matrix.shape[0], size=1, replace=False)
        X_samples = X_matrix[random_indices]

        # Update the dictionary with the initial X and total X matrix
        # This one will just always store the total original X_matrix
        self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['X_matrix'] = X_matrix
        # This one will always store the up-to-date chosen X matrix
        self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['X_sample'] = X_samples

        # Need to store the indices as well for easy access
        total_indexes = np.array([i for i in range(X_matrix.shape[0])])
        train_inds= random_indices 
        test_inds = [i for i in total_indexes if not i in train_inds] 
        self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['total_indexes'] = total_indexes
        self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['train_inds'] = train_inds
        self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['test_inds'] = test_inds

        # Save to pickle file:
        self.save_data()

    def determine_next_experiment_random(self):
        # First import the current indices to be able to use:
        # Note - will need to import the previous test indexes as that is where they are stored from initial
        # determine_first_experiment and then all subsequent experiments index data will be at Test_(n - 1)
        # Note cannot just remake them or will lose all information
        # Want to do something where we populate the correct information first into the correct test?
        
        if self.exp_count == 0:
        
            total_indexes = self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['total_indexes']
            train_inds = self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['train_inds']
            test_inds = self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['test_inds']

        else:

            total_indexes = self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count-1}']['AL']['total_indexes']
            train_inds = self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count-1}']['AL']['train_inds']
            test_inds = self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count-1}']['AL']['test_inds']

        # import the latest X_sample (X_chosen) matrix, note this will also be stored in the previous Test_(n-1)  
        if self.exp_count == 0:

            X_samples = np.array(self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['X_sample'])

        else:

            X_samples = np.array(self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count-1}']['AL']['X_sample'])

        print(f'the previous X_samples matrix imported and is currently active is {X_samples}')

        # Need to convert X_samples into a tensor
        init_x = torch.tensor(X_samples)

        # Now grab a new set of experiments from the available X_matrix, indexed to the available selections remaining from test_inds. Note indexing from original
        # X_Matrix at exp_count = 0
        X_matrix = np.array(self.loaded_data[f'{self.experiment_name}'][f'Test_0']['AL']['X_matrix'])[test_inds]
        X_matrix = torch.tensor(X_matrix)
        random_indices = np.random.choice(X_matrix.shape[0], size=1, replace=False)
        print(f'This is the random index chosen for this run = {random_indices}')
        candidates = X_matrix[random_indices]

        # Update dictionary for newly selected X_samples
        self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['X_sample'] = torch.cat((init_x,candidates),0)

        # Now update all dictionaries and indexes accordingly, storing correctly in the appropriate experimental dictionary 
        print(f"New candidates composition to be added to trainset: {X_matrix[random_indices]}")
       
        #adding the new data point to train set for the next round
        train_inds = np.append(train_inds, random_indices)
        test_inds = [k for k in total_indexes if not k in train_inds]

        # Update the dicitonaries accordingly
        self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['total_indexes']=total_indexes
        self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['train_inds']=train_inds
        self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['test_inds']=test_inds

        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'wb') as f:
            pickle.dump(self.loaded_data, f)

    def determine_next_experiment(self):

        # First import the current indices to be able to use:
        # Note - will need to import the previous test indexes as that is where they are stored from initial
        # determine_first_experiment and then all subsequent experiments index data will be at Test_(n - 1)
        # Note cannot just remake them or will lose all information
        # Want to do something where we populate the correct information first into the correct test?
        
        if self.exp_count == 0:
        
            total_indexes = self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['total_indexes']
            train_inds = self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['train_inds']
            test_inds = self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['test_inds']

        else: # exp_counts are - 1 based on way the data is stored

            total_indexes = self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count-1}']['AL']['total_indexes']
            train_inds = self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count-1}']['AL']['train_inds']
            test_inds = self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count-1}']['AL']['test_inds']

        # import the latest overpotential matrix
        # y in this case is correct to have Test = n because updated with post_processing
        
        # Build an array of all the OP data to use as the y array for the active learning
        print(f'Model update based on the previous {self.exp_count} tests')
        y = np.zeros(self.exp_count+1) # Make the initial array of zeroes for size of exp_count (note +1 is needed since exp_count starts at 0)
        for i in range(self.exp_count+1): 
            y[i] = np.array([self.loaded_data[f'{self.experiment_name}'][f'Test_{i}']['Metric']['CO_Eff']])

        Y_samples = y[:, None] # the data object should be in columns

        # import the latest X_sample (X_chosen) matrix, note this will also be stored in the previous Test_(n-1)  
        if self.exp_count == 0:

            X_samples = np.array(self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['X_sample'])

        else:

            X_samples = np.array(self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count-1}']['AL']['X_sample'])
        
        #new_candidate_pool is the pool that we pick the new candidate from
        ### Note right now I have this just set to Test_0 since that is where it is originally stored 
        total_candidate_pool = self.loaded_data[f'{self.experiment_name}'][f'Test_0']['AL']['X_matrix'] # We need to have this to properly scale the data within the next_points function
        new_candidate_pool = total_candidate_pool[test_inds] # Have the pool be any point remaining to be selected

        init_x = torch.tensor(X_samples)
        init_y = torch.tensor(Y_samples)

        #maximum of the sampled dataset
        best_init_y = init_y.max()
        #best_init_y =torch.tensor(init_y.min().item())

        # generate next points based on discrete input for acq function 
        def next_points(init_x, init_y, best_init_y, new_candidate_pool, total_candidate_pool, n_points):
            
            # First, we will scale/unscale the data within the function:
            x_scaler = StandardScaler()
            y_scaler = StandardScaler()
            
            # The scaling must be fit to the training data (init_x) and the same scale applied to the rest of x
            x_scaler.fit(init_x)
            init_x_scaled = torch.tensor(x_scaler.transform(init_x)) 
            print(f'std of input = {init_x_scaled.mean()}, {init_x_scaled.std()}')
            new_candidate_pool_scaled = torch.tensor(x_scaler.transform(new_candidate_pool)) 
            
            
            # scaling on y is its own
            # NOT, error may occur when running the optimizer re: std not being zero. This will occur when small initial datasets
            # is used due to each individual value having larger impact on the std. See eg. with a tensor of [[1],[-1]], std = root(2).
            print(f'init_y = {init_y}')
            init_y_scaled = torch.tensor(y_scaler.fit_transform(init_y))
            print(f'std of y = {init_y_scaled.mean()},  {init_y_scaled.std()}')

            
            with gpytorch.settings.cholesky_jitter(1e-6):
            #Gaussian process surrogate model
                init_var=torch.ones(init_y.shape, dtype=float)*0 #UPDATE THIS FOR CCUS
                single_model = FixedNoiseGP(init_x_scaled, init_y_scaled, init_var)
                mll= ExactMarginalLogLikelihood(single_model.likelihood, single_model)
                fit_gpytorch_model(mll)
            #acquisition function
                NEI = NoisyExpectedImprovement(single_model, init_x_scaled, num_fantasies=100)
                # EI = qExpectedImprovement (model = single_model, best_f = best_init_y, maximize=True)
                # qNEI = qNoisyExpectedImprovement(model = single_model, X_baseline = init_x)
                # UCB = qUpperConfidenceBound(model = single_model, beta=10)
                #new candidates for the next round of analysis
                candidates , _ = optimize_acqf_discrete(
                            acq_function= NEI, 
                            q=n_points,
                            choices= new_candidate_pool_scaled,
                            max_batch_size=128,
                            unique=1)
                
                # Unscale the candidates
                candidates_unscaled = x_scaler.inverse_transform(candidates)
            
            #save the model checkpoint
            model_save_path = f'{self.root_path}'
            os.makedirs(model_save_path, exist_ok=True)
            
            model_filename = os.path.join(model_save_path, f'model_checkpoint_Test_{self.exp_count}')
            
            torch.save({
                'iteration': self.exp_count,
                'model_state_dict': single_model.state_dict(),
                'train_x_scaled': init_x_scaled,
                'train_y_scaled': init_y_scaled,
                'train_x': init_x,
                'train_y': init_y,
                'init_var': init_var
                }, model_filename)
            
            return candidates_unscaled
        

        # Now run the optimization
        print(f"Optimization commencing...")
        selected_candidates = next_points(init_x, init_y, best_init_y, new_candidate_pool, total_candidate_pool, n_points = 1)

        #Unscale the data
        # candidates_unscaled = x_scaler.inverse_transform(candidates)
        # X_samples_unscaled = x_scaler.inverse_transform(X_samples_scaled)

        #update the dictionary for the new x selected
        self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['X_sample'] = torch.cat((torch.tensor(X_samples),torch.tensor(selected_candidates)),0)
        
        # print the new candidate for person to see
        print(f"New candidate: {selected_candidates}")
        
        # Dump the candidate data so that robot can retrieve the file and information for what X composition to make next run
        with open(f'{self.root_path}{self.experiment_name}_saved_data.pkl', 'wb') as f:
            pickle.dump(self.loaded_data, f)

        #to find the closest set of input data from our test set - note that it works when candidates and candidate pool are np.array()
        tolerance = 1e-6 # The tolerance is needed because we are using float numbers and there can be small differences when using them
        indices = torch.all(torch.abs(total_candidate_pool - selected_candidates) < tolerance, dim=1)
        index = torch.nonzero(indices).squeeze().tolist()
   
    # this step is for when the algorithm is stuck to a certain candidate and the new candidate was already studied
    # its like jumping out of a local minimum or maximum
        # if (index in train_inds): 
        #     w=1
        # else: w=0
        
        # if (w==1):
        #     print("Show Must Go On or (We are at the global optimized point)")
        #     index = np.random.choice(test_inds)
        #     train_inds = np.append(train_inds, index)
        #     test_inds = [k for k in total_indexes if not k in train_inds]
        #     loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['total_indexes']=total_indexes
        #     loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['train_inds']=train_inds
        #     loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['test_inds']=test_inds
        #     #test_inds = np.delete(test_inds, index)
        #     # X_samples =xx[ train_inds, :]
        #     # Y_samples =yy[ train_inds]
        #     # init_x = torch.tensor(X_samples)
        #     # init_y = torch.tensor(Y_samples)
        #     # # Again, normally the robot would provide this, but here we are updating based on the new metric y
        #     # best_init_y =torch.tensor(init_y.max().item())

        # else:   
        print(f"New candidate composition to be added to trainset: {total_candidate_pool[index]}")
        #adding the new data point to train set for the next round
        train_inds = np.append(train_inds, index)
        test_inds = [k for k in total_indexes if not k in train_inds]
        self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['total_indexes']=total_indexes
        self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['train_inds']=train_inds
        self.loaded_data[f'{self.experiment_name}'][f'Test_{self.exp_count}']['AL']['test_inds']=test_inds

        print(f"Best optimization metric thus far is: {best_init_y}")
        
        #save the pickle file
        self.save_data()

    def Sobol_sequence(self):
        # Defining the levels for each feature based on your specifications
        a1_levels = np.round(np.linspace(0.1, 1, num=5), decimals=1)
        a2_levels = np.round(np.linspace(-0.5, 0.5, num=11), decimals=1)
        a3_levels = np.round(np.linspace(5, 60, num=11), decimals=1)

        # Creating a grid of all possible combinations in the discrete space
        a1_grid, a2_grid, a3_grid = np.meshgrid(a1_levels, a2_levels, a3_levels, indexing='ij')
        discrete_space = np.column_stack((a1_grid.ravel(), a2_grid.ravel(), a3_grid.ravel()))

        # Function to scale Sobol points to the range of each feature
        def scale_to_feature_range(point, feature_ranges):
            scaled_point = []
            for i, (min_val, max_val) in enumerate(feature_ranges):
                scaled_value = min_val + point[i] * (max_val - min_val)
                scaled_point.append(scaled_value)
            return scaled_point

        # Define the ranges for each feature
        feature_ranges = [
            (a1_levels.min(), a1_levels.max()), 
            (a2_levels.min(), a2_levels.max()), 
            (a3_levels.min(), a3_levels.max())
        ]

        # Initializing the Sobol sequence generator
        sobol_gen = Sobol(d=3, scramble=False)

        # Generating Sobol sequence points (32 points for better coverage)
        sobol_points = sobol_gen.random_base2(m=5)  # 2^5 = 32 points

        # Scale Sobol points to cover the entire range of each feature
        scaled_sobol_points = np.array([scale_to_feature_range(point, feature_ranges) for point in sobol_points])

        # Function to find the closest discrete point in the space
        def find_closest_discrete_point(continuous_point, discrete_space):
            distances = [euclidean(continuous_point, dp) for dp in discrete_space]
            return discrete_space[np.argmin(distances)]

        # Selecting closest discrete points
        selected_experiments = []
        for point in scaled_sobol_points:
            closest_point = find_closest_discrete_point(point, discrete_space)
            if list(closest_point) not in selected_experiments:  # Check for uniqueness
                selected_experiments.append(list(closest_point))

            if len(selected_experiments) == 10:  # Stop when 10 unique experiments are selected
                break

        # Ensuring 10 unique experiments
        while len(selected_experiments) < 10:
            extra_points = sobol_gen.random(n=10 - len(selected_experiments))
            extra_scaled_points = np.array([scale_to_feature_range(point, feature_ranges) for point in extra_points])
            
            for point in extra_scaled_points:
                closest_point = find_closest_discrete_point(point, discrete_space)
                if list(closest_point) not in selected_experiments:  # Check for uniqueness
                    selected_experiments.append(list(closest_point))

                if len(selected_experiments) == 10:  # Stop when 10 unique experiments are selected
                    break

        # Displaying the selected experiments
        for i, exp in enumerate(selected_experiments, 1):
            print(f"Experiment {i}: {exp}")
