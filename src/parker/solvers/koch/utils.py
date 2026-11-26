"""
Contient les fonctions nécessaire pour la résolution du système d'équations de Wiener Hopf de Koch
"""

from src.constants import *
import numpy as np
from scipy.signal import argrelmin
from scipy.optimize import minimize_scalar

# ---------------- Construction de la matrice de Koch ----------------

def _delta_kr(i,j):
    return 1*(i == j)

def _f_star_f(f,d0):    
    return f*d0/c_0

def _K_f(f_star,M):    
    return 2*np.pi*f_star/np.sqrt(1-M**2)

def _l_f(l0,d0,M):
    return l0/(d0*np.sqrt(1-M**2))

def _l_ratio_f(l_star,M):
    return l_star/np.sqrt(1-M**2)

def _a_f(alpha0,M):
    return np.cos(alpha0)/np.sqrt(1-M**2)

def _b_f(alpha0):
    return np.sin(alpha0)

def _d_f(alpha0,M):
    return np.sqrt(_a_f(alpha0,M)**2+_b_f(alpha0)**2)

def _alpha_f(alpha0,M):
    return np.atan(np.sqrt(1-M**2)*np.tan(alpha0))

def _sigma_f(sigma0,M,f_star,alpha0):
    return sigma0 - M*_K_f(f_star,M)*_a_f(alpha0,M)

def _mu_f(r,f_star,alpha0,M):
    K = _K_f(f_star,M)
    b = _b_f(alpha0)
    if K>r*np.pi/b:
        return -np.sqrt(K**2-(r*np.pi/b)**2)
    else:
        return 1j*np.sqrt(-K**2+(r*np.pi/b)**2)
    
def _sigma_plus_f(r,f_star,alpha0,M,sigma0):
    K = _K_f(f_star,M)
    d = _d_f(alpha0,M)
    sigma = _sigma_f(sigma0,M,f_star,alpha0)
    alpha = _alpha_f(alpha0,M)
    K_frac = (2*r*np.pi-sigma)/d
    if K**2>K_frac**2:
        return K_frac*np.cos(alpha) - np.sin(alpha)*np.sqrt(K**2-K_frac**2)
    else:
        return K_frac*np.cos(alpha) + 1j*np.sin(alpha)*np.sqrt(K_frac**2-K**2)

def _sigma_minus_f(r,f_star,alpha0,M,sigma0):
    K = _K_f(f_star,M)
    d = _d_f(alpha0,M)
    sigma = _sigma_f(sigma0,M,f_star,alpha0)
    alpha = _alpha_f(alpha0,M)
    K_frac = (2*r*np.pi-sigma)/d
    if K**2>K_frac**2:
        return K_frac*np.cos(alpha) + np.sin(alpha)*np.sqrt(K**2-K_frac**2)
    else:
        return K_frac*np.cos(alpha) - 1j*np.sin(alpha)*np.sqrt(K_frac**2-K**2)
    
def _chi_f(xi,alpha0,M):
    alpha = _alpha_f(alpha0,M)
    if alpha==0:
        return -1j*xi/np.pi*(- _a_f(alpha0,M)*(alpha-np.pi/2))
    else:
        return -1j*xi/np.pi*(_b_f(alpha0)*np.log(2*np.sin(alpha)) - _a_f(alpha0,M)*(alpha-np.pi/2))

def _Kcal_plus_f(xi,f_star,alpha0,M,sigma0,Niter):
    K = _K_f(f_star,M)
    b = _b_f(alpha0)
    chi = _chi_f(xi,alpha0,M)
    sigma = _sigma_f(sigma0,M,f_star,alpha0)
    Kcal0 = -K*np.sin(K*b)/(4*np.sin((b*K-sigma)/2)*np.sin((b*K+sigma)/2))
    prod = 1

    for r in range(Niter):
        mu = _mu_f(r,f_star,alpha0,M)
        if mu == 0:
            num = np.nan
        else:
            num = 1+xi/mu
        den = (1+xi/_sigma_plus_f(r,f_star,alpha0,M,sigma0))*(1+(1-_delta_kr(r,0))*xi/_sigma_plus_f(-r,f_star,alpha0,M,sigma0))
        if den == 0:
            prod *= np.nan
        else:
            prod *= num/den

    return Kcal0*np.exp(chi)*prod

