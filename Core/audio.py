import threading
import queue
import pygame
import time


class AudioController:
    """Manages audio playback using Pygame."""
    _instance = None  # Holds the single instance of the class

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of AudioController exists."""
        if not cls._instance:
            cls._instance = super(AudioController, cls).__new__(cls, *args, **kwargs)
            pygame.mixer.init()
            cls._instance.audio_file = 'Resources/audio/track1.wav'
            cls._instance.sound = pygame.mixer.Sound(cls._instance.audio_file)
            cls._instance.volume = 1.0
            cls._instance.is_playing = False
            cls._instance.is_muted = False
        return cls._instance

    def play(self, loops=-1):
        """Play the audio in a loop."""
        if not self.is_playing:
            self.sound.play(loops=loops)
            self.is_playing = True

    def stop(self):
        """Stop the audio if playing."""
        if self.is_playing:
            self.sound.stop()
            self.is_playing = False

    def mute(self):
        """Mute the audio."""
        self.sound.set_volume(0)
        self.is_muted = True

    def unmute(self):
        """Unmute the audio."""
        self.sound.set_volume(self.volume)
        self.is_muted = False

    def set_volume(self, volume):
        """Set the audio volume."""
        self.volume = volume
        if not self.is_muted:
            self.sound.set_volume(volume)

    def change_audio(self, new_file):
        """Change the current audio file."""
        self.stop()
        self.audio_file = new_file
        self.sound = pygame.mixer.Sound(new_file)
        self.set_volume(self.volume)


class AudioThreadManager:
    """Manages audio playback commands in a separate thread."""
    _instance = None  # Holds the single instance of the class

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of AudioThreadManager exists."""
        if not cls._instance:
            cls._instance = super(AudioThreadManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.audio_controller = AudioController()  # Singleton instance of AudioController
            cls._instance.command_queue = queue.Queue()
        return cls._instance

    def run(self):
        """Main loop to process commands."""
        while True:
            command = self.command_queue.get()  # Wait indefinitely for a command
            if command == "play":
                print("triggered")
                self.audio_controller.play()
            elif command == "stop":
                self.audio_controller.stop()
            elif command.startswith("play_with_duration"):
                _, duration = command.split(":")
                self.audio_controller.play()
                time.sleep(int(duration))
                self.audio_controller.stop()
            elif command == "mute":
                self.audio_controller.mute()
            elif command == "unmute":
                self.audio_controller.unmute()
            elif command.startswith("set_volume"):
                _, volume = command.split(":")
                self.audio_controller.set_volume(float(volume))
            elif command.startswith("change_audio"):
                _, new_file = command.split(":")
                self.audio_controller.change_audio(new_file)
            elif command == "quit":
                self.audio_controller.stop()
                break

    def send_command(self, command):
        """Send a command to the audio controller."""
        self.command_queue.put(command)
