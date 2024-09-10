import tkinter as tk
from tkinter import ttk
import csv

def read_csv_file(file_path):
    data = []
    try:
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            
            headers = next(reader)

            for row in reader:
                data.append(row)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return headers, data

class CSVTableViewer(tk.Tk):
    def __init__(self, file_path):
        super().__init__()
        self.title("CSV Table Viewer")

        self.headers, self.data = read_csv_file(file_path)
        self.current_player_index = 0  
        self.timer_id = None  
        self.click_count = 0  
        self.current_price = 0  
        self.latest_team = "" 

        self.tree = ttk.Treeview(self, columns=self.headers, show='headings')
        for header in self.headers:
            self.tree.heading(header, text=header)
            self.tree.column(header, anchor='center', width=100)

        for row in self.data:
            self.tree.insert('', 'end', values=row)

        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        close_button = tk.Button(self, text="Click To Continue", command=self.close_and_open_auction_windows)
        close_button.pack()

    def close_and_open_auction_windows(self):
        self.current_player_index += 1
        self.click_count = 0  
        if self.current_player_index < len(self.data):
            player_row = self.data[self.current_player_index]
            self.open_auction_window(player_row)

    def open_auction_window(self, player_row):
        player_name = player_row[0]
        player_type = player_row[1]
        base_price = float(player_row[2])  

        auctionwindow = tk.Toplevel(self)
        auctionwindow.title(f"Auction Window - {player_name}")

        text1 = tk.Label(auctionwindow, text=f"Player: {player_name}")
        text1.pack()

        text2 = tk.Label(auctionwindow, text=f"Type: {player_type}")
        text2.pack()

        base_price_label = tk.Label(auctionwindow, text=f"Base Price(in lakh): {base_price}")
        base_price_label.pack()

        current_price_label = tk.Label(auctionwindow, text=f"Current Price(in lakh): {base_price}")
        current_price_label.pack()

        time_left_label = tk.Label(auctionwindow, text="Time Left: 5 seconds")
        time_left_label.pack()

        def reset_timer():
            if hasattr(auctionwindow, 'timer_id') and auctionwindow.timer_id is not None:
                auctionwindow.after_cancel(auctionwindow.timer_id)
                auctionwindow.timer_id = None
            update_time_left(5, self.latest_team)

        def update_time_left(time_left, team):
            if time_left > 0:
                time_left_label.config(text=f"Time Left: {time_left} seconds")
                auctionwindow.timer_id = auctionwindow.after(1000, lambda: update_time_left(time_left - 1, team))
            else:
                if auctionwindow.winfo_exists():
                    auctionwindow.destroy()
                    self.close_and_open_auction_windows()

                    if self.latest_team and self.current_price > 0:  
                        print(f"{player_name} went to {self.latest_team} for {self.current_price:.2f} lakhs")
                        
                        csv_file_path = 'ipl.csv'
                        with open(csv_file_path, 'a', newline='') as csvfile:
                            csv_writer = csv.writer(csvfile)

                            if csvfile.tell() == 0:
                                csv_writer.writerow(['Player Name', 'Team', 'Price (in lakh)'])

                            csv_writer.writerow([player_name, self.latest_team, self.current_price])

        update_time_left(5, self.latest_team)

        reset_button = tk.Button(auctionwindow, text="Reset Timer", command=reset_timer)
        reset_button.pack()

        skip_button = tk.Button(auctionwindow, text="Skip", command=lambda: on_skip_button_click())
        skip_button.pack()

        def on_skip_button_click():
            if auctionwindow.winfo_exists():
                auctionwindow.destroy()
                self.close_and_open_auction_windows()
            print(f"{player_name} was not sold")

        frame1 = tk.Frame(auctionwindow)
        frame1.pack(side='top')

        frame2 = tk.Frame(auctionwindow)
        frame2.pack(side='top')

        teams1 = ["RCB", "CSK", "MI", "SRH", "KKR"]
        for team in teams1:
            team_button = tk.Button(frame1, text=team, command=lambda t=team: self.team_button_clicked(t, current_price_label, base_price, reset_timer))
            team_button.pack(side='left')  

        teams2 = ["DC", "KXIP", "RR", "GT", "LSG"]
        for team in teams2:
            team_button = tk.Button(frame2, text=team, command=lambda t=team: self.team_button_clicked(t, current_price_label, base_price, reset_timer))
            team_button.pack(side='left')  

        def on_auction_window_close():
            self.close_and_open_auction_windows()

        auctionwindow.protocol("WM_DELETE_WINDOW", on_auction_window_close)

    def team_button_clicked(self, team, current_price_label, base_price, reset_timer):
        if self.current_player_index < len(self.data):
            player_row = self.data[self.current_player_index]
            player_name = player_row[0]

            if self.click_count == 0:
                self.current_price = base_price  
            else:
                self.current_price = base_price + 0.1 * base_price * self.click_count

            current_price_label.config(text=f"Current Price(in lakh): {self.current_price:.2f}")

            reset_timer()  
            self.click_count += 1  
            self.latest_team = team  

if __name__ == "__main__":
    file_path = 'C:\\Users\\91963\\Downloads\\IPLSTATS.csv'  
    app = CSVTableViewer(file_path)
    app.mainloop()
