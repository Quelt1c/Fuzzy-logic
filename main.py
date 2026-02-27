import numpy as np
import matplotlib.pyplot as plt

# --- ВИХІДНІ ДАНІ ДЛЯ ВАРІАНТА 25 ---
x = np.array([1, 2, 3, 4, 5, 6, 7, 8])
mu_A = np.array([1, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3])
mu_B = np.array([0, 0.3, 0.6, 0.9, 1.0, 0.9, 0.6, 0.3])

# Задаємо альфа-рівень для 3-го завдання (можна змінити на будь-яке інше значення від 0 до 1)
alpha = 0.5 
print(f"Задано альфа-рівень: {alpha}\n")
print(f"Бажаєте змінити альфа-рівень або ж натисність enter, щоб продовжити? (y/n)")
user_input = input().strip().lower()
if user_input == 'y':
    while True:
        try:
            alpha = float(input("Введіть новий альфа-рівень (0 ≤ alpha ≤ 1): "))
            if 0 <= alpha <= 1:
                print(f"Альфа-рівень оновлено: {alpha}\n")
                break
            else:
                print("Помилка: Альфа-рівень повинен бути в діапазоні від 0 до 1. Спробуйте ще раз.")
        except ValueError:
            print("Помилка: Введіть числове значення для альфа-рівня. Спробуйте ще раз.")


# Допоміжна функція для аналітичного представлення
def print_analytic(name, x_vals, mu_vals):
    representation = " + ".join([f"{mu:.2f}/{val}" for val, mu in zip(x_vals, mu_vals)])
    print(f"{name} = {{ {representation} }}")

print("=== ПУНКТ 1: Аналітичне представлення нечітких множин А і В ===")
print_analytic("A", x, mu_A)
print_analytic("B", x, mu_B)
print("\n")

# --- ПУНКТ 2: Функції приналежності нових множин ---
not_A = 1 - mu_A
not_B = 1 - mu_B
A_diff_B = np.minimum(mu_A, 1 - mu_B)  # A \ B
A_int_B = np.minimum(mu_A, mu_B)       # A ∩ B

print("=== ПУНКТ 2: Аналітичне представлення нових множин ===")
print_analytic("Не А (A')", x, not_A)
print_analytic("Не В (B')", x, not_B)
print_analytic("A \\ B", x, A_diff_B)
print_analytic("A ∩ B", x, A_int_B)
print("\n")

# --- ПУНКТ 3: Характеристики та операції ---
print("=== ПУНКТ 3: Характеристики та операції ===")
# Носій (Support) - елементи, де mu > 0
supp_A = x[mu_A > 0]
supp_B = x[mu_B > 0]
print(f"Носій А: {supp_A.tolist()}")
print(f"Носій В: {supp_B.tolist()}")

# Ядро (Core) - елементи, де mu == 1
core_A = x[mu_A == 1]
core_B = x[mu_B == 1]
print(f"Ядро А: {core_A.tolist()}")
print(f"Ядро В: {core_B.tolist()}")

# Альфа-рівень (Alpha-cut) - елементи, де mu >= alpha
alpha_A = x[mu_A >= alpha]
alpha_B = x[mu_B >= alpha]
print(f"Альфа-рівень (alpha={alpha}) для А: {alpha_A.tolist()}")
print(f"Альфа-рівень (alpha={alpha}) для В: {alpha_B.tolist()}")

# Висота (Height)
print(f"Висота А: {np.max(mu_A)}")
print(f"Висота В: {np.max(mu_B)}")

# Операції
alg_int = mu_A * mu_B
alg_union = mu_A + mu_B - alg_int
sym_diff = np.abs(mu_A - mu_B)
conc_A = mu_A**2
dil_A = np.sqrt(mu_A)
bound_int = np.maximum(0, mu_A + mu_B - 1)
bound_union = np.minimum(1, mu_A + mu_B)

print("\n--- Результати операцій ---")
print_analytic("Алгебраїчний перетин", x, alg_int)
print_analytic("Алгебраїчне об'єднання", x, alg_union)
print_analytic("Симетрична різниця", x, sym_diff)
print_analytic("Концентрування А", x, conc_A)
print_analytic("Розведення А", x, dil_A)
print_analytic("Граничний перетин", x, bound_int)
print_analytic("Граничне об'єднання", x, bound_union)

# --- ГРАФІЧНЕ ПРЕДСТАВЛЕННЯ ---
plt.figure(figsize=(14, 10))

# Графік 1: Множини А та В
plt.subplot(2, 2, 1)
plt.plot(x, mu_A, marker='o', label='A', color='blue')
plt.plot(x, mu_B, marker='o', label='B', color='orange')
plt.title('Пункт 1: Множини А та В')
plt.xlabel('x')
plt.ylabel('Ступінь приналежності \u03BC(x)')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

# Графік 2: Доповнення
plt.subplot(2, 2, 2)
plt.plot(x, not_A, marker='s', label='Не А', color='lightblue')
plt.plot(x, not_B, marker='s', label='Не В', color='navajowhite')
plt.title('Пункт 2: Доповнення множин')
plt.xlabel('x')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

# Графік 3: Різниця та Перетин
plt.subplot(2, 2, 3)
plt.plot(x, A_diff_B, marker='^', label='A \ B', color='green')
plt.plot(x, A_int_B, marker='v', label='A ∩ B', color='red')
plt.title('Пункт 2: Різниця та Перетин')
plt.xlabel('x')
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

plt.tight_layout()
plt.show()