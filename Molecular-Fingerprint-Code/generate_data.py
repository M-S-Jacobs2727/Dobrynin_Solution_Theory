import collections
import numpy as np
import pandas as pd
import json
import warnings

Bin = collections.namedtuple('Bin', ['min', 'max', 'inc'])

def create_curves(Bg, Bth, Pe):
    '''
    Generate a set of theoretical specific viscosity curves over a given input of weight-average molecular weight

    Arguments:
        Bg: (float) B-parameter in good regime
        Bth: (float) B-parameter in theta regime
        Pe: (float) Packing number

    Returns:
        arr: (ndarray) Array of parameters in the form of [Pe, Nw, phi, eta_sp]   
    '''

    # generate range of nw, necessary to calculate phi_star
    num_nw_vals = 64
    Nw = np.geomspace(10, 300000, num_nw_vals).astype(int)

    # define number of data points for each nw
    num_data_points_one_nw = 64

    # define concentration threshold where anything past seems unreasonable (towards bulk polymer concentration)
    phi_star_threshold = 0.01
    # init output array, each nw will have x number of data points data points of (phi,eta_sp)
    arr = np.zeros((num_data_points_one_nw*num_nw_vals,4))

    # calculate crossover concentrations
    phi_star = (Bg ** 3) * (Nw ** (1-3*0.588))
    phi_th = (Bth ** 3.0) * (Bth/Bg) ** (1/(2*0.588-1))
    phi_star_star = (Bth ** 4)
    # account for nw where semidilute solution regime starts after theta blob regime
    phi_star[phi_star > phi_th] = (Bth ** 3) * (Nw[phi_star > phi_th] ** (1-3*0.5))

    # generate phi space
    phi = np.geomspace(phi_star,phi_star_threshold,num_data_points_one_nw)

    # calculate g
    g_g = Bg**(3/(3*0.588-1))*(phi)**(1/(1-3*0.588))
    g_th = Bth**(3/(3*0.5-1))*(phi)**(1/(1-3*0.5))
    g = np.minimum(g_g,g_th)

    # calculate Ne
    Ne_g = Pe**2 * (Bg**3/phi)**(1/(3*0.588-1))
    Ne_th = Pe**2*Bth**6*phi**-2
    Ne = np.minimum(Ne_g, Ne_th)

    Nw_g = Nw / g

    # calculate eta_sp
    eta_sp_1 = Nw_g*(1+(Nw/Ne)**2)
    eta_sp_2 = Nw * (1+(Nw/Ne)**2)*phi/Bth**2
    eta_sp = np.minimum(eta_sp_1, eta_sp_2)

    # format nw, phi, eta_sp to return to array
    nw_data = np.sort(np.tile(Nw,num_data_points_one_nw))
    phi_data = np.concatenate((np.hsplit(phi.T,1)), axis=None)
    eta_sp_data = np.concatenate((np.hsplit(eta_sp.T,1)), axis=None)

    # return array of data
    arr[:,0] = Pe
    arr[:,1] = nw_data
    arr[:,2] = phi_data
    arr[:,3] = eta_sp_data

    # Apply 5% noise from gaussian distribution to phi and eta_sp data
    percentage = 0.05
    noise = np.random.normal(0,1, len(arr)) * percentage
    arr[:,2] = arr[:,2] + noise*arr[:,2]
    noise = np.random.normal(0,1, len(arr)) * percentage
    arr[:,3] = arr[:,3] + noise*arr[:,3]

    # delete rows where phi > threshold or eta_sp < 1 or eta_sp > 3.5x10^6
    arr = np.delete(arr, np.where((arr[:,3]<1) | (arr[:,2]>0.01) | (arr[:,3]>3500000)),axis=0)

    return arr

def generate_grid():
    '''
    Read json file "Bg_Bth_Pe_range.json" to generate set of parameters to use for (nw, phi, eta_sp) data generation

    Arguments:
        None

    Returns:
        grid: (dict) Values for Bg, Bth, Pe 
    '''
    with open('Bg_Bth_Pe_range.json') as f:
        range_data = json.load(f)

    params = {}
    params['Bg'] = Bin(range_data['Bg_min'], range_data['Bg_max'], range_data['Bg_inc'])
    params['Bth'] = Bin(range_data['Bth_min'], range_data['Bth_max'], range_data['Bth_inc'])
    params['Pe'] = Bin(range_data['Pe_min'], range_data['Pe_max'], range_data['Pe_inc'])

    grid = {"Bg" : np.round(np.arange(params['Bg'].min, params['Bg'].max+params['Bg'].inc, params['Bg'].inc),2),  

    "Bth" : np.round(np.arange(params['Bth'].min, params['Bth'].max+params['Bth'].inc, params['Bth'].inc),2), 

    "Pe" : np.round(np.arange(params['Pe'].min, params['Pe'].max+params['Pe'].inc, params['Pe'].inc),2),}                               

    return grid

# Main
def main():
    path = "generated_data\\"
    warnings.simplefilter(action='ignore', category=FutureWarning)
    grid = generate_grid()
    col_names = ['Pe', 'Nw', 'phi', 'eta_sp']
    for a in grid['Bg']:
        for b in grid['Bth']:
            df = pd.DataFrame(columns = col_names)
            for c in grid['Pe']:
                arr = create_curves(a, b, c)
                df2 = pd.DataFrame(data=arr, columns=col_names)
                df = df.append(df2)
            df = df.reset_index(drop=True)
            df.to_csv(f"{path}dataset_{a:.2f}_{b:.2f}.csv", index=False)
        print(a)

if __name__ == '__main__':
    main()