# from maze_env import Maze
from stock_env import stock
from RL_brain import DeepQNetwork
import pandas as pd


def game_step(env, observation, step=None, train=True, show_log=False, my_trick=False):
    
    # RL choose action based on observation
    action = RL.choose_action(observation, train)

    # RL take action and get next observation and reward
    observation_, reward, done = env.step(action, show_log=show_log, my_trick=my_trick)

    RL.store_transition(observation, action, reward, observation_)
    # print("total profit:%.3f" % env.total_profit, end='\r')
    if step and (step > 3000) and (step % 8 == 0):
        RL.learn()

    # swap observation
    observation = observation_
    
    return observation, done
    

def run(env_list, max_round):
    step = 0
    total_profit_max = 0
    total_profit_round = 0
    for episode in range(max_round):
        profit = 0
        for env in env_list: # 遍历所有股票
            # initial observation
            observation = env.reset()
    
            while True:
                
                observation, done = game_step(env, observation, step=step)
                # print(observation)
                # break while loop when end of this episode
                if done:
                    break
                step += 1
            profit += env.total_profit
        profit = profit / len(env_list)
        print('epoch:%d, total_profit:%.3f' % (episode, env.total_profit))
        # BackTest(False)
        total_profit = 0
        for env in env_list2:
            BackTest(env, show_log=False, my_trick=True)
            total_profit += env.total_profit
        print(total_profit)
        if total_profit_max < total_profit:
            total_profit_max = total_profit
            total_profit_round = episode
    print(total_profit_round)
        
            
    


def BackTest(env, show_log=True, my_trick=False):
    observation = env.reset()
    # step=0
    while True:
        observation, done = game_step(env, observation, train=False, 
                                      show_log=show_log, my_trick=my_trick)
        # break while loop when end of this episode
        if done:
            break
    # print('total_profit:%.3f' % (env.total_profit))

if __name__ == "__main__":
    max_round = 61
    file_path_list = ['000065.SZ_NormalData.csv', '000544.SZ_NormalData.csv',
                      '000525.SZ_NormalData.csv', '000505.SZ_NormalData.csv',
                      '000045.SZ_NormalData.csv', '000020.SZ_NormalData.csv']
    
    env_list = []
    env_list2 = []
    for file_path in file_path_list:
        
        df = pd.read_csv(file_path)
        df = df.sort_values('trade_date', ascending=True)
        df = df.iloc[22:].reset_index(drop=True) # 去除前几天没有均线信息
        env_list.append(stock(df.iloc[0:1500]))
        env_list2.append(stock(df.iloc[1500:].reset_index(drop=True)))
        
    RL = DeepQNetwork(env_list[0].n_actions, env_list[0].n_features,
                      learning_rate=0.002,
                      reward_decay=0.9,
                      e_greedy=0.9,
                      replace_target_iter=300,
                      memory_size=7000,
                      batch_size=256,
                      # output_graph=True
                      )
    
    run(env_list, max_round)
    
    # env = stock(df)
    # env = BackTest(env, show_log=True)
    # env.draw('trade.png', 'profit.png')
    
    i = 0
    for env in env_list2:
        BackTest(env, show_log=False)
        name1 = 'trade1_' + str(i) + '.png'
        name2 = 'profit1_' + str(i) + '.png'
        env.draw(name1, name2)
        print('total_profit:%.3f' % (env.total_profit))
        i = i + 1
    # # env.draw('trade1.png', 'profit1.png')
    i = 0
    for env in env_list2:
        BackTest(env, show_log=False, my_trick=True)
        name1 = 'trade2_' + str(i) + '.png'
        name2 = 'profit2_' + str(i) + '.png'
        env.draw(name1, name2)
        print('total_profit:%.3f' % (env.total_profit))
        i = i + 1
