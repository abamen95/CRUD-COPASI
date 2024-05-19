import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as messagebox
import sqlite3

class ProductDB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS estudiantes (
                id INTEGER PRIMARY KEY,
                nombre TEXT,
                apellido TEXT,
                documento_identidad TEXT,
                grado TEXT
            )
        """)
        self.conn.commit()

    def execute_query(self, query, *args):
        try:
            self.cursor.execute(query, args)
            self.conn.commit()
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Error de base de datos", str(e))

    def fetch_all_students(self):
        return self.execute_query("SELECT * FROM estudiantes")


class StudentCRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Pagos y Asistencias")
        self.db = ProductDB("estudiantes.db")
        self.create_widgets()
        self.load_students()

    def create_widgets(self):
        self.create_treeview()
        self.create_input_fields()
        self.create_buttons()
        self.create_scrollbars()

    def create_treeview(self):
        self.tree_frame = ttk.Frame(self.root)
        self.tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(self.tree_frame, columns=("ID", "Nombre", "Apellido", "Documento Identidad", "Grado"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre", text="Nombre del Estudiante")
        self.tree.heading("Apellido", text="Apellido")
        self.tree.heading("Documento Identidad", text="Documento de Identidad")
        self.tree.heading("Grado", text="Grado")
        self.tree.pack(side="left", padx=10, pady=10, fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def create_input_fields(self):
        fields = [("Nombre del Estudiante:", 20), ("Apellido:", 20), ("Documento de Identidad:", 20), ("Grado:", 20)]
        self.entries = {}
        for label_text, width in fields:
            label = ttk.Label(self.root, text=label_text)
            label.pack(pady=(0, 5), padx=10, anchor="w")

            entry = ttk.Entry(self.root, width=width)
            entry.pack(pady=(0, 10), padx=10, fill="x")
            self.entries[label_text] = entry

    def create_buttons(self):
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10)

        buttons = [("Agregar", self.add_student), 
                   ("Eliminar", self.remove_student),
                   ("Actualizar", self.update_student),
                   ("Buscar", self.search_student),
                   ("Mostrar Todo", self.show_all_students)]

        for text, command in buttons:
            button = ttk.Button(btn_frame, text=text, command=command)
            button.grid(row=0, column=buttons.index((text, command)), padx=5)

    def create_scrollbars(self):
        scrollbar_y = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar_y.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_x = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        scrollbar_x.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=scrollbar_x.set)

    def load_students(self):
        self.clear_table()
        for row in self.db.fetch_all_students():
            self.tree.insert("", "end", values=row)

    def add_student(self):
        values = [entry.get() for entry in self.entries.values()]
        if all(values):
            self.db.execute_query("INSERT INTO estudiantes (nombre, apellido, documento_identidad, grado) VALUES (?, ?, ?, ?)", *values)
            messagebox.showinfo("Éxito", "Estudiante agregado con éxito")
            self.load_students()
            self.clear_input_fields()
        else:
            messagebox.showerror("Error", "Por favor, complete todos los campos")

    def remove_student(self):
        selected_item = self.tree.selection()
        if selected_item:
            student_id = self.tree.item(selected_item, "values")[0]
            self.db.execute_query("DELETE FROM estudiantes WHERE id=?", student_id)
            messagebox.showinfo("Éxito", "Estudiante eliminado con éxito")
            self.load_students()
        else:
            messagebox.showerror("Error", "Por favor, seleccione un registro para eliminar")

    def update_student(self):
        selected_item = self.tree.selection()
        if selected_item:
            student_id = self.tree.item(selected_item, "values")[0]
            values = [entry.get() for entry in self.entries.values()]
            self.db.execute_query("UPDATE estudiantes SET nombre=?, apellido=?, documento_identidad=?, grado=? WHERE id=?", *(values + [student_id]))
            messagebox.showinfo("Éxito", "Estudiante actualizado con éxito")
            self.load_students()
            self.clear_input_fields()

    def search_student(self):
        search_term = self.entries["Nombre del Estudiante:"].get()
        if search_term:
            self.clear_table()
            for row in self.db.execute_query("SELECT * FROM estudiantes WHERE nombre LIKE ?", '%' + search_term + '%'):
                self.tree.insert("", "end", values=row)
        else:
            messagebox.showerror("Error", "Por favor, ingrese un término de búsqueda")

    def show_all_students(self):
        self.load_students()

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            if values:
                for entry, value in zip(self.entries.values(), values[1:]):
                    entry.delete(0, tk.END)
                    entry.insert(0, value)

    def clear_input_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentCRUDApp(root)
    root.mainloop()