#ifndef OPERATOR_COUNTING_OPERATOR_COUNTING_HEURISTIC_H
#define OPERATOR_COUNTING_OPERATOR_COUNTING_HEURISTIC_H

#include "../heuristic.h"

#include "../lp/lp_solver.h"

#include <memory>
#include <vector>
#include <string>

namespace options {
class Options;
}

namespace operator_counting {
class ConstraintGenerator;

class OCSingleShotHeuristic : public Heuristic {
    std::vector<std::shared_ptr<ConstraintGenerator>> constraint_generators;
    lp::LPSolver lp_solver;
    lp::LPSolver lp_solver_c;
    bool enforce_observations;
    bool soft_constraints;
    bool calculate_delta;
    std::unordered_map<std::string,int> op_indexes;
    std::vector<std::string> observations;
    std::vector<std::string> pruned_observations;
    int num_pruned_observations = 0;

protected:
    virtual int compute_heuristic(const GlobalState &global_state) override;
    int compute_heuristic(const State &state);
    void load_observations();
    void enforce_observation_constraints(std::vector<lp::LPConstraint> &constraints);
    void add_observation_soft_constraints(std::vector<lp::LPVariable> &variables, std::vector<lp::LPConstraint> &constraints);
    void output_results(int result, int result_c);
public:
    explicit OCSingleShotHeuristic(const options::Options &opts);
    ~OCSingleShotHeuristic();
    void map_operators(bool show = false);
    void show_variables_and_objective(const std::vector<lp::LPVariable> &variables, bool show = false);
};
}

#endif
