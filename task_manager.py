import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry
from plyer import notification
import datetime

class TaskManagerGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestionnaire de tâches")

        self.conn = sqlite3.connect('tasks.db')
        self.cursor = self.conn.cursor()

        self.create_table()
        self.create_widgets()
        self.view_tasks()
        self.check_reminders()

        # Lancer la vérification des rappels toutes les minutes
        self.root.after(10000, self.check_reminders)  # 10000 ms = 10 seconde

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                category TEXT,
                description TEXT,
                due_date TEXT,
                priority TEXT,
                completed INTEGER DEFAULT 0,
                reminder_date TEXT,
                reminder_time TEXT
            )
        ''')
        self.conn.commit()

    def create_widgets(self):
        # Frame pour l'entrée des tâches
        entry_frame = tk.Frame(self.root, padx=10, pady=10)
        entry_frame.pack(fill=tk.X)

        self.label_name = tk.Label(entry_frame, text="Nom de la tâche:")
        self.label_name.grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_name = tk.Entry(entry_frame)
        self.entry_name.grid(row=0, column=1, pady=5)

        self.label_category = tk.Label(entry_frame, text="Catégorie:")
        self.label_category.grid(row=1, column=0, sticky=tk.W, pady=5)
        self.entry_category = tk.Entry(entry_frame)
        self.entry_category.grid(row=1, column=1, pady=5)

        self.label_description = tk.Label(entry_frame, text="Description:")
        self.label_description.grid(row=2, column=0, sticky=tk.W, pady=5)
        self.entry_description = tk.Entry(entry_frame)
        self.entry_description.grid(row=2, column=1, pady=5)

        self.label_due_date = tk.Label(entry_frame, text="Date d'échéance:")
        self.label_due_date.grid(row=3, column=0, sticky=tk.W, pady=5)
        self.entry_due_date = DateEntry(entry_frame, date_pattern='y-mm-dd')
        self.entry_due_date.grid(row=3, column=1, pady=5)

        self.label_priority = tk.Label(entry_frame, text="Priorité:")
        self.label_priority.grid(row=4, column=0, sticky=tk.W, pady=5)
        self.priority_var = tk.StringVar()
        self.priority_var.set("Moyenne")  # Définir la priorité par défaut
        self.priority_menu = tk.OptionMenu(entry_frame, self.priority_var, "Haute", "Moyenne", "Basse")
        self.priority_menu.grid(row=4, column=1, pady=5)

        self.label_reminder_date = tk.Label(entry_frame, text="Date de rappel:")
        self.label_reminder_date.grid(row=5, column=0, sticky=tk.W, pady=5)
        self.entry_reminder_date = DateEntry(entry_frame, date_pattern='y-mm-dd')
        self.entry_reminder_date.grid(row=5, column=1, pady=5)

        self.label_reminder_time = tk.Label(entry_frame, text="Heure de rappel:")
        self.label_reminder_time.grid(row=6, column=0, sticky=tk.W, pady=5)
        self.entry_reminder_time = tk.Entry(entry_frame)
        self.entry_reminder_time.insert(0, "HH:MM")  # Format d'heure par défaut
        self.entry_reminder_time.grid(row=6, column=1, pady=5)

        self.add_button = tk.Button(entry_frame, text="Ajouter la tâche", command=self.add_task, bg="#4CAF50", fg="white")
        self.add_button.grid(row=7, column=0, columnspan=2, pady=10)

        # Frame pour le tableau des tâches
        table_frame = tk.Frame(self.root, padx=10, pady=10)
        table_frame.pack(fill=tk.BOTH, expand=True)

        # Création du Treeview
        self.task_table = ttk.Treeview(table_frame, columns=("ID", "Nom", "Catégorie", "Description", "Échéance", "Priorité", "Date de rappel", "Heure de rappel", "Complétée"), show="headings")

        # Définir les en-têtes des colonnes
        self.task_table.heading("ID", text="ID")
        self.task_table.heading("Nom", text="Nom")
        self.task_table.heading("Catégorie", text="Catégorie")
        self.task_table.heading("Description", text="Description")
        self.task_table.heading("Échéance", text="Échéance")
        self.task_table.heading("Priorité", text="Priorité")
        self.task_table.heading("Date de rappel", text="Date de rappel")
        self.task_table.heading("Heure de rappel", text="Heure de rappel")
        self.task_table.heading("Complétée", text="Complétée")

        # Définir la largeur des colonnes
        self.task_table.column("ID", width=50)
        self.task_table.column("Nom", width=150)
        self.task_table.column("Catégorie", width=100)
        self.task_table.column("Description", width=200)
        self.task_table.column("Échéance", width=100)
        self.task_table.column("Priorité", width=80)
        self.task_table.column("Date de rappel", width=120)
        self.task_table.column("Heure de rappel", width=80)
        self.task_table.column("Complétée", width=80)

        self.task_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbars pour le Treeview
        self.scrollbar_y = tk.Scrollbar(table_frame, orient="vertical", command=self.task_table.yview)
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.task_table.configure(yscrollcommand=self.scrollbar_y.set)

        self.scrollbar_x = tk.Scrollbar(table_frame, orient="horizontal", command=self.task_table.xview)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.task_table.configure(xscrollcommand=self.scrollbar_x.set)

        # Frame pour les boutons de modification et suppression
        action_frame = tk.Frame(self.root, padx=10, pady=10)
        action_frame.pack(fill=tk.X)

        self.modify_button = tk.Button(action_frame, text="Modifier la tâche", command=self.modify_task, bg="#2196F3", fg="white")
        self.modify_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = tk.Button(action_frame, text="Supprimer la tâche", command=self.delete_task, bg="#f44336", fg="white")
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.complete_button = tk.Button(action_frame, text="Marquer comme complétée", command=self.complete_task, bg="#FFC107", fg="white")
        self.complete_button.pack(side=tk.LEFT, padx=5)

    def add_task(self):
        task_name = self.entry_name.get()
        category = self.entry_category.get()
        description = self.entry_description.get()
        due_date = self.entry_due_date.get_date().strftime('%Y-%m-%d')
        priority = self.priority_var.get()
        reminder_date = self.entry_reminder_date.get_date().strftime('%Y-%m-%d')
        reminder_time = self.entry_reminder_time.get()

        if task_name:
            self.cursor.execute('''
                INSERT INTO tasks (task_name, category, description, due_date, priority, reminder_date, reminder_time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (task_name, category, description, due_date, priority, reminder_date, reminder_time))
            self.conn.commit()
            messagebox.showinfo("Tâche ajoutée", "Tâche ajoutée avec succès.")
            self.view_tasks()
            self.clear_entries()
        else:
            messagebox.showwarning("Erreur", "Le nom de la tâche est obligatoire.")

    def view_tasks(self):
        self.task_table.delete(*self.task_table.get_children())  # Supprimer les lignes existantes
        self.cursor.execute('SELECT * FROM tasks')
        tasks = self.cursor.fetchall()
        for task in tasks:
            reminder_display = f"{task[7]} {task[8]}" if task[7] and task[8] else ""
            completed_status = "Oui" if task[6] == 1 else "Non"
            self.task_table.insert("", tk.END, values=(task[0], task[1], task[2], task[3], task[4], task[5], reminder_display, completed_status))

    def delete_task(self):
        selected_item = self.task_table.selection()
        if selected_item:
            task_id = self.task_table.item(selected_item)['values'][0]
            self.cursor.execute('DELETE FROM tasks WHERE id=?', (task_id,))
            self.conn.commit()
            messagebox.showinfo("Tâche supprimée", "Tâche supprimée avec succès.")
            self.view_tasks()
        else:
            messagebox.showwarning("Erreur", "Veuillez sélectionner une tâche à supprimer.")

    def modify_task(self):
        selected_item = self.task_table.selection()
        if selected_item:
            task_id = self.task_table.item(selected_item)['values'][0]
            task_name = self.entry_name.get()
            category = self.entry_category.get()
            description = self.entry_description.get()
            due_date = self.entry_due_date.get_date().strftime('%Y-%m-%d')
            priority = self.priority_var.get()
            reminder_date = self.entry_reminder_date.get_date().strftime('%Y-%m-%d')
            reminder_time = self.entry_reminder_time.get()

            if task_name:
                self.cursor.execute('''
                    UPDATE tasks
                    SET task_name=?, category=?, description=?, due_date=?, priority=?, reminder_date=?, reminder_time=?
                    WHERE id=?
                ''', (task_name, category, description, due_date, priority, reminder_date, reminder_time, task_id))
                self.conn.commit()
                messagebox.showinfo("Tâche modifiée", "Tâche modifiée avec succès.")
                self.view_tasks()
                self.clear_entries()
            else:
                messagebox.showwarning("Erreur", "Le nom de la tâche est obligatoire.")
        else:
            messagebox.showwarning("Erreur", "Veuillez sélectionner une tâche à modifier.")

    def complete_task(self):
        selected_item = self.task_table.selection()
        if selected_item:
            task_id = self.task_table.item(selected_item)['values'][0]
            self.cursor.execute('UPDATE tasks SET completed=1 WHERE id=?', (task_id,))
            self.conn.commit()
            messagebox.showinfo("Tâche complétée", "Tâche marquée comme complétée.")
            self.view_tasks()
        else:
            messagebox.showwarning("Erreur", "Veuillez sélectionner une tâche à marquer comme complétée.")

    def check_reminders(self):
        today = datetime.date.today().strftime('%Y-%m-%d')
        now = datetime.datetime.now().strftime("%H:%M")
        self.cursor.execute('SELECT * FROM tasks WHERE reminder_date=? AND reminder_time=? AND completed=0', (today, now))
        reminders = self.cursor.fetchall()
        for reminder in reminders:
            notification.notify(
                title='Rappel de tâche',
                message=f"Tâche: {reminder[1]}\nCatégorie: {reminder[2]}\nDescription: {reminder[3]}\nÉchéance: {reminder[4]}",
                timeout=10
            )
            self.show_text_reminder(reminder)  # Afficher la fenêtre textuelle de rappel
        # Planifier la prochaine vérification dans 60 secondes
        self.root.after(10000, self.check_reminders)  # 10000 ms = 10 seconde

    def show_text_reminder(self, task):
        reminder_window = tk.Toplevel(self.root)
        reminder_window.title("Rappel de tâche")

        reminder_label = tk.Label(reminder_window, text=f"Rappel pour la tâche:\n\nNom: {task[1]}\nCatégorie: {task[2]}\nDescription: {task[3]}\nÉchéance: {task[4]}")
        reminder_label.pack(padx=10, pady=10)

        close_button = tk.Button(reminder_window, text="Fermer", command=reminder_window.destroy)
        close_button.pack(pady=5)

    def clear_entries(self):
        self.entry_name.delete(0, tk.END)
        self.entry_category.delete(0, tk.END)
        self.entry_description.delete(0, tk.END)
        self.entry_due_date.set_date(datetime.date.today())
        self.priority_var.set("Moyenne")
        self.entry_reminder_date.set_date(datetime.date.today())
        self.entry_reminder_time.delete(0, tk.END)
        self.entry_reminder_time.insert(0, "HH:MM")

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerGui(root)
    root.mainloop()