def _Kcal_minus_f(xi,f_star,alpha0,M,sigma0,Niter):
    chi = _chi_f(xi,alpha0,M)
    prod = 1

    for r in range(Niter):
        mu = _mu_f(r,f_star,alpha0,M)
        if mu == 0:
            num = np.nan
        else:
            num = 1-xi/mu
        den = (1+xi/_sigma_minus_f(r,f_star,alpha0,M,sigma0))*(1+(1-_delta_kr(r,0))*xi/_sigma_minus_f(-r,f_star,alpha0,M,sigma0))
        if den == 0:
            prod *= np.nan
        else:
            prod *= num/den

    return np.exp(-chi)*prod

def _P_f(r,f_star,alpha0,l0,d0,M,sigma0,Niter):
    l = _l_f(l0,d0,M)
    mu_r = _mu_f(r,f_star,alpha0,M)
    a = _a_f(alpha0,M)
    b = _b_f(alpha0)
    sigma = _sigma_f(sigma0,M,f_star,alpha0)
    Kcal = _Kcal_minus_f(-mu_r,f_star,alpha0,M,sigma0,Niter)

    return -2*np.exp(1j*l*mu_r)*Kcal**2*(1-(-1)**r*np.cos(a*mu_r+sigma))/(b*mu_r*(1+_delta_kr(r,0)))

def _Q_f(r,f_star,alpha0,l0,d0,M,sigma0,Niter):
    l = _l_f(l0,d0,M)
    mu_r = _mu_f(r,f_star,alpha0,M)
    a = _a_f(alpha0,M)
    b = _b_f(alpha0)
    sigma = _sigma_f(sigma0,M,f_star,alpha0)
    Kcal = _Kcal_plus_f(mu_r,f_star,alpha0,M,sigma0,Niter)

    return 2*np.exp(1j*l*mu_r)*Kcal**2*(1-(-1)**r*np.cos(a*mu_r-sigma))/(b*mu_r*(1+_delta_kr(r,0)))

def _P_ratio_f(r,f_star,alpha0,l_star,M,sigma0,Niter):
    l = _l_ratio_f(l_star,M)
    mu_r = _mu_f(r,f_star,alpha0,M)
    a = _a_f(alpha0,M)
    b = _b_f(alpha0)
    sigma = _sigma_f(sigma0,M,f_star,alpha0)
    Kcal = _Kcal_minus_f(-mu_r,f_star,alpha0,M,sigma0,Niter)

    return -2*np.exp(1j*l*mu_r)*Kcal**2*(1-(-1)**r*np.cos(a*mu_r+sigma))/(b*mu_r*(1+_delta_kr(r,0)))

def _Q_ratio_f(r,f_star,alpha0,l_star,M,sigma0,Niter):
    l = _l_ratio_f(l_star,M)
    mu_r = _mu_f(r,f_star,alpha0,M)
    a = _a_f(alpha0,M)
    b = _b_f(alpha0)
    sigma = _sigma_f(sigma0,M,f_star,alpha0)
    Kcal = _Kcal_plus_f(mu_r,f_star,alpha0,M,sigma0,Niter)

    return 2*np.exp(1j*l*mu_r)*Kcal**2*(1-(-1)**r*np.cos(a*mu_r-sigma))/(b*mu_r*(1+_delta_kr(r,0)))

def _L_ij_f(i,j,d0,l0,f_star,alpha0,M,sigma0,Niter):
    return _P_f(j,f_star,alpha0,l0,d0,M,sigma0,Niter)/(_mu_f(i,f_star,alpha0,M)+_mu_f(j,f_star,alpha0,M))

def _N_ij_f(i,j,d0,l0,f_star,alpha0,M,sigma0,Niter):
    mu_i = _mu_f(i,f_star,alpha0,M)
    mu_j = _mu_f(j,f_star,alpha0,M)
    K = _K_f(f_star,M)
    return _Q_f(j,f_star,alpha0,l0,d0,M,sigma0,Niter)*(M*mu_j+K)/((mu_i+mu_j)*(K-M*mu_i))

