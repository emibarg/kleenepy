from graphviz import Digraph

# ==== ESTADOS Y ESTRUCTURA NFA ====

class State:
    _id = 0
    def __init__(self):
        self.name = f"q{State._id}"
        State._id += 1

class NFA:
    def __init__(self, start, end, transitions):
        self.start = start
        self.end = end
        self.transitions = transitions  # List of (from, symbol, to)

    def __str__(self):
        lines = []
        for f, sym, t in self.transitions:
            lines.append(f"{f.name} (salto {sym}) -> {t.name}")
        lines.append(f"{self.end.name} estado final")
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
            end = State()
            trans = [(start, symbol, end)]
            stack.append(NFA(start, end, trans))
        elif symbol == '+':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            start = State()
            end = State()
            transitions = [
                (start, 'lambda1', nfa1.start),
                (start, 'lambda2', nfa2.start),
                *nfa1.transitions,
                *nfa2.transitions,
                (nfa1.end, 'lambda', end),
                (nfa2.end, 'lambda', end)
            ]
            stack.append(NFA(start, end, transitions))
        elif symbol == '.':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            transitions = [
                *nfa1.transitions,
                (nfa1.end, 'lambda', nfa2.start),
                *nfa2.transitions
            ]
            stack.append(NFA(nfa1.start, nfa2.end, transitions))
        elif symbol == '*':
            nfa = stack.pop()
            start = State()
            end = State()
            transitions = [
                (start, 'lambda1', nfa.start),
                (start, 'lambda2', end),
                *nfa.transitions,
                (nfa.end, 'lambda1', nfa.start),
                (nfa.end, 'lambda2', end)
            ]
            stack.append(NFA(start, end, transitions))
        else:
            raise ValueError(f"Símbolo no reconocido: {symbol}")

    return stack[0]

# ==== DIBUJAR NFA ====

def draw_nfa(nfa, filename="nfa"):
    dot = Digraph(format='png')
    dot.attr(rankdir='LR')

    dot.node("start", shape="point")  # Nodo invisible de entrada
    dot.edge("start", nfa.start.name, label="")  # Flecha a estado inicial

    dot.node(nfa.start.name, shape='circle')
    dot.node(nfa.end.name, shape='doublecircle')

    for frm, sym, to in nfa.transitions:
        dot.node(frm.name, shape='circle')
        dot.node(to.name, shape='doublecircle' if to == nfa.end else 'circle')
        label = 'λ' if sym.startswith('lambda') else sym
        dot.edge(frm.name, to.name, label=label)

    dot.render(filename, view=True)

# ==== MAIN ====

if __name__ == "__main__":
    import sys
    print("Ingrese una expresión regular (ej: (ab+ba)*):")
    expr = input().strip()
    try:
        postfix = infix_to_postfix(expr)
        print(f"Postfija: {postfix}")
        nfa = kleene_algorithm(postfix)
        print("\nTransiciones del AFND:")
        print(nfa)
        draw_nfa(nfa, "nfa_output")
        print("\nSe generó el archivo 'nfa_output.png'")
    except Exception as e:
        print(f"Error: {e}")
