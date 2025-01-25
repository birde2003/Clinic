import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
import datetime
from database.db_handler import get_db_connection, validate_db_schema
from PIL import Image, ImageTk

class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, _):
        """Display text in tooltip window"""
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(tw, text=self.text, background="#ffffe0", 
                        relief="solid", borderwidth=1, padding=2)
        label.pack()

    def hide_tip(self, _):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

class InvoiceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clinic Invoice System")
        self.root.geometry("1200x800")
        
        # Configure styles and theme
        self.style = Style(theme="litera")
        self.current_theme = "litera"
        self.font_header = ("Segoe UI", 12)
        self.font_body = ("Segoe UI", 10)
        
        # Load icons first
        self.load_icons()
        
        # Create main containers
        self.create_navigation()
        self.create_main_content()
        self.create_status_bar()
        
        # Initialize database connection
        self.db_connection = None
        self.connect_database()

    def create_navigation(self):
        nav_frame = ttk.Frame(self.root)
        nav_frame.pack(side="left", fill="y", padx=5, pady=5)
        
        self.buttons = {
            "Dashboard": ttk.Button(nav_frame, text="Dashboard", command=self.show_dashboard,
                                   style="primary.TButton"),
            "Invoices": ttk.Button(nav_frame, text="Invoices", command=self.show_invoices,
                                  style="primary.TButton"),
            "Reports": ttk.Button(nav_frame, text="Reports", command=self.show_reports,
                                 style="primary.TButton"),
            "Settings": ttk.Button(nav_frame, text="Settings", command=self.show_settings,
                                  style="primary.TButton")
        }
        
        for btn in self.buttons.values():
            btn.pack(pady=5, fill="x", ipady=8)

    def create_main_content(self):
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # Create notebook for different sections
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Create tabs
        self.tabs = {
            "Dashboard": ttk.Frame(self.notebook),
            "Invoices": ttk.Frame(self.notebook),
            "Reports": ttk.Frame(self.notebook),
            "Settings": ttk.Frame(self.notebook)
        }
        
        for name, frame in self.tabs.items():
            self.notebook.add(frame, text=name)
            frame.pack_propagate(False)
        
        # Initialize tab content
        self.create_dashboard_tab()
        self.create_invoices_tab()
        self.create_settings_tab()

    def create_dashboard_tab(self):
        # Dashboard content
        pass

    def create_invoices_tab(self):
        frame = self.tabs["Invoices"]
        
        # Filter controls
        filter_frame = ttk.Frame(frame)
        filter_frame.pack(fill="x", padx=5, pady=5)
        
        # Date range filter
        ttk.Label(filter_frame, text="Date Range:").pack(side="left")
        self.start_date = ttk.Entry(filter_frame, width=10)
        self.start_date.pack(side="left", padx=2)
        ttk.Label(filter_frame, text="to").pack(side="left")
        self.end_date = ttk.Entry(filter_frame, width=10)
        self.end_date.pack(side="left", padx=2)
        
        # Owner dropdown
        ttk.Label(filter_frame, text="Owner:").pack(side="left", padx=(10,2))
        self.owner_filter = ttk.Combobox(filter_frame, width=15)
        self.owner_filter.pack(side="left", padx=2)
        
        # Payment method filter
        ttk.Label(filter_frame, text="Payment Method:").pack(side="left", padx=(10,2))
        self.payment_filter = ttk.Combobox(filter_frame, width=15)
        self.payment_filter.pack(side="left", padx=2)
        
        # Outstanding amount
        ttk.Label(filter_frame, text="Outstanding ≤").pack(side="left", padx=(10,2))
        self.max_outstanding = ttk.Entry(filter_frame, width=8)
        self.max_outstanding.pack(side="left", padx=2)
        
        # Filter button
        ttk.Button(filter_frame, text="Apply Filters", command=self.refresh_invoice_list).pack(side="left", padx=10)
        
        # Treeview for invoice listing
        self.tree = ttk.Treeview(frame, columns=("ID", "Date", "Number", "Owner", "Outstanding"), show="headings")
        self.tree.heading("ID", text="ID", command=lambda: self.sort_column("ID", False))
        self.tree.heading("Date", text="Date", command=lambda: self.sort_column("Date", False))
        self.tree.heading("Number", text="Invoice Number", command=lambda: self.sort_column("Number", False))
        self.tree.heading("Owner", text="Owner", command=lambda: self.sort_column("Owner", False))
        self.tree.heading("Outstanding", text="Outstanding", command=lambda: self.sort_column("Outstanding", False))
        
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Form controls
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        self.btn_new = ttk.Button(control_frame, image=self.icons["add"], command=self.new_invoice)
        self.btn_new.pack(side="left", padx=2)
        
        self.btn_edit = ttk.Button(control_frame, image=self.icons["edit"], command=self.edit_invoice)
        self.btn_edit.pack(side="left", padx=2)
        ToolTip(self.btn_edit, "Edit selected invoice")
        
        self.btn_delete = ttk.Button(control_frame, image=self.icons["delete"], command=self.delete_invoice)
        self.btn_delete.pack(side="left", padx=2)
        ToolTip(self.btn_delete, "Delete selected invoice")
        
        self.btn_print = ttk.Button(control_frame, image=self.icons["print"], command=self.print_invoice)
        self.btn_print.pack(side="left", padx=2)
        ToolTip(self.btn_print, "Print selected invoice")

    def create_settings_tab(self):
        frame = self.tabs["Settings"]
        
        theme_frame = ttk.LabelFrame(frame, text="Appearance Settings")
        theme_frame.pack(fill="x", padx=10, pady=10)
        
        self.theme_var = tk.StringVar(value=self.current_theme)
        theme_options = self.style.theme_names()
        
        ttk.Label(theme_frame, text="Select Theme:").pack(side="left", padx=5)
        self.theme_menu = ttk.Combobox(theme_frame, textvariable=self.theme_var, values=theme_options)
        self.theme_menu.pack(side="left", padx=5)
        self.theme_menu.bind("<<ComboboxSelected>>", self.change_theme)

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken")
        self.status_bar.pack(side="bottom", fill="x")
        self.update_status("Ready")

    def load_icons(self):
        icon_size = (24, 24)
        self.icons = {
            "add": ImageTk.PhotoImage(Image.open("icons/add.png").resize(icon_size)),
            "edit": ImageTk.PhotoImage(Image.open("icons/edit.png").resize(icon_size)),
            "delete": ImageTk.PhotoImage(Image.open("icons/delete.png").resize(icon_size)),
            "print": ImageTk.PhotoImage(Image.open("icons/print.png").resize(icon_size)),
            "save": ImageTk.PhotoImage(Image.open("icons/save.png").resize(icon_size))
        }

    def connect_database(self):
        print("Attempting database connection...")  # Debug output
        try:
            with get_db_connection() as conn:
                print(f"Connection object: {conn}")  # Debug output
                validate_db_schema(conn)
                self.update_status("Connected to database")
                print("Database schema validation successful")  # Debug output
        except Exception as e:
            self.update_status(f"Database error: {str(e)}", error=True)
            print(f"Database connection failed: {str(e)}")  # Debug output

    def update_status(self, message, error=False):
        self.status_var.set(message)
        self.status_bar.config(style="danger.TLabel" if error else "")

    def change_theme(self, event):
        new_theme = self.theme_var.get()
        self.style.theme_use(new_theme)
        self.current_theme = new_theme

    def sort_column(self, column, reverse):
        # Sorting functionality for Treeview
        pass

    # Placeholder methods for tab navigation
    def show_dashboard(self): self.notebook.select(self.tabs["Dashboard"])
    def show_invoices(self): self.notebook.select(self.tabs["Invoices"])
    def show_reports(self): self.notebook.select(self.tabs["Reports"])
    def show_settings(self): self.notebook.select(self.tabs["Settings"])
    def new_invoice(self):
        from tkinter import simpledialog, messagebox
        new_data = simpledialog.askstring("New Invoice", "Enter invoice details (CSV):\nDate,Number,Owner,Amount")
        if new_data and messagebox.askyesno("Confirm Create", "Create new invoice?"):
            try:
                date, number, owner, amount = new_data.split(',')
                with get_db_connection() as conn:
                    conn.execute('INSERT INTO Invoices (date_generated, invoice_number, owner, full_amount_pending) '
                               'VALUES (?, ?, ?, ?)', (date, number, owner, float(amount)))
                    conn.commit()
                self.update_status("Invoice created successfully")
                self.refresh_invoice_list()
            except Exception as e:
                self.update_status(f"Create error: {str(e)}", error=True)

    def edit_invoice(self):
        from tkinter import simpledialog, messagebox
        selected = self.tree.selection()
        if not selected:
            self.update_status("No invoice selected", error=True)
            return
            
        invoice_id = self.tree.item(selected[0])['values'][0]
        
        with get_db_connection() as conn:
            invoice_data = conn.execute('''SELECT date_generated, invoice_number, owner, 
                                         full_amount_pending, payment_collected, 
                                         date_of_payment, payment_method 
                                         FROM Invoices WHERE id=?''', (invoice_id,)).fetchone()
        
        current_values = ','.join([
            invoice_data[0],  # date_generated
            invoice_data[1],  # invoice_number
            invoice_data[2],  # owner
            str(invoice_data[3]),  # full_amount_pending
            str(invoice_data[4] if invoice_data[4] else ""),  # payment_collected
            invoice_data[5] if invoice_data[5] else "",  # date_of_payment
            invoice_data[6] if invoice_data[6] else ""  # payment_method
        ])
        
        new_data = simpledialog.askstring("Edit Invoice", 
            "Edit invoice details (CSV):\nDate,Number,Owner,Amount,Paid,PaymentDate,Method",
            initialvalue=current_values)
            
        if new_data:
            try:
                parts = new_data.split(',')
                if len(parts) != 7:
                    raise ValueError("Invalid number of fields")
                    
                update_query = '''UPDATE Invoices SET
                    date_generated = ?,
                    invoice_number = ?,
                    owner = ?,
                    full_amount_pending = ?,
                    payment_collected = ?,
                    date_of_payment = ?,
                    payment_method = ?
                    WHERE id = ?'''
                    
                params = (
                    parts[0], 
                    parts[1],
                    parts[2],
                    float(parts[3]),
                    float(parts[4]) if parts[4] else None,
                    parts[5] if parts[5] else None,
                    parts[6] if parts[6] else None,
                    invoice_id
                )
                
                with get_db_connection() as conn:
                    conn.execute(update_query, params)
                    conn.commit()
                    
                self.update_status(f"Invoice #{invoice_id} updated")
                self.refresh_invoice_list()
                
            except Exception as e:
                self.update_status(f"Update error: {str(e)}", error=True)

    def delete_invoice(self):
        from tkinter import messagebox
        selected = self.tree.selection()
        if not selected:
            self.update_status("No invoice selected", error=True)
            return
            
        invoice_id = self.tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm Delete", f"Delete invoice #{invoice_id}?"):
            try:
                with get_db_connection() as conn:
                    conn.execute('DELETE FROM Invoices WHERE id=?', (invoice_id,))
                    conn.commit()
                self.update_status(f"Invoice #{invoice_id} deleted")
                self.refresh_invoice_list()
            except Exception as e:
                self.update_status(f"Delete error: {str(e)}", error=True)

    def print_invoice(self):
        # Placeholder for printing logic
        pass

    def refresh_invoice_list(self):
        self.tree.delete(*self.tree.get_children())
        query = '''SELECT id, date_generated, invoice_number, owner, outstanding 
                 FROM Invoices WHERE 1=1'''
        params = []
        
        # Date range filter
        start_date = self.start_date.get()
        end_date = self.end_date.get()
        if start_date and end_date:
            try:
                datetime.datetime.strptime(start_date, '%Y-%m-%d')
                datetime.datetime.strptime(end_date, '%Y-%m-%d')
                query += " AND date_generated BETWEEN ? AND ?"
                params.extend([start_date, end_date])
            except ValueError:
                self.update_status("Invalid date format (use YYYY-MM-DD)", error=True)
                return
                
        # Owner filter
        owner = self.owner_filter.get()
        if owner:
            query += " AND owner = ?"
            params.append(owner)
            
        # Outstanding filter
        max_outstanding = self.max_outstanding.get()
        if max_outstanding:
            try:
                query += " AND outstanding <= ?"
                params.append(float(max_outstanding))
            except ValueError:
                self.update_status("Invalid outstanding amount", error=True)
                return
                
        # Populate owner dropdown
        with get_db_connection() as conn:
            owners = [row[0] for row in conn.execute('SELECT DISTINCT owner FROM Invoices')]
            self.owner_filter['values'] = owners
            
        # Execute query
        with get_db_connection() as conn:
            try:
                for row in conn.execute(query, params):
                    self.tree.insert('', 'end', values=row)
            except Exception as e:
                self.update_status(f"Query error: {str(e)}", error=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()
