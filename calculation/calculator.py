import tkinter as tk
from tkinter import messagebox
import re

class Calculator:
    def __init__(self, master):
        self.master = master
        master.title("计算器")
        master.configure(bg='#f0f0f0')
        
        # 设置窗口大小和位置
        master.geometry("300x400")
        master.resizable(False, False)
        
        # 显示框
        self.display = tk.Entry(master, font=('Arial', 18), bd=10, insertwidth=1, width=17, justify='right')
        self.display.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
        
        # 按钮布局
        button_layout = [
            ('C', 1, 0), ('⌫', 1, 1), ('(', 1, 2), (')', 1, 3),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('/', 2, 3),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('*', 3, 3),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('-', 4, 3),
            ('0', 5, 0), ('.', 5, 1), ('=', 5, 2), ('+', 5, 3)
        ]
        
        # 创建按钮
        for (text, row, col) in button_layout:
            self.create_button(text, row, col)
    
    def create_button(self, text, row, col):
        # 设置不同类型按钮的样式
        if text == '=':
            button = tk.Button(self.master, text=text, font=('Arial', 12), 
                              bg='#4CAF50', fg='white', height=2, width=5)
        elif text in ['+', '-', '*', '/']:
            button = tk.Button(self.master, text=text, font=('Arial', 12), 
                              bg='#FF9800', fg='white', height=2, width=5)
        elif text in ['C', '⌫']:
            button = tk.Button(self.master, text=text, font=('Arial', 12), 
                              bg='#F44336', fg='white', height=2, width=5)
        elif text in ['(', ')']:
            button = tk.Button(self.master, text=text, font=('Arial', 12), 
                              bg='#2196F3', fg='white', height=2, width=5)
        else:
            button = tk.Button(self.master, text=text, font=('Arial', 12), 
                              bg='#E0E0E0', height=2, width=5)
        
        button.grid(row=row, column=col, padx=5, pady=5)
        
        # 绑定按钮事件
        if text == '=':
            button.bind('<Button-1>', self.calculate)
        elif text == 'C':
            button.bind('<Button-1>', self.clear)
        elif text == '⌫':
            button.bind('<Button-1>', self.backspace)
        else:
            button.bind('<Button-1>', lambda event, digit=text: self.add_to_display(digit))
    
    def add_to_display(self, value):
        current = self.display.get()
        self.display.delete(0, tk.END)
        self.display.insert(0, current + value)
    
    def clear(self, event):
        self.display.delete(0, tk.END)
    
    def backspace(self, event):
        current = self.display.get()
        self.display.delete(0, tk.END)
        self.display.insert(0, current[:-1])
    
    def calculate(self, event):
        try:
            expression = self.display.get()
            
            # 检查表达式是否合法
            if not self.is_valid_expression(expression):
                messagebox.showerror("错误", "表达式格式不正确")
                return
            
            # 计算结果
            result = eval(expression)
            
            # 显示结果，处理整数和小数的显示
            if result == int(result):
                result = int(result)
            
            self.display.delete(0, tk.END)
            self.display.insert(0, str(result))
        except Exception as e:
            messagebox.showerror("错误", f"计算错误: {str(e)}")
            self.display.delete(0, tk.END)
    
    def is_valid_expression(self, expression):
        # 检查括号是否匹配
        if expression.count('(') != expression.count(')'):
            return False
        
        # 检查表达式格式是否正确
        pattern = r'^[0-9+\-*/().]+$'
        if not re.match(pattern, expression):
            return False
        
        # 检查是否有连续的运算符
        if re.search(r'[+\-*/]{2,}', expression):
            return False
        
        return True

if __name__ == "__main__":
    root = tk.Tk()
    app = Calculator(root)
    root.mainloop()