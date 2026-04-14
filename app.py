from pydoc import text

import flet as ft
import asyncio
import pygame


def main(page: ft.Page):
    # 1. Assets FIRST (so everything can load from it)
    page.assets_dir = "assets"

    # 2. Window / app config
    page.title = "Pomodoro"
    page.window.icon = "assets/icons/yoyo.png"

    # 3. Layout config
    page.padding = 0
    page.spacing = 0

    # 4. Fonts (use paths relative to assets_dir)
    page.fonts = {
        "Roboto": "fonts/Roboto-Regular.ttf",
        "Oi": "fonts/Oi-Regular.ttf",
        "Quantico": "fonts/Quantico-Regular.ttf"
    }

    # 5. External stuff (not related to Flet rendering)
    pygame.mixer.init()

    # Inicialización de variables para el temporizador
    WORK_TIME = 25 * 60
    BREAK_TIME = 5 * 60
    is_running = False
    is_work = True
    remaining_time = WORK_TIME
    timer_task = None


    # Función para seleccionar un audio aleatorio de una carpeta
    def random_audio(folder):
        import random
        from pathlib import Path

        audio_folder = Path("assets/audio") / folder
        files = list(audio_folder.glob("*.mp3"))

        return str(random.choice(files))


    # Funcion para reproducir el audios
    def play(file):
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()


    # Funcion para mover tiempo
    def modify_clock(e):
        nonlocal remaining_time, BREAK_TIME, WORK_TIME

        if is_running:
            return
        elif not is_running:
            if e.control.data == "minutes_up":
                remaining_time += 60

            elif e.control.data == "minutes_down":
                if remaining_time >= 60:
                    remaining_time -= 60

            elif e.control.data == "seconds_up":
                remaining_time += 1

            elif e.control.data == "seconds_down":
                if remaining_time >= 1:
                    remaining_time -= 1

        if is_work:
            WORK_TIME = remaining_time
        else:
            BREAK_TIME = remaining_time

        update_ui()


    # Función para formatear el tiempo en minutos y segundos
    def format_time(seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02}:{secs:02}".replace("", " ")[1:-1]


    # Función para actualizar la interfaz con el tiempo restante y el estatus actual
    def update_ui():
        timer_text.content.value = format_time(remaining_time)

        if is_work:
            status_btn.content.content.value = "WORK"
            bg.bgcolor = "#112D4E"

        else:
            status_btn.content.content.value = "BREAK"
            bg.bgcolor = "#3F72AF"

        page.update()


    # Funcion para cambiar entre modo trabajo y descanso
    def toggle_mode(e):
        nonlocal is_work, is_running, remaining_time

        if is_running:
            return

        is_work = not is_work

        if is_work:
            remaining_time = WORK_TIME
            status_btn.content.content.value = "WORK"
        else:
            remaining_time = BREAK_TIME
            status_btn.content.content.value = "BREAK"

        update_ui()


    # Funcion para el boton de reset
    async def reset_timer(e):
        play(random_audio("other buttons"))

        nonlocal is_running, remaining_time, is_work, timer_task
        
        is_running = False

        if timer_task:
            timer_task.cancel()

        if is_work:
            remaining_time = WORK_TIME
        else:
            remaining_time = BREAK_TIME

        up_btn_minutes.opacity = 1
        down_btn_minutes.opacity = 1
        up_btn_seconds.opacity = 1
        down_btn_seconds.opacity = 1

        control_btn.content.value = "Start"

        update_ui()

    
    # Nueva funcion para unificar control start/pause
    async def timer(e):
        nonlocal is_running, timer_task

        # ▶️ START
        if not is_running:
            up_btn_minutes.opacity = 0
            down_btn_minutes.opacity = 0
            up_btn_seconds.opacity = 0
            down_btn_seconds.opacity = 0

            play(random_audio("start button"))

            is_running = True
            timer_task = asyncio.create_task(run_timer())
            control_btn.content.value = "Pause"
            

        # ⏸️ PAUSE
        else:
            up_btn_minutes.opacity = 1
            down_btn_minutes.opacity = 1
            up_btn_seconds.opacity = 1
            down_btn_seconds.opacity = 1

            play(random_audio("other buttons"))

            is_running = False
            if timer_task:
                timer_task.cancel()

            control_btn.content.value = "Start"
            
        update_ui()


    # Función principal del temporizador que se ejecuta en un bucle asincrónico
    async def run_timer():
        nonlocal remaining_time, is_running, is_work

        while is_running:

            while remaining_time > 0 and is_running:
                await asyncio.sleep(1)
                remaining_time -= 1
                update_ui()

            if not is_running:
                break

            # ⏰ timer reached 0
            if is_work:
                play(random_audio("finish work"))
            else:
                play(random_audio("finish break"))

            # switch mode
            is_work = not is_work
            remaining_time = WORK_TIME if is_work else BREAK_TIME
            update_ui()


    # Textos
    timer_text = ft.Container(
        content=ft.Text(
            size=90,
            color="#F9F7F7",
            font_family="Roboto",
        ),
        padding=ft.Padding.symmetric(vertical=-20)
    )


    # Botones
    status_btn = ft.Container(
        content=ft.TextButton(
            content=ft.Text(
                value="WORK",
                size=60,
                color="#F9F7F7",
                font_family="Oi",
            ),
            on_click=toggle_mode,
            style=ft.ButtonStyle(
                padding=0,  # 👈
                overlay_color="transparent"
            )
        ),
        padding=ft.Padding.symmetric(vertical=20)
    )


    control_btn = ft.Button(
        content=ft.Text(
            "Start",
            weight=ft.FontWeight.BOLD,
            size=30,
        ),
        on_click=timer,
        style=ft.ButtonStyle(
            bgcolor = "#DBE2EF",   #button color
            color = "#3F72AF",      #text color
            text_style=ft.TextStyle(font_family="Quantico"),
            padding=ft.Padding.symmetric(horizontal=40, vertical=17)
        )
    )
    

    reset_btn = ft.IconButton(
        icon=ft.Icons.RESTART_ALT_OUTLINED,
        icon_size=42,
        on_click=reset_timer,
        style=ft.ButtonStyle(
            bgcolor = "#DBE2EF",   #button color
            color = "#3F72AF"  ,    #text color
            padding=9
        )
    )


    up_btn_minutes = ft.IconButton(
        icon=ft.Icons.KEYBOARD_ARROW_UP_ROUNDED,
        data="minutes_up",
        icon_size=16,
        padding=-5,
        style=ft.ButtonStyle(            
            color = "#DBE2EF"  ,    #text color
        ),
        on_click=modify_clock
    )


    down_btn_minutes = ft.IconButton(
        icon=ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED,
        data="minutes_down",
        icon_size=16,
        padding=-5,
        style=ft.ButtonStyle(
            color = "#DBE2EF"  ,    #text color
        ),
        on_click=modify_clock
    )


    up_btn_seconds = ft.IconButton(
        icon=ft.Icons.KEYBOARD_ARROW_UP_ROUNDED,
        data="seconds_up",
        icon_size=16,
        padding=-5,
        style=ft.ButtonStyle(            
            color = "#DBE2EF"  ,    #text color
        ),
        on_click=modify_clock
    )


    down_btn_seconds = ft.IconButton(
        icon=ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED,
        data="seconds_down",
        icon_size=16,
        padding=-5,
        style=ft.ButtonStyle(
            color = "#DBE2EF"  ,    #text color
        ),
        on_click=modify_clock
    )


    timer_controls = ft.Column(
        [
            ft.Row(
                [
                    up_btn_minutes,
                    up_btn_seconds
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=150
            ),
            ft.Container(
                timer_text,
                padding=ft.Padding.symmetric(vertical=0)
            ),
            ft.Row(
                [
                    down_btn_minutes,
                    down_btn_seconds
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=150
            )
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )


    bg = ft.Container(
        expand=True,
        bgcolor="#112D4E",
        animate=ft.Animation(500, "easeInOut"),
        padding=0,
        margin=0,
        content = ft.Column([
                status_btn,
                timer_controls,
                ft.Container(
                    ft.Row(
                        [control_btn, reset_btn],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=40
                    ),
                    margin=ft.Margin.only(top=30)
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


    page.add(bg)


    update_ui()


ft.run(main)