from pycaw.pycaw import AudioUtilities, AudioSession, AudioDevice
import psutil


def get_windows_sound_sources()-> dict[str:dict]:
    """
    Prints all audio sessions currently registered in the Windows sound mixer.
    """
    sessions = AudioUtilities.GetAllSessions()
    the_list:dict[int:str] = {}
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

def print_pids(pids: dict[int:str]):
    for name, pid in pids.items():
        session = AudioDevice(id=pid)
        print(f"App: {name}")
        print(f"  PID: {pid}")
        print(f"  Volume: {session.SimpleAudioVolume.GetMasterVolume():.2f}")
        print(f"  Muted: {session.SimpleAudioVolume.GetMute()}")
        print("-" * 40)

def set_process_volume(pid:int, volume: float)-> bool:
    """
    Set the Windows mixer volume for a specific process.

    Parameters
    ----------
    process_name : str
        Executable name (e.g. "chrome.exe", "vlc.exe")
    volume : float
        Volume level between 0.0 and 1.0
    """
    if not (0.0 <= volume <= 1.0):
        raise ValueError("Volume must be between 0.0 and 1.0")

    try:
        session = AudioDevice(id= pid)
    except: 
        return False # process id not found
    try:
        
            session.SimpleAudioVolume.SetMasterVolume(volume, None)
            return True
    except psutil.NoSuchProcess:
        return False




print_pids(get_windows_sound_sources())
