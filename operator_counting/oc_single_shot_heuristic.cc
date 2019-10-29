#include "oc_single_shot_heuristic.h"
#include "constraint_generator.h"
#include "../option_parser.h"
#include "../plugin.h"
#include "../utils/markup.h"
#include <cmath>
#include <fstream>
#include <ostream>
#include <iostream>
#include <algorithm>
#include <cctype>
#include <locale>

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
      lp_solver(lp::LPSolverType(opts.get_enum("lpsolver"))),
      enforce_observations(opts.get("enforce_observations",false)),
      soft_constraints(opts.get("soft_constraints",false)),

      op_indexes(),
      observations(){

    load_observations();

    vector<lp::LPVariable> variables;
    double infinity = lp_solver.get_infinity();
    for (OperatorProxy op : task_proxy.get_operators()) {
        int op_cost = op.get_cost();
        if (soft_constraints == false) {
            variables.push_back(lp::LPVariable(0, infinity, op_cost));
        } else { // Add variables to create soft constraints
            //variables.push_back(lp::LPVariable(0, infinity, op_cost));
            variables.push_back(lp::LPVariable(0, infinity, 10000*op_cost));
        }
    }

    vector<lp::LPConstraint> constraints;
    for (const auto &generator : constraint_generators) {
        generator->initialize_constraints(task, constraints, infinity);
    }

    map_operators(false);

    if (soft_constraints == true) {
        add_observation_soft_constraints(variables, constraints);
    }
    if(enforce_observations == true) {
        enforce_observation_constraints(constraints);
    }

    show_variables_and_objective(variables, true);

    lp_solver.load_problem(lp::LPObjectiveSense::MINIMIZE, variables, constraints);
}

void OCSingleShotHeuristic::map_operators(bool show) {
    if (show == true) {
        cout << std::endl << string(80, '*') << std::endl;
        cout << "# Mapping X -> op: " << std::endl;
    }
    int i = 0;
    for (OperatorProxy op : task_proxy.get_operators()) {
        // Caching operator variable indexes
        std::string op_name (op.get_name());
        for (size_t i = 0; i< op.get_name().size(); ++i) {
            op_name[i] = tolower(op_name.c_str()[i]);
        }

        op_indexes[op_name] = i;
        if (show == true) {
            cout << "["<< op_name<< "]: " << op_indexes[op_name] << std::endl;
        }
        i++;
    }
    if (show == true) {
        cout << string(80, '*') << std::endl << std::endl;
    }
}

void OCSingleShotHeuristic::show_variables_and_objective(const std::vector<lp::LPVariable> &variables, bool show) {
    if (show == true) {
        cout << std::endl << string(80, '*') << std::endl;
        cout << "# Variables(" << variables.size() << "): " << std::endl;
        for (int i = 0; i < (int) variables.size(); ++i) {
            cout << "X[" << i << "] = Variable('X_" << i << "'";
            cout << ", lb=" << variables[i].lower_bound;
            cout << ", ub=" << variables[i].upper_bound;
            cout << ", cost[" << i << "] = " << variables[i].objective_coefficient << std::endl;
        }
        cout << string(80, '*') << std::endl << std::endl;

        cout << std::endl << string(80, '*') << std::endl;
        cout << "# Objective function: " << std::endl;
        cout << "obj = Objective(";
        for (int i = 0; i < (int) variables.size(); ++i) {
            cout << "cost[" << i << "] * X[" << i << "]";
            if (i < (int) variables.size() - 1) {
                cout << " + ";
            }
        }
        cout << ", direction='min')" << std::endl;
        cout << string(80, '*') << std::endl << std::endl;
    }
}

void OCSingleShotHeuristic::add_observation_soft_constraints(std::vector<lp::LPVariable> &variables, std::vector<lp::LPConstraint> &constraints)
{
	double infinity = lp_solver.get_infinity();
	double count_op_observations;
	std::fstream outfile("altput.txt", std::ios::out|std::ios::app) ;
	std::ostream& outstream = outfile;
	outstream << std::endl << string(80, '*') << std::endl;
	outstream << "Adding soft constraints" << std::endl;
	// Keeps track of obs already with constraints
	std::unordered_set<std::string> constrained;
  for(vector<string>::iterator it = observations.begin() ; it != observations.end(); ++it) {

		//if(true)
		if (constrained.find(*it) == constrained.end())
		{
			constrained.insert(*it);
			// This observed operator is new; count occurrences and add soft constraint
			count_op_observations = std::count(observations.begin(), observations.end(), (*it));
			outstream << "New soft constraint on (" << (*it) << "), index " << std::to_string(op_indexes[*it]) << std::endl;
			// Creates new soft_a variable and new constraint: infinity >= (count_a - soft_a) >= 0
            variables.push_back(lp::LPVariable(0.0, count_op_observations, -10001)); // assumes unit cost
			lp::LPConstraint constraint1(0.0, infinity);
			constraint1.insert(op_indexes[*it], 1.0);
			constraint1.insert(variables.size() - 1, -1.0);
			constraints.push_back(constraint1);

			report_constraint(outfile, constraint1, variables, *it);
		}
		else {
			outstream << "Op " << *it << " was added previously." << std::endl;
			continue;
		}
	}
	outstream << std::endl << string(80, '*') << std::endl;
}

