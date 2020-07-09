#include "oc_single_shot_heuristic.h"

#include "constraint_generator.h"

#include "../option_parser.h"
#include "../plugin.h"

#include "../utils/markup.h"

#include <cmath>
#include <fstream>
#include <algorithm>
#include <cctype>
#include <locale>

using namespace std;

// trim from start (in place)
static inline void ltrim(std::string &s) {
    s.erase(s.begin(), std::find_if(s.begin(), s.end(), [](int ch) {
        return !std::isspace(ch);
    }));
}

// trim from end (in place)
static inline void rtrim(std::string &s) {
    s.erase(std::find_if(s.rbegin(), s.rend(), [](int ch) {
        return !std::isspace(ch);
    }).base(), s.end());
}

// trim from both ends (in place)
static inline void trim(std::string &s) {
    ltrim(s);
    rtrim(s);
}

using namespace std;

namespace operator_counting {

OCSingleShotHeuristic::OCSingleShotHeuristic(const Options &opts)
    : Heuristic(opts),
      constraint_generators(
          opts.get_list<shared_ptr<ConstraintGenerator>>("constraint_generators")),
      lp_h(lp::LPSolverType(opts.get_enum("lpsolver"))),
      lp_h_c(lp::LPSolverType(opts.get_enum("lpsolver"))),
      lp_h_s(lp::LPSolverType(opts.get_enum("lpsolver"))),
      calculate_h(opts.get<bool>("calculate_h")),
      calculate_h_c(opts.get<bool>("calculate_h_c")),
      calculate_h_s(opts.get<bool>("calculate_h_s")),
      filter(opts.get<int>("filter")),
      soft_weight(opts.get<int>("weights")) {

    // Initialize map to convert operator name to operator ID
    map_operators(false);

    // Read observations from file and prune invalid
    load_observations();
    prune_observations();

    // Create heuristic constraints
    double infinity = lp_h.get_infinity();
    vector<lp::LPConstraint> constraints;
    for (const auto &generator : constraint_generators) {
        generator->initialize_constraints(task, constraints, infinity);
    }

    // Create operator variables
    vector<lp::LPVariable> variables;
    for (OperatorProxy op : task_proxy.get_operators()) {
        variables.push_back(lp::LPVariable(0, infinity, op.get_cost()));
    }

    // Initialize LP problem without observation constraints
    if (calculate_h) {
        lp_h.load_problem(lp::LPObjectiveSense::MINIMIZE, variables, constraints);
    }

    // Set observation weights 
    if (calculate_h_s) {
        if (soft_weight == 1) {
            double weight_per_op = 1.0 / 1000;
            for (auto it = observations.begin(); it != observations.end(); ++it)
                if (op_indexes.find(*it) != op_indexes.end())
                    weights[*it] = weight_per_op;
        } else if (soft_weight == 2) {
            double weight_per_op = 1.0;
            for (auto it = observations.begin(); it != observations.end(); ++it)
                if (op_indexes.find(*it) != op_indexes.end())
                    weights[*it] = weight_per_op;
        } else if (soft_weight == 3) {
            double weight_per_op = 1.0;
            double weight = weight_per_op;
            for (auto it = observations.begin(); it != observations.end(); ++it) {
                if (op_indexes.find(*it) != op_indexes.end()) {
                    max_weight += weight;
                    weights[*it] += weight;
                    weight += weight_per_op;
                }
            }
            for (auto it = obs_occurrences.begin(); it != obs_occurrences.end(); ++it)
                weights[it->first] /= it->second;
        }
    }

    // Create observation variables
    for (auto it = valid_obs_occurrences.begin(); it != valid_obs_occurrences.end(); ++it) {
        // Determine how many times the same observed operation occurs.
        string op = it->first;
        int count_obs = it->second;
        cout << "constraint " << op << ": " << std::to_string(op_indexes[op]) << endl;
        int var_id = variables.size();
        variables.push_back(lp::LPVariable(0, count_obs, -weights[op]));
        lp::LPConstraint lt_y(0, infinity);
        lt_y.insert(op_indexes[op], 1);
        lt_y.insert(var_id, -1);
        constraints.push_back(lt_y);
    }

    if (calculate_h_s) {
        lp_h_s.load_problem(lp::LPObjectiveSense::MINIMIZE, variables, constraints);
    }

    if (calculate_h_c) {
        int k = max(0, filter - num_pruned_observations);
        lp::LPConstraint constraint(num_valid_observations - k, infinity);
        int var_id = task_proxy.get_operators().size();
        for (auto it = valid_obs_occurrences.begin(); it != valid_obs_occurrences.end(); ++it) {
            constraint.insert(var_id, 1);
            variables[var_id].objective_coefficient = 0;
            var_id++;
        }
        constraints.push_back(constraint);
        lp_h_c.load_problem(lp::LPObjectiveSense::MINIMIZE, variables, constraints);
    }

}

void OCSingleShotHeuristic::map_operators(bool show) {
    if (show) {
        cout << endl << string(80, '*') << endl;
        cout << "# Mapping X -> op: " << endl;
    }
    int i = 0;
    for (OperatorProxy op : task_proxy.get_operators()) {
        // Caching operator variable indexes
        std::string op_name (op.get_name());
        for (size_t i = 0; i< op.get_name().size(); ++i) {
            op_name[i] = tolower(op_name.c_str()[i]);
        }
        op_indexes[op_name] = i;
        if (show) {
            cout << "["<< op_name<< "]: " << op_indexes[op_name] << endl;
        }
        i++;
    }
    if (show) {
        cout << string(80, '*') << endl;
    }
}

void OCSingleShotHeuristic::show_variables_and_objective(const vector<lp::LPVariable> &variables) {
    cout << endl << string(80, '*') << endl;
    cout << "# Variables(" << variables.size() << "): " << endl;
    for (int i = 0; i < (int) variables.size(); ++i) {
        cout << "X[" << i << "] = Variable('X_" << i << "'";
        cout << ", lb=" << variables[i].lower_bound;
        cout << ", ub=" << variables[i].upper_bound;
        cout << ", cost[" << i << "] = " << variables[i].objective_coefficient << endl;
    }
    cout << string(80, '*') << endl;
    cout << endl << string(80, '*') << endl;
    cout << "# Objective function: " << endl;
    cout << "obj = Objective(";
    for (int i = 0; i < (int) variables.size(); ++i) {
        cout << "cost[" << i << "] * X[" << i << "]";
        if (i < (int) variables.size() - 1) {
            cout << " + ";
        }
    }
    cout << ", direction='min')" << endl;
    cout << string(80, '*') << endl;
}

void OCSingleShotHeuristic::load_observations() {
    // Read observations from file
    cout << endl << string(80, '*') << endl;
    cout << std::endl << "Load observations" << std::endl;
    ifstream obs_file;
    obs_file.open("obs.dat");
    if(obs_file.is_open()){
        while(!obs_file.eof()) {
            string obs;
            getline(obs_file, obs);
            trim(obs);
            if(!obs.empty() && obs[0]!=';') {
                obs = obs.substr(1,obs.length()-2);
                std::string obs_name (obs);
                for (size_t i = 0; i< obs.size(); ++i) {
                    obs_name[i] = tolower(obs.c_str()[i]);
                }
                cout << "Observation: " << obs_name << endl;
                observations.push_back(obs_name);
            }
        }
    }
    cout << endl << string(80, '*') << endl;
    obs_file.close();
    // =-=-=-=-= Each observation is associated with its number of occurrences. =-=-=-=-= //
    obs_occurrences.clear();
    for(auto it = observations.begin() ; it != observations.end(); ++it) {
        obs_occurrences[*it]++;
    }
}

void OCSingleShotHeuristic::prune_observations() { 
    // Debugging output (cumulative: appends new info with each call)
    std::fstream outfile("debug/observation_sanity.txt", std::ios::out|std::ios::app) ;
    // Set output stream (set to std::cout to print to terminal)
    std::ostream& outstream = outfile;
    // Reinitialize class variables for invalid (unmapped) observations.
    num_pruned_observations = 0;
    pruned_observations.clear();
    valid_obs_occurrences.clear();
    vector<string> invalid_operators;
    int num_invalid_operators = 0;
    //outstream << endl << string(80, '*') << endl;
    //outstream << "Enforcing observation constraints" << std::endl;
    outstream << endl<< "-+-"; // marks start
    for (auto it = obs_occurrences.begin(); it != obs_occurrences.end(); ++it) {
        // Observation is mappable?
        // If not: ignore observation, storing it in a separate list.
        if (op_indexes.find(it->first) == op_indexes.end()) {
            //outstream << "[INVALID OP] " << op << endl;
            invalid_operators.push_back(it->first);
            num_invalid_operators += 1;
            num_pruned_observations += it->second;
        } else {
            valid_obs_occurrences[it->first] = it->second;
            num_valid_observations += it->second;
        }
    }
    // =-=-=-=-= Report on pruned and invalid operators/observations. =-=-=-=-= //
    // Basic structure:
    // Print invalid observations, number of operators and total number of observations.
    // Last line holds number of observations and number of invalid observations,
    //  followed by any relevant tags.
    for (int i = 0 ; i < num_invalid_operators; i++) {
        outstream << endl<< "[INVALID OP] " << invalid_operators[i] << ": " << obs_occurrences[invalid_operators[i]] <<" time(s).";
    }
    if (num_pruned_observations > 0) {
        outstream << endl << "# mappable operators: " << op_indexes.size() << endl;
        outstream << "Obs - Total: " << observations.size() << " | Invalid: " << num_pruned_observations;
    }
    outfile.flush();
    outfile.close();
}

void OCSingleShotHeuristic::output_results(double result, double result_c, double result_s) {
    // Log solutions
    cout << endl << string(80, '*') << endl;
    vector<double> solution;
    if (calculate_h_s)
        solution = lp_h_s.extract_solution();
    else if (calculate_h_c)
        solution = lp_h_c.extract_solution();
    else
        solution = lp_h.extract_solution();
    for (int i = 0; i < (int) solution.size(); ++i) {
        cout << "X[" << i << "] = " << solution[i] << endl;
    }
    // Get hits/misses
    double obs_hits = 0, obs_miss = 0;
    unordered_map<string, double> counts;
    for(auto it = observations.begin() ; it != observations.end(); ++it) {
        if (op_indexes.find(*it) != op_indexes.end()) {
            if (solution[op_indexes[*it]] > counts[*it]) {
                obs_hits++;
                counts[*it]++;
            } else {
                obs_miss++;
            }
        }
    }
    cout << "obs-report: " << observations.size() << " " << num_pruned_observations << " " << obs_hits << " " << obs_miss << endl;
    cout << "h-values: " << result << " " << result_c << " " << result_s << endl;
    cout << string(80, '*') << endl << endl;
    // Write result
    cout << "Writing results...";
    ofstream results;
    results.open("ocsingleshot_heuristic_result.dat");
    results << "obs-report: " << observations.size() << " " << num_pruned_observations << " " << obs_hits << " " << obs_miss << endl;
    results << "h-values: " << result << " " << result_c << " " << result_s << endl;
    // Write counts
    int var_i = 0;
    for (OperatorProxy op : task_proxy.get_operators()) {
        if (solution[var_i] > 0) {
            results << "(" << op.get_name() << ") = " << solution[var_i] << endl;
        }
        var_i++;
    }
    results.flush();
    results.close();
    cout << "Done!" << endl;
}

OCSingleShotHeuristic::~OCSingleShotHeuristic() {
}

int OCSingleShotHeuristic::compute_heuristic(const GlobalState &global_state) {
    State state = convert_global_state(global_state);
    return compute_heuristic(state);
}

int OCSingleShotHeuristic::compute_heuristic(const State &state) {
    double result = 0, result_c = 0, result_s = 0;
    assert(!lp_h_c.has_temporary_constraints());
    for (const auto &generator : constraint_generators) {
        if (calculate_h && generator->update_constraints(state, lp_h)) {
            lp_h.clear_temporary_constraints();
            result = DEAD_END;
            calculate_h = false;
        }
        if (calculate_h_c && generator->update_constraints(state, lp_h_c)) {
            lp_h_c.clear_temporary_constraints();
            result_c = DEAD_END;
            calculate_h_c = false;
        }
        if (calculate_h_s && generator->update_constraints(state, lp_h_s)) {
            lp_h_s.clear_temporary_constraints();
            result_s = DEAD_END;
            calculate_h_s = false;
        }
    }
    // LP result without observation constraints
    if (calculate_h) {
        lp_h.solve();
        if (lp_h.has_optimal_solution()) {
            double epsilon = 0.01;
            double objective_value = lp_h.get_objective_value();
            result = ceil(objective_value - epsilon);
        } else {
            result = 0.0 / 0.0;
        }
        cout << "h: " << result << endl;
    }
    // LP result with hard observation constraints
    if (calculate_h_c) {
        lp_h_c.solve();
        if (lp_h_c.has_optimal_solution()) {
            double epsilon = 0.01;
            double objective_value = lp_h_c.get_objective_value();
            result_c = ceil(objective_value - epsilon);
        } else {
            result_c = 0.0 / 0.0;
        }
        cout << "h_c: " << result_c << endl;
    }
    // LP result with soft observation constraints
    if (calculate_h_s) {
        lp_h_s.solve();
        if (lp_h_s.has_optimal_solution()) {
            double epsilon = 0.01;
            double objective_value = lp_h_s.get_objective_value();
            result_s = ceil(objective_value - epsilon) + max_weight;
        } else {
            result_s = 0.0 / 0.0;
        }
        cout << "h_s: " << result_s << endl;
    }

    output_results(result, result_c, result_s);

    exit(EXIT_SUCCESS);
    return 0;
}

static shared_ptr<Heuristic> _parse(OptionParser &parser) {
    parser.document_synopsis(
        "Operator counting heuristic",
        "An operator counting heuristic computes a linear program (LP) in each "
        "state. The LP has one variable Count_o for each operator o that "
        "represents how often the operator is used in a plan. Operator "
        "counting constraints are linear constraints over these varaibles that "
        "are guaranteed to have a solution with Count_o = occurrences(o, pi) "
        "for every plan pi. Minimizing the total cost of operators subject to "
        "some operator counting constraints is an admissible heuristic. "
        "For details, see" + utils::format_conference_reference( // TODO - Change this for our paper
            {"Florian Pommerening", "Gabriele Roeger", "Malte Helmert",
             "Blai Bonet"},
            "LP-based Heuristics for Cost-optimal Planning",
            "http://www.aaai.org/ocs/index.php/ICAPS/ICAPS14/paper/view/7892/8031",
            "Proceedings of the Twenty-Fourth International Conference"
            " on Automated Planning and Scheduling (ICAPS 2014)",
            "226-234",
            "AAAI Press",
            "2014"));

    parser.document_language_support("action costs", "supported");
    parser.document_language_support(
        "conditional effects",
        "not supported (the heuristic supports them in theory, but none of "
        "the currently implemented constraint generators do)");
    parser.document_language_support(
        "axioms",
        "not supported (the heuristic supports them in theory, but none of "
        "the currently implemented constraint generators do)");
    parser.document_property("admissible", "yes");
    parser.document_property(
        "consistent",
        "yes, if all constraint generators represent consistent heuristics");
    parser.document_property("safe", "yes");
    // TODO: prefer operators that are non-zero in the solution.
    parser.document_property("preferred operators", "no");

    parser.add_list_option<shared_ptr<ConstraintGenerator>>(
        "constraint_generators",
        "methods that generate constraints over operator counting variables");
    parser.add_option<bool>("calculate_h", "calculate h-value", "true");
    parser.add_option<bool>("calculate_h_c", "calculate h-value with hard observation constraints", "true");
    parser.add_option<bool>("calculate_h_s", "calculate h-value with soft observation constraints", "true");
    parser.add_option<int>("weights", "weight type for soft constraints", "1");
    parser.add_option<int>("filter", "observation filter", "0");
    lp::add_lp_solver_option_to_parser(parser);
    Heuristic::add_options_to_parser(parser);
    Options opts = parser.parse();
    if (parser.help_mode())
        return nullptr;
    opts.verify_list_non_empty<shared_ptr<ConstraintGenerator>>(
        "constraint_generators");
    if (parser.dry_run())
        return nullptr;
    return make_shared<OCSingleShotHeuristic>(opts);
}

static Plugin<Evaluator> _plugin("ocsingleshot", _parse);
}
