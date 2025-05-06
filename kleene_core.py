from graphviz import Digraph

# ==== ESTADOS Y ESTRUCTURA NFA ====

class State:
    def __init__(self, name=None, is_final=False):
        self.name = name if name else ""  # Will be set during renaming phase
        self.is_final = is_final

class NFA:
    def __init__(self, start, finals, transitions):
        self.start = start
        self.finals = finals if isinstance(finals, list) else [finals]  # List of final states
        self.transitions = transitions  # List of (from, symbol, to)

    def __str__(self):
        lines = []
        for f, sym, t in self.transitions:
            lines.append(f"{f.name} (salto {sym}) -> {t.name}")
        
        # Add final states information
        for final_state in self.finals:
            lines.append(f"{final_state.name} estado final")
        
        return "\n".join(lines)

# ==== CONVERSIÓN INFIJA A POSTFIJA ====

def infix_to_postfix(regex):
    precedence = {'*': 3, '.': 2, '+': 1}
    output = []
    stack = []

    def insert_concatenation(r):
        result = []
        for i in range(len(r)):
            result.append(r[i])
            if i + 1 < len(r):
                if (r[i].isalnum() or r[i] == ')' or r[i] == '*') and (r[i+1].isalnum() or r[i+1] == '('):
                    result.append('.')
        return ''.join(result)

    regex = insert_concatenation(regex)

    for char in regex:
        if char.isalnum():
            output.append(char)
        elif char == '(':
            stack.append(char)
        elif char == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        else:
            while stack and stack[-1] != '(' and precedence[char] <= precedence.get(stack[-1], 0):
                output.append(stack.pop())
            stack.append(char)

    while stack:
        output.append(stack.pop())

    return ''.join(output)

# ==== ALGORITMO DE KLEENE ====

def kleene_algorithm(postfix_expr):
    stack = []

    for symbol in postfix_expr:
        if symbol.isalnum():
            start = State()
            end = State(is_final=True)
            trans = [(start, symbol, end)]
            stack.append(NFA(start, end, trans))
        elif symbol == '+':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            start = State()
            finals = []
            
            # Union of final states
            finals.extend(nfa1.finals)
            finals.extend(nfa2.finals)
            
            transitions = [
                (start, 'lambda1', nfa1.start),
                (start, 'lambda2', nfa2.start),
                *nfa1.transitions,
                *nfa2.transitions
            ]
            stack.append(NFA(start, finals, transitions))
        elif symbol == '.':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            
            # In concatenation, only nfa2's final states remain final
            transitions = [
                *nfa1.transitions,
                *nfa2.transitions
            ]
            
            # Add epsilon transitions from each final state of nfa1 to the start of nfa2
            for final_state in nfa1.finals:
                transitions.append((final_state, 'lambda', nfa2.start))
            
            stack.append(NFA(nfa1.start, nfa2.finals, transitions))
        elif symbol == '*':
            nfa = stack.pop()
            start = State()
            final = State(is_final=True)
            
            transitions = [
                (start, 'lambda1', nfa.start),
                (start, 'lambda2', final),
                *nfa.transitions
            ]
            
            # Add epsilon transitions from each final state back to start and to the new final state
            for final_state in nfa.finals:
                transitions.append((final_state, 'lambda1', nfa.start))
                transitions.append((final_state, 'lambda2', final))
            
            stack.append(NFA(start, [final], transitions))
        else:
            raise ValueError(f"Símbolo no reconocido: {symbol}")

    # After NFA construction, we need to rename all states
    return rename_states(stack[0])

def rename_states(nfa):
    """Rename all states in the NFA using breadth-first search to ensure sequential naming."""
    # BFS traversal to collect states in the order of their distance from the start state
    visited = set()
    queue = [nfa.start]
    ordered_states = []
    
    while queue:
        state = queue.pop(0)
        if state in visited:
            continue
            
        visited.add(state)
        ordered_states.append(state)
        
        # Find all transitions from this state
        next_states = []
        for from_state, _, to_state in nfa.transitions:
            if from_state == state and to_state not in visited and to_state not in queue:
                next_states.append(to_state)
        
        # Sort next states to ensure deterministic ordering
        queue.extend(next_states)
    
    # Make sure all states are included (in case some are unreachable from start)
    all_states = set()
    all_states.add(nfa.start)
    for final_state in nfa.finals:
        all_states.add(final_state)
    
    for from_state, _, to_state in nfa.transitions:
        all_states.add(from_state)
        all_states.add(to_state)
    
    for state in all_states:
        if state not in ordered_states:
            ordered_states.append(state)
    
    # Create a mapping from old states to new names
    state_mapping = {}
    for i, state in enumerate(ordered_states):
        state_mapping[state] = f"q{i}"
    
    # Rename all states
    for state in all_states:
        state.name = state_mapping[state]
    
    return nfa

# ==== DIBUJAR NFA ====

def draw_nfa(nfa, filename="nfa_output"):
    dot = Digraph(format='png')
    dot.attr(rankdir='LR')
    dot.node("", shape='none')  # Flecha inicial
    dot.edge("", nfa.start.name)

    # Add all states
    all_states = set()
    all_states.add(nfa.start)
    for final_state in nfa.finals:
        all_states.add(final_state)
    
    for from_state, _, to_state in nfa.transitions:
        all_states.add(from_state)
        all_states.add(to_state)
    
    for state in all_states:
        # Check if the state is final
        is_final = state in nfa.finals
        shape = 'doublecircle' if is_final else 'circle'
        dot.node(state.name, shape=shape)

    # Add all transitions
    for frm, sym, to in nfa.transitions:
        label = 'ε' if sym.startswith('lambda') else sym
        dot.edge(frm.name, to.name, label=label)

    dot.render(filename, view=False)

# ==== API PARA USO EXTERNO ====

def regex_to_nfa(expr: str, output_file: str = "nfa_output") -> tuple[str, str]:
    postfix = infix_to_postfix(expr)
    nfa = kleene_algorithm(postfix)
    draw_nfa(nfa, output_file)
    return postfix, str(nfa)