void OCSingleShotHeuristic::add_supersoft_noisy(std::vector<lp::LPVariable> &variables, std::vector<lp::LPConstraint> &constraints) {
	double infinity = lp_solver.get_infinity();
	double count_op_observations;
	std::unordered_set<std::string> constrained;
	std::fstream outfile("alteput.txt", std::ios::out|std::ios::app) ;

	std::ostream& outstream = outfile;//std::cout;
	outstream << std::endl << string(80, '*') << std::endl;
  outstream << "Adding noise-cancelling soft constraints" << std::endl;
	// Sanity check constraint for noisy domains:
	// sum soft_op >= num_observations - 2
	lp::LPConstraint constraint_soft_sum(observations.size() - 2,  infinity);

  for(vector<string>::iterator it = observations.begin() ; it != observations.end(); ++it) {
		outstream << "This is op " << *it << std::endl;

		if(constrained.find(*it) == constrained.end()) {
			constrained.insert(*it);
			outstream << "Super soft constraint on (" << (*it) << "), index "<< std::to_string(op_indexes[*it]) << std::endl;
			count_op_observations = std::count(observations.begin(), observations.end(), (*it));

			variables.push_back(lp::LPVariable(0.0, count_op_observations, -1.0)); // assumes unit cost
			lp::LPConstraint constraint1(0.0, infinity);
			constraint1.insert(op_indexes[*it], 1.0);
			constraint1.insert(variables.size() - 1, -1.0);
			constraints.push_back(constraint1);
			report_constraint(outstream, constraint1, variables, *it);

			constraint_soft_sum.insert(variables.size()-1, +1.0);
		}
		else {
			outstream << "Op " << *it << " was added previously." << std::endl;
			continue;
		}
	}
	constraints.push_back(constraint_soft_sum);
	outstream << std::endl << string(80, '*') << std::endl;
}

void OCSingleShotHeuristic::add_observation_overlap_constraints(std::vector<lp::LPVariable> &variables, std::vector<lp::LPConstraint> &constraints) {
    double infinity = lp_solver.get_infinity();
		std::ostream& outstream = std::cout;
    outstream << std::endl << string(80, '*') << std::endl;
    outstream << "Adding overlap constraints" << std::endl;

		std::unordered_set<std::string> constrained;
    for(vector<string>::iterator it = observations.begin() ; it != observations.end(); ++it) {

			if(constrained.find(*it) == constrained.end()) {
				constrained.insert(*it);
				outstream << "Adding overlap constraint on (" << (*it) << "), index " << std::to_string(op_indexes[*it]) << std::endl;

				variables.push_back(lp::LPVariable(-infinity, infinity, -1.0));
        lp::LPConstraint constraint(0.0, 0.0);
        constraint.insert(op_indexes[*it], 1.0);
        constraint.insert(variables.size() - 1, -1.0);
				constraints.push_back(constraint);

				report_constraint(outstream, constraint, variables, *it);
			}
			else continue;
    }
    outstream << std::endl << string(80, '*') << std::endl;
}

void OCSingleShotHeuristic::enforce_observation_constraints(std::vector<lp::LPConstraint> &constraints) {
	double infinity = lp_solver.get_infinity();
	double count_op_observations;
	std::ostream& outstream = std::cout;
	outstream << std::endl << string(80, '*') << std::endl;
  outstream << "Enforcing observation constraints" << std::endl;

	std::unordered_set<std::string> constrained;
  for(vector<string>::iterator it = observations.begin() ; it != observations.end(); ++it) {
		if(constrained.find(*it) == constrained.end()) {
			constrained.insert(*it);
			outstream << "Adding hard constraint on (" << (*it) << "), index " << std::to_string(op_indexes[*it]) << std::endl;

			count_op_observations = std::count(observations.begin(), observations.end(), (*it));
			outstream << "operator observed " << count_op_observations << " time(s)." << std::endl;
			outstream << "constraint " << (*it) << ": " << std::to_string(op_indexes[*it]) << std::endl;
			lp::LPConstraint constraint(count_op_observations, infinity);
			constraint.insert(op_indexes[*it], 1);
			constraints.push_back(constraint);

		}
		else continue;
  }
    outstream << std::endl << string(80, '*') << std::endl;
}

