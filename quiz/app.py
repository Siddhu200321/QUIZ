import pygame, pyttsx3, time, threading, random, requests, csv, os, html
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# ─── SETUP ─────────────────────────────
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("🤖 Robot Quiz")
font = pygame.font.SysFont("Arial", 24)
small_font = pygame.font.SysFont("Arial", 20)
clock = pygame.time.Clock()

# ─── ASSETS ────────────────────────────
robot_idle = pygame.transform.scale(pygame.image.load("assets/robot_frames/robot1.png"), (300,300))
robot_talk = pygame.transform.scale(pygame.image.load("assets/robot_frames/robot2.png"), (300,300))
correct_sfx = pygame.mixer.Sound("assets/sounds/correct.mp3")
wrong_sfx = pygame.mixer.Sound("assets/sounds/wrong.mp3")
pygame.mixer.music.load("assets/sounds/bg_music.mp3")
pygame.mixer.music.play(-1)

# ─── TTS ENGINE ───────────────────────
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# ─── GLOBAL STATE ─────────────────────
username, language, difficulty = "", "python", "easy"
questions, used_q = [], set()
score, q_index = 0, 0
timer_limit = 30
session_log = []

# ─── QUIZ FUNCTIONS ───────────────────
def speak(text):
    def anim():
        for _ in range(len(text)//5):
            screen.blit(robot_talk,(50,50)); pygame.display.update(); time.sleep(0.15)
            screen.blit(robot_idle,(50,50)); pygame.display.update(); time.sleep(0.15)
    threading.Thread(target=anim, daemon=True).start()
    engine.say(text); engine.runAndWait()

CATEGORY = {"python":18,"html":18,"css":18,"js":18}
def fetch_questions():
    url = f"https://opentdb.com/api.php?amount=10&category={CATEGORY[language]}&difficulty={difficulty}&type=multiple"
    res = requests.get(url).json()
    arr=[]
    for r in res["results"]:
        q=html.unescape(r["question"])
        corr=html.unescape(r["correct_answer"])
        opts=[html.unescape(o) for o in r["incorrect_answers"]]+[corr]
        random.shuffle(opts)
        arr.append({"question":q,"options":opts,"answer":corr})
    random.shuffle(arr)
    return arr

# ─── DRAWING & UI ────────────────────
def draw_text(text, x, y, color=(255,255,255)):
    screen.blit(font.render(text, True, color), (x,y))

def draw_timer_bar(elapsed):
    width = 400 * (1 - elapsed / timer_limit)
    pygame.draw.rect(screen, (180, 50, 50), (400, 620, width, 20))
    remaining = max(0, int(timer_limit - elapsed))
    draw_text(f"Time Left: {remaining}s", 820, 620)

def update_score():
    draw_text(f"Score: {score}", 50, 20)

def draw_buttons():
    global btn_exit, btn_next, btn_prev
    btn_exit = pygame.Rect(860,20,100,40)
    btn_next = pygame.Rect(650,620,120,40)
    btn_prev = pygame.Rect(450,620,120,40)
    for rect, text in [(btn_exit,"Exit"),(btn_prev,"\u25c0 Prev"),(btn_next,"Next \u25b6")]:
        col=(200,0,0) if text=="Exit" else (0,150,0)
        hcol=(col[0]+30,min(col[1]+30,255),min(col[2]+30,255)) if rect.collidepoint(pygame.mouse.get_pos()) else col
        pygame.draw.rect(screen,hcol,rect)
        draw_text(text, rect.x+10, rect.y+8)

# ─── SESSION EXPORT ──────────────────
def export_csv():
    os.makedirs("reports", exist_ok=True)
    path=f"reports/{username}_{int(time.time())}.csv"
    with open(path,"w",newline="") as f:
        csv.writer(f).writerows([["Q","Your","Correct","Correct?"]]+session_log)

def export_pdf():
    os.makedirs("reports",exist_ok=True)
    tm=time.strftime("%Y%m%d_%H%M%S")
    pdf=f"reports/{username}_{tm}.pdf"
    c=canvas.Canvas(pdf,pagesize=letter)
    c.drawString(50,750,f"Quiz Report: {username}")
    c.drawString(50,730,f"Score: {score}/{len(session_log)}")
    corrects=sum(1 for l in session_log if l[3]=="Yes")
    plt.bar(["Correct","Wrong"],[corrects,len(session_log)-corrects])
    plt.savefig("reports/chart.png")
    c.drawImage("reports/chart.png",50,500,width=200,height=200)
    c.showPage(); c.save()

# ─── MAIN QUIZ LOOP ──────────────────
def quiz_loop():
    global score,q_index
    speak(f"Starting quiz: {language}, {difficulty}")
    while q_index < len(questions):
        q=questions[q_index]
        if q["question"] in used_q:
            q_index+=1; continue
        used_q.add(q["question"])
        speak(q["question"]); time.sleep(0.5)
        for opt in q["options"]: speak(opt); time.sleep(0.2)

        start=time.time(); elapsed=0; chosen=None
        answered=False
        while elapsed<timer_limit and not answered:
            screen.fill((20,20,40)); screen.blit(robot_idle,(50,50))
            draw_text(q["question"],50,370)
            for idx,opt in enumerate(q["options"]):
                draw_text(f"{idx+1}. {opt}",70,410+idx*30)
            draw_timer_bar(elapsed); update_score(); draw_buttons()
            pygame.display.update(); elapsed=time.time()-start
            for e in pygame.event.get():
                if e.type==pygame.QUIT: return
                if e.type==pygame.MOUSEBUTTONDOWN:
                    if btn_exit.collidepoint(e.pos): return
                if e.type==pygame.KEYDOWN and pygame.K_1<=e.key<=pygame.K_4:
                    chosen=e.key-pygame.K_1; answered=True
            clock.tick(30)

        your = q["options"][chosen] if answered else "TIMEOUT"
        correct = q["answer"]
        was = "Yes" if your==correct else "No"
        session_log.append([q["question"],your,correct,was])
        if was=="Yes": correct_sfx.play(); speak("Correct"); score+=1
        else:
            wrong_sfx.play(); speak("Wrong"); speak(f"The correct answer: {correct}")
        q_index+=1; time.sleep(1)

    export_csv(); export_pdf()
    speak("Quiz complete! See report.")
    show_leaderboard()

# ─── START MENU (ALIGNED) ─────────────────────
def start_menu():
    global username, language, difficulty
    base_x = 600  # aligned X position after robot
    input_box = pygame.Rect(base_x, 180, 300, 40)
    dd_lang = pygame.Rect(base_x, 240, 300, 40)
    dd_diff = pygame.Rect(base_x, 300, 300, 40)

    cols_inactive = pygame.Color('gray70')
    cols_active = pygame.Color('dodgerblue')
    active = False
    text = ""
    dd_open1 = dd_open2 = False
    opts_lang = list(CATEGORY.keys())
    opts_diff = ["easy", "medium", "hard"]
    selL, selD = opts_lang[0], opts_diff[0]
    btn_start = pygame.Rect(420, 380, 200, 50)

    while True:
        screen.fill((10, 10, 50))
        screen.blit(robot_idle, (50, 50))

       # Labels aligned to the left of input boxes
        draw_text("Enter Name:", base_x - 130, input_box.y + 10)
        draw_text("Select Topic:", base_x - 130, dd_lang.y + 10)
        draw_text("Difficulty:", base_x - 130, dd_diff.y + 10)

        # Input box
        pygame.draw.rect(screen, cols_active if active else cols_inactive, input_box, 2)
        screen.blit(font.render(text, True, (255, 255, 255)), (input_box.x + 5, input_box.y + 5))

        # Dropdowns
        pygame.draw.rect(screen, cols_active if dd_open1 else cols_inactive, dd_lang, 2)
        screen.blit(font.render(selL, True, (255, 255, 255)), (dd_lang.x + 5, dd_lang.y + 5))
        if dd_open1:
            for i, o in enumerate(opts_lang):
                r = pygame.Rect(dd_lang.x, dd_lang.y + 40 * (i + 1), dd_lang.w, 40)
                pygame.draw.rect(screen, cols_inactive, r)
                screen.blit(font.render(o, True, (255, 255, 255)), (r.x + 5, r.y + 5))

        pygame.draw.rect(screen, cols_active if dd_open2 else cols_inactive, dd_diff, 2)
        screen.blit(font.render(selD, True, (255, 255, 255)), (dd_diff.x + 5, dd_diff.y + 5))
        if dd_open2:
            for i, o in enumerate(opts_diff):
                r = pygame.Rect(dd_diff.x, dd_diff.y + 40 * (i + 1), dd_diff.w, 40)
                pygame.draw.rect(screen, cols_inactive, r)
                screen.blit(font.render(o, True, (255, 255, 255)), (r.x + 5, r.y + 5))

        # Start button
        pygame.draw.rect(screen, (0, 200, 0), btn_start)
        draw_text("Start Quiz", btn_start.x + 40, btn_start.y + 10)

        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(e.pos):
                    active = True
                    dd_open1 = dd_open2 = False
                elif dd_lang.collidepoint(e.pos):
                    dd_open1 = not dd_open1
                    active = False
                    dd_open2 = False
                elif dd_diff.collidepoint(e.pos):
                    dd_open2 = not dd_open2
                    active = False
                    dd_open1 = False
                elif btn_start.collidepoint(e.pos) and text.strip():
                    username = text
                    language = selL
                    difficulty = selD
                    return
                elif dd_open1:
                    for i, o in enumerate(opts_lang):
                        r = pygame.Rect(dd_lang.x, dd_lang.y + 40 * (i + 1), dd_lang.w, 40)
                        if r.collidepoint(e.pos):
                            selL = o
                            dd_open1 = False
                elif dd_open2:
                    for i, o in enumerate(opts_diff):
                        r = pygame.Rect(dd_diff.x, dd_diff.y + 40 * (i + 1), dd_diff.w, 40)
                        if r.collidepoint(e.pos):
                            selD = o
                            dd_open2 = False
            if e.type == pygame.KEYDOWN and active:
                if e.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif e.key != pygame.K_RETURN:
                    text += e.unicode
        clock.tick(30)

# ─── SHOW LEADERBOARD ─────────────────
def show_leaderboard():
    draw_text("Top Scores:", 400, 150, (255, 255, 0))
    if os.path.exists("leaderboard.csv"):
        with open("leaderboard.csv") as f:
            lines = sorted(list(csv.reader(f)), key=lambda x: int(x[1]), reverse=True)[:5]
        for i, (n, s) in enumerate(lines):
            draw_text(f"{i+1}. {n} - {s}", 400, 200 + i*30)
    pygame.display.update()
    time.sleep(5)

# ─── MAIN ────────────────────────────
if __name__ == "__main__":
    start_menu()
    speak(f"Hello {username}! Topic: {language}, Difficulty: {difficulty}")
    questions = fetch_questions()
    quiz_loop()
    pygame.quit()
