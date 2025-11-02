#!/usr/bin/env python3
"""
AiProxy CLI Tool - Song Project Upload

Command-line tool for uploading files to Song Projects.
"""
import click
import requests
import json
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from datetime import datetime, UTC
import urllib3
import fnmatch

# Disable SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()
CONFIG_DIR = Path.home() / ".aiproxy"
CONFIG_FILE = CONFIG_DIR / "config.json"
GLOBAL_IGNORE_FILE = CONFIG_DIR / ".aiproxyignore"


# ============================================================
# Config Management (with 0600 permissions!)
# ============================================================


def load_config():
    """Load config from ~/.aiproxy/config.json"""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception as e:
            console.print(f"[red]✗ Error reading config file: {e}[/red]")
            return None
    return None


def save_config(config):
    """Save config with strict file permissions (0600)"""
    try:
        CONFIG_DIR.mkdir(exist_ok=True, mode=0o700)
        CONFIG_FILE.write_text(json.dumps(config, indent=2))
        os.chmod(CONFIG_FILE, 0o600)
        console.print(
            "[green]✓ Config saved to ~/.aiproxy/config.json (permissions: 0600)[/green]"
        )
    except Exception as e:
        console.print(f"[red]✗ Error saving config: {e}[/red]")
        sys.exit(1)


def load_ignore_patterns(upload_dir):
    """
    Load ignore patterns from .aiproxyignore files

    Checks two locations:
    1. ~/.aiproxy/.aiproxyignore (global)
    2. {upload_dir}/.aiproxyignore (local, higher priority)

    Returns list of patterns (glob-style like .gitignore)
    """
    patterns = []

    # Load global ignore file
    if GLOBAL_IGNORE_FILE.exists():
        try:
            for line in GLOBAL_IGNORE_FILE.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
        except Exception as e:
            console.print(f"[dim yellow]Warning: Could not read global .aiproxyignore: {e}[/dim yellow]")

    # Load local ignore file (in upload directory)
    local_ignore = Path(upload_dir) / ".aiproxyignore"
    if local_ignore.exists():
        try:
            for line in local_ignore.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.append(line)
        except Exception as e:
            console.print(f"[dim yellow]Warning: Could not read local .aiproxyignore: {e}[/dim yellow]")

    return patterns


def should_ignore(file_path, upload_dir, patterns):
    """
    Check if file should be ignored based on patterns

    Supports:
    - Exact match: .DS_Store
    - Wildcards: Icon*, *.tmp
    - Directories: node_modules/, .git/
    """
    if not patterns:
        return False

    # Get relative path from upload_dir
    try:
        rel_path = file_path.relative_to(upload_dir)
    except ValueError:
        # File is not relative to upload_dir
        return False

    # Check each pattern
    for pattern in patterns:
        # Directory pattern (ends with /)
        if pattern.endswith("/"):
            # Check if any parent directory matches
            for parent in rel_path.parents:
                if fnmatch.fnmatch(parent.name, pattern.rstrip("/")):
                    return True
        else:
            # File pattern - check filename and full relative path
            if fnmatch.fnmatch(file_path.name, pattern) or fnmatch.fnmatch(str(rel_path), pattern):
                return True

    return False


def check_token_expiry(config):
    """Check if JWT token is expired"""
    if "expires_at" not in config:
        return False

    try:
        expires_at_str = config["expires_at"]

        # Try ISO format first (e.g., "2024-11-03T10:30:00Z")
        try:
            expires_at = datetime.fromisoformat(
                expires_at_str.replace("Z", "+00:00")
            )
        except ValueError:
            # Try RFC 2822 format (e.g., "Mon, 03 Nov 2025 12:18:39 GMT")
            from email.utils import parsedate_to_datetime
            expires_at = parsedate_to_datetime(expires_at_str)

        if datetime.now(UTC) >= expires_at:
            console.print(
                "[yellow]⚠ Token expired. Please login again.[/yellow]"
            )
            return False
        return True
    except Exception as e:
        # If we can't parse the date, assume token is still valid
        # (better to let the backend reject it than block the user)
        console.print(f"[dim]Warning: Could not parse token expiry date: {e}[/dim]")
        return True


