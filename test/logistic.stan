data {
    int N; // # of samples
    int n[N]; // # of alive seeds + # of dead seeds for each sample
    vector<lower=0>[N] x; // sizees
    int<lower=0> y[N]; //# of alive seeds 
    vector<lower=0, upper=1>[N] f; // # factor  [C/T]
}

parameters{
    real b1;
    real b2;
    real b3;
}

transformed parameters{
    vector<lower=0>[N] theta; // lambda_i for each sample
    for (i in 1:N) {
        theta[i] <- inv_logit(b1 + b2 * x[i] + b3 * f[i]);
    }
}

model{
    for (i in 1:N) {
        y[i] ~ binomial(n[i], theta[i]);
    }
}
