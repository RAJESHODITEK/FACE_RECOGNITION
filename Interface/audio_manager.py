import customtkinter as ctk
from tkinter import StringVar
from Core.Recognistion_process.ConfigLoader import ConfigLoader
from Core.audio import AudioController  # Import AudioController


class AudioManagerInterface(ctk.CTkFrame):
    def __init__(self, *args, root_width: int = 1920, root_height: int = 1080, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize AudioController (Singleton instance)
        self.audio_controller = AudioController()

        # Premium color scheme
        self.colors = {
            'bg_primary': "#1E1E2E",
            'bg_secondary': "#2A2A3C",
            'accent': "#7F3DFF",
            'accent_hover': "#6A2EE8",
            'text_primary': "#FFFFFF",
            'text_secondary': "#B4B4C7",
            'success': "#34D399",
            'error': "#EF4444"
        }

        self.configure(fg_color='#F1F5FA', corner_radius=0)
        self.config = ConfigLoader()

        # Calculate dimensions for a more balanced layout
        self.i_form_width = int(root_width * 0.85)
        self.i_form_height = int(root_height * 0.75)

        # Main form frame with gradient-like effect
        self.frame_form = ctk.CTkFrame(
            self,
            width=self.i_form_width,
            height=self.i_form_height,
            fg_color=self.colors['bg_secondary'],
            corner_radius=20,
            border_width=2,
            border_color=self.colors['accent']
        )
        self.frame_form.pack(side="top", expand=True, padx=40, pady=30)
        self.frame_form.grid_columnconfigure((0, 1), weight=1)

        # Enhanced heading with modern typography
        self.label_heading = ctk.CTkLabel(
            self.frame_form,
            text="Audio Manager",
            text_color=self.colors['text_primary'],
            font=("Helvetica", 32, "bold"),
            anchor="center"
        )
        self.label_heading.pack(pady=(25, 5))

        # Stylish subtitle
        self.label_below_heading = ctk.CTkLabel(
            self.frame_form,
            text="Experience superior sound control",
            text_color=self.colors['text_secondary'],
            font=("Helvetica", 16),
            anchor="center"
        )
        self.label_below_heading.pack(pady=(0, 20))

        # Create main content container
        self.content_frame = ctk.CTkFrame(
            self.frame_form,
            fg_color="transparent"
        )
        self.content_frame.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        self.content_frame.grid_columnconfigure((0, 1), weight=1, uniform="column")

        # Left Column (Audio Controls)
        self.left_column = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.colors['bg_primary'],
            corner_radius=15
        )
        self.left_column.grid(row=0, column=0, padx=15, pady=10, sticky="nsew")

        # Audio Controls Header
        self.label_controls = ctk.CTkLabel(
            self.left_column,
            text="Audio Controls",
            text_color=self.colors['text_primary'],
            font=("Helvetica", 22, "bold"),
            anchor="center"
        )
        self.label_controls.pack(padx=20, pady=(20, 15))

        # Enhanced Audio Toggle Button
        self.audio_toggle_button = ctk.CTkButton(
            self.left_column,
            text="Audio On",
            command=self.toggle_audio,
            width=180,
            height=40,
            corner_radius=20,
            fg_color=self.colors['success'],
            hover_color="#2AAA80",
            font=("Helvetica", 16, "bold")
        )
        self.audio_toggle_button.pack(padx=20, pady=15)

        # Volume Control with improved styling
        self.volume_label = ctk.CTkLabel(
            self.left_column,
            text="Volume Control",
            text_color=self.colors['text_secondary'],
            font=("Helvetica", 16)
        )
        self.volume_label.pack(padx=20, pady=(20, 5))

        self.volume_slider = ctk.CTkSlider(
            self.left_column,
            from_=0,
            to=100,
            command=self.adjust_volume,
            width=250,
            progress_color=self.colors['accent'],
            button_color=self.colors['accent'],
            button_hover_color=self.colors['accent_hover']
        )
        self.volume_slider.pack(padx=20, pady=10)
        self.volume_slider.set(50)

        # Track Selection with modern styling
        self.track_label = ctk.CTkLabel(
            self.left_column,
            text="Select Track",
            text_color=self.colors['text_secondary'],
            font=("Helvetica", 16)
        )
        self.track_label.pack(padx=20, pady=(20, 5))

        self.track_var = StringVar(value="Track 1")
        self.track_combobox = ctk.CTkComboBox(
            self.left_column,
            values=["Track 1", "Track 2", "Track 3"],
            variable=self.track_var,
            command=self.change_track,
            width=250,
            height=35,
            fg_color=self.colors['bg_secondary'],
            border_color=self.colors['accent'],
            button_color=self.colors['accent'],
            button_hover_color=self.colors['accent_hover'],
            dropdown_hover_color=self.colors['accent'],
            font=("Helvetica", 14)
        )
        self.track_combobox.pack(padx=20, pady=(5, 20))

        # Right Column (Player Controls)
        self.right_column = ctk.CTkFrame(
            self.content_frame,
            fg_color=self.colors['bg_primary'],
            corner_radius=15
        )
        self.right_column.grid(row=0, column=1, padx=15, pady=10, sticky="nsew")

        # Enhanced Track Info Display
        self.track_info_label = ctk.CTkLabel(
            self.right_column,
            text="Now Playing",
            text_color=self.colors['text_primary'],
            font=("Helvetica", 22, "bold")
        )
        self.track_info_label.pack(padx=20, pady=(20, 5))

        self.current_track_label = ctk.CTkLabel(
            self.right_column,
            text="Select a track to begin",
            text_color=self.colors['text_secondary'],
            font=("Helvetica", 16)
        )
        self.current_track_label.pack(padx=20, pady=(0, 20))

        # Stylish Play/Pause Button
        self.play_button = ctk.CTkButton(
            self.right_column,
            text="Play",
            command=self.toggle_play,
            width=180,
            height=40,
            corner_radius=20,
            fg_color=self.colors['accent'],
            hover_color=self.colors['accent_hover'],
            font=("Helvetica", 16, "bold")
        )
        self.play_button.pack(padx=20, pady=15)

        # Enhanced Timeline
        self.timeline_slider = ctk.CTkSlider(
            self.right_column,
            from_=0,
            to=100,
            command=self.update_time,
            width=250,
            progress_color=self.colors['accent'],
            button_color=self.colors['accent'],
            button_hover_color=self.colors['accent_hover']
        )
        self.timeline_slider.set(0)
        self.timeline_slider.pack(padx=20, pady=(20, 5))

        # Time Display
        self.current_time = StringVar(value="00:00")
        self.time_label = ctk.CTkLabel(
            self.right_column,
            textvariable=self.current_time,
            text_color=self.colors['text_secondary'],
            font=("Helvetica", 14)
        )
        self.time_label.pack(padx=20, pady=(5, 20))

        # Initialize audio state variables
        self.current_track = None
        self.is_playing = False
        self.audio = None
        self.initialize_audio_state()

    def initialize_audio_state(self):
        if self.config.get('audio', 'OFF') == 'ON':
            self.audio_toggle_button.configure(
                text="Audio On",
                fg_color=self.colors['success'],
                hover_color="#2AAA80"
            )
            self.is_playing = True
        else:
            self.audio_toggle_button.configure(
                text="Audio Off",
                fg_color=self.colors['error'],
                hover_color="#DC2626"
            )
            self.is_playing = False

    def toggle_audio(self):
        if self.audio_toggle_button._text == "Audio On":
            self.audio_toggle_button.configure(
                text="Audio Off",
                fg_color=self.colors['error'],
                hover_color="#DC2626"
            )
            self.config.update_json_key('audio', 'OFF')
            self.config._load_config()
            self.audio_controller.stop()  # Stop audio via controller
            self.is_playing = False
        else:
            self.audio_toggle_button.configure(
                text="Audio On",
                fg_color=self.colors['success'],
                hover_color="#2AAA80"
            )
            self.config.update_json_key('audio', 'ON')
            self.config._load_config()
            self.audio_controller.play()  # Start audio via controller
            self.is_playing = True

    def update_time(self, value):
        minutes = int(value // 60)
        seconds = int(value % 60)
        self.current_time.set(f"{minutes:02}:{seconds:02}")

    def toggle_play(self):
        if self.is_playing:
            self.audio_controller.stop()  # Pause audio via controller
            self.play_button.configure(text="Play")
        else:
            self.audio_controller.play()  # Resume audio via controller
            self.play_button.configure(text="Pause")

    def adjust_volume(self, volume):
        self.audio_controller.set_volume(volume / 100)  # Set volume via controller

    def change_track(self, track):
        track_paths = {
            "Track 1": "Resources/audio/track1.wav",
            "Track 2": "Resources/audio/track2.wav",
            "Track 3": "Resources/audio/track3.wav"
        }
        track_path = track_paths.get(track)
        if track_path:
            self.current_track_label.configure(text=f"Currently playing: {track}")
            self.audio_controller.change_audio(track_path)  # Change track via controller
            self.audio = track_path
            self.is_playing = True
            self.timeline_slider.set(0)
            self.current_time.set("00:00")
