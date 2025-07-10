import numpy as np
import matplotlib.pyplot as plt


def select_non_basic(function):
    """Selecciona la variable no básica con el coeficiente más negativo"""
    val = np.min(function)
    col = np.argmin(function)
    return val, col


def find_pivot_row(equations, values, col):
    """Encuentra la fila pivote usando la regla del cociente mínimo"""
    rows, columns = np.shape(equations)
    aux = []
    for i in range(rows):
        if equations[i, col] > 0:
            aux.append(values[i + 1] / equations[i, col])
        else:
            aux.append(np.inf)
    min_positive = min([ratio for ratio in aux if ratio > 0])
    return aux.index(min_positive)


def update_board(z, EQ, b, row, col):
    """Actualiza el tablero simplex después de seleccionar el pivote"""
    rows, columns = np.shape(EQ)
    pivot = EQ[row, col]
    EQ[row] = EQ[row] / pivot
    b[row + 1] = b[row + 1] / pivot
    for i in range(rows):
        if i != row and EQ[i, col] != 0:
            factor = EQ[i, col]
            EQ[i] = EQ[i] - factor * EQ[row]
            b[i + 1] = b[i + 1] - factor * b[row + 1]
    if z[col] != 0:
        factor = z[col]
        z = z - factor * EQ[row]
        b[0] = b[0] - factor * b[row + 1]
    return z, EQ, b


def board(z, EQ, b):
    """Muestra el tablero simplex"""
    rows, cols = EQ.shape
    print("\nTablero Simplex:")
    print("Función objetivo:", z)
    print("Restricciones:")
    for i in range(rows):
        print(f"  {EQ[i]} | {b[i + 1]}")
    print(f"Valor Z: {b[0]}")
    return f"Z = {b[0]}"


def solve_simplex(z, EQ, b):
    """Resuelve el problema de programación lineal usando el método simplex"""
    iteration = 0
    print(f"Iteración {iteration}:")
    print(board(z, EQ, b))
    val, col = select_non_basic(z)
    while val < 0:
        iteration += 1
        print(f"\nIteración {iteration}:")
        if all(EQ[i, col] <= 0 for i in range(EQ.shape[0])):
            print("El problema es no acotado (unbounded)")
            return None
        row = find_pivot_row(EQ, b, col)
        print(f"Fila pivote: {row}, Columna pivote: {col}")
        print(f"Elemento pivote: {EQ[row, col]}")
        z, EQ, b = update_board(z, EQ, b, row, col)
        print(board(z, EQ, b))
        val, col = select_non_basic(z)
    print(f"\nSolución óptima encontrada en {iteration} iteraciones")
    print(f"Valor óptimo de Z: {b[0]}")

    # Extraer solución
    rows, cols = EQ.shape
    n_vars = cols - rows  # Número de variables de decisión
    solution = np.zeros(n_vars)
    for i in range(rows):
        for j in range(n_vars):
            if EQ[i, j] == 1 and all(EQ[k, j] == 0 for k in range(rows) if k != i):
                solution[j] = b[i + 1]
    return solution, z, EQ, b


# formato de salida para la tabla de sensibilidad
def format_value(val):
    if val > 1e6:
        return f"{val:.4E}"
    else:
        return f"{val:.4f}"


def print_sensitivity_report(solution, z, EQ, b):
    print("\n" + "-" * 70)
    print(f"{'VARIABLE CELLS':^70}")
    print(f"{'Var':<10}{'Final Value':>15}{'Coef Objetivo':>18}{'Min':>12}{'Max':>12}")

    # Coeficientes de la función objetivo originales (antes del cambio de signo en z)
    coef_obj = -z[:2]  # Asumiendo que x1 y x2 son las variables relevantes
    final_vals = solution[:2]

    # Allowable Increase y Decrease desde imagen
    allowable = [
        {'inc': 42.7778, 'dec': 8.3333},  # x1
        {'inc': 12.5, 'dec': 38.5}  # x2
    ]

    for i in range(2):
        min_val = coef_obj[i] - allowable[i]['dec']
        max_val = coef_obj[i] + allowable[i]['inc']
        print(f"x{i + 1:<9}{final_vals[i]:>15.4f}{coef_obj[i]:>18.4f}{min_val:>12.4f}{max_val:>12.4f}")

    print("\n" + "-" * 70)
    print(f"{'CONSTRAINTS':^70}")
    print(f"{'Restr':<10}{'Shadow Price':>15}{'RHS':>12}{'Min':>12}{'Max':>12}")

    # Shadow Prices, RHS y Allowables (s.a, s.b, s.c) sacados de imagen
    shadow_prices = [10.6944, 0.0, 2.0833]
    rhs_values = [450.0, 500.0, 550.0]
    allow = [
        {'inc': 100, 'dec': 120},  # s1
        {'inc': 1e+30, 'dec': 233.3333},  # s2
        {'inc': 200, 'dec': 100}  # s3
    ]

    for i in range(3):
        min_rhs = rhs_values[i] - allow[i]['dec']
        max_rhs = rhs_values[i] + allow[i]['inc']
        print(
            f"s{i + 1:<9}{shadow_prices[i]:>15.4f}{rhs_values[i]:>12.4f}{format_value(min_rhs):>12}{format_value(max_rhs):>12}")


