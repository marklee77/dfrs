import random

def gen_linear_prob(seed=None, num_dimensions=1, num_bins=0, num_items=0,
                    cov=0.0, slack=None, **kwargs):

    random.seed(seed) 

    bins = [[max(1, min(int(random.normalvariate(50, 50 * cov)), 100))
              for i in range(num_dimensions)]
              for j in range(num_bins)]

    bindim_totals = [sum(bin_[i] for bin_ in bins) 
                     for i in range(num_dimensions)]

    items = [[random.randint(1, 100) for i in range(num_dimensions)] 
             for j in range(num_items)]

    itemdim_totals = [sum(item[i] for item in items)
                      for i in range(num_dimensions)]

    itemfuncs = []
    for item in items:
        for i in range(num_dimensions):
            if slack is not None:
                item[i] = max(1, int(item[i] * (1.0 - slack) * 
                                     bindim_totals[i] / itemdim_totals[i]))
        itemmin = [random.randint(1, x) for x in item]
        itemfunc = 'lambda x: [x*(a - b) + b for (a, b) in zip(%s, %s)]' % (
            str(item), str(itemmin))
        itemfuncs.append(itemfunc)

    problem = {
        'seed' : seed, 'num_dimensions' : num_dimensions, 'num_bins' : num_bins,
        'num_items' : num_items, 'cov' : cov, 'slack' : slack, 'bins' : bins,
        'itemfuncs' : itemfuncs
    }

    return dict(list(problem.items()) + list(kwargs.items()))

