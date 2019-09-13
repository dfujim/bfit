/* List of functions for which we integrate numerically 
 * Derek Fujimoto
 June 2018
 */ 
#ifndef INTEGRATION_FNS_H
#define INTEGRATION_FNS_H

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
};

#endif // INTEGRATION_FNS_H //
