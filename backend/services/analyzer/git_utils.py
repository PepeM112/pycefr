import configparser
from pathlib import Path


def get_remote_origin_url(directory: str | Path) -> str:
    """Extract the remote origin URL from a local .git/config, normalized to HTTPS."""
    git_config = Path(directory) / ".git" / "config"
    if not git_config.is_file():
        return ""
    config = configparser.ConfigParser()
    config.read(git_config)
    if 'remote "origin"' not in config:
        return ""
    url = config['remote "origin"'].get("url", "")
    if not url:
        return ""
    if url.startswith("git@"):
        url_part = url[4:]
        return "https://" + url_part.replace(":", "/", 1).removesuffix(".git")
    return url.removesuffix(".git")
