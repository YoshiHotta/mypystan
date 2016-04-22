
data{
 int<lower=1> n;
 vector[n] x;
 vector[n] y;
}

parameters{
 real<lower=0> alpha;
 real<lower=0> delta;
 real<lower=0> dx;
}

model{
 matrix[n,n] cov;
 vector[n] mu;
 
 for(i in 1:n){
  for(j in 1:i-1){
   cov[i,j] <- alpha*exp(-(x[i]-x[j])*(x[i]-x[j])/(2.0*dx*dx));
   cov[j,i] <- cov[i,j];
  }
  cov[i,i] <- alpha + delta;
  mu[i] <- 0.0;
 }
 
 y ~ multi_normal(mu, cov);
}

generated quantities{
 vector[n] t; // prediction of y at the same x
 
 // this block is just introduced not to output these defined quantities
 {
  matrix[n,n] cov_yy;
  matrix[n,n] cov_yt;
  matrix[n,n] cov_tt;
  matrix[n,n] inv_cov_yy;
  
  for(i in 1:n){
   for(j in 1:i-1){
    cov_yy[i,j] <- alpha*exp(-(x[i]-x[j])*(x[i]-x[j])/(2.0*dx*dx));
    cov_yy[j,i] <- cov_yy[i,j];
    cov_yt[i,j] <- cov_yy[i,j];
    cov_yt[j,i] <- cov_yy[i,j];
    cov_tt[i,j] <- cov_yy[i,j];
    cov_tt[j,i] <- cov_yy[i,j];
   }
   cov_yy[i,i] <- alpha + delta;
   cov_yt[i,i] <- alpha;
   cov_tt[i,i] <- alpha;
  }
  
  inv_cov_yy <- inverse(cov_yy);
  t <- multi_normal_rng(cov_yt * inv_cov_yy * y, cov_tt - cov_yt * inv_cov_yy * cov_yy);
 }
 
}
