import customtkinter
import tkinter

root = customtkinter.CTk()
radio_var = tkinter.IntVar(0)

def radiobutton_event():
    print("radiobutton toggled, current value:", radio_var.get())

root = customtkinter.CTk()

radiobutton_1 = customtkinter.CTkRadioButton(master=root, text="CTkRadioButton 1",
                                             command=radiobutton_event, variable= radio_var, value=1)
radiobutton_2 = customtkinter.CTkRadioButton(master=root, text="CTkRadioButton 2",
                                             command=radiobutton_event, variable= radio_var, value=2)

radiobutton_1.pack(padx=20, pady=10)
radiobutton_2.pack(padx=20, pady=10)