import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry
from plyer import notification
import datetime
import time

class TaskManagerGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestionnaire de tâches")

        self.conn = sqlite3.connect('tasks.db')
        self.cursor = self.conn.cursor()

        self.create_table()
        self.alter_table()
        self.create_widgets()
        self.view_tasks()
        self.check_reminders()

        # Lancer la vérification des rappels toutes les minutes
        self.root.after(60000, self.check_reminders)  # 60000 ms = 1 minute

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

    def alter_table(self):
        # Pas de modification nécessaire ici si les colonnes sont déjà présentes
        pass

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

        # Frame pour l'affichage des tâches
        task_frame = tk.Frame(self.root, padx=10, pady=10)
        task_frame.pack(fill=tk.BOTH, expand=True)

        self.task_list = tk.Listbox(task_frame, width=80, height=15)
        self.task_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(task_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.task_list.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.task_list.yview)

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
        self.task_list.delete(0, tk.END)
        self.cursor.execute('SELECT * FROM tasks')
        tasks = self.cursor.fetchall()
        if tasks:
            for task in tasks:
                reminder_display = f"Date: {task[7]}, Heure: {task[8]}" if task[7] and task[8] else ""
                task_display = f"ID: {task[0]}, Nom: {task[1]}, Catégorie: {task[2]}, Description: {task[3]}, Échéance: {task[4]}, Priorité: {task[5]} {reminder_display}"
                if task[6] == 1:
                    task_display += " (Complétée)"
                self.task_list.insert(tk.END, task_display)
        else:
            self.task_list.insert(tk.END, "Aucune tâche trouvée.")

    def delete_task(self):
        selected_task = self.task_list.curselection()
        if selected_task:
            task_id = self.task_list.get(selected_task).split(",")[0].split(":")[1].strip()
            self.cursor.execute('DELETE FROM tasks WHERE id=?', (task_id,))
            self.conn.commit()
            messagebox.showinfo("Tâche supprimée", "Tâche supprimée avec succès.")
            self.view_tasks()
        else:
            messagebox.showwarning("Erreur", "Veuillez sélectionner une tâche à supprimer.")

    def modify_task(self):
        selected_task = self.task_list.curselection()
        if selected_task:
            task_id = self.task_list.get(selected_task).split(",")[0].split(":")[1].strip()
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
        selected_task = self.task_list.curselection()
        if selected_task:
            task_id = self.task_list.get(selected_task).split(",")[0].split(":")[1].strip()
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
        # Planifier la prochaine vérification dans 60 secondes
        self.root.after(60000, self.check_reminders)  # 60000 ms = 1 minute

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
