import tkinter as tk #視窗
from tkinter import ttk,messagebox
from PIL import Image,ImageTk
import tkinter.font as tkFont
import datasource as ds
import tkintermapview #地圖
import os

#標籤
class TKLable(tk.Label):
    def __init__(self,parents,**kwargs):
        super().__init__(parents,**kwargs)
        helv26=tkFont.Font(family='微軟正黑體',size=12,weight='bold') #先設定字體格式
        self.config(font=helv26,foreground="#FFFFFF") 

#一般按鈕
class TKButton(tk.Button):
    def __init__(self,parents,**kwargs): #**kwargs 打包
        super().__init__(parents,**kwargs) #**kwargs 打開
        

#主視窗設定
class Window(tk.Tk):
    def __init__(self):
        super().__init__()
        self.config(bg= '#345678')#設定背景藍色

        #建立Label pack是由上而下!
        title=tk.Label(self,text="垃圾車資訊",bg= '#345678') #類似CSS padding的設定 上下左右各推30
        titlefont=tkFont.Font(family='微軟正黑體',size=18,weight='bold') #先設定字體格式
        title.config(font=titlefont,foreground="#FFFFFF")        
        title.pack(padx=10,pady=10)

        

        #新增notebook(分頁)
        notebook = ttk.Notebook(self)
        notebook.pack(pady=0, expand=True)

        #新增frames
        MapFrame = ttk.Frame(notebook, width=800, height=500)
        KeywordFrame = ttk.Frame(notebook, width=800, height=500)
        
        MapFrame.pack(fill='both', expand=True)
        KeywordFrame.pack(fill='both', expand=True)
        
        # 將frames放到notebook
        notebook.add(KeywordFrame, text='以區域時段搜尋')
        notebook.add(MapFrame, text='以地圖搜尋')
        
        

    #------區域時段搜尋框架--------
        #放選單的框架
        mainFrame = tk.Frame(KeywordFrame,width=800,height=500)
        mainFrame.pack()

        #建立關鍵字的label
        TKLable(mainFrame, text="街道名稱",bd=3).grid(row=0,column=0)
        self.search = tk.Entry(mainFrame, width=50)
        self.search.grid(row=0, column=1,columnspan=3)
        
        
        #建立Combo的Label
        TKLable(mainFrame, text="請選擇行政區",bd=3).grid(row=1,column=0)
        #抓取台北行政區
        self.TaipeiArea_dict=ds.Get_TaipeiArea()
        #台北市行政區下拉選單
        self.TaipeiAreaValue = tk.StringVar()
        self.TaipeiArea_Combo = ttk.Combobox(mainFrame,values=list(self.TaipeiArea_dict.keys()),justify="center",textvariable=self.TaipeiAreaValue)
        self.TaipeiArea_Combo.grid(column=1,row=1)  
        self.TaipeiArea_Combo.current(0)


        #綁定選擇區域事件
        self.TaipeiArea_Combo.bind('<<ComboboxSelected>>',self.change_AreaVillage_Combo)


        TKLable(mainFrame, text="請選擇村里").grid(row=1,column=2)
        #村里下拉選單(依據選擇的行政區連動)
        AreaVillageValue= tk.StringVar()
        self.AreaVillage_Combo = ttk.Combobox(mainFrame,values=["全部"],justify="center",textvariable=AreaVillageValue)
        self.AreaVillage_Combo.grid(column=3,row=1) 
        self.AreaVillage_Combo.current(0)



        #建立抵達時間的Label
        TKLable(mainFrame, text="請選擇抵達時間區間").grid(row=2,column=0)
        self.TimeStart = tk.Entry(mainFrame, width=10)
        self.TimeStart.grid(row=2, column=1)
        TKLable(mainFrame, text="~").grid(row=2,column=2)
        self.TimeEnd = tk.Entry(mainFrame, width=10)
        self.TimeEnd.grid(row=2, column=3)
        
        #搜尋按鈕
        self.keyButton=TKButton(mainFrame,text="搜尋",command=self.KeySearch)
        self.keyButton.grid(row=4,columnspan=4)


        







    #------地圖搜尋框架--------
        #上方搜尋地址
        self.marker_list = []
        self.marker_path = None
        self.search_marker = None
        self.search_in_progress = False
        searchFrame = tk.Frame(MapFrame,width=800,height=500)
        searchFrame.pack()

        self.search_bar = tk.Entry(searchFrame, width=50)
        self.search_bar.grid(row=0, column=0, pady=10, padx=10, sticky="we")
        self.search_bar.focus()

        self.search_bar_button = tk.Button(master=searchFrame, width=8, text="Search", command=self.MapSearch)
        self.search_bar_button.grid(row=0, column=1, pady=10, padx=10)

        self.search_bar_clear = tk.Button(master=searchFrame, width=8, text="Clear", command=self.MapClear)
        self.search_bar_clear.grid(row=0, column=2, pady=10, padx=10)



        self.map_widget = tkintermapview.TkinterMapView(MapFrame, width=800, height=600, corner_radius=0)
        self.map_widget.pack(fill="both", expand=True)
        self.map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)
        # map_widget.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.map_widget.set_position(25.1150128,121.5361573)  # 設置初始座標(台北職能學院)
        self.map_widget.set_zoom(15) #縮放程度


        # load images
        current_path = os.path.join(os.path.dirname(os.path.abspath(__file__))) #設定路徑
        self.truck_image = ImageTk.PhotoImage(Image.open(os.path.join(current_path, "images", "truck.png")).resize((40, 40))) #將圖改成垃圾車
        # marker_2 = self.map_widget.set_marker(25.1150128,121.5361573, text="測試19:00", icon=self.truck_image) #設定新座標
        
        self.set_truckPoint()


    #下拉連動選單
    def change_AreaVillage_Combo(self,event):
        towncode01=self.TaipeiArea_dict[self.TaipeiAreaValue.get()]
        value=ds.Get_AreaVillage(towncode01)
        self.AreaVillage_Combo.config(values=value)
        self.AreaVillage_Combo.current(0)
    
    #區域地區關鍵字搜尋
    def KeySearch():
        pass


    #地圖地址搜尋按鈕
    def MapSearch(self, event=None):
        if not self.search_in_progress:
            self.search_in_progress = True
            if self.search_marker not in self.marker_list:
                self.map_widget.delete(self.search_marker)

            address = self.search_bar.get()
            self.search_marker = self.map_widget.set_address(address, marker=True)
            if self.search_marker is False:
                # address was invalid (return value is False)
                self.search_marker = None
            self.search_in_progress = False


    #地圖地址清除按鈕
    def MapClear(self):
        self.search_bar.delete(0, last=tk.END)
        self.map_widget.delete(self.search_marker)

    #把垃圾車點放到地圖上
    def set_truckPoint(self):
        garbagestation_list=ds.Get_garbageStation()
        for item in garbagestation_list:
            x=float(item["經度"])
            y=float(item["緯度"])
            time=f'{item["抵達時間"][:2]}:{item["抵達時間"][2:]}'
            if int(x)//100!=1: #把經度大於100就不帶入
                self.map_widget.set_marker(x,y, text=time, icon=self.truck_image, marker_color_circle="black",  font=("Helvetica Bold", 12)) #設定新座標
                
            else: #有一筆api資料錯誤會導致程式不能跑
                print("----")
                print(x)
                print(y)
                print(item["地點"])
                # self.map_widget.set_marker(y,x, text=item["抵達時間"], icon=self.truck_image) #設定新座標
        #目前套件未支援點擊座標位置可以顯示對應的內容
        # self.map_widget.add_left_click_map_command(self.left_click_event)
        # self.map_widget.add_right_click_menu_command(label="Add Marker",command=self.add_marker_event,pass_coords=True)

    # def left_click_event(coordinates_tuple):
    #     print("Left click event with coordinates:", coordinates_tuple)

    # def add_marker_event(self,coords):
    #     print("Add marker:", coords)
    #     new_marker = self.map_widget.set_marker(coords[0], coords[1], text="new marker")
    







        # # Combobox creation
        # n = tk.StringVar()
        # monthchoosen = ttk.Combobox(window, width = 27, textvariable = n)

        # # Adding combobox drop down list
        # monthchoosen['values'] = (' January',
        # 					' February',
        # 					' March',
        # 					' April',
        # 					' May',
        # 					' June',
        # 					' July',
        # 					' August',
        # 					' September',
        # 					' October',
        # 					' November',
        # 					' December')

        # monthchoosen.place(x=400,y=200)
        # monthchoosen.current()









def main():
    window=Window()
    window.title("垃圾車停靠讚")
    window.resizable(0,0) #禁止拖拉視窗調整視窗大小
    window.geometry("800x500")


    # a=ds.Get_garbageStation()
    # print(a)

   # label text for title
    # TKLable(window, text = "垃圾車資訊").place(x=20,y=20)

    # label
    # TKLable(window, text = "請選擇地區:").place(x=200,y=200)

    # mainFrame = tk.Frame(window,bg='#345678',width=800,height=500)
    # mainFrame.pack()

    
    window.mainloop()



if __name__ =="__main__":
    main()