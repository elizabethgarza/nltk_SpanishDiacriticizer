import argparse
import itertools
import nltk
import os
import pandas
import pickle
from tqdm import tqdm
import unidecode

import preprocess
import clsfr_prep

"""
TODOs for branch = `split`:

--fix code under optional args
--try optional args on `baby_data_sets`
--fix code so that files print to the correct directories
--train `ESTA` on `full.txt`
--git commit

TODOS for branch = `optimize for-loops`
--start optimizing for-loops in preprocess.py 

TODOS for branch = `melliza clean-up`
--get rid of bad entries 
--re-run code to regenerate CSV file
--draw a histogram to see the distribution of mellizas 
--update READ.me on data based on all of this work

LASTLY: 
--start retraining clsfrs
"""

if __name__ =='__main__': 
    parser = argparse.ArgumentParser(description='Trains nltk naive bayes classifiers and loads them into pickle files')
    parser.add_argument('corpus_path', help='str: path to corpus file')
    parser.add_argument('eval_data', help='must input either `dev` or `test` as arguments; this indicates whether to evaluate on dev or test ')
    parser.add_argument('-no', help='int: number of classifiers that are to be trained')
    parser.add_argument('-m1_m2', help='str: melliza pair to be classified with dash in between; e.g. `él_el` ')
    args = parser.parse_args()


    if args.m1_m2:

        os.chdir('..')
        os.chdir('data/pickles') 
        
        melliza1 = args.m1_m2.split('_')[0]
        melliza2 = args.m1_m2.split('_')[-1]
        
        # makes train, dev and test for training and evaluation phase
        train, dev, test = preprocess.Preprocess(args.corpus_path, melliza1, melliza2).train_dev_test()

        # preprocesses train in order to train clsfr
        train = clsfr_prep.Clsfr_Prep(train, dev, test).train_prep()

        # trains clsfr 
        clsfr = nltk.classify.naivebayes.NaiveBayesClassifier.train(train)

        # calculates micro `dev` and `test`accuracies
        # prints dev accuracies to a file for error analysis
        if args.eval_data == 'dev':
            os.chdir('micro_devs')
            with open(f'{unidecode.unidecode(melliza1)}_dev.txt', 'w') as sink: 
                for item in dev: 
                    print(item[0][0], file=sink)   # to join the tokenized_sents into one big list, the line is:  `print(list(itertools.chain.from_iterable(list_object)))`
                print(file=sink)   
            dev = clsfr_prep.Clsfr_Prep(train, dev, test).dev_prep()
            clsfr_accuracy = nltk.classify.util.accuracy(clsfr, dev)
            print(f'{unidecode.unidecode(melliza1)} accuracy:  {clsfr_accuracy:.4f}')          
        elif args.eval_data == 'test':
            test = clsfr_prep.Clsfr_Prep(train, dev, test).test_prep()
            clsfr_accuracy = nltk.classify.util.accuracy(clsfr, dev)
            print(f'{unidecode.unidecode(melliza1)} accuracy:  {clsfr_accuracy:.4f}')

    else: 

        os.chdir('..')
        os.chdir('data')

        # loads the csv file
        if args.no:
            mellizas = pandas.read_csv('top_200_mellizas.csv', sep=',', nrows=int(args.no)) # if you are making classifiers in batches, add argument `skiprows = [i for i in range(1,no_of_rows_to_skip)]`
        else: 
            mellizas = pandas.read_csv('top_200_mellizas.csv', sep=',').head(200)

        # transfers data from `mellizas` object above into a list object.
        max1_max2_tokens = mellizas['MAX1_MELLIZA'] + '\t'+ mellizas['MAX2_MELLIZA'] 

        # iterates through mellizas list object above, one row at a time and appends them to `clsfr_accuracies`
        clsfr_accuracies = []
        for row in tqdm(max1_max2_tokens): 
            tokenized_row = row.split()
            melliza1 = tokenized_row[0]
            melliza2 = tokenized_row[-1]

            # makes train, dev and test for training and evaluation phase
            train, dev, test = preprocess.Preprocess(args.corpus_path, melliza1, melliza2).train_dev_test()

            # continues to preprocesses train, dev and test for training and evaluation phase
            # trains classifier 
            train = clsfr_prep.Clsfr_Prep(train, dev, test).train_prep()
            clsfr = nltk.classify.naivebayes.NaiveBayesClassifier.train(train)
            
            # calculates micro `dev` and `test`accuracies
            # prints dev accuracies to a file for error analysis
            if args.eval_data == 'dev':
                os.chdir('micro_devs')
                with open(f'{unidecode.unidecode(melliza1)}_dev.txt', 'w') as sink: 
                    for item in dev: 
                        print(item[0][0], file=sink)   # to join the tokenized_sents into one big list, the line is:  `print(list(itertools.chain.from_iterable(list_object)))`
                    print(file=sink)   
                dev = clsfr_prep.Clsfr_Prep(train, dev, test).dev_prep()
                clsfr_accuracy = nltk.classify.util.accuracy(clsfr, dev)
                print(f'{unidecode.unidecode(melliza1)} accuracy:  {clsfr_accuracy:.4f}')          
            
            elif args.eval_data == 'test':
                test = clsfr_prep.Clsfr_Prep(train, dev, test).test_prep()
                clsfr_accuracy = nltk.classify.util.accuracy(clsfr, dev)
                print(f'{unidecode.unidecode(melliza1)} accuracy:  {clsfr_accuracy:.4f}')
                clsfr_accuracies.append((unidecode.unidecode(melliza1),clsfr_accuracy))

            # loads the clfr onto a pickle file
            os.chdir('..')
            os.chdir('pickles')
            saved_clsfr = open(f'{unidecode.unidecode(melliza1)}.pickle', 'wb')
            pickle.dump(clsfr, saved_clsfr)
            saved_clsfr.close()

        # prints evaluation results to a file 
        with open('dev_eval.txt', 'w') as sink:
            for clsfr_accuracy in clsfr_accuracies:  
                print(clsfr_accuracy, file=sink)
            print(file=sink)

    



                


    




            






        
