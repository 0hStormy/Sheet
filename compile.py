import os
import shutil
from pathlib import Path

BASE_DIR = Path('.')
GTK_DIR = BASE_DIR / 'gtk-3.0'
ACCENT_DIR = GTK_DIR / 'accent'
SCHEME_DIR = GTK_DIR / 'scheme'
BUILD_DIR = BASE_DIR / 'dist'

STATIC_FILES = ['widgets.css']
ROOT_FILES = ['index.theme']

def get_css_files(directory):
    return [f for f in directory.glob('*.css')]

def format_name(name):
    return name.stem.capitalize()

def make_gtk_css(accent_file, scheme_file):
    return (
        '@import url("widgets.css");\n'
        f'@import url("accent/{accent_file.name}");\n'
        f'@import url("scheme/{scheme_file.name}");\n'
    )

def build_theme(accent, scheme):
    theme_name = f"Sheet-{format_name(accent)}-{format_name(scheme)}"
    theme_path = BUILD_DIR / theme_name
    gtk3_path = theme_path / 'gtk-3.0'
    gtk4_path = theme_path / 'gtk-4.0'

    print(f"🛠 Building {theme_name}")

    gtk3_path.mkdir(parents=True, exist_ok=True)

    # Copy static GTK files
    for file_name in STATIC_FILES:
        shutil.copy2(GTK_DIR / file_name, gtk3_path)

    # Copy selected accent and scheme
    accent_target = gtk3_path / 'accent'
    scheme_target = gtk3_path / 'scheme'
    accent_target.mkdir(exist_ok=True)
    scheme_target.mkdir(exist_ok=True)
    shutil.copy2(accent, accent_target / accent.name)
    shutil.copy2(scheme, scheme_target / scheme.name)

    # Write gtk.css
    gtk_css_path = gtk3_path / 'gtk.css'
    with open(gtk_css_path, 'w') as f:
        f.write(make_gtk_css(accent, scheme))

    # Create gtk-4.0 symlink or fallback copy
    if not gtk4_path.exists():
        try:
            gtk4_path.symlink_to('gtk-3.0', target_is_directory=True)
        except OSError:
            shutil.copytree(gtk3_path, gtk4_path)

    # Copy top-level files
    for file_name in ROOT_FILES:
        src = BASE_DIR / file_name
        if src.exists():
            shutil.copy2(src, theme_path / file_name)

    # Zip the theme folder
    zip_path = shutil.make_archive(str(theme_path), 'zip', root_dir=BUILD_DIR, base_dir=theme_name)
    print(f"Created zip: {zip_path}")

def main():
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir()

    accents = get_css_files(ACCENT_DIR)
    schemes = get_css_files(SCHEME_DIR)

    for accent in accents:
        for scheme in schemes:
            build_theme(accent, scheme)

    print("All themes built, zipped, and folders cleaned up.")

if __name__ == '__main__':
    main()
