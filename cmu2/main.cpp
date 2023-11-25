

#include <iostream>
#include <vector>
#include <cmath>
#include <fstream>

using namespace std;

double f(double x){
    return x*(x*x-7)/(-6);
}

void writePointstoFile(vector<double> x, vector<double> y, string filename){
    ofstream file(filename);
    if (file.is_open()){
        for(unsigned long i=0; i<x.size(); i++){
            file << x[i] << " " << y[i] << endl;
        }
        cout << x.size() << " Points writen to " << filename << endl;
    }
    else{
        cout << "Wrong, file is not open" << endl;
    }
}


double f1(double x1, double x2, double p1, double p2, double t, double c) {
    return x2;
}

double f2(double x1, double x2, double p1, double p2, double t, double c) {
    return (p2 * exp(-c * t)) / 2;
}

double f3(double x1, double x2, double p1, double p2, double t, double c) {
    return -48 / (1 + exp(-c * t));
}

double f4(double x1, double x2, double p1, double p2, double t, double c) {
    return -p1;
}

class rungeKutta{
public:
    vector<double> x1_;
    vector<double> x2_;
    vector<double> p1_;
    vector<double> p2_;
    double q_;
    double s_;
    void computeParam(double a, double b, double c, int n, double h);
};

void rungeKutta::computeParam(double a, double b, double c, int n, double h) {
    vector<double> x1(n + 1, 0.0);
    vector<double> x2(n + 1, 0.0);
    vector<double> p1(n + 1, 0.0);
    vector<double> p2(n + 1, 0.0);

    x1[0] = a;
    x2[0] = 0;
    p1[0] = 0;
    p2[0] = b;

    for (int i = 0; i < n; ++i) {
        double k11 = f1(x1[i], x2[i], p1[i], p2[i], i * h, c);
        double k21 = f2(x1[i], x2[i], p1[i], p2[i], i * h, c);
        double k31 = f3(x1[i], x2[i], p1[i], p2[i], i * h, c);
        double k41 = f4(x1[i], x2[i], p1[i], p2[i], i * h, c);

        double k12 = f1(x1[i] + h * k11 / 2, x2[i] + h * k21 / 2, p1[i] + h * k31 / 2, p2[i] + h * k41 / 2, i * h + h / 2, c);
        double k22 = f2(x1[i] + h * k11 / 2, x2[i] + h * k21 / 2, p1[i] + h * k31 / 2, p2[i] + h * k41 / 2, i * h + h / 2, c);
        double k32 = f3(x1[i] + h * k11 / 2, x2[i] + h * k21 / 2, p1[i] + h * k31 / 2, p2[i] + h * k41 / 2, i * h + h / 2, c);
        double k42 = f4(x1[i] + h * k11 / 2, x2[i] + h * k21 / 2, p1[i] + h * k31 / 2, p2[i] + h * k41 / 2, i * h + h / 2, c);

        double k13 = f1(x1[i] + h * k12 / 2, x2[i] + h * k22 / 2, p1[i] + h * k32 / 2, p2[i] + h * k42 / 2, i * h + h / 2, c);
        double k23 = f2(x1[i] + h * k12 / 2, x2[i] + h * k22 / 2, p1[i] + h * k32 / 2, p2[i] + h * k42 / 2, i * h + h / 2, c);
        double k33 = f3(x1[i] + h * k12 / 2, x2[i] + h * k22 / 2, p1[i] + h * k32 / 2, p2[i] + h * k42 / 2, i * h + h / 2, c);
        double k43 = f4(x1[i] + h * k12 / 2, x2[i] + h * k22 / 2, p1[i] + h * k32 / 2, p2[i] + h * k42 / 2, i * h + h / 2, c);

        double k14 = f1(x1[i] + h * k13, x2[i] + h * k23, p1[i] + h * k33, p2[i] + h * k43, i * h + h, c);
        double k24 = f2(x1[i] + h * k13, x2[i] + h * k23, p1[i] + h * k33, p2[i] + h * k43, i * h + h, c);
        double k34 = f3(x1[i] + h * k13, x2[i] + h * k23, p1[i] + h * k33, p2[i] + h * k43, i * h + h, c);
        double k44 = f4(x1[i] + h * k13, x2[i] + h * k23, p1[i] + h * k33, p2[i] + h * k43, i * h + h, c);

        double r = x1[i] + h / 6 * (k11 + 2 * (k12 + k13) + k14);
        x1[i + 1] = r;

        r = x2[i] + h / 6 * (k21 + 2 * (k22 + k23) + k24);
        x2[i + 1] = r;

        r = p1[i] + h / 6 * (k31 + 2 * (k32 + k33) + k34);
        p1[i + 1] = r;

        r = p2[i] + h / 6 * (k41 + 2 * (k42 + k43) + k44);
        p2[i + 1] = r;
    }

    q_ = x1[n];
    s_ = p2[n];
    x1_=x1; x2_=x2; p1_=p1; p2_=p2;
}

vector<double> newton(double c, double eps, double h, int n) {
    double a1 = 1;
    double b1 = 1;

    double a = 0;
    double b = 0;
    
    rungeKutta Ka, Kb, Kc;
    
    Ka.computeParam(a+h, b, c, n, h);
    Kb.computeParam(a, b+h, c, n, h);
    Kc.computeParam(a, b, c, n, h);
    
    while (true) {
        
        Ka.computeParam(a+h, b, c, n, h);
        Kb.computeParam(a, b+h, c, n, h);
        Kc.computeParam(a, b, c, n, h);
        double x1_a = (Ka.q_-Kc.q_) / h;
        double x1_b = (Kb.q_-Kc.q_) / h;
        
        double x2_a = (Ka.s_-Kc.s_) / h;
        double x2_b = (Kb.s_-Kc.s_) / h;

        double det = x1_a * x2_b - x2_a * x1_b;

        double u11 = x2_b / det;
        double u12 = -x1_b / det;
        double u21 = -x2_a / det;
        double u22 = x1_a / det;

        a1 = a - u11 * Kc.q_ - u12 * Kc.s_;
        b1 = b - u21 * Kc.q_ - u22 * Kc.s_;

        if ((a - a1) * (a - a1) + (b - b1) * (b - b1) < eps) {
            break;
        }
        
        a = a1;
        b = b1;
    }
    
    vector<double> res;
    res.push_back(a);
    res.push_back(b);
    return res;
}


int main() {
    int n = 100;
    double h = 1.0 / n;
    double eps=0.001;
    double c=3;
    
    vector<double> t;
    for (int i = 0; i <= n; ++i) {
        t.push_back(i * h);
    }
    double a, b;
    a=newton(c, eps, h, n)[0];
    b=newton(c, eps, h, n)[1];
    
    rungeKutta R;
    R.computeParam(a, b, c, n, h);
    
    
    writePointstoFile(t, R.x1_, "x1_3.txt");
    writePointstoFile(t, R.x2_, "x2_3.txt");
    writePointstoFile(t, R.p1_, "p1_3.txt");
    writePointstoFile(t, R.p2_, "p2_3.txt");
    
    return 0;
}

