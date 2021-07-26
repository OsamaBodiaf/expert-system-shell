# University project by Osama Bodiaf (@OsamaBodiaf), for the sixth semester AI class.
# Dedicated to "Fishy", a "smort" fish that loves collecting data.

import sys
import os
from tkinter import *
from tkinter import scrolledtext


# An Atom holds a statement and its associated truth value
class Atom:
    # Constructor
    def __init__(self, statement, value):
        self.statement = statement
        self.value = value

    # Getters
    def get_statement(self):
        return self.statement

    def get_value(self):
        return self.value

    # Setters
    def set_statement(self, statement):
        self.statement = statement
        return self

    def set_value(self, value):
        self.value = boolean(value)
        return self

    # Representation
    def __str__(self):
        return "It's " + str(
            self.value).lower() + " that \"" + self.statement + "\""

    def __repr__(self):
        return self.__str__()


# A Rule holds the antecedent and consequent of a rule
class Rule:
    # Constructor
    def __init__(self, antecedent, consequent):
        self.antecedent = antecedent
        self.consequent = consequent

    # Return whether the antecedent is true based on known facts
    def is_applicable(self, facts):
        words = self.antecedent.split()
        expression = ""
        previous_word = None
        for word in words:
            if word in ['and', 'or', 'not', '(', ')']:
                expression += word + " "
            elif word in facts.keys():
                expression += str(facts[word].get_value()) + " "
            elif previous_word == "not":
                expression += "True "
            else:
                expression += "False "
            previous_word = word

        return eval(expression)

    def antecedent_length(self):
        return len(self.antecedent.split())

    # Getters
    def get_antecedent(self):
        return self.antecedent

    def get_consequent(self):
        return self.consequent

    def get_premises(self):
        premises = []
        for word in self.antecedent.split():
            if word in ['and', 'or', 'not', '(', ')']:
                continue
            else:
                premises.append(word)
        return premises

    # Representation
    def __str__(self):
        return "if " + self.get_antecedent() + " then " + self.get_consequent()

    def __repr__(self):
        return self.__str__()


# Helper function to sort rules based on the number of premises
def sort(rules):
    sorted_rules = [None] * len(rules)
    c = 0
    for rule in rules:
        i = 0
        while i < c:
            if (len(rule.get_premises()) > len(sorted_rules[i].get_premises())):
                f = c
                while i < f:
                    sorted_rules[f] = sorted_rules[f-1]
                    f -= 1
                break
            else:
                i += 1
        sorted_rules[i] = rule
        c += 1
    return sorted_rules


# Irrevocable forward chaining, with depth-first search strategy, favoring rules with most premises
def forward_chain(facts, hypotheses, rules, goal=None):
    applicable_rules = []
    inapplicable_rules = []

    # select applicable rules
    for rule in rules:
        if rule.is_applicable(facts):
            applicable_rules.append(rule)
        else:
            inapplicable_rules.append(rule)

    # sort applicable rules based on number of premises
    applicable_rules = sort(applicable_rules)

    # while there are applicable rules
    while len(applicable_rules) > 0:
        # remove first one, and move its consequent to facts dictionary
        key = applicable_rules.pop(0).get_consequent()
        make_fact(key, hypotheses, facts)

        i = 0
        f = len(inapplicable_rules)
        # for each rule in the inapplicable list
        while i < f:
            # if it becomes applicable
            if inapplicable_rules[i].is_applicable(facts):
                # move it to the applicable list, then sort again
                applicable_rules.append(inapplicable_rules.pop(i))
                applicable_rules = sort(applicable_rules)
                # the next rule will fall back to the current position,
                # so don't increment position, just reduce the size
                f -= 1
            else:
                # increment curent position to check for next rule
                i += 1

        # if the goal is reached, stop
        if goal in facts.keys():
            break


