from tkinter import *
import subprocess
import shutil
# ---------------------------- CONSTANTS ------------------------------- #
PINK = "#e2979c"
RED = "#e7305b"
GREEN = "#9bdeac"
YELLOW = "#f7f5dd"
FONT_NAME = "Courier"
WORK_MIN = 25
SHORT_BREAK_MIN = 5
LONG_BREAK_MIN = 15
reps = 0
timer = None

# ---------------------------- notifications ------------------------------- #
def send_notification(title: str, message: str):
    """
    Use the system 'notify-send' on Linux if available.
    Falls back to printing to stdout if not present.
    """
    if shutil.which("notify-send"):
        # non-blocking; ignore errors
        try:
            subprocess.run(["notify-send", title, message], check=False)
        except Exception:
            pass
    else:
        # fallback for environments without notify-send
        print(f"NOTIFY: {title} - {message}")

# ---------------------------- TIMER RESET ------------------------------- # 

def reset_timer():    
    window.after_cancel(timer)
    canvas.itemconfig(timer_text, text="00:00")
    title_lable.config(text="Timer", fg=GREEN)
    check_marks.config(text="")
    global reps
    reps = 0


# ---------------------------- TIMER MECHANISM ------------------------------- # 

def start_timer():
    global reps

    work_sec = WORK_MIN * 60
    short_break_sec = SHORT_BREAK_MIN * 60
    long_break_sec = LONG_BREAK_MIN * 60

    reps += 1
    if reps % 8 == 0:
        title_lable.config(text="Long Break", fg=RED)
        send_notification("Long Break started", "Take a longer break.")
        count_down(long_break_sec)
        
    elif reps % 2 == 0:
        title_lable.config(text="Short Break", fg=PINK)
        send_notification("Short Break started", "Quick rest — relax for a bit.")
        count_down(short_break_sec)
    else:
        title_lable.config(text="Work", fg=GREEN)
        send_notification("Work session started", "Focus for your work session.")
        count_down(work_sec)
    

# ---------------------------- COUNTDOWN MECHANISM ------------------------------- # 

def count_down(count):

    global timer
    count_min = int(count // 60)
    count_sec = int(count % 60)
    if count_sec < 10:
        count_sec = f"0{count_sec}"

    canvas.itemconfig(timer_text, text=f"{count_min}:{count_sec}")
    if count > 0:
        timer = window.after(1000, count_down, count - 1)
    else:
        finished_session = title_lable.cget("text")
        if finished_session == "Work":
            send_notification("Work session ended", "Time for a break!")
        else:
            send_notification(f"{finished_session} ended", "Time to get back to work!")
        start_timer()
        marks = ""
        work_sessions = reps // 2
        for _ in range(work_sessions):
            marks += "✔️"
        check_marks.config(text=marks)
         
# ---------------------------- UI SETUP ------------------------------- #

window = Tk()
window.title("Pomodoro")
window.config(padx=100, pady=50, bg=YELLOW)

canvas = Canvas(width=200, height=224, bg=YELLOW, highlightthickness=0)
tomato_img = PhotoImage(file="./tomato.png")
canvas.create_image(100, 112, image=tomato_img)
timer_text = canvas.create_text(100, 130, text="00:00", fill="white", font=(FONT_NAME, 35, "bold"))
canvas.grid(column=1, row=1)

title_lable = Label(text="Timer", fg=GREEN, bg=YELLOW, font=(FONT_NAME, 50))
title_lable.grid(column=1, row=0)

start_button = Button(text="Start", highlightthickness=0, command=start_timer)
start_button.grid(column=0, row=2)

reset_button = Button(text="Reset", highlightthickness=0, command=reset_timer)
reset_button.grid(column=2, row=2)

check_marks = Label(fg=GREEN, bg=YELLOW, font=(FONT_NAME, 20))
check_marks.grid(column=1, row=3)






window.mainloop()