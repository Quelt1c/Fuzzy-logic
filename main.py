import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import numpy as np
import json
import os

def union(R1, R2):
    return np.maximum(R1, R2)

def intersection(R1, R2):
    return np.minimum(R1, R2)

def difference(R1, R2):
    return np.minimum(R1, 1 - R2)

def symmetric_difference(R1, R2):
    return np.maximum(
        np.minimum(R1, 1 - R2),
        np.minimum(1 - R1, R2)
    )

def complement(R):
    return 1 - R

def max_min_composition(R1, R2):
    n = R1.shape[0]
    result = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            result[i, j] = max(min(R1[i, k], R2[k, j]) for k in range(n))
    return result

def max_prod_composition(R1, R2):
    n = R1.shape[0]
    result = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            result[i, j] = max(R1[i, k] * R2[k, j] for k in range(n))
    return result

def check_reflexive(R):
    n = R.shape[0]
    for i in range(n):
        if R[i, i] != 1.0:
            return False, f"R[{i+1},{i+1}] = {R[i,i]:.2f} ≠ 1"
    return True, "Всі діагональні елементи = 1"

def check_irreflexive(R):
    n = R.shape[0]
    for i in range(n):
        if R[i, i] != 0.0:
            return False, f"R[{i+1},{i+1}] = {R[i,i]:.2f} ≠ 0"
    return True, "Всі діагональні елементи = 0"

def check_symmetric(R):
    n = R.shape[0]
    for i in range(n):
        for j in range(n):
            if abs(R[i, j] - R[j, i]) > 1e-9:
                return False, f"R[{i+1},{j+1}]={R[i,j]:.2f} ≠ R[{j+1},{i+1}]={R[j,i]:.2f}"
    return True, "R[i,j] = R[j,i] для всіх i,j"

def check_antisymmetric(R):
    n = R.shape[0]
    for i in range(n):
        for j in range(i+1, n):
            if R[i, j] > 0 and R[j, i] > 0 and i != j:
                return False, f"R[{i+1},{j+1}]={R[i,j]:.2f} > 0 та R[{j+1},{i+1}]={R[j,i]:.2f} > 0"
    return True, "Немає пари (i≠j) де обидва R[i,j]>0 і R[j,i]>0"

def check_asymmetric(R):
    ok, msg = check_antisymmetric(R)
    if not ok:
        return False, msg
    irr_ok, irr_msg = check_irreflexive(R)
    if not irr_ok:
        return False, f"Не іррефлексивне: {irr_msg}"
    return True, "Антисиметричне + Іррефлексивне"

def check_transitive(R):
    n = R.shape[0]
    comp = max_min_composition(R, R)
    for i in range(n):
        for j in range(n):
            if comp[i, j] > R[i, j] + 1e-9:
                return False, f"(R∘R)[{i+1},{j+1}]={comp[i,j]:.2f} > R[{i+1},{j+1}]={R[i,j]:.2f}"
    return True, "R∘R ⊆ R (max-min)"

COLORS = {
    "bg":        "#0F1117",
    "surface":   "#1A1D2E",
    "panel":     "#232640",
    "accent":    "#6C63FF",
    "accent2":   "#00D4AA",
    "accent3":   "#FF6B6B",
    "text":      "#E8E9F0",
    "text_dim":  "#7B7D8E",
    "border":    "#2E3150",
    "green":     "#00D4AA",
    "red":       "#FF6B6B",
    "entry_bg":  "#141627",
}

