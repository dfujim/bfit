/* List of functions for which we integrate numerically 
 * Derek Fujimoto
 * October 2017
 */ 

#ifndef INTEGRATION_FNS_CPP
#define INTEGRATION_FNS_CPP

#include <math.h>
#include "DEIntegrator.h"

/// ======================================================================= ///
/// Stretched exponential class for integration
class StrExp
{
    public:
        double lambda;      // 1/T1
        double beta;        // beta
        double lifetime;    // probe lifetime 
        double t;           // time
    
        // Constructor
        StrExp(double t1,double lambda1,double beta1,double probelife)
        {
            lambda = lambda1;
            beta = beta1;
            lifetime = probelife;
            t = t1;
        }
    
        // Calculator
        double operator()(double tprime) const
        {
            return exp((tprime-t)/lifetime)*exp(-pow((t-tprime)*lambda,beta));
        }
};

/// ======================================================================= ///
/// Stretched exponential class for integration
class MixedStrExp
{
    public:
        double lambda1;      // 1/T1
        double beta1;        // beta
        double lambda2;      // 1/T1
        double beta2;        // beta
        double alpha;       // mixing parameter
        double lifetime;    // probe lifetime 
        double t;           // time
    
        // Constructor
        MixedStrExp(double t1,double lambda11,double beta11,double lambda21,
                double beta21,double alpha1, double probelife)
        {
            lambda1 = lambda11;
            lambda2 = lambda21;
            beta1 = beta11;
            beta2 = beta21;
            alpha = alpha1;
            lifetime = probelife;
            t = t1;
        }
    
        // Calculator
        double operator()(double tprime) const
        {
            return exp((tprime-t)/lifetime)*
                    (alpha*exp(-pow((t-tprime)*lambda1,beta1))+
                    (1-alpha)*exp(-pow((t-tprime)*lambda2,beta2)));
        }
};

/// ======================================================================= ///
/// Integral of stretched exponential from 0 to x
class Integrator
{
    public:
        // Variables
        double lifetime;
    
        // Methods
        Integrator(double lifetime);
        double StrExp(double t, double tprime, double lamb, double beta);
        double MixedStrExp(double t, double tprime, double lamb1, double beta1, 
                double lamb2, double beta2, double amp);
};


/// ======================================================================= ///
/// Integrator Class Methods ///

// Constructor ----------------------------------------------------------------
Integrator::Integrator(double lifetime)
{
    this->lifetime = lifetime;
}

// Integrate StrExp -----------------------------------------------------------
double Integrator::StrExp(double t, double tprime, double lamb, double beta)
{
    return DEIntegrator<StrExp>::Integrate(StrExp(t,lamb,beta,lifetime),0,
                                           tprime,1e-6);
}

// Integrate MixedStrExp ------------------------------------------------------
double Integrator::MixedStrExp(double t, double tprime, double lamb1, 
                               double beta1, double lamb2, double beta2, 
                               double amp)
{
    return DEIntegrator<MixedStrExp>::Integrate(MixedStrExp(t,lamb1,beta1,lamb2,
            beta2,aamp,life),0,tprime,1e-6);
}

#endif // INTEGRATION_FNS_CPP
