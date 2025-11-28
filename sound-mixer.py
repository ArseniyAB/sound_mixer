from nicegui import ui, app 
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from ctypes import cast, POINTER
import faulthandler

faulthandler.enable(all_threads= True)


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
        ui.slider(min=0, max=100, value=50, step=1).on("update:model-value", lambda e: set_master_volume(e))

    ui.separator()

    ui.label("Applications").classes("text-xl mt-4")

    session_container = ui.column()

    def refresh_sessions():
        session_container.clear()

        for session, simple_volume, name in get_audio_sessions():
            with ui.row().classes("items-center gap-4"):

                ui.label(name).classes("w-48")

                current_vol = int(simple_volume.GetMasterVolume() * 100)

                ui.slider(min=0, max=100, value=current_vol, step=1).on("update:model-value",
                      lambda e, sv=simple_volume: sv.SetMasterVolume(e.value / 100, None))
                

                ui.checkbox("Mute", value=simple_volume.GetMute(),on_change= lambda e, sv=simple_volume: sv.SetMute(e, None))
            # mute_checkbox.on_change(lambda e, sv=simple_volume: sv.SetMute(e.value, None))

            

    refresh_sessions()

    ui.button("Refresh", on_click=refresh_sessions).classes("mt-4")


# --- Master volume using pycaw ---
def set_master_volume(event):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        AudioUtilities.IAudioEndpointVolume._iid_,
        23,  # CLSCTX_ALL
        None
    )
    volume = cast(interface, POINTER(AudioUtilities.IAudioEndpointVolume))
    volume.SetMasterVolumeLevelScalar(event.value / 100, None)


# --- Run NiceGUI ---

build_ui()
ui.run(port=8080)