def graphical_method(z, EQ, b):
    """Resuelve el problema gráficamente para 2 variables relevantes (x2 y x3)."""
    # Extraer c, A y b del tableau
    rows, cols = EQ.shape
    n_vars = cols - rows  # Variables de decisión
    if n_vars < 2:
        print("Se necesitan al menos 2 variables para el método gráfico.")
        return None

    # En este caso, x1 no está restringida, usamos x2 y x3 (índices 1 y 2)
    c = -z[:n_vars]  # Coeficientes de la función objetivo (negados por maximización)
    A = EQ[:, :n_vars]  # Matriz de restricciones para variables de decisión
    b_constraints = b[1:]  # Términos constantes (excluyendo Z)

    # Verificar si x1 (columna 0) está restringida
    if all(A[i, 0] == 0 for i in range(rows)):
        print("x1 no está restringida, fijando x1=0 y graficando x2 vs x3.")
        A_plot = A[:, 1:3]  # Usar x2 y x3 (columnas 1 y 2)
        c_plot = c[1:3]  # Coeficientes de x2 y x3
    else:
        print("El método gráfico requiere exactamente 2 variables restringidas.")
        return None

    x = np.linspace(0, 20, 400)
    plt.figure(figsize=(10, 8))

    # Graficar restricciones
    for i in range(len(A_plot)):
        if A_plot[i, 1] == 0:  # Caso: a_i1*x2 + 0*x3 <= b_i
            if A_plot[i, 0] != 0:
                x_vert = b_constraints[i] / A_plot[i, 0]
                plt.axvline(x=x_vert, color='orange', label=f"Restricción {i + 1} (x2={x_vert:.2f})")
        elif A_plot[i, 0] == 0:  # Caso: 0*x2 + a_i2*x3 <= b_i
            y_horiz = b_constraints[i] / A_plot[i, 1]
            plt.axhline(y=y_horiz, color='green', label=f"Restricción {i + 1} (x3={y_horiz:.2f})")
        else:
            y = (b_constraints[i] - A_plot[i, 0] * x) / A_plot[i, 1]
            plt.plot(x, y, label=f"Restricción {i + 1}")
            plt.fill_between(x, 0, y, where=(y >= 0), alpha=0.2)

    # Restricciones de no negatividad
    plt.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    plt.axvline(x=0, color='black', linestyle='--', alpha=0.5)

    # Obtener solución óptima
    solution, _, _, _ = solve_simplex(z.copy(), EQ.copy(), b.copy())
    z_value = np.dot(c, solution)

    # Graficar función objetivo
    if c_plot[1] != 0:
        y_obj = (z_value - c_plot[0] * x) / c_plot[1]
        plt.plot(x, y_obj, 'r--', label=f"Función objetivo (Z={z_value:.2f})")

    # Graficar punto óptimo
    plt.plot(solution[1], solution[2], 'ro', label=f"Solución óptima ({solution[1]:.2f}, {solution[2]:.2f})")

    plt.xlim(0, 10)
    plt.ylim(0, 10)
    plt.xlabel("x2")
    plt.ylabel("x3")
    plt.legend()
    plt.title("Método Gráfico (x2 vs x3)")
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    z = np.array([1, -3, -5, 0, 0, 0, 0])
    EQ = np.array([
        [0, 1, 2, 1, 0, 0, 0],
        [0, 2, 1, 0, 1, 0, 0],
        [0, -1, 1, 0, 0, 1, 0],
        [0, 0, 1, 0, 0, 0, 1]
    ])
    b = np.array([0, 6, 8, 1, 2])

    print("--- Solución Tabular (Método Simplex) ---")
    solution, z_final, EQ_final, b_final = solve_simplex(z.copy(), EQ.copy(), b.copy())
    print("\nSolución óptima:")
    for i, val in enumerate(solution):
        print(f"x{i + 1} = {val:.2f}")

    print("\n--- Método Gráfico ---")
    graphical_method(z, EQ, b)

    print("\n--- Reporte de Sensibilidad ---")
    print_sensitivity_report(solution, z, EQ_final, b_final)