# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 08:50:10 2020

@author: hcb
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim

np.random.seed(1)
torch.manual_seed(41)
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device = 'cpu'

class DQN(nn.Module):
    def __init__(self, input_shape, n_actions):
        super(DQN, self).__init__()
        units = 32
        self.fc1 = nn.Linear(input_shape, units)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(units, n_actions)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x
    
# Deep Q Network off-policy
class DeepQNetwork:
    def __init__(
            self,
            n_actions,
            n_features,
            learning_rate=0.01,
            reward_decay=0.9,
            e_greedy=0.9,
            replace_target_iter=300,
            memory_size=500,
            batch_size=32,
            e_greedy_increment=None,
            output_graph=False,
    ):
        self.n_actions = n_actions
        self.n_features = n_features
        self.lr = learning_rate
        self.gamma = torch.tensor(reward_decay, dtype=torch.float)
        self.epsilon_max = e_greedy
        self.replace_target_iter = replace_target_iter
        self.memory_size = memory_size
        self.batch_size = batch_size
        self.epsilon_increment = e_greedy_increment
        self.epsilon = 0 if e_greedy_increment is not None else self.epsilon_max

        # total learning step
        self.learn_step_counter = 0

        # initialize zero memory [s, a, r, s_]
        self.memory = np.zeros((self.memory_size, n_features * 2 + 2))
        
        self.net = DQN(n_features, n_actions).to(device)
        self.tgt_net = DQN(n_features, n_actions).to(device)
        
        self.optimizer = optim.Adam(self.net.parameters(), lr=self.lr)


    def store_transition(self, s, a, r, s_):
        if not hasattr(self, 'memory_counter'):
            self.memory_counter = 0

        transition = np.hstack((s, [a, r], s_))

        # replace the old memory with new memory
        index = self.memory_counter % self.memory_size
        self.memory[index, :] = transition

        self.memory_counter += 1

    def choose_action(self, observation, train=True):
        # to have batch dimension when feed into tf placeholder
        observation = [observation[np.newaxis, :]]
        observation = torch.tensor(observation, dtype=torch.float32).to(device)
        
        if np.random.uniform() < self.epsilon or (train == False):
            # forward feed the observation and get q value for every actions
            actions_value = self.net(observation).detach().cpu().squeeze(0)
            action = np.argmax(actions_value)
        else:
            action = np.random.randint(0, self.n_actions)
        return action

    def learn(self):
        self.net.train()
        self.tgt_net.train()
        # check to replace target parameters
        if self.learn_step_counter % self.replace_target_iter == 0:
            self.tgt_net.load_state_dict(self.net.state_dict())
            # print('\ntarget_params_replaced\n')
            
        # sample batch memory from all memory
        if self.memory_counter > self.memory_size:
            sample_index = np.random.choice(self.memory_size, size=self.batch_size)
        else:
            sample_index = np.random.choice(self.memory_counter, size=self.batch_size)
        
        batch_memory = self.memory[sample_index, :]
        s_ = torch.tensor(batch_memory[:, -self.n_features:], dtype=torch.float32).to(device)
        s = torch.tensor(batch_memory[:, :self.n_features], dtype=torch.float32).to(device)
        eval_act_index = batch_memory[:, self.n_features].astype(int)
        reward = torch.tensor(batch_memory[:, self.n_features + 1], dtype=torch.float32)
        
        q_next = self.tgt_net(s_)
        q_eval = self.net(s)

        # # change q_target w.r.t q_eval's action
        q_target = q_eval.clone()

        batch_index = np.arange(self.batch_size, dtype=np.int32)
        max_, _ = torch.max(q_next, dim=1)
        q_target[batch_index, eval_act_index] = reward + self.gamma * max_
        
        # loss backpropogation
        self.optimizer.zero_grad()
        loss = nn.MSELoss()(q_eval, q_target)
#        print(loss)
        loss.backward()
        self.optimizer.step()
        
        # increasing epsilon
        self.epsilon = self.epsilon + self.epsilon_increment if self.epsilon < self.epsilon_max else self.epsilon_max
        self.learn_step_counter += 1
        