def _L_ij_ratio_f(i,j,l_star,f_star,alpha0,M,sigma0,Niter):
    return _P_ratio_f(j,f_star,alpha0,l_star,M,sigma0,Niter)/(_mu_f(i,f_star,alpha0,M)+_mu_f(j,f_star,alpha0,M))

def _N_ij_ratio_f(i,j,l_star,f_star,alpha0,M,sigma0,Niter):
    mu_i = _mu_f(i,f_star,alpha0,M)
    mu_j = _mu_f(j,f_star,alpha0,M)
    K = _K_f(f_star,M)
    return _Q_ratio_f(j,f_star,alpha0,l_star,M,sigma0,Niter)*(M*mu_j+K)/((mu_i+mu_j)*(K-M*mu_i))

###################################
# building a matrix of the form : #
#                                 #        
#     | I_N+1 |  -L   |           #          
#     |_______|_______|           #      
#     |       |       |           #            
#     |  N    | I_N+1 |           #     
#                                 #
###################################     


def _build_matrix(N_size,d0,l0,f,alpha0,M,sigma0,Niter):
    f_star = _f_star_f(f,d0)
    mat = np.zeros((2*N_size+2,2*N_size+2))
    for i in range(2*N_size+2):
        mat[i,i] = 1
    for i in range(N_size+1):
        # print('building matrix line '+str(i))
        for j in range(N_size+1):
            L_ij = _L_ij_f(i,j,d0,l0,f_star,alpha0,M,sigma0,Niter)
            N_ij = _N_ij_f(i,j,d0,l0,f_star,alpha0,M,sigma0,Niter)
            mat[i,N_size+1+j] = -L_ij
            mat[N_size+1+i,j] =  N_ij
    return mat

def _build_matrix_ratio(N_size,l_star,f_star,alpha0,M,sigma0,Niter):
    # print(f_star)
    mat = np.zeros((2*N_size+2,2*N_size+2))
    for i in range(2*N_size+2):
        mat[i,i] = 1
    for i in range(N_size+1):
        # print('building matrix line '+str(i))
        for j in range(N_size+1):
            L_ij = _L_ij_ratio_f(i,j,l_star,f_star,alpha0,M,sigma0,Niter)
            N_ij = _N_ij_ratio_f(i,j,l_star,f_star,alpha0,M,sigma0,Niter)
            # print(L_ij)
            mat[i,N_size+1+j] = -np.real(L_ij)
            mat[N_size+1+i,j] =  np.real(N_ij)
    return mat

# ---------------- Résolution par optimisation du déterminant ----------------

def koch2D_solver(N_x,N_y,b,s,chi,M,N_matrix,Niter,N_sumsize):
    b_star  = b/s
    alpha0  = np.pi/2-chi
    sigma0  = -(N_y+1)*np.pi

    def det_equations(Kstar):
        """
        Calcul du déterminant de la matrice correspondant aux équations données par la méthode de Wiener Hopf en fonction du nombre d'onde adimensionné Kstar dans le but de déterminer la valeur de Kstar pour laquelle ce déterminant s'annule
    
        Fonction pour la pulsation omega_2D
        """
        return np.linalg.det(_build_matrix_ratio(N_matrix,b_star,Kstar,alpha0,M,sigma0,N_sumsize))

    min_bounds  = [N_y/2+1e-5 , (N_y+1)/2 - 1e-5]

    X = np.linspace(min_bounds[0],min_bounds[1],Niter)
    Y = np.array([det_equations(k) for k in X])

    min = X[argrelmin(Y)]

    if min[N_x]*0.95<min_bounds[0]:
        bound_low = min_bounds[0]
    else:
        bound_low = min[N_x]*0.95

    if min[N_x]*1.05>min_bounds[1]:
        bound_high = min_bounds[1]
    else:
        bound_high = min[N_x]*1.05

    new_bounds = [bound_low,bound_high]

    root = minimize_scalar(det_equations,bounds=new_bounds,method='bounded')

    return root.x*c_0/s # type: ignore