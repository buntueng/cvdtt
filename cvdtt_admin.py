import mysql.connector
from pathlib import Path
import tkinter as tk
import customtkinter
import yaml
from yaml.loader import SafeLoader
import logging
import sqlite3
from tkinter.ttk import Notebook, Style
from tkinter import ttk,Tk, font
from tkcalendar import DateEntry

app_name = "CVDTT_ADMIN"
login_pass = False
thai_large_font =("TH Niramit AS", 37)
thai_font = ("TH Niramit AS", 23)
eng_font = ("Time New Roman",12)

terminate_app_flag = True
# ============= set path to files ==================================================================================
current_path = Path(__file__).resolve().parents[0]
logging_file_path = Path(current_path, 'template.log')
yml_config_path = Path(current_path, 'config.yml')
yml_query_path = Path(current_path, 'main_query.yml')
# =========================== sub program ==========================================================================
def read_yml(file_path):
    yml_params = None
    if file_path.is_file():
        with open(file_path,'r') as yml_file:
            yml_params = yaml.load(yml_file, Loader=SafeLoader)
    else:
        logging.warning("file path is not here")
    return yml_params

def write_yml(py_obj,file_path):
    with open(file_path, 'w',) as obj_file :
        yaml.dump(py_obj,obj_file,sort_keys=False) 

#===================== setup logging module =========================================================================
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

fileHandler = logging.FileHandler(filename=logging_file_path)
fileHandler.setFormatter(logging_format)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logging_format)
logger.addHandler(consoleHandler)

class tkinterApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        global terminate_app_flag
        
        tk.Tk.__init__(self, *args, **kwargs)
        self.resizable(False, False)
        
        self.title('CVDTT - Administrator')
        self.configure(bg='#ccffcc')
        container = tk.Frame(self)
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        self.frames = {}
        for F in (LoginPage, WorkingPage, ErrorPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky ="nsew")

        self.configuration_params = read_yml(yml_config_path)
        self.all_query_library = read_yml(yml_query_path)
        if self.configuration_params == None or self.all_query_library == None:
            terminate_app_flag = True
            logging.info('please add yml files to current folder')
            self.show_frame(ErrorPage)
        else:
            self.show_frame(LoginPage)
        # =========== event binding ===========
        self.bind('<Return>', self.enter_pressed)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def enter_pressed(self,event):
        logging.debug(event)

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        lp_login_frame = customtkinter.CTkFrame(self, fg_color="#FFFFFF",width=200,height=200,corner_radius=20)
        lp_login_frame.place(relx=0.5, rely=0.5,anchor=tk.CENTER)

        lp_label = tk.Label(lp_login_frame,text="ลงชื่อเพื่อเข้าใช้งานระบบ",background="#FFFFFF",font=thai_font)
        lp_username_label = tk.Label(lp_login_frame,text="Username",background="#FFFFFF",font=eng_font)
        lp_username_entry = customtkinter.CTkEntry(lp_login_frame,width=350,corner_radius=10,font=thai_font)
        lp_password_label = tk.Label(lp_login_frame,text="Password",background="#FFFFFF",font=eng_font)
        lp_password_entry = customtkinter.CTkEntry(lp_login_frame,width=350,corner_radius=10,font=thai_font,show="*")
        lp_login_button = customtkinter.CTkButton(lp_login_frame,text="Login",width=350,height=50,font=thai_font)

        lp_label.grid(row=0,column=0,padx=50,sticky=tk.W,pady=(50,0))
        lp_username_label.grid(row=1, column=0,padx=50,pady=(10,0),sticky=tk.W)
        lp_username_entry.grid(row=2, column = 0,padx=50,pady=10,sticky=tk.W)
        lp_password_label.grid(row=3, column = 0,padx=50,sticky=tk.W)
        lp_password_entry.grid(row=4, column = 0,padx=50,pady=10,sticky=tk.W)
        lp_login_button.grid(row=5, column = 0,padx=50,pady=(20,70),sticky=tk.W)
        
        if terminate_app_flag:
            logging.debug('Terminate app')
            self.after(1000,self.run_working_page)
        
    
    def run_working_page(self):
        self.controller.show_frame(WorkingPage)

class WorkingPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        style = ttk.Style(self.controller)
        style.theme_create( "BTStyle", parent="alt", settings={
                            "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0] } },
                            "TNotebook.Tab": {"configure": {"padding": [10, 10] },}},  )
        style.theme_use('BTStyle')
        style.configure('TNotebook', tabposition='nw', background="#FFFFFF", padding=(10, 0, 10, 5),tabmargins=0)
        style.map('lefttab.TNotebook', background= [("selected", "#FFFFFF")])
        
        # ============================== notebook tabs ===================================
        self.notebook = ttk.Notebook(self, style='lefttab.TNotebook')
        self.user_manager_frame = tk.Frame(self.notebook, bg='#FFFFFF')
        self.job_manager_frame = tk.Frame(self.notebook, bg='#FFFFFF')
        self.lab_manager_frame = tk.Frame(self.notebook, bg='#FFFFFF')
        self.experiment_manager_frame = tk.Frame(self.notebook, bg='#FFFFFF')
        self.stock_manager_frame = tk.Frame(self.notebook, bg='#FFFFFF')
        self.setup_pc_frame =tk.Frame(self.notebook, bg='#FFFFFF')
        self.setup_server_db_frame =tk.Frame(self.notebook, bg='#FFFFFF')
        self.logout_frame =tk.Frame(self.notebook, bg='#FFFFFF')

        self.notebook_tab_dictionary = {'User Manager':self.user_manager_frame,
                                        'Job Manager':self.job_manager_frame,
                                        'Lab Manager':self.lab_manager_frame,
                                        'Experiment Manager':self.experiment_manager_frame,
                                        'Stock Manager':self.stock_manager_frame,
                                        'Setup Server Database':self.setup_server_db_frame,
                                        'Setup PC':self.setup_pc_frame,
                                        'Logout':self.logout_frame,
                                        }

        self.notebook.add(self.notebook_tab_dictionary['User Manager'], text='User Manager')
        self.notebook.add(self.notebook_tab_dictionary['Job Manager'], text='Job Manager')
        self.notebook.add(self.notebook_tab_dictionary['Lab Manager'], text='Lab Manager')
        self.notebook.add(self.notebook_tab_dictionary['Experiment Manager'], text= 'Experiment Manager')
        self.notebook.add(self.notebook_tab_dictionary['Stock Manager'], text='Stock Manager')
        self.notebook.add(self.notebook_tab_dictionary['Setup Server Database'], text='Setup Server Database')
        self.notebook.add(self.notebook_tab_dictionary['Setup PC'], text='Setup PC')
        self.notebook.add(self.notebook_tab_dictionary['Logout'], text='Logout')

        self.notebook.grid(row=0, column=0,sticky='we')
        self.notebook.bind('<<NotebookTabChanged>>',self.process_notebook_tab_change)

        self.init_job_manager_tab()
        self.init_user_manager_tab()
        self.init_lab_manager()
        self.init_experiment_manager()
        self.init_db_manager()
    # ============================= database manager tab =============================
    def init_db_manager(self):
        db_manger_frame = tk.Frame(master= self.setup_server_db_frame,bg="#FFFFFF")
        db_manger_frame.grid(row=0,column=0)
        treeview_style = ttk.Style()
        treeview_style.configure("custom.Treeview", highlightthickness=10, bd=10, font=('Time New Roman', 9))
        treeview_style.configure("custom.Treeview.Heading", font=('TH Niramit AS', 16,'bold'))
        treeview_style.layout("custom.Treeview", [('custom.Treeview.treearea', {'sticky': 'nswe'})])
        treeview_style.configure("custom.Treeview", background="#EEFFFF",fieldbackground="black", foreground="black")
        treeview_style.map("custom.Treeview", background=[("selected", "green")])
    #===================================== TOP FRAME =======================================
        dm_top_frame = tk.Frame(db_manger_frame,bg="#FFFFFF")
        dm_top_frame.grid(row=0,column=0,padx=10,pady=10,sticky=tk.W)
    #===================================== BOTTOM LEFT FRAME ===============================
        dm_bottom_left_frame = tk.Frame(db_manger_frame,bg="#FFFFFF")
        dm_bottom_left_frame.grid(row=1,column=0,padx=10,pady=10,sticky=tk.W)
    #===================================== BOTTOM RIGHT FRAME ===============================
        dm_bottom_right_frame = tk.Frame(db_manger_frame,bg="#FFFFFF")
        dm_bottom_right_frame.grid(row=1,column=0,padx=(640,0),pady=10,sticky=tk.N)
    #===================================== TOP RIGHT FRAME =================================
        dm_right_top_frame = tk.Frame(db_manger_frame,bg="#FFFFFF")
        dm_right_top_frame.grid(row=0,column=1,padx=10,pady=10,sticky=tk.NW)
    #===================================== BOTTOM RIGHT FRAME ==============================
        dm_right_bottom_frame = tk.Frame(db_manger_frame,bg="#FFFFFF")
        dm_right_bottom_frame.grid(row=1,column=1,padx=10,pady=10,sticky=tk.NW)
    #===================================== DM TREE VIEW ====================================
        dm_table_summary_treeview_colum = ("order_number","table_name", "field_name","type","nullable","key","default","extra")
        self.dm_table_summary_treeview = ttk.Treeview(master=dm_top_frame, columns=dm_table_summary_treeview_colum, style="custom.Treeview", show='headings',height=15,selectmode="browse",)
        self.dm_table_summary_treeview.heading("order_number",text="ลำดับ")
        self.dm_table_summary_treeview.column("order_number", width=100,anchor=tk.CENTER)
        self.dm_table_summary_treeview.heading("table_name",text="ชื่อตาราง")
        self.dm_table_summary_treeview.column("table_name", width=200,anchor=tk.CENTER)
        self.dm_table_summary_treeview.heading("field_name",text="ชื่อ Field")
        self.dm_table_summary_treeview.column("field_name", width=200,anchor=tk.CENTER)
        self.dm_table_summary_treeview.heading("type",text="data type")
        self.dm_table_summary_treeview.column("type", width=100,anchor=tk.CENTER)
        self.dm_table_summary_treeview.heading("nullable",text="Null")
        self.dm_table_summary_treeview.column("nullable", width=80,anchor=tk.CENTER)
        self.dm_table_summary_treeview.heading("key",text="Key")
        self.dm_table_summary_treeview.column("key", width=130,anchor=tk.CENTER) 
        self.dm_table_summary_treeview.heading("default",text="Default")
        self.dm_table_summary_treeview.column("default", width=250,anchor=tk.CENTER)
        self.dm_table_summary_treeview.heading("extra",text="Extra")
        self.dm_table_summary_treeview.column("extra", width=200,anchor=tk.CENTER)
        self.dm_table_summary_treeview.grid(row=1,column=0,sticky=tk.W,columnspan=5)

        self.dm_experiment_summary_CTklabel = customtkinter.CTkLabel(master=dm_top_frame,text="ตารางในฐานข้อมูล",bg_color="#FFFFFF",font=("TH Niramit AS", 23,'bold'))
        self.dm_experiment_summary_CTklabel.grid(row=0,column=0,pady=(5,10),sticky=tk.W)
    #==================================== DM BOTTOM LEFT FRAME =============================
        dm_query_list_treeview_colum = ("order_number","query",)
        self.dm_query_list_treeview = ttk.Treeview(master=dm_bottom_left_frame, columns=dm_query_list_treeview_colum, style="custom.Treeview", show='headings',height=12,selectmode="browse",)
        self.dm_query_list_treeview.heading("order_number",text="ลำดับ")
        self.dm_query_list_treeview.column("order_number", minwidth=10, width=130,)
        self.dm_query_list_treeview.heading("query",text="รายการ Query ที่บันทึกไว้")
        self.dm_query_list_treeview.column("query", minwidth=10, width=500,)
        self.dm_query_list_treeview.grid(row=1,column=0,sticky=tk.W,columnspan=5)
    #==================================== DM BOTTOM RIGHT FRAME ============================
        self.dm_query_name_label = customtkinter.CTkLabel(master=dm_bottom_right_frame,text="ชื่อ Query",bg_color="#FFFFFF",font=thai_font)
        self.dm_query_message_label = customtkinter.CTkLabel(master=dm_bottom_right_frame,text="คำสั่ง Query",bg_color="#FFFFFF",font=thai_font)
        self.dm_query_name_entry = customtkinter.CTkEntry(master=dm_bottom_right_frame,width=550,font=thai_font)
        self.dm_query_message_CTkTextbox = customtkinter.CTkTextbox(master=dm_bottom_right_frame,width=550,height=220,font=thai_font)

        self.dm_query_name_label.grid(row=0,column=0,padx=(10,0),sticky=tk.W)
        self.dm_query_message_label.grid(row=1,column=0,padx=(10,0),pady=(20,0),sticky=tk.NW)
        self.dm_query_name_entry.grid(row=0,column=1,padx=(20,0),sticky=tk.W)
        self.dm_query_message_CTkTextbox.grid(row=1,column=1,padx=(20,0),pady=(20,5),sticky=tk.NW)
    #==================================== TOP RIGHT FRAME ===================================

        self.dm_delete_table_button = customtkinter.CTkButton(master=dm_right_top_frame, text="ลบตาราง",font=thai_font, width =170, height=40,command=self.dm_delete_table_button_pressed)
        self.dm_clear_all_data_button = customtkinter.CTkButton(master=dm_right_top_frame, text="ล้างข้อมูล",font=thai_font, width =170, height=40,command=self.dm_clear_all_data_button_pressed)

        self.dm_delete_table_button.grid(row=0,column=0,pady=(40,20),sticky=tk.N,)
        self.dm_clear_all_data_button.grid(row=1,column=0,sticky=tk.N,)
    #==================================== TOP RIGHT FRAME ===================================
        self.dm_execution_button = customtkinter.CTkButton(master=dm_right_bottom_frame, text="Execute",font=thai_font, width =170, height=40,command=self.dm_execution_button_pressed)
        self.dm_load_query_button = customtkinter.CTkButton(master=dm_right_bottom_frame, text="แก้ไข Query",font=thai_font, width =170, height=40,command=self.dm_load_query_button_pressed)
        self.dm_save_query_button = customtkinter.CTkButton(master=dm_right_bottom_frame, text="บันทึก Query",font=thai_font, width =170, height=40,command=self.dm_save_query_button_pressed)

        self.dm_delete_query_button = customtkinter.CTkButton(master=dm_right_bottom_frame, text="ลบ query ในลิสต์",font=thai_font, width =170, height=40,command=self.dm_delete_query_button_pressed)

        self.dm_execution_button.grid(row=0,column=0,sticky=tk.N,)
        self.dm_load_query_button.grid(row=1,column=0,sticky=tk.N,pady=20)
        self.dm_save_query_button.grid(row=2,column=0,sticky=tk.N,)
        self.dm_delete_query_button.grid(row=3,column=0,sticky=tk.N,pady=20)
    # ============================ experiment manager tab ==========================
    def init_experiment_manager(self):
        em_frame = tk.Frame(self.experiment_manager_frame,bg='#FFFFFF',border=0)
        em_frame.grid(row=0,column=0,padx=10,pady=10)

        em_bottom_frame = tk.Frame(em_frame,bg='#FFFFFF',border=0)
        em_button_frame = tk.Frame(em_bottom_frame,bg='#FFFFFF',border=0)

        em_bottom_frame.grid(row=2,column=0,padx=10,pady=10,sticky=tk.NW)
        em_button_frame.grid(row=0,column=3,rowspan=10,pady=50,padx=100,sticky=tk.NW)

        self.em_experiment_summary_label = customtkinter.CTkLabel(master=em_frame,text="สรุปรายการทดสอบ",font=thai_font)
        # =================================== treeview table =====================================
        treeview_style = ttk.Style()
        treeview_style.configure("custom.Treeview", highlightthickness=0, bd=0, font=('TH Niramit AS', 17))
        treeview_style.configure("custom.Treeview.Heading", font=('TH Niramit AS', 16,'bold'))
        treeview_style.layout("custom.Treeview", [('custom.Treeview.treearea', {'sticky': 'nswe'})])
        treeview_style.configure("custom.Treeview", background="#EEFFFF",fieldbackground="black", foreground="black")

        lab_experiment_summary_column = ("order_number", "lab_name","experiment_name","processing_time","comment")
        self.em_experiment_summary_treeview = ttk.Treeview(em_frame, columns= lab_experiment_summary_column, style="custom.Treeview", show='headings',height=20)
        self.em_experiment_summary_treeview.heading("order_number", text="ลำดับ")
        self.em_experiment_summary_treeview.column("order_number", minwidth=0, width=50, stretch=tk.NO) 
        self.em_experiment_summary_treeview.heading("lab_name", text="ชื่อห้องปฏิบัติการ")
        self.em_experiment_summary_treeview.column("lab_name", minwidth=0, width=400)
        self.em_experiment_summary_treeview.heading("experiment_name", text="รายการทดสอบ")
        self.em_experiment_summary_treeview.column("experiment_name", minwidth=0, width=400)
        self.em_experiment_summary_treeview.heading("processing_time", text="เวลาดำเนินงาน(วัน)")
        self.em_experiment_summary_treeview.column("processing_time", minwidth=0, width=100)
        self.em_experiment_summary_treeview.heading("comment", text="หมายเหตุ")
        self.em_experiment_summary_treeview.column("comment", minwidth=0, width=600)

        self.em_experiment_information_label = customtkinter.CTkLabel(master=em_bottom_frame,text="ข้อมูลการทดสอบ",font=thai_font)

        self.em_experiment_name_label = customtkinter.CTkLabel(master=em_bottom_frame,text="รายการทดสอบ",font=thai_font)
        self.em_experiment_name_entry = customtkinter.CTkEntry(master=em_bottom_frame,width=350,font=thai_font)
        self.em_delete_experiment_button = customtkinter.CTkButton(master=em_button_frame, text="ลบรายการทดสอบ",font=thai_font, width =180, height=50)

        self.em_lab_name_label = customtkinter.CTkLabel(master=em_bottom_frame,text="ห้องปฏิบัติการ",font=thai_font)
        self.em_lab_name_CTkComboBox = customtkinter.CTkComboBox(master=em_bottom_frame,width=350,font=thai_font,values=["Lab1", "Lab2","Lab3"])
        self.em_add_experiment_button = customtkinter.CTkButton(master=em_button_frame, text="เพิ่มรายการทดสอบ",font=thai_font, width =180, height=50)

        self.em_processing_time_label = customtkinter.CTkLabel(master=em_bottom_frame,text="เวลาดำเนินการ",font=thai_font)
        self.em_processing_time_entry = customtkinter.CTkEntry(master=em_bottom_frame,width=100,font=thai_font)
        self.em_processing_time_unit_label = customtkinter.CTkLabel(master=em_bottom_frame,text="วัน",font=thai_font)
        self.em_update_experiment_buttom = customtkinter.CTkButton(master=em_button_frame, text="แก้ไขข้อมูล",font=thai_font, width =180, height=50)

        self.em_experiment_comment_label = customtkinter.CTkLabel(master=em_bottom_frame,text="หมายเหตุ",font=thai_font)
        self.em_experiment_comment_CTkTextBox = customtkinter.CTkTextbox(master=em_bottom_frame,width=350,height=90,font=thai_font,border_width=2)

        self.em_experiment_summary_label.grid(row=0,column=0,pady= (0,10),columnspan=10,sticky=tk.W)
        self.em_experiment_summary_treeview.grid(row=1,column=0,columnspan=4,sticky=tk.NW)

        self.em_experiment_information_label.grid(row=2,column=0,pady= 10,columnspan=10,sticky=tk.NW)

        self.em_experiment_name_label.grid(row=3,column=0,columnspan=2,sticky=tk.NW)
        self.em_experiment_name_entry.grid(row=3,column=1,padx=10,columnspan=2,sticky=tk.NW)
        
        self.em_lab_name_label.grid(row=4,column=0,pady = 10,sticky=tk.NW)
        self.em_lab_name_CTkComboBox.grid(row=4,column=1,padx=10,pady = 10,columnspan=2,sticky=tk.NW)
        
        self.em_processing_time_label.grid(row=5,column=0,sticky=tk.NW)
        self.em_processing_time_entry.grid(row=5,column=1,padx=10,columnspan=2,sticky=tk.NW)
        self.em_processing_time_unit_label.grid(row=5,column=2,padx=10 ,sticky=tk.NW)
        
        self.em_experiment_comment_label.grid(row=6,column=0,pady = 10,sticky=tk.NW)
        self.em_experiment_comment_CTkTextBox.grid(row=6,column=1,padx=10,pady = (10,0),columnspan=2,sticky=tk.NW)

        self.em_delete_experiment_button.grid(row=0,column=0,sticky=tk.W)
        self.em_add_experiment_button.grid(row=1,column=0,pady = 10,sticky=tk.W)
        self.em_update_experiment_buttom.grid(row=2,column=0,sticky=tk.W)

    # =========================== job manager tab ====================================
    def init_job_manager_tab(self):
        jm_frame = tk.Frame(self.job_manager_frame,bg='#FFFFFF',border=0)
        jm_frame.grid(row=0,column=0,padx=10,pady=10)

        self.jm_start_date_label = customtkinter.CTkLabel(master=jm_frame,text="เลือกช่วงเวลาค้นหา เริ่มตั้งแต่วันที่",font=thai_font)
        self.jm_start_date_date_entry = DateEntry(master=jm_frame,selectmode='day',font=eng_font,width=9)
        self.jm_stop_date_label = customtkinter.CTkLabel(master=jm_frame,text="ถึงวันที่",font=thai_font)
        self.jm_stop_date_date_entry = DateEntry(master=jm_frame,selectmode='day',font=eng_font,width=9)
        self.jm_search_button = customtkinter.CTkButton(master=jm_frame,text='ค้นหา',font=thai_font,command=self.jm_search_button_pressed)
        self.jm_summary_lab_label = customtkinter.CTkLabel(master=jm_frame,text="สรุปงานของห้องปฏิบัติการ",font=thai_font)

        treeview_style = ttk.Style()
        treeview_style.configure("custom.Treeview", highlightthickness=0, bd=0, font=('TH Niramit AS', 17))
        treeview_style.configure("custom.Treeview.Heading", font=('TH Niramit AS', 16,'bold'))
        treeview_style.layout("custom.Treeview", [('custom.Treeview.treearea', {'sticky': 'nswe'})])
        treeview_style.configure("custom.Treeview", background="#EEFFFF",fieldbackground="black", foreground="black")

        lab_treeview_column = ("lab_name", "total_job","success_job","progress_job","canel_job")
        self.jm_lab_summary_treeview = ttk.Treeview(jm_frame, columns=lab_treeview_column, style="custom.Treeview", show='headings',height=10)
        self.jm_lab_summary_treeview.heading("lab_name", text="ห้องปฏิบัติการ")
        self.jm_lab_summary_treeview.column("lab_name", minwidth=0, width=340, stretch=tk.NO) 
        self.jm_lab_summary_treeview.heading("total_job", text="งานที่รับทั้งหมด")
        self.jm_lab_summary_treeview.column("total_job", minwidth=0, width=180)
        self.jm_lab_summary_treeview.heading("success_job", text="งานที่เสร็จสิ้น")
        self.jm_lab_summary_treeview.column("success_job", minwidth=0, width=180)
        self.jm_lab_summary_treeview.heading("progress_job", text="อยู่ระหว่างดำเนินการ")
        self.jm_lab_summary_treeview.column("progress_job", minwidth=0, width=180)
        self.jm_lab_summary_treeview.heading("canel_job", text="ยกเลิก")
        self.jm_lab_summary_treeview.column("canel_job", minwidth=0, width=180)

        self.jm_lab_in_progress_label = customtkinter.CTkLabel(master=jm_frame,text="รายการงานที่อยู่ระหว่างดำเนินการ",font=thai_font)

        lab_in_progress_column = ("order_number", "job_name","present_status","comment")
        self.jm_lab_in_progress_treeview = ttk.Treeview(jm_frame, columns=lab_in_progress_column, style="custom.Treeview", show='headings',height=20)
        self.jm_lab_in_progress_treeview.heading("order_number", text="ลำดับ")
        self.jm_lab_in_progress_treeview.column("order_number", minwidth=0, width=60, stretch=tk.NO) 
        self.jm_lab_in_progress_treeview.heading("job_name", text="งานที่อยู่ระหว่างดำเนินการ")
        self.jm_lab_in_progress_treeview.column("job_name", minwidth=0, width=300)
        self.jm_lab_in_progress_treeview.heading("present_status", text="สถานะปัจจุบัน")
        self.jm_lab_in_progress_treeview.column("present_status", minwidth=0, width=200)
        self.jm_lab_in_progress_treeview.heading("comment", text="หมายเหตุ")
        self.jm_lab_in_progress_treeview.column("comment", minwidth=0, width=500)
        self.finished_job_button = customtkinter.CTkButton(master=jm_frame,text="งานที่เสร็จสิ้น",font=thai_font,width=200,height=50)
        self.running_job_button = customtkinter.CTkButton(master=jm_frame,text="งานที่กำลังดำเนินการ",font=thai_font,width=200,height=50)
        self.cancel_job_button = customtkinter.CTkButton(master=jm_frame,text="งานที่ยกเลิก",font=thai_font,width=200,height=50)
        self.running_job_detail_button = customtkinter.CTkButton(master=jm_frame,text="รายละเอียด",font=thai_font,width=200,height=50)

        self.jm_start_date_label.grid(row=0,column=0,sticky=tk.W)
        self.jm_start_date_date_entry.grid(row=0,column=1,padx=10,sticky=tk.W)
        self.jm_stop_date_label.grid(row=0,column=2,sticky=tk.W)
        self.jm_stop_date_date_entry.grid(row=0,column=3,padx=10,sticky=tk.W)
        self.jm_search_button.grid(row=0,column=4,sticky=tk.W)
        self.jm_summary_lab_label.grid(row=1,column=0,sticky=tk.W)
        self.jm_lab_summary_treeview.grid(row=2,column=0,columnspan=20,rowspan=5,sticky=tk.W)
        self.jm_lab_in_progress_label.grid(row=7,column=0,sticky=tk.W,pady=(20,0))
        self.jm_lab_in_progress_treeview.grid(row=8,column=0,columnspan=20,sticky=tk.W)

        self.finished_job_button.grid(row=2,column=22,sticky=tk.N,padx=10)
        self.running_job_button.grid(row=3,column=22,sticky=tk.N,padx=10)
        self.cancel_job_button.grid(row=4,column=22,sticky=tk.N,padx=10)
        self.running_job_detail_button.grid(row=8,column=22,sticky=tk.N)

    # ============================= user manager tab =================================
    def init_user_manager_tab(self):
        treeview_style = ttk.Style()
        treeview_style.configure("custom.Treeview", highlightthickness=10, bd=10, font=('TH Niramit AS', 17))
        treeview_style.configure("custom.Treeview.Heading", font=('TH Niramit AS', 16,'bold'))
        treeview_style.layout("custom.Treeview", [('custom.Treeview.treearea', {'sticky': 'nswe'})])
        treeview_style.configure("custom.Treeview", background="#EEFFFF",fieldbackground="black", foreground="black")
        treeview_style.map("custom.Treeview", background=[("selected", "green")])

        um_top_frame = tk.Frame(self.user_manager_frame,bg="#FFFFFF")
        um_main_frame = tk.Frame(self.user_manager_frame,bg="#FFFFFF")
        um_right_frame = tk.Frame(self.user_manager_frame,bg="#FFFFFF")
        um_top_frame.grid(row=0,column=0,padx=10,pady=10,sticky=tk.W)
        um_main_frame.grid(row=1,column=0,padx=10,pady=10,sticky=tk.W)
        um_right_frame.grid(row=0,column=1,padx=10,pady=10,rowspan=2,sticky=tk.NW)

        # ========== top frame ============================
        self.um_search_user_label = customtkinter.CTkLabel(master=um_top_frame,text="ชื่อหรือนามสกุลผู้ที่ต้องการค้นหา",bg_color="#FFFFFF",font=thai_font)
        self.um_search_user = customtkinter.CTkEntry(master=um_top_frame,width=500,bg_color="#FFFFFF",font=thai_font)
        self.um_search_user_button = customtkinter.CTkButton(master=um_top_frame,text="ค้นหา",width=200,bg_color="#FFFFFF",font=thai_font)
        # self.um_search_result_label = customtkinter.CTkLabel(master=um_top_frame,text="ผลการค้นหา",bg_color="#FFFFFF",font=thai_font)

        search_user_column = ("order","name", "surname","lab_name","comment")
        self.um_search_user_result_treeview = ttk.Treeview(master=um_top_frame, columns=search_user_column, style="custom.Treeview", show='headings',height=4,selectmode="browse")
        self.um_search_user_result_treeview.heading("order", text="ลำดับที่")
        self.um_search_user_result_treeview.column("order", minwidth=0, width=50,anchor=tk.CENTER)
        self.um_search_user_result_treeview.heading("name", text="ชื่อ")
        self.um_search_user_result_treeview.column("name", minwidth=0, width=250,anchor=tk.CENTER) 
        
        self.um_search_user_result_treeview.heading("surname", text="นามสกุล")
        self.um_search_user_result_treeview.column("surname", minwidth=0, width=250,anchor=tk.CENTER)
        self.um_search_user_result_treeview.heading("lab_name", text="ห้องปฏิบัติการ")
        self.um_search_user_result_treeview.column("lab_name", minwidth=0, width=300,anchor=tk.CENTER)
        self.um_search_user_result_treeview.heading("comment", text="หมายเหตุ")
        self.um_search_user_result_treeview.column("comment", minwidth=0, width=300,anchor=tk.CENTER)

        # self.um_search_user_result_treeview.insert("",'end',values=('1','อ้ายมา','ฟั่งไป','Biochem Lab',''))
        # self.um_search_user_result_treeview.insert("",'end',values=('2','อ้ายใจ','ฟั่งมา','Biochem Lab',''))

        self.um_search_user_label.grid(row=0,column=0,sticky=tk.W)
        self.um_search_user.grid(row=0,column=1,padx=20)
        self.um_search_user_button.grid(row=0,column=2)
        # self.um_search_result_label.grid(row=1,column=0,sticky=tk.W)
        self.um_search_user_result_treeview.grid(row=2,column=0,sticky=tk.W,columnspan=5,pady=(20,0))
        # =========== main frame ==========================
        self.um_user_title_label =customtkinter.CTkLabel(master=um_main_frame,text = 'คำนำหน้า' ,font=thai_font)
        self.um_user_title_entry = customtkinter.CTkEntry(master=um_main_frame,width=350,font=thai_font)

        self.um_name_label =customtkinter.CTkLabel(master=um_main_frame,text = 'ชื่อ' ,font=thai_font)
        self.um_surname_label =customtkinter.CTkLabel(master=um_main_frame,text = 'นามสกุล' ,font=thai_font)

        self.um_user_name_label =customtkinter.CTkLabel(master=um_main_frame,text = 'Username' ,font=thai_font)
        self.um_password_label =customtkinter.CTkLabel(master=um_main_frame,text = 'Password' ,font=thai_font)
        self.um_lab_name_label =customtkinter.CTkLabel(master=um_main_frame,text = 'ห้องแลป' ,font=thai_font)
        self.um_address_label =customtkinter.CTkLabel(master=um_main_frame,text = 'ที่อยู่' ,font=thai_font)
        # self.um_internal_phon_label =customtkinter.CTkLabel(master=um_main_frame,text = 'เบอร์ภายใน' ,font=thai_font)
        self.um_phone_number_label =customtkinter.CTkLabel(master=um_main_frame,text = 'เบอร์โทร' ,font=thai_font)
        self.um_email_label =customtkinter.CTkLabel(master=um_main_frame,text = 'Email' ,font=thai_font)
        # self.um_line_id_label =customtkinter.CTkLabel(master=um_main_frame,text = 'Line ID' ,font=thai_font)
        # self.um_occupation_label =customtkinter.CTkLabel(master=um_main_frame,text = 'ตำแหน่ง' ,font=thai_font)

        self.um_name_entry = customtkinter.CTkEntry(master=um_main_frame,width=350,font=thai_font)
        self.um_surname_entry = customtkinter.CTkEntry(master=um_main_frame,width=350,font=thai_font)
        self.um_user_name_entry = customtkinter.CTkEntry(master=um_main_frame,width=350,font=thai_font)
        self.um_password_entry = customtkinter.CTkEntry(master=um_main_frame,width=350,font=thai_font)
        self.um_lab_name_option = customtkinter.CTkComboBox(master=um_main_frame,width=350,font=thai_font,values=["Lab1", "Lab2","Lab3"])
        self.um_address_textbox = customtkinter.CTkTextbox(master=um_main_frame,width=350,height=70,font=thai_font,border_width=2)
        # self.um_internal_phon_entry = customtkinter.CTkEntry(master=um_main_frame,width=350,font=thai_font)
        self.um_phon_number_entry = customtkinter.CTkEntry(master=um_main_frame,width=350,font=thai_font)
        self.um_email_entry = customtkinter.CTkEntry(master=um_main_frame,width=350,font=thai_font)
        # self.um_line_id_entry = customtkinter.CTkEntry(master=um_main_frame,width=350,font=thai_font)
        # self.um_occupation_option = customtkinter.CTkComboBox(master=um_main_frame,width=350,font=thai_font,values=["ตำแหน่ง1", "ตำแหน่ง2","ตำแหน่ง3"])

        self.um_user_title_label.grid(row=0,column=0,sticky=tk.NW)
        self.um_user_title_entry.grid(row=0,column=1,padx = 10,pady=(0,10),sticky=tk.NW)
        self.um_name_label.grid(row=1,column=0,sticky=tk.NW)
        self.um_name_entry.grid(row=1,column=1,padx = 10,sticky=tk.NW)
        self.um_surname_label.grid(row=1,column=2,padx=10,sticky=tk.NE)
        self.um_surname_entry.grid(row=1,column=3,sticky=tk.NW)

        self.um_user_name_label.grid(row=2,column=0,pady=10,sticky=tk.NW)
        self.um_user_name_entry.grid(row=2,column=1,pady=10,padx = 10,sticky=tk.NW)

        self.um_password_label.grid(row=3,column=0,sticky=tk.NW)
        self.um_password_entry.grid(row=3,column=1,padx = 10,sticky=tk.NW)

        self.um_lab_name_label.grid(row=4,column=0,pady=10,sticky=tk.NW)
        self.um_address_label.grid(row=5,column=0,sticky=tk.NW)
        # self.um_internal_phon_label.grid(row=6,column=0,pady=10,sticky=tk.NW)
        self.um_phone_number_label.grid(row=7,column=0,sticky=tk.NW)
        self.um_email_label.grid(row=8,column=0,pady=10,sticky=tk.NW)
        # self.um_line_id_label.grid(row=9,column=0,sticky=tk.NW)
        # self.um_occupation_label.grid(row=10,column=0,pady=10,sticky=tk.NW)

        self.um_lab_name_option.grid(row=4,column=1,padx = 10,pady = 10,sticky=tk.NW)
        self.um_address_textbox.grid(row=5,column=1,padx = 10,sticky=tk.NW)
        # self.um_internal_phon_entry.grid(row=6,column=1,padx = 10,pady = 10,sticky=tk.NW)
        self.um_phon_number_entry.grid(row=7,column=1,padx = 10,sticky=tk.NW)
        self.um_email_entry.grid(row=8,column=1,padx = 10,pady = 10,sticky=tk.NW)
        # self.um_line_id_entry.grid(row=9,column=1,padx = 10,sticky=tk.NW) 
        # self.um_occupation_option.grid(row=10,column=1,padx = 10,pady = 10,sticky=tk.NW)

        self.um_signature_cavas = tk.Canvas(master=um_main_frame, bg='white', width=350, height=350)
        self.um_signature_label = customtkinter.CTkLabel(master=um_main_frame,text='ลายมือ',font=thai_font)
        self.um_signature_cavas.grid(row=2,column=3,columnspan=2,rowspan=10,sticky=tk.NS,pady=20)
        self.um_signature_label.grid(row=12,column=3,columnspan=2,sticky=tk.N)

        # ========= right frame ===============
        self.um_load_infomation_button = customtkinter.CTkButton(master=um_right_frame, text="แสดงข้อมูล",font=thai_font, width =180, height=50)
        self.um_clear_infomation_button = customtkinter.CTkButton(master=um_right_frame, text="ล้างข้อมูล",font=thai_font, width =180, height=50)
        self.um_clear_signature_button = customtkinter.CTkButton(master=um_right_frame, text="แก้ไขลายมือ",font=thai_font, width =180, height=50,command= lambda:self.um_signature_cavas.delete('all'))
        self.um_update_user_button = customtkinter.CTkButton(master=um_right_frame, text="ปรับปรุงข้อมูล",font=thai_font, width =180, height=50)
        self.um_add_user_button = customtkinter.CTkButton(master=um_right_frame, text="สร้าง User ใหม่",font=thai_font, width =180, height=50)
        self.um_remove_user_button = customtkinter.CTkButton(master=um_right_frame, text="ลบ User ออก",font=thai_font, width =180, height=50)

        self.um_load_infomation_button.grid(row=0,column=5,sticky=tk.N,pady = (70,80))
        self.um_clear_infomation_button.grid(row=1,column=5,sticky=tk.NW)
        self.um_clear_signature_button.grid(row=2,column=5,sticky=tk.NW,pady=(20,70))
        self.um_update_user_button.grid(row=3,column=5,sticky=tk.NW)
        self.um_add_user_button.grid(row=4,column=5,sticky=tk.NW,pady=10)
        self.um_remove_user_button.grid(row=5,column=5,sticky=tk.NW)


        self.previous_x = None
        self.previous_y = None

        self.um_signature_cavas.bind("<B1-Motion>", self.on_mouse_press_cenvas)
        self.um_signature_cavas.bind('<ButtonRelease-1>', self.disconnect_canva_line)

    # ============================ lab manager tab ===================================
    def init_lab_manager(self):
        treeview_style = ttk.Style()
        treeview_style.configure("custom.Treeview", highlightthickness=10, bd=10, font=('TH Niramit AS', 17))
        treeview_style.configure("custom.Treeview.Heading", font=('TH Niramit AS', 16,'bold'))
        treeview_style.layout("custom.Treeview", [('custom.Treeview.treearea', {'sticky': 'nswe'})])
        treeview_style.configure("custom.Treeview", background="#EEFFFF",fieldbackground="black", foreground="black")
        treeview_style.map("custom.Treeview", background=[("selected", "green")])

        lm_top_frame = tk.Frame(self.lab_manager_frame,bg="#FFFFFF")
        lm_top_frame.grid(row=0,column=0,padx=10,pady=10,sticky=tk.W)

        lm_left_frame = tk.Frame(self.lab_manager_frame,bg="#FFFFFF")
        lm_left_frame.grid(row=1,column=0,padx=10,pady=10,sticky=tk.W)
        lm_right_frame = tk.Frame(self.lab_manager_frame,bg="#FFFFFF")
        lm_right_frame.grid(row=1,column=0,padx=10,pady=10,sticky=tk.NE)
        #=========================================================== Top frame ===============================================

        self.lm_lab_summary_label = customtkinter.CTkLabel(master=lm_top_frame,text="สรุปรายชื่อห้องปฏิบัติการ",bg_color="#FFFFFF",font=thai_font)
        self.lm_lab_summary_label.grid(row=0,column=0,sticky=tk.W)
        #========================= tree view ========================================
        lm_lab_summary_treeview_colum = ("order_number","lab_name", "comment",)
        self.lm_lab_summary_treeview = ttk.Treeview(master=lm_top_frame, columns=lm_lab_summary_treeview_colum, style="custom.Treeview", show='headings',height=20,selectmode="browse",)
        self.lm_lab_summary_treeview.heading("order_number",text="ลำดับ")
        self.lm_lab_summary_treeview.column("order_number", minwidth=10, width=100,anchor=tk.CENTER)
        self.lm_lab_summary_treeview.heading("lab_name",text="ชื่อห้องปฏิบัติการ")
        self.lm_lab_summary_treeview.column("lab_name", minwidth=10, width=300,anchor=tk.CENTER)
        self.lm_lab_summary_treeview.heading("comment",text="หมายเหตุ")
        self.lm_lab_summary_treeview.column("comment", minwidth=10, width=600,anchor=tk.W)


        self.lm_lab_summary_treeview.grid(row=1,column=0,sticky=tk.W,columnspan=5)
        #========================== DEBUG =========================================
        # self.lm_lab_summary_treeview.insert("",'end',values=('1','Lab_1','OKKKKKKKKKKKKKKKKKKK'))
        # self.lm_lab_summary_treeview.insert("",'end',values=('2','Lab_2','YOOOOOOOOOOOOOOOOOOO'))
        #===============================================Left frame =====================================================================
        self.lm_laboratory_data_label = customtkinter.CTkLabel(master=lm_left_frame,text="ข้อมูลห้องปฏิบัติการ",bg_color="#FFFFFF",font=("TH Niramit AS", 23,'bold'))
        self.lm_lab_name_label = customtkinter.CTkLabel(master=lm_left_frame,text="ห้องปฏิบัติการ",bg_color="#FFFFFF",font=thai_font)
        self.lm_lab_comment_label = customtkinter.CTkLabel(master=lm_left_frame,text="หมายเหตุ",bg_color="#FFFFFF",font=thai_font)
        self.lm_lab_name_entry = customtkinter.CTkEntry(master=lm_left_frame,width=550,font=thai_font)
        self.lm_lab_comment_CTkTextbox = customtkinter.CTkTextbox(master=lm_left_frame,width=550,height=150,font=thai_font)

        self.lm_laboratory_data_label.grid(row=0,column=0,sticky=tk.W)
        self.lm_lab_name_label.grid(row=1,column=0,padx=10,sticky=tk.W)
        self.lm_lab_comment_label.grid(row=2,column=0,padx=10,pady = 15,sticky=tk.NW)
        self.lm_lab_name_entry.grid(row=1,column=1,padx = (10,0),pady = 15,sticky=tk.NW)
        self.lm_lab_comment_CTkTextbox.grid(row=2,column=1,padx = 10,sticky=tk.NW)
        #============================================== Right frame=============================================================================
        self.lm_delete_lab_button = customtkinter.CTkButton(master=lm_right_frame, text="ลบรายชื่อห้องปฏิบัติการ",font=thai_font, width =250, height=60)
        self.lm_add_lab_button = customtkinter.CTkButton(master=lm_right_frame, text="เพิ่มรายชื่อห้องปฏิบัติการ",font=thai_font, width =250, height=60)
   
        self.lm_delete_lab_button.grid(row=0,column=0,sticky=tk.N,pady = (50,0))
        self.lm_add_lab_button.grid(row=1,column=0,sticky=tk.N,pady = (17,0))


    # ============================ stock manager tab =================================
    def init_setup_pc_tab(self):
        pass
        
    # ============================================ events handles =========================================
    def dm_load_query_button_pressed(self):
        if self.dm_query_list_treeview.focus() != "":
            dm_selected_query_item = self.dm_query_list_treeview.selection()[0]
            query_key = self.dm_query_list_treeview.item(dm_selected_query_item)['values'][1]

            query_dictionary_from_yml = None
            query_dictionary_from_yml = read_yml(yml_query_path)
            if query_dictionary_from_yml != None:
                # clear query name and query string
                self.dm_query_name_entry.delete(0,tk.END)
                self.dm_query_message_CTkTextbox.delete("1.0","end-1c")

                self.dm_query_name_entry.insert(tk.END,query_key)
                self.dm_query_message_CTkTextbox.insert(tk.END,query_dictionary_from_yml[query_key])

    def dm_execution_button_pressed(self):
        if self.dm_query_list_treeview.focus() != "":
            dm_selected_query_item = self.dm_query_list_treeview.selection()[0]
            query_key = self.dm_query_list_treeview.item(dm_selected_query_item)['values'][1]

            query_dictionary_from_yml = None
            query_dictionary_from_yml = read_yml(yml_query_path)
            if query_dictionary_from_yml != None:
                # create connection and add detail to treeview
                server_host = self.controller.configuration_params['server_detail']['address']
                server_port = self.controller.configuration_params['server_detail']['port']
                database_name = self.controller.configuration_params['server_detail']['database']
                user_account = self.controller.configuration_params['admin_login']['username']
                user_password = self.controller.configuration_params['admin_login']['password']

                try:
                    main_db = mysql.connector.connect(  host = server_host,
                                                        port = int(server_port),
                                                        database = database_name,
                                                        user = user_account,
                                                        password = user_password     )
                    main_cursor = main_db.cursor()
                    query_string = query_dictionary_from_yml[query_key]
                    main_cursor.execute(query_string)
                    main_db.commit()
                    main_cursor.close()
                    main_db.close()

                    self.read_database_tables_from_server_to_dm()
                except Exception as Ex:
                    tk.messagebox.showerror(title="SQL command error", message="%s"%(Ex))
                    # logging.error("Error: %s"%(Ex))

    def dm_clear_all_data_button_pressed(self):
        if self.dm_table_summary_treeview.focus() != "":
            dm_selected_table_item = self.dm_table_summary_treeview.selection()[0]
            table_key = self.dm_table_summary_treeview.item(dm_selected_table_item)['values'][1]
            if table_key != "":
                # create connection and add detail to treeview
                server_host = self.controller.configuration_params['server_detail']['address']
                server_port = self.controller.configuration_params['server_detail']['port']
                database_name = self.controller.configuration_params['server_detail']['database']
                user_account = self.controller.configuration_params['admin_login']['username']
                user_password = self.controller.configuration_params['admin_login']['password']

                try:
                    main_db = mysql.connector.connect(  host = server_host,
                                                        port = int(server_port),
                                                        database = database_name,
                                                        user = user_account,
                                                        password = user_password     )
                    main_cursor = main_db.cursor()
                    query_string = "TRUNCATE TABLE " + table_key
                    main_cursor.execute(query_string)
                    main_cursor.close()
                    main_db.close()
                except Exception as Ex:
                    logging.error("Error: %s"%(Ex))
                #======== reload table ==========================

    def dm_delete_table_button_pressed(self):
        if self.dm_table_summary_treeview.focus() != "":
            dm_selected_table_item = self.dm_table_summary_treeview.selection()[0]
            table_key = self.dm_table_summary_treeview.item(dm_selected_table_item)['values'][1]
            if table_key != "":
                # create connection and add detail to treeview
                server_host = self.controller.configuration_params['server_detail']['address']
                server_port = self.controller.configuration_params['server_detail']['port']
                database_name = self.controller.configuration_params['server_detail']['database']
                user_account = self.controller.configuration_params['admin_login']['username']
                user_password = self.controller.configuration_params['admin_login']['password']

                try:
                    main_db = mysql.connector.connect(  host = server_host,
                                                        port = int(server_port),
                                                        database = database_name,
                                                        user = user_account,
                                                        password = user_password     )
                    main_cursor = main_db.cursor()
                    query_string = "DROP TABLE IF EXISTS " + table_key
                    main_cursor.execute(query_string)
                    main_cursor.close()
                    main_db.close()
                    #======== reload table ==========================
                    self.read_database_tables_from_server_to_dm()
                except Exception as Ex:
                    logging.error("Error: %s"%(Ex))
            

    def dm_delete_query_button_pressed(self):
        if self.dm_query_list_treeview.focus() != "":
            # dm_selected_query_inndex = self.dm_query_list_treeview.index(self.dm_query_list_treeview.focus())
            dm_selected_query_item = self.dm_query_list_treeview.selection()[0]
            query_key = self.dm_query_list_treeview.item(dm_selected_query_item)['values'][1]

            query_dictionary_from_yml = None
            query_dictionary_from_yml = read_yml(yml_query_path)
            if query_dictionary_from_yml == None:
                query_dictionary_from_yml = {}
            query_dictionary_from_yml.pop(query_key, None)
            write_yml(query_dictionary_from_yml,yml_query_path)

            self.update_query_from_yml()

    def dm_save_query_button_pressed(self):
        query_dictionary_from_yml = None
        # read query dictionary
        if self.dm_query_name_entry.get() != "":
            query_dictionary_from_yml = read_yml(yml_query_path)
            if query_dictionary_from_yml == None:
                query_dictionary_from_yml = {}
            temp_query_name = self.dm_query_name_entry.get()
            temp_query_string = self.dm_query_message_CTkTextbox.get("1.0", "end-1c")

            if temp_query_name in query_dictionary_from_yml.keys():
                query_dictionary_from_yml.update({temp_query_name:temp_query_string})
            else:
                query_dictionary_from_yml[temp_query_name] = temp_query_string
            
            write_yml(query_dictionary_from_yml,yml_query_path)
            #==================== clear textbox and entry ==========
            self.dm_query_message_CTkTextbox.delete("1.0","end-1c")
            self.dm_query_name_entry.delete(0,tk.END)
            #=============== update treeview ==================
            self.update_query_from_yml()

    def process_notebook_tab_change(self,event):
        #=============== tabs should order as defined in dictionary ============================
        active_tab_index = self.notebook.index(self.notebook.select())
        if active_tab_index == list(self.notebook_tab_dictionary.keys()).index('User Manager'):
            logging.debug("User manager tab is activated")
        elif active_tab_index == list(self.notebook_tab_dictionary.keys()).index('Job Manager'):
            logging.debug("Job manager tab is activated")
        elif active_tab_index == list(self.notebook_tab_dictionary.keys()).index('Lab Manager'):
            logging.debug("Lab manager tab is activated")
        elif active_tab_index == list(self.notebook_tab_dictionary.keys()).index('Experiment Manager'):
            logging.debug("Experiment manager tab is activated")
        elif active_tab_index == list(self.notebook_tab_dictionary.keys()).index('Stock Manager'):
            logging.debug("Stock manager tab is activated")
        elif active_tab_index == list(self.notebook_tab_dictionary.keys()).index('Setup Server Database'):
            self.read_database_tables_from_server_to_dm()
            self.update_query_from_yml()
            
        elif active_tab_index == list(self.notebook_tab_dictionary.keys()).index('Setup PC'):
            logging.debug("Setup PC tab is activated")
        elif active_tab_index == list(self.notebook_tab_dictionary.keys()).index('Logout'):
            logging.debug("Logout tab is activated")

    def update_query_from_yml(self):
        global yml_query_path
        #dictionary_from_yml = None
        dictionary_from_yml = read_yml(yml_query_path)
        if dictionary_from_yml != None:
            for item in self.dm_query_list_treeview.get_children():
                self.dm_query_list_treeview.delete(item)
            for query_index,available_query_name in enumerate(dictionary_from_yml):
                self.dm_query_list_treeview.insert("",'end',values=(query_index+1,available_query_name))
            
    def read_database_tables_from_server_to_dm(self):
        # clear treeview
        for item in self.dm_table_summary_treeview.get_children():
            self.dm_table_summary_treeview.delete(item)
        # create connection and add detail to treeview
        server_host = self.controller.configuration_params['server_detail']['address']
        server_port = self.controller.configuration_params['server_detail']['port']
        database_name = self.controller.configuration_params['server_detail']['database']
        user_account = self.controller.configuration_params['admin_login']['username']
        user_password = self.controller.configuration_params['admin_login']['password']

        try:
            main_db = mysql.connector.connect(  host = server_host,
                                                port = int(server_port),
                                                database = database_name,
                                                user = user_account,
                                                password = user_password     )
            main_cursor = main_db.cursor()
            query_string = "Show tables;"
            main_cursor.execute(query_string)
            table_names = main_cursor.fetchall()

            for order_index,current_table in enumerate(table_names):
                query_string = "DESCRIBE " + database_name + "." + current_table[0]
                main_cursor.execute(query_string)
                current_table_detail = main_cursor.fetchall()
                for field_index,field_detail in enumerate(current_table_detail):
                    if field_index == 0:
                        self.dm_table_summary_treeview.insert("",'end',values=(str(order_index+1),current_table,field_detail[0],field_detail[1],field_detail[2],field_detail[3],field_detail[4],field_detail[5]))
                    else:
                        self.dm_table_summary_treeview.insert("",'end',values=("","",field_detail[0],field_detail[1],field_detail[2],field_detail[3],field_detail[4],field_detail[5]))
            main_cursor.close()
            main_db.close()
        except Exception as Ex:
            logging.error("Error: %s"%(Ex))

    def on_mouse_press_cenvas(self,event):
        if self.previous_x and self.previous_y:
            self.um_signature_cavas.create_line((self.previous_x, self.previous_y, event.x, event.y), width=4)
            self.previous_x, self.previous_y = event.x, event.y
        else:
            self.previous_x, self.previous_y = event.x, event.y

    def disconnect_canva_line(self,event):
        self.previous_x = None
        self.previous_y = None

    def jm_search_button_pressed(self):
        logging.debug('jm button pressed')

class ErrorPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        error_main_frame = customtkinter.CTkFrame(self, fg_color="#FFFFFF",width=200,height=200,corner_radius=20)
        error_main_frame.place(relx=0.5, rely=0.5,anchor=tk.CENTER)

        error_message_label = tk.Label(error_main_frame,text="โปรดตรวจสอบ yml ไฟล์",background="#FFFFFF",font=thai_font)
        error_button = customtkinter.CTkButton(master=error_main_frame,text="OK")
        error_message_label.grid(row=0,column=0)
        error_button.grid(row=0,column=0)
        

if __name__ == "__main__":
    main_app = tkinterApp()
    main_app.defaultFont = font.nametofont("TkDefaultFont")
    main_app.defaultFont.configure(family="Time New Roman", size=13)
    main_app.eval('tk::PlaceWindow . topleft')
    main_app.mainloop()
