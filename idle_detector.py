"""
Idle detector module to detect user inactivity
"""
import ctypes
from ctypes import Structure, windll, c_uint, sizeof, byref


class LASTINPUTINFO(Structure):
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]


class IdleDetector:
    def __init__(self, idle_threshold=60):
        """
        Initialize idle detector
        
        Args:
            idle_threshold: Seconds of inactivity before considered idle (default: 60)
        """
        self.idle_threshold = idle_threshold * 1000  # Convert to milliseconds

    def get_idle_duration(self):
        """
        Get the duration of user inactivity in seconds
        
        Returns:
            Number of seconds the user has been idle
        """
        lastInputInfo = LASTINPUTINFO()
        lastInputInfo.cbSize = sizeof(lastInputInfo)
        windll.user32.GetLastInputInfo(byref(lastInputInfo))
        millis = windll.kernel32.GetTickCount() - lastInputInfo.dwTime
        return millis / 1000.0

    def is_user_idle(self):
        """
        Check if user is currently idle
        
        Returns:
            True if user is idle, False otherwise
        """
        idle_duration = self.get_idle_duration()
        return idle_duration > (self.idle_threshold / 1000)