# Attemptive backward chaining, with depth-first search strategy, favoring rules selected first
# If the goal is factual, return the truth value associated with its statement, otherwise return None
def backward_chain(facts, hypotheses, rules, goal, trace):
    global waiting

    # if goal is already a fact
    if goal in facts.keys():
        trace.append("'" + goal + "' was found in facts.")
        return facts[goal].get_value()

    # else, select rules with goal in consequent
    selected_rules = []
    for rule in rules:
        if rule.get_consequent() in [goal, "not " + goal]:
            selected_rules.append(rule)

    trace.append("Selected rules that have '" + goal + "' in consequent.")
    # for each selected rule
    for rule in selected_rules:
        # for each of its premises
        for premise in rule.get_premises():
            # if the premise is not a fact, determine its value
            if premise not in facts.keys():
                backward_chain(facts, hypotheses, rules, premise, trace)
        trace.append("Determined whether the rule \"" + str(rule) +
                     "\" is applicable.")

        # after determining the antecedent, if the rule is applicable
        if rule.is_applicable(facts):
            make_fact(goal, hypotheses, facts)
            if "not" in rule.get_consequent():
                facts[goal].set_value(not facts[goal].get_value())
            trace.append("The rule \"" + str(rule) +
                         "\" was applied to determine the value of '" + goal +
                         "'.")
            return facts[goal].get_value()

    trace.append("'" + goal + "' couldn't be determined based on known facts.")
    # if goal is undetermined based on known facts
    # if it is already a hypothesis
    if goal in hypotheses.keys():
        assert_value(goal)
    else:
        add_atom(goal)

    return None


# GUI component to add an Atom for the goal
def add_atom(goal):
    top = Toplevel()
    top.title("Add a fact for '" + goal + "'?")
    lbl_statement = Label(
        top, text="Enter statement for '" + goal + "'", padx=10, pady=10)
    lbl_statement.grid(row=0, column=0, columnspan=2)
    e_statement = Entry(top, borderwidth=5, relief=FLAT, width=80)
    e_statement.grid(row=1, column=0, columnspan=2)
    lbl_value = Label(top, text="Select value for '" + goal + "'\t", padx=5)
    lbl_value.grid(row=2, column=0, sticky='e')
    value = StringVar(top)
    value.set("True")
    opt = OptionMenu(top, value, "True", "False")
    opt.grid(row=2, column=1, padx=10, pady=10, sticky='w')
    frm_buttons = Frame(top)
    frm_buttons.columnconfigure(0, weight=1)
    frm_buttons.columnconfigure(1, weight=1)
    btn_cancel = Button(frm_buttons, text="Cancel",
                        pady=5, command=top.destroy)
    btn_cancel.grid(row=0, column=0, sticky='ew')
    btn_approve = Button(frm_buttons, text="Add Fact", pady=5, command=lambda: approve_atom(
        goal, e_statement.get(), value.get(), top))
    btn_approve.grid(row=0, column=1, sticky='ew')
    frm_buttons.grid(row=3, columnspan=2, sticky='ew')


# Helper function to approve an Atom
def approve_atom(goal, statement, value, window):
    facts[goal] = Atom(goal, True)
    facts[goal].set_statement(statement)
    facts[goal].set_value(value)
    window.destroy()
    store_hypotheses()
    store_facts()
    trace.append("'" + goal + "' was determined based on user input.")
    result = "\"" + statement + "\" is " + value
    show_query_result_frame(result)


# GUI component to assert a value
def assert_value(goal):
    top = Toplevel()
    top.title("Assert truth value for '" + goal + "'?")
    lbl = Label(top, text="Select value for " + goal +
                ": \t\"" + hypotheses[goal].get_statement() + "\" is", padx=5)
    lbl.grid(row=0, column=0, sticky='e')
    value = StringVar(top)
    value.set("True")
    opt = OptionMenu(top, value, "True", "False")
    opt.grid(row=0, column=1, padx=10, pady=10, sticky='w')
    frm_buttons = Frame(top)
    frm_buttons.columnconfigure(0, weight=1)
    frm_buttons.columnconfigure(1, weight=1)
    btn_cancel = Button(frm_buttons, text="Cancel",
                        pady=5, command=top.destroy)
    btn_cancel.grid(row=0, column=0, sticky='ew')
    btn_approve = Button(frm_buttons, text="Assert", pady=5, command=lambda: approve_value(
        goal, value.get(), top))
    btn_approve.grid(row=0, column=1, sticky='ew')
    frm_buttons.grid(row=1, columnspan=2, sticky='ew')


# Helper function to approve a value
def approve_value(goal, value, window):
    hypotheses[goal].set_value(value)
    make_fact(goal, hypotheses, facts)
    window.destroy()
    store_hypotheses()
    store_facts()
    trace.append("'" + goal + "' was determined based on user input.")
    result = "\"" + facts[goal].get_statement() + "\" is " + value
    show_query_result_frame(result)


