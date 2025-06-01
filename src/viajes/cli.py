"""
Command Line Interface for the RAG chatbot.
"""
import click
from . import config


@click.group()
def cli():
    """RAG Chatbot CLI - Manage and interact with the chatbot."""
    pass


@cli.command()
@click.option('--name', default='User', help='The name to greet')
def hello(name):
    """Simple command to test the CLI is working."""
    click.echo(f'Hello {name}! The configuration is loaded correctly.')
    # We can test that we have access to the configuration
    click.echo('OpenAI API Key is configured: ' + ('✓' if config.OPENAI_API_KEY else '✗'))
    click.echo('Supabase is configured: ' + ('✓' if config.SUPABASE_URL and config.SUPABASE_KEY else '✗'))
    click.echo('Langfuse is configured: ' + ('✓' if config.LANGFUSE_PUBLIC_KEY and config.LANGFUSE_SECRET_KEY else '✗'))


if __name__ == '__main__':
    cli()