FONT_TITLE  = ("Segoe UI", 18, "bold")
FONT_H2     = ("Segoe UI", 13, "bold")
FONT_H3     = ("Segoe UI", 11, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_MONO   = ("Consolas", 10)
FONT_CELL   = ("Consolas", 11)

class MatrixWidget(tk.Frame):
    """Editable NxN matrix with colored cells."""
    def __init__(self, parent, size=5, label="", **kwargs):
        super().__init__(parent, bg=COLORS["panel"], **kwargs)
        self.size = size
        self.entries = []

        if label:
            tk.Label(self, text=label, font=FONT_H3,
                     bg=COLORS["panel"], fg=COLORS["accent"]).grid(
                row=0, column=0, columnspan=size, pady=(4, 6))

        for i in range(size):
            row_entries = []
            for j in range(size):
                e = tk.Entry(self, width=5, justify="center",
                             font=FONT_CELL,
                             bg=COLORS["entry_bg"],
                             fg=COLORS["text"],
                             insertbackground=COLORS["accent"],
                             relief="flat",
                             bd=0,
                             highlightthickness=1,
                             highlightcolor=COLORS["accent"],
                             highlightbackground=COLORS["border"])
                e.grid(row=i+1, column=j, padx=2, pady=2, ipady=4)
                e.bind("<FocusIn>",  lambda ev, en=e: en.config(highlightbackground=COLORS["accent"]))
                e.bind("<FocusOut>", lambda ev, en=e: en.config(highlightbackground=COLORS["border"]))
                row_entries.append(e)
            self.entries.append(row_entries)

    def get_matrix(self):
        n = self.size
        M = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                val = self.entries[i][j].get().strip()
                try:
                    v = float(val)
                    if not (0.0 <= v <= 1.0):
                        raise ValueError(f"Значення {v} поза [0,1]")
                    M[i, j] = v
                except ValueError as ex:
                    raise ValueError(f"Помилка в рядку {i+1}, стовпці {j+1}: {ex}")
        return M

    def set_matrix(self, M):
        for i in range(self.size):
            for j in range(self.size):
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].insert(0, f"{M[i,j]:.2f}".rstrip('0').rstrip('.') or '0')

    def clear(self):
        for i in range(self.size):
            for j in range(self.size):
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].insert(0, "0")


def fmt_matrix(M, name=""):
    n = M.shape[0]
    lines = []
    if name:
        lines.append(f"  {name}")
        lines.append("  " + "─" * (7 * n))
    for i in range(n):
        row = "  │ " + "  ".join(f"{M[i,j]:.2f}" for j in range(n)) + " │"
        lines.append(row)
    if name:
        lines.append("  " + "─" * (7 * n))
    return "\n".join(lines)

class FuzzyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Нечіткі Відношення  ·  Лабораторна №2")
        self.configure(bg=COLORS["bg"])
        self.geometry("1100x780")
        self.minsize(900, 600)

        self._build_ui()
        
    def _build_ui(self):
        hdr = tk.Frame(self, bg=COLORS["accent"], height=4)
        hdr.pack(fill="x")

        title_bar = tk.Frame(self, bg=COLORS["surface"])
        title_bar.pack(fill="x")
        tk.Label(title_bar,
                 text="🔮  Нечіткі Відношення",
                 font=FONT_TITLE,
                 bg=COLORS["surface"],
                 fg=COLORS["text"]).pack(side="left", padx=20, pady=12)
        tk.Label(title_bar,
                 text="Лабораторна робота №2",
                 font=FONT_BODY,
                 bg=COLORS["surface"],
                 fg=COLORS["text_dim"]).pack(side="right", padx=20)

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook",
                        background=COLORS["bg"],
                        borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=COLORS["surface"],
                        foreground=COLORS["text_dim"],
                        padding=[16, 8],
                        font=FONT_H3,
                        borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", COLORS["panel"])],
                  foreground=[("selected", COLORS["accent"])])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        
        self.tab_input = tk.Frame(nb, bg=COLORS["bg"])
        nb.add(self.tab_input, text=" ① Введення даних ")

        
        self.tab_ops = tk.Frame(nb, bg=COLORS["bg"])
        nb.add(self.tab_ops, text=" ② Операції ")

        
        self.tab_props = tk.Frame(nb, bg=COLORS["bg"])
        nb.add(self.tab_props, text=" ③ Властивості R1 ")

        self._build_input_tab()
        self._build_ops_tab()
        self._build_props_tab()

    

    def _build_input_tab(self):
        t = self.tab_input

        
        btn_frame = tk.Frame(t, bg=COLORS["bg"])
        btn_frame.pack(pady=14, padx=16, anchor="w")

        self._btn(btn_frame, "📂  Завантажити з файлу", self._load_file, COLORS["accent"]).pack(side="left", padx=6)
        self._btn(btn_frame, "💾  Зберегти у файл",    self._save_file, COLORS["accent2"]).pack(side="left", padx=6)
        self._btn(btn_frame, "📋  Приклад (Варіант 25)", self._load_example, COLORS["panel"]).pack(side="left", padx=6)
        self._btn(btn_frame, "🗑  Очистити",            self._clear_matrices, COLORS["accent3"]).pack(side="left", padx=6)

        
        tk.Label(t,
                 text="Введіть значення від 0 до 1 у клітинки матриць (або завантажте файл .json / .txt)",
                 font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(pady=(0, 10))

        
        sz_frame = tk.Frame(t, bg=COLORS["bg"])
        sz_frame.pack()
        tk.Label(sz_frame, text="Розмір матриці:", font=FONT_BODY,
                 bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left", padx=6)
        self.size_var = tk.IntVar(value=5)
        for s in [3, 4, 5, 6]:
            tk.Radiobutton(sz_frame, text=str(s), variable=self.size_var, value=s,
                           command=self._resize_matrices,
                           bg=COLORS["bg"], fg=COLORS["text"],
                           selectcolor=COLORS["accent"],
                           activebackground=COLORS["bg"],
                           font=FONT_BODY).pack(side="left")

        
        mat_frame = tk.Frame(t, bg=COLORS["bg"])
        mat_frame.pack(pady=16)

        self.r1_widget = MatrixWidget(mat_frame, size=5, label="  Матриця R1")
        self.r1_widget.pack(side="left", padx=30)

        sep = tk.Frame(mat_frame, bg=COLORS["border"], width=2)
        sep.pack(side="left", fill="y", pady=10)

        self.r2_widget = MatrixWidget(mat_frame, size=5, label="  Матриця R2")
        self.r2_widget.pack(side="left", padx=30)

        
        self._btn(t, "✅  Застосувати матриці", self._apply_matrices,
                  COLORS["accent"]).pack(pady=10)

        
        self.status_var = tk.StringVar(value="ℹ️  Введіть або завантажте дані")
        tk.Label(t, textvariable=self.status_var,
                 font=FONT_BODY, bg=COLORS["bg"],
                 fg=COLORS["text_dim"]).pack()

        
        self._load_example()

    

    def _build_ops_tab(self):
        t = self.tab_ops

        top = tk.Frame(t, bg=COLORS["bg"])
        top.pack(fill="x", padx=16, pady=12)

        tk.Label(top, text="Виберіть операцію та натисніть «Обчислити»",
                 font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["text_dim"]).pack(side="left")

        self._btn(top, "▶  Всі операції", self._run_all_ops,
                  COLORS["accent"]).pack(side="right", padx=6)

        
        ops_frame = tk.Frame(t, bg=COLORS["surface"])
        ops_frame.pack(fill="x", padx=16, pady=4)

        ops = [
            ("R1 ∪ R2  (Об'єднання)",       lambda: self._run_op("union")),
            ("R1 ∩ R2  (Перетин)",           lambda: self._run_op("intersection")),
            ("R1 \\ R2  (Різниця)",          lambda: self._run_op("difference")),
            ("R1 △ R2  (Симетрична різниця)", lambda: self._run_op("sym_diff")),
            ("R1 ∘ R2  (Max-Min)",           lambda: self._run_op("maxmin")),
            ("R1 ∘ R2  (Max-Prod)",          lambda: self._run_op("maxprod")),
            ("¬R1  (Доповнення)",             lambda: self._run_op("complement")),
        ]
        for i, (name, cmd) in enumerate(ops):
            self._btn(ops_frame, name, cmd, COLORS["panel"]).grid(
                row=i//4, column=i%4, padx=6, pady=6, sticky="ew")
        for c in range(4):
            ops_frame.columnconfigure(c, weight=1)

        
        res_frame = tk.Frame(t, bg=COLORS["panel"], bd=0)
        res_frame.pack(fill="both", expand=True, padx=16, pady=10)

        tk.Label(res_frame, text="Результати", font=FONT_H3,
                 bg=COLORS["panel"], fg=COLORS["accent"]).pack(anchor="w", padx=10, pady=6)

        self.ops_text = scrolledtext.ScrolledText(
            res_frame, font=FONT_MONO, wrap="none",
            bg=COLORS["entry_bg"], fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            selectbackground=COLORS["accent"],
            relief="flat", bd=0,
            padx=12, pady=8)
        self.ops_text.pack(fill="both", expand=True, padx=6, pady=(0, 8))

        self._btn(t, "🔄  Обчислити всі & показати", self._run_all_ops,
                  COLORS["accent2"]).pack(pady=6)

    

    def _build_props_tab(self):
        t = self.tab_props

        tk.Label(t, text="Аналіз властивостей матриці R1",
                 font=FONT_H2, bg=COLORS["bg"], fg=COLORS["text"]).pack(pady=12)
        tk.Label(t, text="Натисніть «Перевірити» — програма визначить кожну властивість",
                 font=FONT_BODY, bg=COLORS["bg"], fg=COLORS["text_dim"]).pack()

        self._btn(t, "🔍  Перевірити властивості R1",
                  self._check_props, COLORS["accent"]).pack(pady=14)

        cards_frame = tk.Frame(t, bg=COLORS["bg"])
        cards_frame.pack(fill="both", expand=True, padx=24)

        props = [
            ("Рефлексивність",    "R[i,i] = 1 для всіх i"),
            ("Іррефлексивність",  "R[i,i] = 0 для всіх i"),
            ("Симетричність",     "R[i,j] = R[j,i]"),
            ("Антисиметричність", "R[i,j]>0 та R[j,i]>0 ⟹ i=j"),
            ("Асиметричність",    "Антисим. + Іррефлексивна"),
            ("Транзитивність",    "R∘R ⊆ R (max-min)"),
        ]

        self.prop_labels = {}
        self.prop_details = {}

        for idx, (name, formula) in enumerate(props):
            card = tk.Frame(cards_frame, bg=COLORS["panel"],
                            relief="flat", bd=0,
                            highlightthickness=1,
                            highlightbackground=COLORS["border"])
            card.grid(row=idx//2, column=idx%2, padx=8, pady=8, sticky="nsew")
            cards_frame.columnconfigure(0, weight=1)
            cards_frame.columnconfigure(1, weight=1)

            tk.Label(card, text=name, font=FONT_H3,
                     bg=COLORS["panel"], fg=COLORS["text"]).pack(anchor="w", padx=12, pady=(10,2))
            tk.Label(card, text=formula, font=("Consolas", 9),
                     bg=COLORS["panel"], fg=COLORS["text_dim"]).pack(anchor="w", padx=12)

            lbl = tk.Label(card, text="—", font=("Segoe UI", 12, "bold"),
                           bg=COLORS["panel"], fg=COLORS["text_dim"])
            lbl.pack(anchor="w", padx=12, pady=(4,2))
            self.prop_labels[name] = lbl

            det = tk.Label(card, text="", font=("Consolas", 9),
                           bg=COLORS["panel"], fg=COLORS["text_dim"],
                           wraplength=340, justify="left")
            det.pack(anchor="w", padx=12, pady=(0,10))
            self.prop_details[name] = det

    

    def _btn(self, parent, text, cmd, color):
        return tk.Button(parent, text=text, command=cmd,
                         bg=color, fg=COLORS["text"],
                         font=FONT_BODY,
                         relief="flat", bd=0, padx=14, pady=7,
                         cursor="hand2",
                         activebackground=COLORS["accent"],
                         activeforeground=COLORS["text"])

    def _get_matrices(self):
        R1 = self.r1_widget.get_matrix()
        R2 = self.r2_widget.get_matrix()
        return R1, R2

    def _apply_matrices(self):
        try:
            R1, R2 = self._get_matrices()
            if R1.shape != R2.shape:
                messagebox.showerror("Помилка", "Матриці мають різні розміри!")
                return
            self.R1 = R1
            self.R2 = R2
            self.status_var.set(f"✅  Матриці {R1.shape[0]}×{R1.shape[1]} успішно завантажено")
        except ValueError as e:
            messagebox.showerror("Помилка введення", str(e))

    def _load_example(self):
        R1 = np.array([
            [1.0, 0.8, 0.2, 0.5, 0.0],
            [0.8, 1.0, 0.0, 0.3, 0.5],
            [0.2, 0.0, 1.0, 0.1, 0.1],
            [0.0, 0.3, 0.2, 1.0, 0.0],
            [0.0, 0.5, 0.1, 0.4, 1.0],
        ])
        R2 = np.array([
            [1.0, 0.3, 0.2, 0.5, 0.0],
            [0.0, 1.0, 0.0, 0.0, 0.5],
            [0.2, 0.0, 1.0, 0.1, 0.1],
            [0.5, 0.0, 0.2, 1.0, 0.0],
            [0.0, 0.4, 0.1, 0.4, 1.0],
        ])
        self.r1_widget.set_matrix(R1)
        self.r2_widget.set_matrix(R2)
        self.R1, self.R2 = R1, R2
        self.status_var.set("✅  Завантажено Варіант 25")

    def _clear_matrices(self):
        self.r1_widget.clear()
        self.r2_widget.clear()
        self.R1 = self.R2 = None
        self.status_var.set("🗑  Матриці очищено")

    def _resize_matrices(self):
        n = self.size_var.get()
        
        for w in (self.r1_widget, self.r2_widget):
            parent = w.master
            w.destroy()
        mat_frame = self.tab_input.winfo_children()[4]  
        
        messagebox.showinfo("Зміна розміру",
            f"Перезапустіть програму або введіть дані вручну для {n}×{n} матриці.\n"
            "Або скористайтесь файлом .json з полем 'size'.")

    def _load_file(self):
        path = filedialog.askopenfilename(
            title="Відкрити файл матриць",
            filetypes=[("JSON файли", "*.json"),
                       ("Текстові файли", "*.txt"),
                       ("Всі файли", "*.*")])
        if not path:
            return
        try:
            if path.endswith(".json"):
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                R1 = np.array(data["R1"], dtype=float)
                R2 = np.array(data["R2"], dtype=float)
            else:
                
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                blocks = [b.strip() for b in text.strip().split("\n\n") if b.strip()]
                if len(blocks) < 2:
                    raise ValueError("Файл має містити дві матриці, розділені порожнім рядком")
                R1 = np.array([[float(x) for x in row.split()] for row in blocks[0].split("\n")], dtype=float)
                R2 = np.array([[float(x) for x in row.split()] for row in blocks[1].split("\n")], dtype=float)

            if R1.shape != R2.shape:
                raise ValueError("Матриці різних розмірів!")
            n = R1.shape[0]
            if n != self.r1_widget.size:
                messagebox.showwarning("Розмір",
                    f"Матриця {n}×{n}, але поточний інтерфейс — {self.r1_widget.size}×{self.r1_widget.size}.\n"
                    "Дані все одно будуть відображені коректно у розрахунках.")

            self.r1_widget.set_matrix(R1)
            self.r2_widget.set_matrix(R2)
            self.R1, self.R2 = R1, R2
            self.status_var.set(f"✅  Завантажено: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Помилка читання файлу", str(e))

    def _save_file(self):
        try:
            R1, R2 = self._get_matrices()
        except ValueError as e:
            messagebox.showerror("Помилка", str(e))
            return

        path = filedialog.asksaveasfilename(
            title="Зберегти матриці",
            defaultextension=".json",
            filetypes=[("JSON файли", "*.json"),
                       ("Текстові файли", "*.txt")])
        if not path:
            return
        try:
            if path.endswith(".json"):
                data = {"R1": R1.tolist(), "R2": R2.tolist()}
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                with open(path, "w", encoding="utf-8") as f:
                    for i in range(R1.shape[0]):
                        f.write(" ".join(str(R1[i,j]) for j in range(R1.shape[1])) + "\n")
                    f.write("\n")
                    for i in range(R2.shape[0]):
                        f.write(" ".join(str(R2[i,j]) for j in range(R2.shape[1])) + "\n")
            messagebox.showinfo("Збережено", f"Файл збережено:\n{path}")
        except Exception as e:
            messagebox.showerror("Помилка збереження", str(e))

    

    def _ensure_matrices(self):
        if not hasattr(self, "R1") or self.R1 is None:
            try:
                self._apply_matrices()
            except Exception:
                pass
        if not hasattr(self, "R1") or self.R1 is None:
            messagebox.showwarning("Дані", "Спочатку введіть або завантажте матриці!")
            return False
        return True

    def _run_op(self, op):
        if not self._ensure_matrices():
            return
        R1, R2 = self.R1, self.R2
        ops_map = {
            "union":       (union(R1, R2),              "R1 ∪ R2  —  Об'єднання"),
            "intersection":(intersection(R1, R2),       "R1 ∩ R2  —  Перетин"),
            "difference":  (difference(R1, R2),         "R1 \\ R2  —  Різниця"),
            "sym_diff":    (symmetric_difference(R1,R2),"R1 △ R2  —  Симетрична різниця"),
            "maxmin":      (max_min_composition(R1,R2), "R1 ∘ R2  —  Max-Min композиція"),
            "maxprod":     (max_prod_composition(R1,R2),"R1 ∘ R2  —  Max-Prod композиція"),
            "complement":  (complement(R1),             "¬R1  —  Доповнення"),
        }
        result, title = ops_map[op]
        txt = f"\n{'═'*50}\n  {title}\n{'═'*50}\n"
        txt += fmt_matrix(result) + "\n"

        self.ops_text.insert(tk.END, txt)
        self.ops_text.see(tk.END)

    def _run_all_ops(self):
        if not self._ensure_matrices():
            return
        R1, R2 = self.R1, self.R2
        self.ops_text.delete("1.0", tk.END)

        header = f"  Лабораторна №2  —  Нечіткі відношення\n"
        header += f"  R1 та R2: матриці {R1.shape[0]}×{R1.shape[1]}\n"
        header += "═" * 56 + "\n\n"
        self.ops_text.insert(tk.END, header)

        sections = [
            ("R1 — вхідна матриця",              R1),
            ("R2 — вхідна матриця",              R2),
            ("R1 ∪ R2  (Об'єднання)",            union(R1, R2)),
            ("R1 ∩ R2  (Перетин)",               intersection(R1, R2)),
            ("R1 \\ R2  (Різниця)",              difference(R1, R2)),
            ("R1 △ R2  (Симетрична різниця)",     symmetric_difference(R1, R2)),
            ("R1 ∘ R2  (Max-Min композиція)",     max_min_composition(R1, R2)),
            ("R1 ∘ R2  (Max-Prod композиція)",    max_prod_composition(R1, R2)),
            ("¬R1  (Доповнення до R1)",           complement(R1)),
        ]
        for name, mat in sections:
            block = f"  ┌─ {name}\n"
            block += fmt_matrix(mat) + "\n\n"
            self.ops_text.insert(tk.END, block)

        self.ops_text.see("1.0")

    

    def _check_props(self):
        if not self._ensure_matrices():
            return
        R1 = self.R1

        checks = [
            ("Рефлексивність",    check_reflexive(R1)),
            ("Іррефлексивність",  check_irreflexive(R1)),
            ("Симетричність",     check_symmetric(R1)),
            ("Антисиметричність", check_antisymmetric(R1)),
            ("Асиметричність",    check_asymmetric(R1)),
            ("Транзитивність",    check_transitive(R1)),
        ]

        for name, (ok, detail) in checks:
            lbl = self.prop_labels[name]
            det = self.prop_details[name]
            if ok:
                lbl.config(text="✅  ТАК", fg=COLORS["green"])
            else:
                lbl.config(text="❌  НІ",  fg=COLORS["red"])
            det.config(text=detail)






if __name__ == "__main__":
    app = FuzzyApp()
    app.mainloop()