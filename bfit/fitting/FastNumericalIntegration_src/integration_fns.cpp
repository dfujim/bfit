/* List of functions for which we integrate numerically 
 * Derek Fujimoto
 June 2018
 */ 

#ifndef INTEGRATION_FNS_CPP
#define INTEGRATION_FNS_CPP

#include <math.h>
#include "DEIntegrator.h"
#include "integration_fns.h"

/// ======================================================================= ///
/// Stretched exponential class for integration
class StrExpClss
{
    public:
        double lambda;      // 1/T1
        double beta;        // beta
        double lifetime;    // probe lifetime 
        double t;           // time
    
        // Constructor
        StrExpClss(double t1,double lambda1,double beta1,double probelife)
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
/// Integrator Class Methods ///

// Constructor ----------------------------------------------------------------
Integrator::Integrator(double lifetime)
{
    this->lifetime = lifetime;
}

// Integrate StrExp -----------------------------------------------------------
double Integrator::StrExp(double t, double tprime, double lamb, double beta)
{
    return DEIntegrator<StrExpClss>::Integrate(StrExpClss(t,lamb,beta,lifetime),
                                               0,tprime,1e-6);
}

#endif // INTEGRATION_FNS_CPP
