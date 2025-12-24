from dataclasses import dataclass
from pycaw.pycaw import AudioUtilities, AudioSession, AudioDevice
import psutil





def get_windows_sound_sources() -> dict[str:dict]:
    """
    Prints all audio sessions currently registered in the Windows sound mixer.
    """
    sessions = AudioUtilities.GetAllSessions()
    the_list: dict[int:str] = {}
    if not sessions:
        print("No active audio sessions found.")
        return

    for session in sessions:
        name = "System Sound"
        pid = session.ProcessId

        if pid:
            try:
                name = psutil.Process(pid).name()
            except psutil.NoSuchProcess:
                name = f"PID {pid}"
        the_list[pid] = name

    return the_list