# Wyvern of Marina

**Wyvern of Marina** is an all‑in‑one Discord bot built with `discord.py` for the community server *The Marina*.  
It provides moderation utilities, a lightweight economy, birthday reminders, custom trigger/reaction behavior, and a structured help system.

While the implementation is public for learning and collaboration, the bot is primarily designed for this specific community server.

---

## Features

- **Custom command framework**  
  - Uses `discord.ext.commands` with a `!w` prefix and multiple cogs under `exts/` (fun, economy, admin, flair, birthday, music, misc, events).

- **Rich help system**  
  - Dynamically builds help embeds from text files in `docs/`.  
  - Organizes commands into pages (home, fun, economy, admin, flair, birthday, music, misc) with titles and descriptions.

- **Economy system**  
  - Tracks coins, bank balances, and karma for server members.  
  - Initializes new members with starting values and persists state.

- **Birthday automation**  
  - Stores user time zones and birthdays.  
  - Sends a celebratory message with a custom image and assigns/removes a birthday role automatically.

- **Reactive events & triggers**  
  - Responds to message content via configurable triggers, reactions, and reply phrases loaded from `docs/`.  
  - Includes message delete/edit “snipe” functionality with short‑lived in‑memory storage.

- **Presence & UX**  
  - Periodically rotates the bot’s game presence from a curated list.  
  - Custom join/leave flows and lightweight moderation feedback.

- **Health check endpoint**  
  - Optional HTTP `/health` route via `aiohttp` to integrate with uptime monitoring.

---

## Tech stack

- **Language**: Python (3.8–3.13)  
- **Discord**: `discord.py` (commands, cogs, intents)  
- **Web**: `aiohttp` (simple health server)  
- **Config**: `python-dotenv` for environment variable loading  
- **Data**: CSV files via `pandas` for persistent per‑user data

---

## Data & privacy

- User‑specific data (economy values, birthdays, etc.) is stored in CSV files under `csv/`.  
- These CSV files are **intentionally git‑ignored** and are **not** part of the public repository to avoid exposing any user information.  
- The repository only includes text assets needed to understand or extend the bot.

---

## Project structure (high level)

- `main.py` – bot bootstrap, help command, extension loading, health server  
- `exts/` – cogs for events, fun commands, economy, admin, flair, birthdays, music, etc.  
- `utils.py` – shared utilities, state management, and helper functions  
- `docs/` – text assets for help pages, triggers, messages, and other configuration‑like data  
- `img/` – static images used by the bot (e.g., birthday GIFs)

---

### License

This project is licensed under **Creative Commons Attribution–NoDerivatives 4.0 International (CC BY‑ND 4.0)**.  
See `LICENSE` for the full license text.
