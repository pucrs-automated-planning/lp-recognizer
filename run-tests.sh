#!/usr/bin/env bash
export FD_HOME=/Users/meneguzzi/Documents/workspace-planning/fast-downward

mv new_constraint.txt _new_constraint.txt

${FD_HOME}/fast-downward.py --build=release64 domain.pddl pb4-g1.pddl --search "astar(operatorcounting([lmcut_constraints(), pho_constraints(), state_equation_constraints()]))" "$@" >log1.txt
grep "# Objective value" log1.txt

${FD_HOME}/fast-downward.py --build=release64 domain.pddl pb4-g2.pddl --search "astar(operatorcounting([lmcut_constraints(), pho_constraints(), state_equation_constraints()]))" "$@" >log2.txt
grep "# Objective value" log2.txt

${FD_HOME}/fast-downward.py --build=release64 domain.pddl pb4-g3.pddl --search "astar(operatorcounting([lmcut_constraints(), pho_constraints(), state_equation_constraints()]))" "$@" >log3.txt
grep "# Objective value" log3.txt

${FD_HOME}/fast-downward.py --build=release64 domain.pddl pb4-g4.pddl --search "astar(operatorcounting([lmcut_constraints(), pho_constraints(), state_equation_constraints()]))" "$@" >log4.txt
grep "# Objective value" log4.txt

cp _new_constraint.txt new_constraint.txt

${FD_HOME}/fast-downward.py --build=release64 domain.pddl pb4-g1.pddl --search "astar(operatorcounting([lmcut_constraints(), pho_constraints(), state_equation_constraints()]))" "$@" >log1c.txt
grep "# Objective value" log1c.txt

${FD_HOME}/fast-downward.py --build=release64 domain.pddl pb4-g2.pddl --search "astar(operatorcounting([lmcut_constraints(), pho_constraints(), state_equation_constraints()]))" "$@" >log2c.txt
grep "# Objective value" log2c.txt

${FD_HOME}/fast-downward.py --build=release64 domain.pddl pb4-g3.pddl --search "astar(operatorcounting([lmcut_constraints(), pho_constraints(), state_equation_constraints()]))" "$@" >log3c.txt
grep "# Objective value" log3c.txt

${FD_HOME}/fast-downward.py --build=release64 domain.pddl pb4-g4.pddl --search "astar(operatorcounting([lmcut_constraints(), pho_constraints(), state_equation_constraints()]))" "$@" >log4c.txt
grep "# Objective value" log4c.txt