# Transfer an Atom with provided key from Hypotheses to Facts if it is a Hypothesis,
# otherwise create it on the fly and add it to Facts
def make_fact(key, hypotheses, facts):
    if key in hypotheses:
        facts[key] = hypotheses.pop(key)
    else:
        facts[key] = Atom(key, True)


# Parse files and populate the relevant data structures
def parse_atom(line):
    line_parts = line.split(":", 1)
    if len(line_parts) > 1:
        key = line_parts[0].strip()
        atom_parts = line_parts[1].split(".", 1)
    else:
        atom_parts = line_parts[0].split(".", 1)
        key = atom_parts[0].strip()
    statement = atom_parts[0].strip()
    if len(atom_parts) > 1:
        value = boolean(atom_parts[1].strip())
    else:
        value = True
    return key, statement, value


def populate_hypotheses():
    file = open(os.path.join(sys.path[0], 'hypotheses.txt'), 'r')
    lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line.startswith("#") or line == "":
            continue
        key, statement, value = parse_atom(line)
        hypotheses[key] = Atom(statement, value)
    file.close()


def populate_facts():
    file = open(os.path.join(sys.path[0], 'facts.txt'), 'r')
    lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line.startswith("#") or line == "":
            continue
        key, statement, value = parse_atom(line)
        facts[key] = Atom(statement, value)
    file.close()


def populate_rules():
    file = open(os.path.join(sys.path[0], 'rules.txt'), 'r')
    lines = file.readlines()
    for line in lines:
        line = line.strip()
        if line.startswith("#") or line == "":
            continue
        line_parts = line.split("then", 1)
        antecedent = line_parts[0].split("if", 1)[1].strip()
        consequent = line_parts[1].strip()
        rules.append(Rule(antecedent, consequent))
    file.close()


def populate():
    populate_hypotheses()
    populate_facts()
    populate_rules()


def boolean(expression):
    return str(expression).lower() not in [
        "false", "faux", "f", "no", "non", "n", "0"
    ]


# Store information of the knowlede base in files
def store_hypotheses():
    file = open(os.path.join(sys.path[0], 'hypotheses.txt'), 'w')
    content = ""
    for key in hypotheses:
        statement, value = hypotheses[key].get_statement(
        ), hypotheses[key].get_value()
        content += key + ": " + statement + ". " + str(value) + "\n"
    file.write(content.strip())
    file.close()


def store_facts():
    file = open(os.path.join(sys.path[0], 'facts.txt'), 'w')
    content = ""
    for key in facts:
        statement, value = facts[key].get_statement(), facts[key].get_value()
        content += key + ": " + statement + ". " + str(value) + "\n"
    file.write(content.strip())
    file.close()


# GUI component to open files for editing
def open_(target):
    top = Toplevel()
    top.title(target.title())
    file = open(os.path.join(sys.path[0], target + '.txt'), 'r')
    content = file.read()
    file.close()
    st[target] = scrolledtext.ScrolledText(top, width=80, height=20)
    st[target].insert(END, content)
    st[target].grid(row=0, columnspan=3)
    st[target].focus()
    btn_cancel = Button(top, text="Cancel", width=20,
                        pady=10, command=top.destroy)
    btn_cancel.grid(row=1, column=0, sticky="ew")
    btn_save = Button(top, text="Save", width=20,
                      pady=10, command=lambda: save_(target))
    btn_save.grid(row=1, column=1, sticky="ew")
    btn_save_close = Button(top, text="Save & Close", width=20,
                            pady=10, command=lambda: save_close_(target, top))
    btn_save_close.grid(row=1, column=2, sticky="ew")


# Helper function to save files
def save_(target):
    file = open(os.path.join(sys.path[0], target + '.txt'), 'w')
    content = st[target].get("1.0", END)
    file.write(content)
    file.close()
    initialise()


# Helper function to save and close files
def save_close_(target, window):
    save_(target)
    window.destroy()


# GUI component to show the learn frame
def show_learn_frame():
    frm_query.destroy()
    global frm_learn
    frm_learn.destroy()
    frm_learn = Frame(root, padx=10, pady=10)
    frm_learn_input = Frame(frm_learn, padx=10, pady=10)
    lbl_goal = Label(frm_learn_input, text="Goal's Key:")
    lbl_goal.grid(row=0, column=0, padx=6)
    e_goal = Entry(frm_learn_input, width=10, borderwidth=5, relief=FLAT)
    e_goal.grid(row=0, column=1)
    btn_infer = Button(frm_learn_input, text="Learn", padx=10,
                       command=lambda: learn(e_goal.get()))
    btn_infer.grid(row=0, column=2, padx=10)
    frm_learn_input.pack()
    frm_learn.pack()