void OCSingleShotHeuristic::report_constraint(ostream& stream,lp::LPConstraint constraint,
std::vector<lp::LPVariable> &variables, std::string op) {
	// Prints information regarding a single, just-added constraint to given output stream (default cout).
	stream << std::endl << string(40, '-') << std::endl;
	stream << "X[" << op_indexes[op] << "] = Variable('X_" << op_indexes[op]  << "'";
	stream << ", lb=" << variables[op_indexes[op]].lower_bound;
	stream << ", ub=" << variables[op_indexes[op]].upper_bound;
	stream << ", cost[" << op_indexes[op] << "] = " << variables[op_indexes[op]].objective_coefficient << std::endl;
	stream << "X[" << variables.size() - 1 << "] = Variable('X_" << variables.size() - 1  << "'";
	stream << ", lb=" << variables[variables.size() - 1].lower_bound;
	stream << ", ub=" << variables[variables.size() - 1].upper_bound;
	stream << ", cost[" << variables.size() - 1 << "] = " << variables[variables.size() - 1].objective_coefficient << std::endl;

	stream << "constraint variables: " << constraint.get_variables()[0];
	stream << ", " << constraint.get_variables()[1] << " - ";
	stream << "constraint coefficients: " << constraint.get_coefficients()[0];
	stream << ", " << constraint.get_coefficients()[1] << std::endl << std::endl;
	stream << std::endl << string(40, '-') << std::endl;
}

void OCSingleShotHeuristic::load_observations() {
    // Read observations from file
    cout << std::endl << string(80, '*') << std::endl;
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
                cout << "Observation: " << obs_name << std::endl;
                observations.push_back(obs_name);
            }
        }
    }
    cout << std::endl << string(80, '*') << std::endl;

    obs_file.close();
}

void OCSingleShotHeuristic::output_results(int result) {
    cout << std::endl << string(80, '*') << std::endl;
    vector<double> solution = lp_solver.extract_solution();
    for (int i = 0; i < (int) solution.size(); ++i) {
        cout << "X[" << i << "] = " << solution[i] << std::endl;
    }
    std::cout << "# observations in solution (" << observations.size() << "): " << std::endl;
    double sat_observations = 0.0;
    for(vector<string>::iterator it = observations.begin() ; it != observations.end(); ++it) {
        cout << (*it) << ": " << solution[op_indexes[*it]] << std::endl;
        sat_observations += solution[op_indexes[*it]];
    }
    cout << "# sat observations: " << sat_observations << std::endl;
    cout << "# h-value: " << result << std::endl;
    cout << string(80, '*') << std::endl;

    cout << std::endl << string(80, '*') << std::endl;

    cout << "Writing results" << std::endl;
    ofstream results;
    //cout << "Writing results" << std::endl;
    results.open("ocsingleshot_heuristic_result.dat");
    results << "-- ";
    results << std::endl << result << std::endl;
    // Printing counts
    int var_i=0;
    vector<double> counts = lp_solver.extract_solution();
    for (OperatorProxy op : task_proxy.get_operators()) {
        // cout << "(" << op.get_name() << ") = " << counts[var_i] << std::endl;
        if (counts[var_i] > 0 ) {
            results << "(" << op.get_name() << ") = " << counts[var_i] << std::endl;
        }
        var_i++;
    }

    results.flush();
    results.close();
}

OCSingleShotHeuristic::~OCSingleShotHeuristic() {
}

int OCSingleShotHeuristic::compute_heuristic(const GlobalState &global_state) {
    State state = convert_global_state(global_state);
    return compute_heuristic(state);
}

int OCSingleShotHeuristic::compute_heuristic(const State &state) {
    assert(!lp_solver.has_temporary_constraints());
    for (const auto &generator : constraint_generators) {
          bool dead_end = generator->update_constraints(state, lp_solver);
        if (dead_end) {
            lp_solver.clear_temporary_constraints();
            return DEAD_END;
        }
    }

    int result;
    lp_solver.solve();
    if (lp_solver.has_optimal_solution()) {
        double epsilon = 0.01;
        double objective_value = lp_solver.get_objective_value();
        result = ceil(objective_value - epsilon);

    } else {
        result = DEAD_END;
    }

    lp_solver.print_statistics();

    ///////////////////////////////////////////////////////////////////
    output_results(result);

	//// Returning failure for deadend states makes the rest of the recognizer hang
    // if(result == DEAD_END)
//         exit(EXIT_FAILURE);
//     else
//         exit(EXIT_SUCCESS);
	exit(EXIT_SUCCESS);
    ///////////////////////////////////////////////////////////////////

    lp_solver.clear_temporary_constraints();
    return result;
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
    parser.add_option<bool>("enforce_observations", "whether or not to enforce constraints on observations");
    parser.add_option<bool>("soft_constraints", "whether or not to use observations as soft constraints");
    //parser.add_option<bool>("new_soft", "whether or not to use observations as soft constraints");

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
