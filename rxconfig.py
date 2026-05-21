import reflex as rx

config = rx.Config(
    app_name="reflex_clash",
    # Use this format for SQLite in production
    db_url="sqlite:///reflex.db", 
    plugins=[
        rx.plugins.RadixThemesPlugin(),
        rx.plugins.SitemapPlugin(),
    ],
)
