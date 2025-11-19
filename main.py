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
current_count = 0
is_paused = False

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
    # Cancel the running timer
    if timer is not None:
        window.after_cancel(timer)
    
    # Reset UI elements
    canvas.itemconfig(timer_text, text="00:00")
    title_lable.config(text="Timer", fg=GREEN)
    check_marks.config(text="")
    
    # Reset global state variables
    global reps
    global is_paused
    global current_count
    reps = 0
    is_paused = False
    current_count = 0
    
    # Reset button text
    pause_resume_button.config(text="Pause")


# ---------------------------- TIMER MECHANISM ------------------------------- # 

def start_timer():
    global reps
    global is_paused
    
    # If a timer is already running or paused, don't start a new one
    if timer is not None or is_paused:
        return

    work_sec = WORK_MIN * 60
    short_break_sec = SHORT_BREAK_MIN * 60
    long_break_sec = LONG_BREAK_MIN * 60

    reps += 1
    
    # Configure the session type and start the countdown
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
    
# ---------------------------- PAUSE/RESUME MECHANISM ------------------------------- #

def pause_resume_timer():
    global is_paused
    global timer
    
    if timer is None and not is_paused:
        # Prevent pausing if the timer hasn't started yet
        return
        
    if not is_paused:
        # PAUSE
        is_paused = True
        window.after_cancel(timer)
        timer = None  # Clear the timer ID
        pause_resume_button.config(text="Resume")
        
        # Update UI to reflect pause
        current_title = title_lable.cget("text")
        title_lable.config(text=f"{current_title} (Paused)", fg=RED)
        
    else:
        # RESUME
        is_paused = False
        pause_resume_button.config(text="Pause")
        
        # Restore original title
        current_title = title_lable.cget("text").replace(" (Paused)", "")
        if "Work" in current_title:
             title_lable.config(text="Work", fg=GREEN)
        elif "Short" in current_title:
            title_lable.config(text="Short Break", fg=PINK)
        elif "Long" in current_title:
            title_lable.config(text="Long Break", fg=RED)
            
        # Continue countdown from the saved count
        if current_count > 0:
            count_down(current_count)

# ---------------------------- COUNTDOWN MECHANISM ------------------------------- # 

def count_down(count):

    global timer
    global current_count
    
    # Check for paused state *before* scheduling the next step
    if is_paused:
        current_count = count # Save remaining time
        return
        
    current_count = count # Always save the current count
    
    count_min = int(count // 60)
    count_sec = int(count % 60)
    if count_sec < 10:
        count_sec = f"0{count_sec}"

    canvas.itemconfig(timer_text, text=f"{count_min}:{count_sec}")
    
    if count > 0:
        # Continue counting down after 1 second
        timer = window.after(1000, count_down, count - 1)
    else:
        # Timer finished
        finished_session = title_lable.cget("text").replace(" (Paused)", "")
        
        # Send notification
        if finished_session == "Work":
            send_notification("Work session ended", "Time for a break!")
        else:
            send_notification(f"{finished_session} ended", "Time to get back to work!")
            
        # Start the next session (break or work)
        start_timer()
        
        # Update checkmarks
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
start_button.grid(column=0, row=2, padx=(0, 20)) # Added padding for spacing

reset_button = Button(text="Reset", highlightthickness=0, command=reset_timer)
reset_button.grid(column=2, row=2, padx=(20, 0)) # Added padding for spacing

# New Pause/Resume Button
pause_resume_button = Button(text="Pause", highlightthickness=0, command=pause_resume_timer)
pause_resume_button.grid(column=1, row=2, pady=(10, 0)) # Centered below the timer**

check_marks = Label(fg=GREEN, bg=YELLOW, font=(FONT_NAME, 20))
check_marks.grid(column=1, row=3)

window.mainloop()