# ============================================================
# CLI Commands
# ============================================================


@click.group()
def cli():
    """AiProxy CLI Tool - Song Project Management"""
    pass


@cli.command()
@click.option(
    "--api-url",
    default=None,
    help="API base URL (overrides config file)",
)
def login(api_url):
    """Login and save JWT token"""
    console.print("[bold]AiProxy CLI Login[/bold]")

    # Load existing config to get API URL if not provided via --api-url
    if api_url is None:
        existing_config = load_config()
        if existing_config and "api_url" in existing_config:
            api_url = existing_config["api_url"]
            console.print(f"[dim]Using API URL from config: {api_url}[/dim]")
        else:
            api_url = "https://macstudio/aiproxysrv"
            console.print(f"[dim]No config found, using default: {api_url}[/dim]")

    console.print(f"API URL: [bold]{api_url}[/bold]\n")

    email = console.input("Email: ")
    password = console.input("Password: ", password=True)

    # Call login endpoint
    url = f"{api_url}/api/v1/user/login"

    try:
        with console.status("[bold green]Logging in...[/bold green]"):
            response = requests.post(
                url,
                json={"email": email, "password": password},
                verify=False,  # Self-signed cert
                timeout=30,
            )

        if response.status_code == 200:
            data = response.json()

            # Save config
            config = {
                "api_url": api_url,
                "jwt_token": data["token"],
                "email": email,
                "expires_at": data["expires_at"],
                "ssl_verify": False,
            }
            save_config(config)

            console.print("[green]✓ Login successful![/green]")
            console.print(f"[dim]Token expires: {data['expires_at']}[/dim]")

        else:
            error = response.json().get("error", "Unknown error")
            console.print(f"[red]✗ Login failed: {error}[/red]")
            sys.exit(1)

    except requests.exceptions.Timeout:
        console.print("[red]✗ Connection timeout[/red]")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        console.print(f"[red]✗ Connection error: Cannot reach {api_url}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("project_id")
@click.argument("folder_id")
@click.argument("local_path", type=click.Path(exists=True), default=".")
def upload(project_id, folder_id, local_path):
    """Upload files recursively to song project folder

    If local_path is omitted, uses current directory (.)

    Examples:
        aiproxy-cli upload <project-id> <folder-id> ~/Music/
        aiproxy-cli upload <project-id> <folder-id> .
        aiproxy-cli upload <project-id> <folder-id>  (uses current dir)
    """

    # Load config
    config = load_config()
    if not config:
        console.print(
            "[red]✗ Not logged in. Run: aiproxy-cli login[/red]"
        )
        sys.exit(1)

    # Check token expiry
    if not check_token_expiry(config):
        console.print("[yellow]Run: aiproxy-cli login[/yellow]")
        sys.exit(1)

    # Scan directory recursively
    local_path = Path(local_path)
    files = []
    ignored_files = []

    console.print(f"[bold]Scanning directory:[/bold] {local_path}")

    # Load ignore patterns
    ignore_patterns = load_ignore_patterns(local_path)
    if ignore_patterns:
        console.print(f"[dim]Loaded {len(ignore_patterns)} ignore patterns from .aiproxyignore[/dim]")

    for file_path in local_path.rglob("*"):
        if file_path.is_file():
            # Check if file should be ignored
            if should_ignore(file_path, local_path, ignore_patterns):
                ignored_files.append(file_path)
            else:
                files.append(file_path)

    if not files:
        console.print("[yellow]✗ No files found (or all files ignored)[/yellow]")
        if ignored_files:
            console.print(f"[dim]Ignored {len(ignored_files)} files based on .aiproxyignore[/dim]")
        sys.exit(0)

    total_size = sum(f.stat().st_size for f in files)
    console.print(
        f"Found [bold]{len(files)}[/bold] files "
        f"(total size: [bold]{total_size / (1024*1024):.1f} MB[/bold])"
    )
    if ignored_files:
        console.print(f"[dim]Ignored {len(ignored_files)} files based on .aiproxyignore[/dim]")
    console.print()

    # Upload files in batches (10 files per request for smoother progress)
    BATCH_SIZE = 10
    uploaded = 0
    failed = 0
    errors = []

    url = f"{config['api_url']}/api/v1/song-projects/{project_id}/folders/{folder_id}/batch-upload"
    headers = {"Authorization": f"Bearer {config['jwt_token']}"}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TextColumn("[bold blue]{task.completed}/{task.total}[/bold blue]"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:

        task = progress.add_task("Uploading files...", total=len(files))

        for i in range(0, len(files), BATCH_SIZE):
            batch = files[i : i + BATCH_SIZE]
            batch_start_index = i

            # Prepare multipart form data with relative paths
            file_objects = []
            relative_paths = []
            for f in batch:
                try:
                    # Calculate relative path from upload directory (preserves subdirectories)
                    rel_path = f.relative_to(local_path)
                    # Use forward slashes for cross-platform compatibility
                    rel_path_str = str(rel_path).replace("\\", "/")

                    file_objects.append(("files", (rel_path_str, open(f, "rb"))))
                    relative_paths.append(rel_path_str)
                except Exception as e:
                    failed += 1
                    errors.append({"filename": f.name, "error": f"Cannot read file: {str(e)}"})
                    progress.update(task, advance=1)
                    continue

            if not file_objects:
                continue

            # Update progress incrementally during batch upload
            # Advance progress by 1 file every time we process a file in the batch
            batch_files_processed = 0

            try:
                # Show intermediate progress while uploading
                progress.update(task, description=f"Uploading batch {i//BATCH_SIZE + 1}/{(len(files) + BATCH_SIZE - 1)//BATCH_SIZE}...")

                response = requests.post(
                    url,
                    files=file_objects,
                    headers=headers,
                    verify=config.get("ssl_verify", False),
                    timeout=600,  # 10min timeout for large uploads
                )

                # Close file handles
                for _, (_, fh) in file_objects:
                    try:
                        fh.close()
                    except Exception:
                        pass

                if response.status_code == 200:
                    result = response.json()["data"]
                    uploaded += result["uploaded"]
                    failed += result["failed"]
                    errors.extend(result["errors"])
                else:
                    # Batch upload failed
                    failed += len(batch)
                    error_msg = response.json().get("error", f"HTTP {response.status_code}")
                    errors.append({"error": f"Batch upload failed: {error_msg}"})

            except requests.exceptions.Timeout:
                failed += len(batch)
                errors.append({"error": "Request timeout (10min)"})
            except Exception as e:
                failed += len(batch)
                errors.append({"error": str(e)})

            # Advance progress by number of files in batch
            progress.update(task, advance=len(batch), description="Uploading files...")

    # Summary
    console.print("\n[bold]Upload Summary[/bold]")
    console.print(f"[green]✓ Uploaded:[/green] {uploaded} files")

    if failed > 0:
        console.print(f"[red]✗ Failed:[/red]   {failed} files")
        for error in errors[:10]:  # Show max 10 errors
            filename = error.get("filename", "Unknown")
            error_msg = error.get("error", "Unknown error")
            console.print(f"  [dim red]- {filename}: {error_msg}[/dim red]")

        if len(errors) > 10:
            console.print(
                f"  [dim]... and {len(errors) - 10} more errors[/dim]"
            )


@cli.command()
@click.argument("project_id")
@click.argument("folder_id")
@click.argument("local_path", type=click.Path(), default=".")
def download(project_id, folder_id, local_path):
    """Download all files from song project folder (reconstructs directory structure)

    If local_path is omitted, uses current directory (.)

    Examples:
        aiproxy-cli download <project-id> <folder-id> ~/Music/
        aiproxy-cli download <project-id> <folder-id> .
        aiproxy-cli download <project-id> <folder-id>  (uses current dir)
    """

    # Load config
    config = load_config()
    if not config:
        console.print(
            "[red]✗ Not logged in. Run: aiproxy-cli login[/red]"
        )
        sys.exit(1)

    # Check token expiry
    if not check_token_expiry(config):
        console.print("[yellow]Run: aiproxy-cli login[/yellow]")
        sys.exit(1)

    # Fetch file list from API
    url = f"{config['api_url']}/api/v1/song-projects/{project_id}/folders/{folder_id}/files"
    headers = {"Authorization": f"Bearer {config['jwt_token']}"}

    console.print(f"[bold]Fetching file list from server...[/bold]")

    try:
        response = requests.get(
            url,
            headers=headers,
            verify=config.get("ssl_verify", False),
            timeout=30,
        )

        if response.status_code != 200:
            error = response.json().get("error", f"HTTP {response.status_code}")
            console.print(f"[red]✗ Failed to fetch file list: {error}[/red]")
            sys.exit(1)

        files = response.json()["data"]

        if not files:
            console.print("[yellow]✗ No files found in folder[/yellow]")
            sys.exit(0)

        total_size = sum(f["file_size_bytes"] for f in files)
        console.print(
            f"Found [bold]{len(files)}[/bold] files "
            f"(total size: [bold]{total_size / (1024*1024):.1f} MB[/bold])"
        )
        console.print()

    except requests.exceptions.Timeout:
        console.print("[red]✗ Connection timeout[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗ Error: {str(e)}[/red]")
        sys.exit(1)

    # Download files with progress
    local_path = Path(local_path)
    downloaded = 0
    failed = 0
    errors = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TextColumn("[bold blue]{task.completed}/{task.total}[/bold blue]"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:

        task = progress.add_task("Downloading files...", total=len(files))

        for file in files:
            try:
                # Get relative path (e.g., "Media/drums.wav")
                relative_path = file["relative_path"]
                download_url = file["download_url"]

                # Remove folder name prefix (e.g., "01 Arrangement/Media/drums.wav" → "Media/drums.wav")
                # Folder name is everything before the first "/"
                if "/" in relative_path:
                    # Skip first component (folder name)
                    parts = relative_path.split("/", 1)
                    if len(parts) > 1:
                        relative_path = parts[1]

                # Create target path
                target_file = local_path / relative_path

                # Create subdirectories if needed
                target_file.parent.mkdir(parents=True, exist_ok=True)

                # Download file
                file_response = requests.get(
                    download_url,
                    verify=config.get("ssl_verify", False),
                    timeout=600,  # 10min timeout for large files
                    stream=True,
                )

                if file_response.status_code == 200:
                    with open(target_file, "wb") as f:
                        for chunk in file_response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    downloaded += 1
                else:
                    failed += 1
                    errors.append({
                        "filename": file["filename"],
                        "error": f"HTTP {file_response.status_code}"
                    })

            except Exception as e:
                failed += 1
                errors.append({
                    "filename": file.get("filename", "Unknown"),
                    "error": str(e)
                })

            progress.update(task, advance=1)

    # Summary
    console.print("\n[bold]Download Summary[/bold]")
    console.print(f"[green]✓ Downloaded:[/green] {downloaded} files")

    if failed > 0:
        console.print(f"[red]✗ Failed:[/red]     {failed} files")
        for error in errors[:10]:  # Show max 10 errors
            filename = error.get("filename", "Unknown")
            error_msg = error.get("error", "Unknown error")
            console.print(f"  [dim red]- {filename}: {error_msg}[/dim red]")

        if len(errors) > 10:
            console.print(
                f"  [dim]... and {len(errors) - 10} more errors[/dim]"
            )

    console.print(f"\n[dim]Files downloaded to: {local_path.absolute()}[/dim]")


if __name__ == "__main__":
    cli()
