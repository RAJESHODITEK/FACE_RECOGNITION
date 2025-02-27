import customtkinter as ctk
from PIL import Image
import webbrowser

# Set default appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Premium Movie Hub")

        # Set window size to 80% of screen dimensions and center it
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)

        # Calculate position for center of screen
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        # Set window size and position
        self.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Configure colors
        self.netflix_red = "#E50914"
        self.dark_bg = "#141414"
        self.card_bg = "#1F1F1F"
        self.hover_bg = "#2D2D2D"

        # Movie categories with links and descriptions
        self.movie_categories = {
            "Latest Movies": {
                "link": "https://filmyzilla.net.pl/category/398/2025-latest-bollywood-movies/default/1.html",
                "description": "Fresh releases straight from the cinema",
                "icon": "🎬"
            },
            "Netflix Series": {
                "link": "https://filmyzilla.net.pl/category/Tv-shows.html",
                "description": "Binge-worthy shows and series",
                "icon": "📺"
            },
            "Bollywood Movies": {
                "link": "https://filmyzilla.net.pl/category/398/2025-latest-bollywood-movies/default/1.html",
                "description": "Best of Indian cinema",
                "icon": "🎭"
            },
            "Hollywood Movies": {
                "link": "https://filmyzilla.net.pl/category/400/2025-latest-hollywood-hindi-dubbed-movies/default/1.html",
                "description": "Blockbusters and classics",
                "icon": "🌟"
            },
            "Tamil Movies": {
                "link": "https://filmyzilla.net.pl/category/399/2025-latest-south-indian-hindi-dubbed-movies/default/1.html",
                "description": "South Indian cinema excellence",
                "icon": "🎪"
            }
        }

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Set window background
        self.configure(fg_color=self.dark_bg)

        # Create main interface
        self.create_interface()

    def open_movie_link(self, url):
        webbrowser.open(url)

    def create_interface(self):
        # Create main scrollable container
        main_container = ctk.CTkScrollableFrame(self, fg_color=self.dark_bg)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Header section
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(20, 40))

        try:
            logo_image = ctk.CTkImage(Image.open("logo.png"), size=(60, 60))
            logo_label = ctk.CTkLabel(header_frame, image=logo_image, text="")
            logo_label.pack(side="left", padx=20)
        except:
            pass

        ctk.CTkLabel(
            header_frame,
            text="PREMIUM MOVIE HUB",
            font=("Arial Black", 40, "bold"),
            text_color=self.netflix_red
        ).pack(side="left", padx=20)

        # Create movie grid
        movie_grid = ctk.CTkFrame(main_container, fg_color="transparent")
        movie_grid.pack(fill="x", padx=20)
        movie_grid.grid_columnconfigure((0, 1, 2), weight=1)

        # Create movie cards
        for idx, (title, info) in enumerate(self.movie_categories.items()):
            row = idx // 3
            col = idx % 3

            # Create card frame
            card = ctk.CTkFrame(
                movie_grid,
                fg_color=self.card_bg,
                corner_radius=15
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

            # Make cards expand properly
            card.grid_columnconfigure(0, weight=1)

            # Icon and title
            title_frame = ctk.CTkFrame(card, fg_color="transparent")
            title_frame.pack(fill="x", padx=20, pady=(20, 10))

            ctk.CTkLabel(
                title_frame,
                text=info["icon"],
                font=("Arial", 40)
            ).pack(side="left", padx=(0, 10))

            ctk.CTkLabel(
                title_frame,
                text=title,
                font=("Arial Black", 24, "bold"),
                text_color=self.netflix_red
            ).pack(side="left")

            # Description
            ctk.CTkLabel(
                card,
                text=info["description"],
                font=("Arial", 16),
                wraplength=300
            ).pack(fill="x", padx=20, pady=(0, 20))

            # Watch button
            ctk.CTkButton(
                card,
                text="WATCH NOW",
                command=lambda l=info["link"]: self.open_movie_link(l),
                fg_color=self.netflix_red,
                hover_color="#FF0F1A",
                height=40,
                corner_radius=20,
                font=("Arial Black", 14)
            ).pack(padx=20, pady=(0, 20), fill="x")


if __name__ == "__main__":
    app = App()
    app.mainloop()