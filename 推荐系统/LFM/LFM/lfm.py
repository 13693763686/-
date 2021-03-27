import numpy as np
import sys
import read_file
import operator

def lfm_train(train_data,F,alpha,beta,step):
    """
    Args:
        train_data: train_data for lfm
        F: user vector len, item vector len
        alpha: regularization facotr
        beta:learning rate
        step:iteration number

    Returns:
        dict: key itemid. value:np.array()
        dict: key userid, value:np.array()
    """
    user_vec = {}
    item_vec = {}
    for step_index in range(step):
        for data_instance in train_data:
            userid, itemid, label = data_instance
            if userid not in user_vec:
                user_vec[userid] = init_model(F)
            if itemid not in item_vec:
                item_vec[itemid] = init_model(F)
            delta = label - model_predict(user_vec[userid],item_vec[itemid])
            for index in range(F):
                user_vec[userid][index] += beta*(delta*item_vec[itemid][index] - alpha*user_vec[userid][index])
                item_vec[itemid][index] += beta*(delta*user_vec[userid][index] - alpha*item_vec[itemid][index])
            beta = beta * 0.9
    return user_vec, item_vec



def  init_model(vector_len):
    """
    Args:
        vector_len: the len of the vector
    Returns:
        embedding vector
    """
    ##there may be some tricks for initilization
    return np.random.rand(vector_len)

def model_predict(user_vector,item_vector):
    """
    Args:
        user_vector: --
        item_vector: ---
    Returns:
        the predicted score
    """
    res = np.dot(user_vector,item_vector)/(np.linalg.norm(user_vector)*np.linalg.norm(item_vector))
    return res

def model_train_process():
    """
    test lfm training process
    """
    train_data=read_file.get_train_data("../data/ratings.txt")
    user_vec, item_vec = lfm_train(train_data, 50, 0.01, 0.1, 50)
    for userid in user_vec:
        recom_result = give_recom_result(user_vec, item_vec, userid)

def give_recom_result(user_vec, item_vec, userid):
    """
    use lfm model result give fix userid recom result
    Args:
        user_vec: lfm model result
        item_vec:lfm model result
        userid:fix userid
    Return:
        a list:[(itemid, score)...]
    """
    fix_num = 10
    if userid not in user_vec:
        return []
    record = {}
    recom_list = []
    user_vector = user_vec[userid]
    for itemid in item_vec:
        item_vector = item_vec[itemid]
        res = np.dot(user_vector, item_vector)/(np.linalg.norm(user_vector)*np.linalg.norm(item_vector))
        record[itemid] = res
    # the usage of operator.itemgetter(1) function
    for zuhe in sorted(record.items(), key= operator.itemgetter(1), reverse=True)[:fix_num]:
        itemid = zuhe[0]
        score = round(zuhe[1], 3)
        recom_list.append((itemid, score))
    return recom_list