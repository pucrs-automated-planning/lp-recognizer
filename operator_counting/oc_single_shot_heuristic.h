#ifndef OPERATOR_COUNTING_OPERATOR_COUNTING_HEURISTIC_H
#define OPERATOR_COUNTING_OPERATOR_COUNTING_HEURISTIC_H

#include "../heuristic.h"

#include "../lp/lp_solver.h"

#include <memory>
#include <vector>
#include <string>
#include <ostream>

namespace options {
class Options;
}

namespace operator_counting {
class ConstraintGenerator;

class OCSingleShotHeuristic : public Heuristic {
    std::vector<std::shared_ptr<ConstraintGenerator>> constraint_generators;
    lp::LPSolver lp_solver;
    bool enforce_observations;
    bool soft_constraints;
    std::unordered_map<std::string,int> op_indexes;
    std::vector<std::string> observations;
protected:
    virtual int compute_heuristic(const GlobalState &global_state) override;
    int compute_heuristic(const State &state);
    void load_observations();
    void enforce_observation_constraints(std::vector<lp::LPConstraint> &constraints);
    void add_observation_soft_constraints(std::vector<lp::LPVariable> &variables, std::vector<lp::LPConstraint> &constraints);
	  void add_supersoft_noisy(std::vector<lp::LPVariable> &variables, std::vector<lp::LPConstraint> &constraints);
    void add_observation_overlap_constraints(std::vector<lp::LPVariable> &variables, std::vector<lp::LPConstraint> &constraints);

    void report_constraint(std::ostream& stream,lp::LPConstraint constraint, std::vector<lp::LPVariable> &variables, std::string op);
    void output_results(int result);
public:
    explicit OCSingleShotHeuristic(const options::Options &opts);
    ~OCSingleShotHeuristic();
    void map_operators(bool show = false);
    void show_variables_and_objective(const std::vector<lp::LPVariable> &variables, bool show = false);
};
}

#endif