# Helper function
def learn(goal=None):
    global frm_learn_result
    frm_learn_result.destroy()
    frm_learn_result = Frame(frm_learn, padx=10, pady=10)
    old_count = len(facts)
    forward_chain(facts, hypotheses, rules, goal)
    store_hypotheses()
    store_facts()
    diff = len(facts) - old_count
    lbl_info = Label(frm_learn_result, text=str(
        diff) + " new facts were learned.")
    lbl_info.grid(row=0, column=0, sticky='ew')
    frm_learn_result.pack()


# GUI component to show the query frame
def show_query_frame():
    frm_learn.destroy()
    global frm_query
    frm_query.destroy()
    frm_query = Frame(root, padx=10, pady=10)
    frm_query_input = Frame(frm_query, padx=10, pady=10)
    lbl_goal = Label(frm_query_input, text="Goal's Key:")
    lbl_goal.grid(row=0, column=0, padx=6)
    e_goal = Entry(frm_query_input, width=10, borderwidth=5, relief=FLAT)
    e_goal.grid(row=0, column=1)
    btn_infer = Button(frm_query_input, text="Query", padx=10,
                       command=lambda: infer(e_goal.get()))
    btn_infer.grid(row=0, column=2, padx=10)
    frm_query_input.pack()
    frm_query.pack()


# GUI component to show the result of a query
def show_query_result_frame(result):
    global frm_query_result
    frm_query_result.destroy()
    frm_query_result = Frame(frm_query, padx=10, pady=10)
    lbl_result = Label(frm_query_result, text=result)
    lbl_result.grid(row=0, column=0, sticky='e')
    btn_trace = Button(frm_query_result, text="Explain", padx=10,
                       command=lambda: show_trace(lbl_trace))
    btn_trace.grid(row=0, column=1, padx=10, sticky='w')
    lbl_trace = Label(frm_query_result)
    frm_query_result.pack()


# Helper function
def infer(goal):
    global trace
    trace = []
    result = str(backward_chain(facts, hypotheses, rules, goal, trace))
    store_hypotheses()
    store_facts()
    if result == "None":
        result = "Undecidable"
    else:
        result = "\"" + facts[goal].get_statement() + "\" is " + result
    show_query_result_frame(result)


# GUI component to show explanations
def show_trace(lbl):
    content = ""
    for action in trace:
        content += action + "\n"
    lbl.configure(text=content.strip())
    lbl.grid(row=1, columnspan=2, pady=(10, 0))


def initialise():
    global hypotheses, facts, rules, trace
    hypotheses = {}
    facts = {}
    rules = []
    trace = []
    populate()


# Main program
if __name__ == "__main__":
    initialise()

    # Scrolled Texts dictionary, for the text editors
    st = {}

    root = Tk()
    root.title(
        "Fishy Expert System Shell")

    frm_btns = Frame(root)
    frm_learn = Frame(root, padx=10, pady=10)
    frm_learn_result = Frame(frm_learn, padx=10, pady=10)
    frm_query = Frame(root, padx=10, pady=10)
    frm_query_result = Frame(frm_query, padx=10, pady=10)

    btn_hypotheses = Button(frm_btns, text="Hypotheses",
                            width=20, pady=10, command=lambda: open_('hypotheses'))
    btn_facts = Button(frm_btns, text="Facts", width=20,
                       pady=10, command=lambda: open_('facts'))
    btn_rules = Button(frm_btns, text="Rules", width=20,
                       pady=10, command=lambda: open_('rules'))

    btn_learn = Button(frm_btns, text="Learn", pady=10,
                       command=show_learn_frame)
    btn_query = Button(frm_btns, text="Query", pady=10,
                       command=show_query_frame)

    btn_hypotheses.grid(row=0, column=0, columnspan=2)
    btn_facts.grid(row=0, column=2, columnspan=2)
    btn_rules.grid(row=0, column=4, columnspan=2)

    btn_learn.grid(row=1, column=0, columnspan=3, sticky="ew")
    btn_query.grid(row=1, column=3, columnspan=3, sticky="ew")

    frm_btns.pack()
    root.mainloop()
