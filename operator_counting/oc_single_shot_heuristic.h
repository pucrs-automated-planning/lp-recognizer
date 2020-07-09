#ifndef OPERATOR_COUNTING_OPERATOR_COUNTING_HEURISTIC_H
#define OPERATOR_COUNTING_OPERATOR_COUNTING_HEURISTIC_H

#include "../heuristic.h"

#include "../lp/lp_solver.h"

#include <memory>
#include <vector>
#include <string>
#include <unordered_map>

namespace options {
class Options;
}

namespace operator_counting {
class ConstraintGenerator;

class OCSingleShotHeuristic : public Heuristic {
    std::vector<std::shared_ptr<ConstraintGenerator>> constraint_generators;
    lp::LPSolver lp_h;
    lp::LPSolver lp_h_c;
    lp::LPSolver lp_h_s;
    bool calculate_h, calculate_h_c, calculate_h_s;
    int filter;

    std::unordered_map<std::string,int> op_indexes;
    std::vector<std::string> observations;
    std::vector<std::string> pruned_observations;
    std::unordered_map<std::string, int> obs_occurrences;
    std::unordered_map<std::string, int> valid_obs_occurrences;
    int num_pruned_observations = 0;
    int num_valid_observations = 0;

    int soft_weight;
    std::unordered_map<std::string, double> weights;
    double max_weight = 0;

protected:
    virtual int compute_heuristic(const GlobalState &global_state) override;
    int compute_heuristic(const State &state);
    void load_observations();
    void prune_observations();
    void output_results(double result, double result_c, double result_s);
public:
    explicit OCSingleShotHeuristic(const options::Options &opts);
    ~OCSingleShotHeuristic();
    void map_operators(bool show = false);
    void show_variables_and_objective(const std::vector<lp::LPVariable> &variables);
};
}

#endif
