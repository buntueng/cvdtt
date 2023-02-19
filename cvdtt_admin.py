import mysql.connector
from pathlib import Path
import tkinter as tk
import customtkinter
import yaml
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

# ============= set path to files ==================================================================================
current_path = Path(__file__).resolve().parents[0]
logging_file_path = Path(current_path, 'template.log')

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
        tk.Tk.__init__(self, *args, **kwargs)
        self.resizable(False, False)
        
        self.title('CVDTT - Administrator')
        self.configure(bg='#ccffcc')
        container = tk.Frame(self)
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        self.frames = {}
        for F in (LoginPage, WorkingPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky ="nsew")
        self.show_frame(LoginPage)

        # =========== event binding ===========
        self.bind('<Return>', self.enter_pressed_loginpage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def enter_pressed_loginpage(self,event):
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
        # bt = tk.Button(login)
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

        self.notebook.add(self.user_manager_frame, text='User Manager')
        self.notebook.add(self.job_manager_frame, text='Job Manager')
        self.notebook.add(self.lab_manager_frame, text='Lab Manager')
        self.notebook.add(self.experiment_manager_frame, text= "Experiment manager")
        # self.notebook.add(self.stock_manager_frame, text='Stock Manager')
        self.notebook.add(self.setup_server_db_frame, text='Setup Server Database')
        # self.notebook.add(self.setup_pc_frame, text='Setup PC')
        self.notebook.add(self.logout_frame, text='Logout')

        self.notebook.grid(row=0, column=0,sticky='we')
        self.notebook.bind('<<NotebookTabChanged>>',self.process_notebook_tab_change)

        self.init_job_manager_tab()
        self.init_user_manager_tab()
        self.init_lab_manager()
        self.init_experiment_manager()
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
    # =========================== lab manager tab ====================================
    def init_lab_manager(self):
        lm_frame = tk.Frame(self.lab_manager_frame,bg="#FFFFFF")
        lm_frame.grid(row=0,column=0,padx=10,pady=10)

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
        self.jm_lab_summary_treeview.column("lab_name", minwidth=0, width=640, stretch=tk.NO) 
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
        self.jm_lab_in_progress_treeview.column("job_name", minwidth=0, width=400)
        self.jm_lab_in_progress_treeview.heading("present_status", text="สถานะปัจจุบัน")
        self.jm_lab_in_progress_treeview.column("present_status", minwidth=0, width=200)
        self.jm_lab_in_progress_treeview.heading("comment", text="หมายเหตุ")
        self.jm_lab_in_progress_treeview.column("comment", minwidth=0, width=700)
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
        self.um_search_user_result_treeview.column("order", minwidth=0, width=50)
        self.um_search_user_result_treeview.heading("name", text="ชื่อ")
        self.um_search_user_result_treeview.column("name", minwidth=0, width=250, stretch=tk.NO) 
        
        self.um_search_user_result_treeview.heading("surname", text="นามสกุล")
        self.um_search_user_result_treeview.column("surname", minwidth=0, width=250)
        self.um_search_user_result_treeview.heading("lab_name", text="ห้องปฏิบัติการ")
        self.um_search_user_result_treeview.column("lab_name", minwidth=0, width=300)
        self.um_search_user_result_treeview.heading("comment", text="หมายเหตุ")
        self.um_search_user_result_treeview.column("comment", minwidth=0, width=300)

        self.um_search_user_result_treeview.insert("",'end',values=('1','อ้ายมา','ฟั่งไป','Biochem Lab',''))
        self.um_search_user_result_treeview.insert("",'end',values=('2','อ้ายใจ','ฟั่งมา','Biochem Lab',''))

        self.um_search_user_label.grid(row=0,column=0,sticky=tk.W)
        self.um_search_user.grid(row=0,column=1,padx=20)
        self.um_search_user_button.grid(row=0,column=2)
        # self.um_search_result_label.grid(row=1,column=0,sticky=tk.W)
        self.um_search_user_result_treeview.grid(row=2,column=0,sticky=tk.W,columnspan=5)
        # =========== main frame ==========================
        self.um_user_title_label =customtkinter.CTkLabel(master=um_main_frame,text = 'คำนำหน้า' ,font=thai_font)
        self.um_user_title_entry = customtkinter.CTkEntry(master=um_main_frame,width=350,font=thai_font)

        self.um_name_label =customtkinter.CTkLabel(master=um_main_frame,text = 'ชื่อ' ,font=thai_font)
        self.um_surname_label =customtkinter.CTkLabel(master=um_main_frame,text = 'นามสกุล' ,font=thai_font)

        self.um_user_name_label =customtkinter.CTkLabel(master=um_main_frame,text = 'Username' ,font=thai_font)
        self.um_password_label =customtkinter.CTkLabel(master=um_main_frame,text = 'Password' ,font=thai_font)
        self.um_lab_name_label =customtkinter.CTkLabel(master=um_main_frame,text = 'ห้องแลป' ,font=thai_font)
        self.um_address_label =customtkinter.CTkLabel(master=um_main_frame,text = 'ที่อยู่' ,font=thai_font)
        self.um_internal_phon_label =customtkinter.CTkLabel(master=um_main_frame,text = 'เบอร์ภายใน' ,font=thai_font)
        self.um_phone_number_label =customtkinter.CTkLabel(master=um_main_frame,text = 'เบอร์โทร' ,font=thai_font)
        self.um_email_label =customtkinter.CTkLabel(master=um_main_frame,text = 'Email' ,font=thai_font)
        self.um_line_id_label =customtkinter.CTkLabel(master=um_main_frame,text = 'Line ID' ,font=thai_font)
        self.um_occupation_label =customtkinter.CTkLabel(master=um_main_frame,text = 'ตำแหน่ง' ,font=thai_font)

        self.um_name_entry = customtkinter.CTkEntry(master=um_main_frame,width=350,font=thai_font)
        self.um_surname_entry = customtkinter.CTkEntry(master=um_main_frame,width=350,font=thai_font)
        self.um_user_name_entry = customtkinter.CTkEntry(master=um_main_frame,width=350,font=thai_font)
        self.um_password_entry = customtkinter.CTkEntry(master=um_main_frame,width=350,font=thai_font)
        self.um_lab_name_option = customtkinter.CTkComboBox(master=um_main_frame,width=350,font=thai_font,values=["Lab1", "Lab2","Lab3"])
        self.um_address_textbox = customtkinter.CTkTextbox(master=um_main_frame,width=350,height=70,font=thai_font,border_width=2)
        self.um_internal_phon_entry = customtkinter.CTkEntry(master=um_main_frame,width=350,font=thai_font)
        self.um_phon_number_entry = customtkinter.CTkEntry(master=um_main_frame,width=350,font=thai_font)
        self.um_email_entry = customtkinter.CTkEntry(master=um_main_frame,width=350,font=thai_font)
        self.um_line_id_entry = customtkinter.CTkEntry(master=um_main_frame,width=350,font=thai_font)
        self.um_occupation_option = customtkinter.CTkComboBox(master=um_main_frame,width=350,font=thai_font,values=["ตำแหน่ง1", "ตำแหน่ง2","ตำแหน่ง3"])

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
        self.um_internal_phon_label.grid(row=6,column=0,pady=10,sticky=tk.NW)
        self.um_phone_number_label.grid(row=7,column=0,sticky=tk.NW)
        self.um_email_label.grid(row=8,column=0,pady=10,sticky=tk.NW)
        self.um_line_id_label.grid(row=9,column=0,sticky=tk.NW)
        self.um_occupation_label.grid(row=10,column=0,pady=10,sticky=tk.NW)

        self.um_lab_name_option.grid(row=4,column=1,padx = 10,pady = 10,sticky=tk.NW)
        self.um_address_textbox.grid(row=5,column=1,padx = 10,sticky=tk.NW)
        self.um_internal_phon_entry.grid(row=6,column=1,padx = 10,pady = 10,sticky=tk.NW)
        self.um_phon_number_entry.grid(row=7,column=1,padx = 10,sticky=tk.NW)
        self.um_email_entry.grid(row=8,column=1,padx = 10,pady = 10,sticky=tk.NW)
        self.um_line_id_entry.grid(row=9,column=1,padx = 10,sticky=tk.NW) 
        self.um_occupation_option.grid(row=10,column=1,padx = 10,pady = 10,sticky=tk.NW)

        self.um_signature_cavas = tk.Canvas(master=um_main_frame, bg='white', width=450, height=450)
        self.um_signature_label = customtkinter.CTkLabel(master=um_main_frame,text='ลายมือ',font=thai_font)
        self.um_signature_cavas.grid(row=2,column=3,columnspan=2,rowspan=9,sticky=tk.NS,pady=20)
        self.um_signature_label.grid(row=11,column=3,columnspan=2,sticky=tk.N)

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
    def init_lab_manager_tab(self):
        pass

    # ============================ stock manager tab =================================
    def init_setup_pc_tab(self):
        pass
        
    # ============================================ events handles =========================================
    def process_notebook_tab_change(self,event):
        active_tab_index = self.notebook.index(self.notebook.select())
        if active_tab_index == 5:
            self.controller.show_frame(LoginPage)

    
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

if __name__ == "__main__":
    main_app = tkinterApp()
    main_app.defaultFont = font.nametofont("TkDefaultFont")
    main_app.defaultFont.configure(family="Time New Roman", size=13)
    main_app.eval('tk::PlaceWindow . topleft')
    main_app.mainloop()