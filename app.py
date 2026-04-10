from pydoc import text

import flet as ft
import asyncio
import pygame


def main(page: ft.Page):
    pygame.mixer.init()
    page.title = "Pomodoro"
    page.window_width = 300
    page.window_height = 400
    # page.vertical_alignment = ft.MainAxisAlignment.CENTER
    # page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.padding = 0
    page.spacing = 0
    # page.bgcolor = "#112D4E"


    # Inicialización de variables para el temporizador
    WORK_TIME = 6 #25 * 60
    BREAK_TIME = 6 #5 * 60
    is_running = False
    is_work = True
    remaining_time = WORK_TIME
    timer_task = None


    # Función para seleccionar un audio aleatorio de una carpeta
    def random_audio(folder):
        import random
        from pathlib import Path

        audio_folder = Path("audio") / folder
        files = list(audio_folder.glob("*.mp3"))

        return str(random.choice(files))


    # Funcion para reproducir el audios
    def play(file):
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()


    # Función para formatear el tiempo en minutos y segundos
    def format_time(seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02}:{secs:02}"


    # Función para actualizar la interfaz con el tiempo restante y el estatus actual
    def update_ui():
        timer_text.value = format_time(remaining_time)

        if is_work:
            status_text.value = "WORK"
            bg.bgcolor = "#112D4E"

        else:
            status_text.value = "BREAK"
            bg.bgcolor = "#3F72AF"

        page.update()


    # Funcion para el boton de reset
    async def reset_timer(e):

        play(random_audio("other buttons"))

        nonlocal is_running, remaining_time, is_work, timer_task
        is_running = False
        if timer_task:
            timer_task.cancel()
        is_work = True
        remaining_time = WORK_TIME
        update_ui()

    
    # Nueva funcion para unificar control start/pause
    async def timer(e):
        nonlocal is_running, timer_task

        # ▶️ START
        if not is_running:
            play(random_audio("start button"))
            is_running = True
            timer_task = asyncio.create_task(run_timer())
            control_btn.content.value = "Pause"

        # ⏸️ PAUSE
        else:
            play(random_audio("other buttons"))
            is_running = False
            if timer_task:
                timer_task.cancel()
            control_btn.content.value = "Start"
        
        control_btn.update()


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
    timer_text = ft.Text(
        value="25:00",
        size=60,
        color="#F9F7F7",
        font_family="Times New Roman"
    )


    status_text = ft.Text(
        value="WORK",
        size=40,
        color="#F9F7F7",
        font_family="Times New Roman"
    )


    # Botones
    control_btn = ft.Button(
        content=ft.Text(
            "Start",
            weight=ft.FontWeight.BOLD,
            size=16,
        ),
        on_click=timer,
        style=ft.ButtonStyle(
            bgcolor = "#DBE2EF",   #button color
            color = "#3F72AF",      #text color
            text_style=ft.TextStyle(font_family="Times New Roman"),
            padding=20
        )
    )
    

    reset_btn = ft.IconButton(
        icon=ft.Icons.RESTART_ALT_OUTLINED,
        on_click=reset_timer,
        style=ft.ButtonStyle(
            bgcolor = "#DBE2EF",   #button color
            color = "#3F72AF"  ,    #text color
            text_style=ft.TextStyle(font_family="Times New Roman")
        )
    )


    bg = ft.Container(
        expand=True,
        bgcolor="#112D4E",
        animate=ft.Animation(500, "easeInOut"),
        padding=0,
        margin=0,
    )


    bg.content = ft.Column([
            status_text,
            timer_text,
            ft.Row(
                [control_btn, reset_btn],
                alignment=ft.MainAxisAlignment.CENTER
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    page.add(bg)


    update_ui()


ft.run(main)