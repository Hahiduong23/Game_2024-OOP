import tkinter as tk
import random
import csv
import os
from tkinter import messagebox
from abc import ABC, abstractmethod
class User:
    def __init__(self, username):
        self.username = username
class GameMode(ABC):
    @abstractmethod
    def create_widgets(self):
        pass
    @abstractmethod
    def update_grid_ui(self):
        pass
class Tile:
    def __init__(self, value=0):
        self.__value = value 
    def set_value(self, value):
        self.__value = value
    def get_value(self):
        return self.__value
class Board:
    def __init__(self):
        self.__grid = [[Tile() for _ in range(4)] for _ in range(4)]  # Private grid
        self.__best_score = 0  
        self.add_new_tile()
        self.add_new_tile()

    def add_new_tile(self):
        empty_cells = [(i, j) for i in range(4) for j in range(4) if self.__grid[i][j].get_value() == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.__grid[i][j].set_value(2)

    def get_grid_values(self):
        return [[self.__grid[i][j].get_value() for j in range(4)] for i in range(4)]
   
    def compress(self):
        changed = False
        new_grid = [[Tile() for _ in range(4)] for _ in range(4)]
        for i in range(4):
            pos = 0
            for j in range(4):
                if self.__grid[i][j].get_value() != 0:
                    new_grid[i][pos].set_value(self.__grid[i][j].get_value())
                    if j != pos:
                        changed = True
                    pos += 1
        self.__grid = new_grid
        return changed
    
    def merge(self):
        changed = False
        for i in range(4):
            for j in range(3):
                if self.__grid[i][j].get_value() == self.__grid[i][j + 1].get_value() and self.__grid[i][j].get_value() != 0:
                    new_value = self.__grid[i][j].get_value() * 2
                    self.__grid[i][j].set_value(new_value)
                    self.__grid[i][j + 1].set_value(0)
                    changed = True
                    if new_value > self.__best_score:
                        self.__best_score = new_value
        return changed
    
    def reverse(self):
        for i in range(4):
            self.__grid[i] = self.__grid[i][::-1]

    def transpose(self):
        self.__grid = [list(row) for row in zip(*self.__grid)]

    def move_left(self):
        changed1 = self.compress()
        changed2 = self.merge()
        self.compress()
        return changed1 or changed2
    
    def move_right(self):
        self.reverse()
        changed = self.move_left()
        self.reverse()
        return changed
    
    def move_up(self):
        self.transpose()
        changed = self.move_left()
        self.transpose()
        return changed
    
    def move_down(self):
        self.transpose()
        changed = self.move_right()
        self.transpose()
        return changed
    
    def check_state(self):
        for i in range(4):
            for j in range(4):
                if self.__grid[i][j].get_value() == 2048:
                    return 'WON'
        for i in range(4):
            for j in range(4):
                if self.__grid[i][j].get_value() == 0:
                    return 'GAME NOT OVER'
        for i in range(3):
            for j in range(3):
                if self.__grid[i][j].get_value() == self.__grid[i + 1][j].get_value() or self.__grid[i][j].get_value() == self.__grid[i][j + 1].get_value():
                    return 'GAME NOT OVER'
        for j in range(3):
            if self.__grid[3][j].get_value() == self.__grid[3][j + 1].get_value():
                return 'GAME NOT OVER'
        for i in range(3):
            if self.__grid[i][3].get_value() == self.__grid[i + 1][3].get_value():
                return 'GAME NOT OVER'
        return 'LOST'

    def get_best_score(self):
        return self.__best_score

    def reset(self):
        self.__grid = [[Tile() for _ in range(4)] for _ in range(4)]
        self.add_new_tile()
        self.add_new_tile()


class Game2048(GameMode):
    def __init__(self, root, user, mode):
        self._root = root 
        self._root.title("2048 OOP")
        self._root.geometry("400x450")
        self._board = Board()
        self.user = user
        self.mode = mode
        self._board._Board__best_score = self.get_existing_score()
        self.create_widgets()
        self.update_grid_ui()

    def create_widgets(self):
        self._frame = tk.Frame(self._root, bg="#bbada0")
        self._frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self._tiles = [[tk.Label(self._frame, text="", width=4, height=2, bg="#cdc1b4", font=('Arial', 24, 'bold'), anchor='center') for _ in range(4)] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                self._tiles[i][j].grid(row=i, column=j, padx=5, pady=5, sticky='nsew')
        for i in range(4):
            self._frame.grid_columnconfigure(i, weight=1)
            self._frame.grid_rowconfigure(i, weight=1)
        self._score_label = tk.Label(self._root, text="Best Score: 0", font=('Arial', 18))
        self._score_label.pack()
        self._root.bind("<Key>", self.key_pressed)

    def update_grid_ui(self):
        grid_values = self._board.get_grid_values()
        for i in range(4):
            for j in range(4):
                value = grid_values[i][j]
                color = self.get_color(value)
                text = str(value) if value != 0 else ''
                self._tiles[i][j].config(text=text, bg=color)
        best_score = self._board.get_best_score()
        self._score_label.config(text=f"Best Score: {best_score}")

    def get_color(self, value):
        colors = {
            2: '#fdd0dc', 4: '#fcb3c2', 8: '#f8a2b7',
            16: '#f7819f', 32: '#f76c7c', 64: '#f64d65',
            128: '#f64d6f', 256: '#f65f6f', 512: '#f67272',
            1024: '#f67d7d', 2048: '#f68888'
        }
        return colors.get(value, '#faf8ef')

    def start_game(self):
        """Initialize or (re)start a normal game.

        Ensures the board has starting tiles and updates the UI so
        callers (ModeSelection) can safely call this on any Game2048
        instance (including subclasses that override it).
        """
        # If the board is empty (all zeros), let Board add two tiles.
        grid = self._board.get_grid_values()
        if all(all(cell == 0 for cell in row) for row in grid):
            self._board.add_new_tile()
            self._board.add_new_tile()
        # Update UI to reflect current board state
        self.update_grid_ui()

    def key_pressed(self, event):
        if event.keysym in ['Up','w', 'W']:
            changed = self._board.move_up()
        elif event.keysym in ['Down', 's','S']:
            changed = self._board.move_down()
        elif event.keysym in ['Left', 'a', 'A']:
            changed = self._board.move_left()
        elif event.keysym in ['Right', 'd', 'D']:
            changed = self._board.move_right()
        else:
            return
        if changed:
            self._board.add_new_tile()
            self.update_grid_ui()
            state = self._board.check_state()
        if state == 'WON':
            self.show_game_over("Chúc mừng! Bạn đã thắng!")
        elif state == 'LOST':
            self.show_game_over("Game Over! Bạn đã thua!")

    def get_existing_score(self):
        try:
            with open('best_scores.csv', mode = 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == self.user.username and row[1] == self.mode:
                        return int(row[2])
        except FileNotFoundError:
            pass
        return 0
    
    def save_best_score(self):
        filename = 'best_scores.csv'
        updated = False
        rows = []
        file_exists = os.path.isfile(filename)
        if file_exists:
            with open(filename, mode='r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if row[0] == self.user.username:
                        if self.mode == 'Normal Mode':
                            row[1] = max(int(row[1]), self._board.get_best_score())
                        elif self.mode == 'Easy Mode':
                            row[2] = max(int(row[2]), self._board.get_best_score())
                        elif self.mode == 'Competition Mode':
                            row[3] = max(int(row[3]), self._board.get_best_score())
                        updated = True
                    rows.append(row)

        if not file_exists:
            rows.append(['username', 'normal_score', 'easy_score', 'competition_score'])  # Tiêu đề
            rows.append([self.user.username, 0, 0, 0])  # Khởi tạo điểm số

        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            for row in rows:
                writer.writerow(row)
            if not updated:
                new_row = [self.user.username, 0, 0, 0]
                if self.mode == 'Normal Mode':
                    new_row[1] = self._board.get_best_score()
                elif self.mode == 'Easy Mode':
                    new_row[2] = self._board.get_best_score()
                elif self.mode == 'Competition Mode':
                    new_row[3] = self._board.get_best_score()
                writer.writerow(new_row)

    def show_game_over(self, message):
        replay = messagebox.askyesno("2048", f"{message}\nBạn có muốn chơi lại không?")
        self.save_best_score()
        if replay:
            if isinstance(self, Game2048EasyMode):
                    self.reset()
            else:
                self._board.reset()
                self.update_grid_ui()
        else:
            self._root.destroy()  
            root = tk.Tk()  
            menu = ModeSelection(root, self.user)
            root.mainloop()


           
class Game2048EasyMode(Game2048):
    def __init__(self, root, user, mode):
        super().__init__(root, user, mode)
        self.start_game() 

    def start_game(self):
        self._board._Board__grid = [[Tile() for _ in range(4)] for _ in range(4)]
        empty_cells = [(i, j) for i in range(4) for j in range(4)]
        if len(empty_cells) >= 2:
            first, second = random.sample(empty_cells, 2)
            self._board._Board__grid[first[0]][first[1]].set_value(8)  
            self._board._Board__grid[second[0]][second[1]].set_value(8)  
        self.update_grid_ui()  

    def add_new_tile(self):
        empty_cells = [(i, j) for i in range(4) for j in range(4) if self._board.get_grid_values()[i][j] == 0]
        if empty_cells:
            i, j = random.choice(empty_cells)
            self._board._Board__grid[i][j].set_value(8)

    def reset(self):
        self._board._Board__grid = [[Tile() for _ in range(4)] for _ in range(4)]
        empty_cells = [(i, j) for i in range(4) for j in range(4)]
        if len(empty_cells) >= 2:
            first, second = random.sample(empty_cells, 2)
            self._board._Board__grid[first[0]][first[1]].set_value(8)  
            self._board._Board__grid[second[0]][second[1]].set_value(8)  
        self.update_grid_ui() 

    def key_pressed(self, event):
        if event.keysym in ['Up','w','W'] :
            changed = self._board.move_up()
        elif event.keysym in ['Down','s','S']:
            changed = self._board.move_down()
        elif event.keysym in ['Left','a','A']:
            changed = self._board.move_left()
        elif event.keysym in ['Right','d','D']:
            changed = self._board.move_right()
        else:
            return
        if changed:
            self.add_new_tile()  
            self.update_grid_ui() 
            state = self._board.check_state()  
        if state == 'WON':
            self.show_game_over("Chúc mừng! Bạn đã thắng!")  
        elif state == 'LOST':
            self.show_game_over("Game Over! Bạn đã thua!")  


class Game2048CompetitionMode(Game2048):
    def __init__(self, root, user, mode):
        super().__init__(root, user, mode)
        self.move_counter = 0  
        self.update_move_counter()  

    def create_widgets(self):
        super().create_widgets()
        self._move_label = tk.Label(self._root, text="Moves: 0", font=('Arial', 18))
        self._move_label.pack()

    def update_move_counter(self):
        self._move_label.config(text=f"Moves: {self.move_counter}")

    def key_pressed(self, event):
        changed = False
        if event.keysym in ['Up','w','W']:
            changed = self._board.move_up()
        elif event.keysym in ['Down','s','S']:
            changed = self._board.move_down()
        elif event.keysym in ['Left','a','A']:
            changed = self._board.move_left()
        elif event.keysym in ['Right','d','D']:
            changed = self._board.move_right()
        else:
            return

        if changed:
            self._board.add_new_tile()  
            self.move_counter += 1  
            self.update_move_counter()  
        self.update_grid_ui() 

        state = self._board.check_state()
        if state == 'WON':
            self.show_game_over(f"Chúc mừng! Bạn đã thắng với {self.move_counter} nước đi!")
        elif state == 'LOST':
            self.show_game_over(f"Game Over! Bạn đã thua sau {self.move_counter} nước đi!")

    def show_game_over(self, message):
        super().show_game_over(message)
        self.move_counter = 0  
        self.update_move_counter() 


class ModeSelection:
    def __init__(self, root, user):
        self._root = root
        self.user = user
        self._root.title("2048 - Chọn chế độ chơi")
        self._root.geometry("300x250")  
        self.create_widgets()

    def create_widgets(self):
        label = tk.Label(self._root, text=f" hellu {self.user.username}, Chọn chế độ chơi:", font=('Arial', 16))
        label.pack(pady=20)

        normal_button = tk.Button(self._root, text="Normal Mode", font=('Arial', 14), command=self.start_normal_mode)
        normal_button.pack(pady=10)

        easy_button = tk.Button(self._root, text="Easy Mode", font=('Arial', 14), command=self.start_easy_mode)
        easy_button.pack(pady=10)

        competition_button = tk.Button(self._root, text="Competition Mode", font=('Arial', 14), command=self.start_competition_mode)
        competition_button.pack(pady=10)
        
        exit_button = tk.Button(self._root, text="Exit", font=('Arial', 14), command=self._root.quit)
        exit_button.pack(pady=10)
    
    def start_normal_mode(self):
        self._root.destroy()  
        root = tk.Tk()
        game = Game2048(root, self.user, 'Normal Mode')
        game.start_game()
        root.mainloop()

    def start_easy_mode(self):
        self._root.destroy()  
        root = tk.Tk()
        game = Game2048EasyMode(root, self.user, 'Easy Mode')
        game.start_game()
        root.mainloop()

    def start_competition_mode(self):
        self._root.destroy()  
        root = tk.Tk()
        game = Game2048CompetitionMode(root, self.user, 'Competition Mode') 
        game.start_game() 
        root.mainloop()

    def exit_game(self):
        self._root.destroy()


class Username:
    def __init__(self, root):
        self._root = root
        self._root.title('Nhập tên ng dùng: ')
        self._root.geometry('300x150')
        self.create_widgets()
    
    def create_widgets(self):
        label = tk.Label(self._root, text="Nhập tên người dùng:", font=('Arial', 14))
        label.pack(pady=20)

        self._username_entry = tk.Entry(self._root, font=('Arial', 14))
        self._username_entry.pack(pady=10)

        submit_button = tk.Button(self._root, text="Submit", font=('Arial', 14), command=self.submit_username)
        submit_button.pack(pady=10)
    def submit_username(self):
        username = self._username_entry.get()
        if username:
            self._root.destroy()
            root = tk.Tk()
            user = User(username)
            ModeSelection(root, user)
            root.mainloop()
        else:
            messagebox.showerror("Error", "Vui lòng nhập tên người dùng!")


if __name__ == "__main__":
    root = tk.Tk()
    username = Username(root)
    root.mainloop()