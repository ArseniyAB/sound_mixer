from nicegui import ui, app
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from ctypes import cast, POINTER
import threading
import time


def get_audio_sessions():
    """Return a list of (session, simple_volume, display_name)."""
    sessions = AudioUtilities.GetAllSessions()
    result = []
    for session in sessions:
        if session.Process and session.Process.name():
            display_name = session.Process.name()
        else:
            display_name = session.DisplayName or "Unknown"

        simple_volume = session._ctl.QueryInterface(ISimpleAudioVolume)
        result.append((session, simple_volume, display_name))
    return result


def build_ui():
    ui.label("Windows Audio Mixer (NiceGUI)").classes("text-2xl font-bold")

    with ui.card().classes("p-4"):
        ui.label("Master Volume").classes("text-xl")

        # --- Master Volume Control ---
        master_volume_slider = ui.slider(min=0, max=100, value=50, step=1)
        master_volume_slider.on("update:model-value", lambda e: set_master_volume(e.value))

    ui.separator()

    ui.label("Applications").classes("text-xl mt-4")

    session_container = ui.column()

    def refresh_sessions():
        session_container.clear()

        for session, simple_volume, name in get_audio_sessions():
            row = ui.row().classes("items-center gap-4")

            ui.label(name).classes("w-48")

            current_vol = int(simple_volume.GetMasterVolume() * 100)

            slider = ui.slider(min=0, max=100, value=current_vol, step=1)
            slider.on("update:model-value",
                      lambda e, sv=simple_volume: sv.SetMasterVolume(e.value / 100, None))

            mute_checkbox = ui.checkbox("Mute", value=simple_volume.GetMute())
            mute_checkbox.on_change(lambda e, sv=simple_volume: sv.SetMute(e.value, None))

            row()

    refresh_sessions()

    ui.button("Refresh", on_click=refresh_sessions).classes("mt-4")


# --- Master volume using pycaw ---
def set_master_volume(value):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        AudioUtilities.IAudioEndpointVolume._iid_,
        23,  # CLSCTX_ALL
        None
    )
    volume = cast(interface, POINTER(AudioUtilities.IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(value / 100, None)


# --- Run NiceGUI ---
if __name__ == "__main__":
    build_ui()
    ui.run(port=8080)
