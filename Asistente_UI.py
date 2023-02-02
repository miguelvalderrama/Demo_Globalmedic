import customtkinter
import farmacias
import os
import json
import database
import shutil
import sqlite3
import datetime
from tkinter import ttk, messagebox, filedialog
from PIL import ImageTk, Image

droguerias = [['Biomedic', 'Sajja Medic', 'Tiares', 'Marquez y Koteich'], 
            ['Plus Medical', 'Prueba', 'Gracitana Medicinas', 'Gracitana Material Medico'],
            ['Drolvilla Nacionales', 'Drolvilla Importados','Unipharma','Drosalud']]

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):

    WIDTH = 1080
    HEIGHT = 600
    WIDTH_USER = 240
    HEIGHT_USER = 260

    def __init__(self):
        super().__init__()

        self.title("Visualizador de precios")
        self.geometry(f"{App.WIDTH_USER}x{App.HEIGHT_USER}")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)  # call .on_closing() when app gets closed
        self.usuario = {'Miguel Valderrama', ''}
        self.confirmed_user = False

        screen_width = self.winfo_screenwidth()  # Width of the screen
        screen_height = self.winfo_screenheight() # Height of the screen
        
        # Calculate Starting X and Y coordinates for Window
        x = (screen_width/2) - (App.WIDTH_USER/2)
        y = (screen_height/2) - (App.HEIGHT_USER/2)
        
        self.geometry('%dx%d+%d+%d' % (App.WIDTH_USER, App.HEIGHT_USER, x, y))

        try:
            self.conn = sqlite3.connect('database.db')
            # Create a cursor
            self.cursor = self.conn.cursor()
        except Exception as error:
            messagebox.showerror('Error', error)
            self.destroy()
            exit()
            
        self.main_app()
            
    def main_app(self):

        self.geometry(f"{App.WIDTH}x{App.HEIGHT}")

        with open('config.json', 'r') as json_file:
            self.config_file = json.load(json_file)

        self.ultima_actualizacion = self.config_file['last_update']
        self.tasa_dia = self.config_file['tasa']

        self.style = ttk.Style()
        self.style.configure("Treeview", font=("Roboto", -12))
        self.style.configure("Treeview.Heading", font=("Roboto", -12, "bold"))

        # Full size window
        self.state("zoomed")

        # ============ create two frames ============

        # configure grid layout (2x1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.frame_left = customtkinter.CTkFrame(master=self,
                                                 corner_radius=0,
                                                 width=100)
        self.frame_left.grid(row=0, column=0, sticky="nswe")

        self.frame_right = customtkinter.CTkFrame(master=self)
        self.frame_right.grid(row=0, column=1, sticky="nswe", padx=10, pady=20)

        # ============ frame_left ============

        # configure grid layout (1x11)
        self.frame_left.grid_rowconfigure(0)   # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(5, weight=1)  # empty row as spacing
        self.frame_left.grid_rowconfigure(8, minsize=20)    # empty row with minsize as spacing
        self.frame_left.grid_rowconfigure(11, minsize=10)  # empty row with minsize as spacing

        self.update_ico = ImageTk.PhotoImage(Image.open('./assets/update.png'))
        self.button_1 = customtkinter.CTkButton(master=self.frame_left,
                                                text="",
                                                image=self.update_ico,
                                                command=self.actualizar_archivos,
                                                height=50,
                                                width=60)
        self.button_1.grid(row=2, column=0, pady=10, padx=10)

        self.historico_ico = ImageTk.PhotoImage(Image.open('./assets/historico.png'))
        self.button_3 = customtkinter.CTkButton(master=self.frame_left,
                                                text="",
                                                image=self.historico_ico,
                                                command="",
                                                width=60)
        self.button_3.grid(row=3, column=0, pady=10, padx=10)

        self.label_last_update = customtkinter.CTkLabel(master=self.frame_left,
                                              text="Actualizado:\n" + self.ultima_actualizacion,
                                              text_font=("Roboto Medium", -12),
                                              width=30)  # font name and size in px
        self.label_last_update.grid(row=8, column=0, pady=10)

        self.config_ico = ImageTk.PhotoImage(Image.open('./assets/config.png'))
        self.button_4 = customtkinter.CTkButton(master=self.frame_left,
                                                text="",
                                                command='',
                                                image=self.config_ico,
                                                width=60)
        self.button_4.grid(row=9, column=0, pady=10, padx=10, sticky="w")

        self.button_4.configure(state='disabled')

        # ============ frame_right ============

        # # configure grid layout (1x2)
        self.frame_right.grid_rowconfigure(0, weight=1)
        self.frame_right.grid_columnconfigure((0,1,2,3), weight=1)

        self.frame_info = customtkinter.CTkFrame(master=self.frame_right,
                                                    corner_radius=6)
        self.frame_info.grid(row=0, column=0, columnspan=4, pady=10, padx=10, sticky="nsew")

        # configure grid layout (2x4)
        self.frame_info.grid_rowconfigure(1, weight=1)
        self.frame_info.grid_columnconfigure(0, weight=1)

        # ============ FRAME FOR DESCRIPTION SEARCH ==============
        self.frame_descrip= customtkinter.CTkFrame(master=self.frame_info,
                                                    corner_radius=0)
        self.frame_descrip.grid(row=1, column=0, columnspan=3, sticky="nsew")
        self.frame_descrip.grid_columnconfigure((0,1,2,3), weight=1)
        self.frame_descrip.grid_rowconfigure((0,1,2), weight=1)


        self.ls_trees_descrip = []
        for row_n, grupo in enumerate(droguerias):
            for col_n, drog in enumerate(grupo):
                self.tree_descrip = ttk.Treeview(self.frame_descrip, columns=(drog, 'Precio'), show='headings')
                self.tree_descrip.grid(row=row_n, column=col_n, sticky='nswe', pady=3, padx=2)
                self.tree_descrip.heading(drog, text=drog)
                self.tree_descrip.column(drog, width=300)
                self.tree_descrip.heading('Precio', text='Precio $')
                self.tree_descrip.column('Precio', width=40, anchor='center')
                self.ls_trees_descrip.append((self.tree_descrip, drog))
                # Configure treeview tag colors
                self.tree_descrip.tag_configure('Even', background='lightgray')
                self.tree_descrip.tag_configure('Odd', background='white')
        
        for tree in self.ls_trees_descrip:
            tree[0].bind("<Double-1>", self.make_lambda(tree[0]))
            tree[0].bind("<Return>", self.make_lambda(tree[0]))

        self.search_entry = customtkinter.CTkEntry(master=self.frame_right,
                                                border_width=2,  # <- custom border_width
                                                fg_color=None)  # <- no fg_color
        self.search_entry.grid(row=1, column=0, columnspan=2, rowspan=2,  pady=10, padx=20, sticky="we")

        # set default values
        self.search_entry.bind("<Return>", lambda event: [self.search_and_update_tree(), self.search_entry.delete(0,'end')])
    
    def make_lambda(self, tree):
        return lambda event : self.show_product_full_name(event, tree)
    
    def show_product_full_name(self, event, tree):
        item = tree.selection()[0]
        values = tree.item(item, "values")
        messagebox.showinfo('Producto', f'{values[0]}\n$. {values[1]}\nBs. {round(float(values[1])*float(self.tasa_dia), ndigits=2)}\n{values[2]}')

    '''def config(self):
        self.config_window = customtkinter.CTkToplevel(self)
        self.config_window.title("Configuración")
        self.config_window.geometry("400x200")
        self.config_window.maxsize(400, 200)
        self.config_window.grid_rowconfigure(0, weight=1)
        self.config_window.grid_columnconfigure(0, weight=1)
        self.config_window.update_idletasks()
        x = (self.config_window.winfo_screenwidth() - self.config_window.winfo_reqwidth()) / 2
        y = (self.config_window.winfo_screenheight() - self.config_window.winfo_reqheight()) / 2
        self.config_window.geometry("+%d+%d" % (x, y))

        # Create string variable for each farmacias activas
        self.farmacias_activas_var = []
        for i in range(len(self.farmacias_activas)):
            self.farmacias_activas_var.append(customtkinter.StringVar())
            self.farmacias_activas_var[i].set(self.farmacias_activas[i])


        # Make 3 CTkOptionMenu with the farmacias activas as default
        self.optionmenu_1 = customtkinter.CTkOptionMenu(self.config_window,
                                                        values=self.farmacias_names,
                                                        variable=self.farmacias_activas_var[0],
                                                        width=100)
        self.optionmenu_1.grid(row=0, column=0, columnspan=3, pady=10, padx=20, sticky="we")

        self.optionmenu_2 = customtkinter.CTkOptionMenu(self.config_window, 
                                                        values=self.farmacias_names,
                                                        variable=self.farmacias_activas_var[1],
                                                        width=100)
        self.optionmenu_2.grid(row=1, column=0, columnspan=3, pady=10, padx=20, sticky="we")

        self.optionmenu_3 = customtkinter.CTkOptionMenu(self.config_window,
                                                        values=self.farmacias_names,
                                                        variable=self.farmacias_activas_var[2],
                                                        width=100)
        self.optionmenu_3.grid(row=2, column=0, columnspan=3, pady=10, padx=20, sticky="we")

        self.button_6 = customtkinter.CTkButton(master=self.config_window,
                                                text="Guardar",
                                                command=self.save_config,
                                                width=150)
        self.button_6.grid(row=3, column=0, pady=10, padx=20)

        self.config_window.bind("<Escape>", lambda event: self.config_window.destroy())'''
             
    '''def save_config(self):
        # Get the values of the 3 CTkOptionMenu
        self.farmacias_activas = []
        for i in range(len(self.farmacias_activas_var)):
            self.farmacias_activas.append(self.farmacias_activas_var[i].get())
        
        if len(set(self.farmacias_activas)) != 3:
            messagebox.showerror("Error", "No pueden haber farmacias repetidas")
            return self.config_window.destroy()

        # Update farmacias.json config file
        for farmacia in self.json_config['farmacias']:
            if self.json_config['farmacias'][farmacia]["nombre"] in self.farmacias_activas:
                self.json_config['farmacias'][farmacia]["estado"] = "Activo"
            else:
                self.json_config['farmacias'][farmacia]["estado"] = "Inactivo"
        with open("config.json", "w") as f:
            json.dump(self.json_config, f, indent=4)
        
        self.save_last_update()
        farmacias.prepare_final_csv()
        self.config_window.destroy()'''

    def actualizar_archivos(self):
        #Create a new window
        self.update_window = customtkinter.CTkToplevel(self)
        self.update_window.title("Actualizar archivos")
        self.update_window.geometry("520x360")
        self.update_window.grid_rowconfigure(0, weight=1)
        self.update_window.grid_columnconfigure(0, weight=1)

        # Set window in the center of the screen
        self.update_window.update_idletasks()
        x = (self.update_window.winfo_screenwidth() - self.update_window.winfo_reqwidth()) / 2
        y = (self.update_window.winfo_screenheight() - self.update_window.winfo_reqheight()) / 2
        self.update_window.geometry("+%d+%d" % (x, y))

        # Create a frame
        self.update_frame = customtkinter.CTkFrame(self.update_window)
        self.update_frame.grid(row=0, column=0, columnspan=3, rowspan=3, pady=10, padx=10, sticky="nswe")
        self.update_frame.grid_rowconfigure((0,1,2,3,4,5), weight=1)
        self.update_frame.grid_columnconfigure((0,1), weight=1)

        self.update_label_1 = customtkinter.CTkLabel(self.update_frame, text=self.label_last_update.text)
        self.update_label_1.grid(row=0, column=0, columnspan=2, pady=10, padx=10, sticky="we")

        # Create a label
        self.update_label_2 = customtkinter.CTkLabel(self.update_frame,
                                                        text="Archivos seleccionados:",
                                                        text_font=("Roboto Medium", -16))
        self.update_label_2.grid(row=2, column=0, columnspan=3, pady=10, padx=10, sticky="nwe")

        # Create a listbox
        self.update_listbox = customtkinter.CTkTextbox(self.update_frame,
                                                        width=50,
                                                        height=100)
        self.update_listbox.grid(row=3, column=0, columnspan=3, pady=10, padx=10, sticky="nswe")
        self.files_in_listbox = []
        # Update listbox
        self.update_file_list()

        # Create a checkbox
        self.checkbox_archivos = customtkinter.CTkCheckBox(self.update_frame,
                                                        text='Agregar Archivos',
                                                        onvalue='on',
                                                        offvalue='off')
        self.checkbox_archivos.grid(row=4, column=0, columnspan=2, pady=10, padx=10, sticky="we")

        # Create a button
        self.update_button_2 = customtkinter.CTkButton(self.update_frame,
                                                        text="Actualizar",
                                                        command=self.catch_errors_helper)
        self.update_button_2.grid(row=5, column=0, columnspan=1, pady=10, padx=10, sticky="we")

        # Create a button
        self.update_button_3 = customtkinter.CTkButton(self.update_frame,
                                                        text="Agregar",
                                                        fg_color='#23395d',
                                                        command=self.add_file)
        self.update_button_3.grid(row=5, column=1, columnspan=1, pady=10, padx=10, sticky="we")

        self.update_window.bind("<Escape>", lambda event: self.update_window.destroy())
    
    def catch_errors_helper(self):
        try:
            farmacias.prepare_final_csv(self.checkbox_archivos.get())
            database.update_products_wt_description()
        except Exception as error:
            messagebox.showerror('Error', error)
        else:
            self.save_last_update()
            self.not_found_drogs()
            self.update_window.destroy()
            messagebox.showinfo('ACTUALIZADO', 'Actualizacion exitosa!')

    def add_file(self):
        filenames = filedialog.askopenfilenames()
        for file in filenames:
            filename = file.split('/')[-1]
            shutil.copy(file, f'./Archivos/{filename}')
        self.update_file_list()

    def update_file_list(self):
        # Get the files
        self.update_listbox.configure(state="normal")
        self.files = os.listdir("Archivos")
        self.files = [file for file in self.files if file.endswith(".xlsx") or file.endswith(".xls")]
        # Update the listbox
        for file in self.files:
            if file in self.files_in_listbox:
                continue
              # Add the file name to the listbox
            self.update_listbox.insert("end", "•" + file + "\n")
            self.files_in_listbox.append(file)
        self.update_listbox.configure(state="disabled")
        # Focus on update window
        self.update_window.focus()
    
    def save_last_update(self):
        self.config_file["last_update"] = datetime.datetime.now().strftime("%d/%m/%Y\n%H:%M")
        with open("config.json", "w") as f:
            json.dump(self.config_file, f, indent=4)
        # Update the label
        self.label_last_update.configure(text="Actualizado:\n" + self.config_file["last_update"])

    def not_found_drogs(self):
        # Open a new window
        self.not_found_window = customtkinter.CTkToplevel(self)
        self.not_found_window.title("Droguerias no encontradas")
        self.not_found_window.geometry("420x190")
        self.not_found_window.grid_rowconfigure(0, weight=1)
        self.not_found_window.grid_columnconfigure(0, weight=1)

        # Set window in the center of the screen
        self.not_found_window.update_idletasks()
        x = (self.not_found_window.winfo_screenwidth() - self.not_found_window.winfo_reqwidth()) / 2
        y = (self.not_found_window.winfo_screenheight() - self.not_found_window.winfo_reqheight()) / 2
        self.not_found_window.geometry("+%d+%d" % (x, y))

        # Create a frame
        self.not_found_frame = customtkinter.CTkFrame(self.not_found_window)
        self.not_found_frame.grid(row=0, column=0, columnspan=3, rowspan=3, pady=10, padx=10, sticky="nswe")
        self.not_found_frame.grid_rowconfigure((0,1), weight=1)
        self.not_found_frame.grid_columnconfigure(0, weight=1)

        # Label
        self.not_found_label_1 = customtkinter.CTkLabel(self.not_found_frame,
                                                        text="Droguerias no encontradas:",
                                                        text_font=("Roboto Medium", -16))
        self.not_found_label_1.grid(row=0, column=0, columnspan=3, pady=10, padx=10, sticky="nswe")

        # Create a listbox
        self.not_found_listbox = customtkinter.CTkTextbox(self.not_found_frame,
                                                        width=50,
                                                        height=120)
        self.not_found_listbox.grid(row=1, column=0, columnspan=3, pady=10, padx=10, sticky="nswe")

        self.not_found_window.bind("<Escape>", lambda event: self.not_found_window.destroy())

        # Update listbox
        self.not_found_listbox_update()

    def not_found_listbox_update(self):
        self.list_not_found = []
        # Update the listbox
        for file in os.listdir("Archivos"):
            # Add the file name to the listbox
            self.not_found_listbox.insert("end", "•" + file + "\n")
            self.list_not_found.append(file)
        self.not_found_listbox.configure(state="disabled")
        if self.list_not_found == []:
            self.not_found_window.destroy()

    def search_and_update_tree(self):
        search_text = self.mejora_busqueda(self.search_entry.get(), 'descripcion')
        # Get the search text
        self.conn.rollback()
        for tree, drog in self.ls_trees_descrip:
            tree.delete(*tree.get_children())
            self.cursor.execute(f'''SELECT
                                    *
                                FROM
                                    visualizador_precios_drogueria_descripcion
                                WHERE drogueria = '{drog}'
                                AND descripcion LIKE {search_text}
                                ORDER BY costo''')
            data = self.cursor.fetchall()
            counter = 0
            for row in data:
                if counter % 2 == 0:
                    tag = "Even"
                else:
                    tag = "Odd"
                counter += 1
                tree.insert("", "end", values=row, tags=tag)

    def mejora_busqueda(self, text, nombre):
        query = f"'%{text.split(' ')[0]}%'"
        if text.split(' ')[1:] != []:
            for word in text.split(' ')[1:]:
                query += f" AND {nombre} LIKE '%{word}%'"
        return query
    
    def destroy_all_widgets(self):
        for widget in self.winfo_children():
            widget.destroy()
        
    def on_closing(self, event=0):
        self.conn.close()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()
