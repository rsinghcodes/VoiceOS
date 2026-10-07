"""
LiveKit Agents Worker Entrypoint.

Usage:
    python -m app.voice.livekit.entrypoint dev
    python -m app.voice.livekit.entrypoint start
"""

from livekit.agents import WorkerOptions, cli
from app.voice.livekit.agent import create_voice_agent


async def entrypoint(ctx):
    """Worker entrypoint called when a new room session is dispatched."""
    await create_voice_agent(ctx)


def main():
    """Run the LiveKit agent worker."""
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))


if __name__ == "__main__":
    main()
