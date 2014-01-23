import numpy as np

from mrjob.job import MRJob
from itertools import combinations, permutations

from scipy.stats.stats import pearsonr
import math

class RestaurantSimilarities(MRJob):
#I got -8.65973959208e-15, so indeed very tiny.
    def steps(self):
        "the steps in the map-reduce process"
        thesteps = [
            self.mr(mapper=self.line_mapper, reducer=self.users_items_collector),
            self.mr(mapper=self.pair_items_mapper, reducer=self.calc_sim_collector)
        ]
        return thesteps

    def line_mapper(self,_,line):
        "this is the complete implementation"
        user_id,business_id,stars,business_avg,user_avg=line.split(',')
        yield user_id, (business_id,stars,business_avg,user_avg)

    def users_items_collector(self, user_id, values):
        """
        #iterate over the list of tuples yielded in the previous mapper
        #and append them to an array of rating information
        """
        val_array = []
        for val in values:
            val_array.append(val)
        yield user_id, val_array        


    def pair_items_mapper(self, user_id, values):
        """
        ignoring the user_id key, take all combinations of business pairs
        and yield as key the pair id, and as value the pair rating information
        """
        #pass #your code here        
        combination_dict = {}
        for v in values:
            (business_id,stars,business_avg,user_avg) = v
            combination_dict[business_id] = (stars, business_avg, user_avg)
        combination_input = combination_dict.keys()
        combination_input = sorted(combination_input)
        combination_output = combinations(combination_input, 2)
        for co in combination_output:
            co1, co2 = co
            pair_rating = [combination_dict[co1], combination_dict[co2]]
            yield co, pair_rating

    def calc_sim_collector(self, key, values):
        """
        Pick up the information from the previous yield as shown. Compute
        the pearson correlation and yield the final information as in the
        last line here.
        """
        (rest1, rest2), common_ratings = key, values
        
        rest1_ratings = []
        rest2_ratings = []
        n_common = 0
        for v in values:
            n_common += 1
            v1 = v[0] #star
            v2 = v[1] #user avg
            
            diff1=float(v1[0]) - float(v1[2]) # star - user avg
            diff2=float(v2[0]) - float(v2[2])
 
            rest1_ratings.append(diff1)
            rest2_ratings.append(diff2)

        rho=pearsonr(rest1_ratings, rest2_ratings)[0]
        if math.isnan(rho):
            rho = 0
        
        yield (rest1, rest2), (rho, n_common)


#Below MUST be there for things to work
if __name__ == '__main__':
    RestaurantSimilarities.run()