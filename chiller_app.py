import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ChillerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chiller Efficiency & COP Simulator Dashboard")
        self.geometry("950x650")
        
        # Style Configuration
        style = ttk.Style()
        style.theme_use('clam')
        
        # Left Panel (Inputs)
        left = ttk.LabelFrame(self, text=" ⚙️ Inputs ", padding=15)
        left.pack(side="left", fill="y", padx=10, pady=10)
        
        ttk.Label(left, text="Chilled Water Flow (m³/h):").pack(anchor="w", pady=(5,0))
        self.e_flow = ttk.Entry(left)
        self.e_flow.insert(0, "115.5")
        self.e_flow.pack(fill="x", pady=(0,10))
        
        ttk.Label(left, text="CHWR Temp (°C):").pack(anchor="w", pady=(5,0))
        self.e_chwr = ttk.Entry(left)
        self.e_chwr.insert(0, "12.0")
        self.e_chwr.pack(fill="x", pady=(0,10))
        
        ttk.Label(left, text="CHWS Temp (°C):").pack(anchor="w", pady=(5,0))
        self.e_chws = ttk.Entry(left)
        self.e_chws.insert(0, "7.0")
        self.e_chws.pack(fill="x", pady=(0,10))
        
        ttk.Label(left, text="Total Power (kW):").pack(anchor="w", pady=(5,0))
        self.e_pwr = ttk.Entry(left)
        self.e_pwr.insert(0, "85.0")
        self.e_pwr.pack(fill="x", pady=(0,15))
        
        btn = ttk.Button(left, text="คำนวณและอัปเดต", command=self.calculate)
        btn.pack(fill="x", pady=10)
        
        # Right Panel
        right = ttk.Frame(self, padding=10)
        right.pack(side="right", fill="both", expand=True)
        
        # Cards
        kpi_frame = ttk.Frame(right)
        kpi_frame.pack(fill="x", pady=5)
        
        self.lbl_cap = ttk.Label(kpi_frame, text="Cooling Load\n0.0 TON", font=("Helvetica", 14, "bold"), relief="solid", padding=10, justify="center")
        self.lbl_cap.pack(side="left", expand=True, fill="x", padx=5)
        
        self.lbl_cop = ttk.Label(kpi_frame, text="Chiller COP\n0.00", font=("Helvetica", 14, "bold"), relief="solid", padding=10, justify="center", foreground="#0066cc")
        self.lbl_cop.pack(side="left", expand=True, fill="x", padx=5)
        
        self.lbl_kwton = ttk.Label(kpi_frame, text="Specific Power\n0.00 kW/TON", font=("Helvetica", 14, "bold"), relief="solid", padding=10, justify="center")
        self.lbl_kwton.pack(side="left", expand=True, fill="x", padx=5)
        
        # Simulation
        sim_frame = ttk.LabelFrame(right, text=" 🎛️ Simulation ", padding=10)
        sim_frame.pack(fill="x", pady=10)
        
        self.lbl_sim = ttk.Label(sim_frame, text="จำลองปรับอุณหภูมิ CHWS: 7.0 °C", font=("Helvetica", 11, "bold"))
        self.lbl_sim.pack(anchor="w")
        
        self.slider = ttk.Scale(sim_frame, from_=5.0, to=11.0, value=7.0, command=self.on_slide)
        self.slider.pack(fill="x", pady=5)
        
        self.lbl_sim_res = ttk.Label(sim_frame, text="Simulated COP: - | Est. Energy Saving: -", foreground="green")
        self.lbl_sim_res.pack(anchor="w")
        
        # Graph
        self.graph_frame = ttk.Frame(right)
        self.graph_frame.pack(fill="both", expand=True, pady=5)
        
        self.calculate()

    def calculate(self):
        try:
            flow = float(self.e_flow.get())
            chwr = float(self.e_chwr.get())
            chws = float(self.e_chws.get())
            pwr = float(self.e_pwr.get())
            
            dT = chwr - chws
            kw = (flow * 1000 * 4.186 * dT) / 3600
            ton = kw / 3.517
            cop = kw / pwr if pwr > 0 else 0
            kw_ton = pwr / ton if ton > 0 else 0
            
            self.lbl_cap.config(text=f"Cooling Load\n{ton:.1f} TON")
            self.lbl_cop.config(text=f"Chiller COP\n{cop:.2f}")
            self.lbl_kwton.config(text=f"Specific Power\n{kw_ton:.2f} kW/TON")
            
            self.slider.set(chws)
            self.on_slide(chws)
            self.plot_graph(flow, chwr, chws, pwr)
        except ValueError:
            pass

    def on_slide(self, val):
        try:
            s_chws = float(val)
            b_chws = float(self.e_chws.get())
            flow = float(self.e_flow.get())
            chwr = float(self.e_chwr.get())
            b_pwr = float(self.e_pwr.get())
            
            diff = s_chws - b_chws
            s_pwr = b_pwr * (1 - (diff * 0.025))
            s_dT = chwr - s_chws
            s_kw = (flow * 1000 * 4.186 * s_dT) / 3600
            s_cop = s_kw / s_pwr if s_pwr > 0 else 0
            saving = diff * 2.5
            
            self.lbl_sim.config(text=f"จำลองปรับอุณหภูมิ CHWS: {s_chws:.1f} °C")
            self.lbl_sim_res.config(text=f"Simulated COP: {s_cop:.2f}  |  Est. Energy Saving: {saving:+.1f} %")
        except ValueError:
            pass

    def plot_graph(self, flow, chwr, base_chws, base_pwr):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
            
        temps = [5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0]
        cops = []
        for t in temps:
            diff = t - base_chws
            pwr = base_pwr * (1 - (diff * 0.025))
            dT = chwr - t
            kw = (flow * 1000 * 4.186 * dT) / 3600
            cops.append(kw / pwr if pwr > 0 else 0)
            
        fig, ax = plt.subplots(figsize=(6, 2.5), dpi=100)
        ax.plot(temps, cops, color='#0066cc', marker='o', linewidth=2)
        ax.axvline(x=base_chws, color='red', linestyle='--', label=f'Current ({base_chws}°C)')
        ax.set_title("CHWS Temp vs COP Trend", fontsize=10)
        ax.set_xlabel("CHWS Temp (°C)", fontsize=8)
        ax.set_ylabel("COP", fontsize=8)
        ax.grid(True, linestyle=':')
        ax.legend(fontsize=8)
        
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

if __name__ == "__main__":
    app = ChillerApp()
    app.mainloop()