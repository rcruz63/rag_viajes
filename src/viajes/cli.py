"""
Command Line Interface for the RAG chatbot.
"""

import tempfile
import click
from pathlib import Path
from pymupdf4llm import to_markdown
from . import config
import subprocess


@click.group()
def cli():
    """RAG Chatbot CLI - Manage and interact with the chatbot."""
    pass


@cli.command()
@click.option("--name", default="User", help="The name to greet")
def hello(name):
    """Simple command to test the CLI is working."""
    click.echo(f"Hello {name}! The configuration is loaded correctly.")
    # We can test that we have access to the configuration
    click.echo(
        "OpenAI API Key is configured: " + ("✓" if config.OPENAI_API_KEY else "✗")
    )
    click.echo(
        "Supabase is configured: "
        + ("✓" if config.SUPABASE_URL and config.SUPABASE_KEY else "✗")
    )
    click.echo(
        "Langfuse is configured: "
        + ("✓" if config.LANGFUSE_PUBLIC_KEY and config.LANGFUSE_SECRET_KEY else "✗")
    )


@cli.command()
@click.argument(
    "pdf_path", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory to save the Markdown file. If not provided, a temporary directory will be used.",
)
def convert_pdf_pymu(pdf_path: Path, output_dir: Path | None = None):
    """Convert a PDF file to Markdown using PyMuPDF.

    The output Markdown will preserve structure and page breaks.

    Args:
        pdf_path: Path to the PDF file to convert
        output_dir: Optional directory to save the output. If not provided, uses a temp directory
    """
    try:
        # If no output directory is provided, create a temporary one
        if output_dir is None:
            output_dir = Path(tempfile.mkdtemp())
        else:
            output_dir.mkdir(parents=True, exist_ok=True)

        # Generate the output filename
        output_file = output_dir / f"{pdf_path.stem}.md"

        # Convert PDF to Markdown using PyMuPDF
        pages_data = to_markdown(pdf_path, write_images=False, page_chunks=True)

        # Add title and format pages with markers
        title = f"# {pdf_path.stem}\n\n"
        formatted_pages = []
        for i, page_dict in enumerate(pages_data, 1):
            if isinstance(page_dict, dict):
                # Extraer el texto del diccionario de la página
                page_text = page_dict.get("text", "")
                # Solo añadir la página si tiene contenido de texto
                if page_text.strip():
                    page_content = f"<!-- PAGE {i} START -->\n\n{page_text}\n\n<!-- PAGE {i} END -->\n"
                    formatted_pages.append(page_content)

        # Combine all content
        final_content = title + "\n".join(formatted_pages)

        # Write the final content to file
        Path(output_file).write_text(final_content, encoding="utf-8")

        click.echo("Successfully converted PDF to Markdown!")
        click.echo(f"Output file: {output_file}")

    except Exception as e:
        click.echo(f"Error converting PDF: {str(e)}", err=True)
        raise click.Abort()


@cli.command()
@click.argument(
    "pdf_path", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory to save the Markdown file. If not provided, a temporary directory will be used.",
)
def convert_pdf_docetl(pdf_path: Path, output_dir: Path | None = None):
    """Convert a PDF file to Markdown using docetl CLI.

    The output Markdown will attempt to preserve tables and page breaks.
    """
    try:
        if output_dir is None:
            output_dir = Path(tempfile.mkdtemp())
        else:
            output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{pdf_path.stem}_docetl.md"

        # Run docetl CLI to convert PDF to Markdown
        # Assumes docetl is installed and available in PATH
        # Typical usage: docetl convert --input <pdf> --output <md> --format markdown
        cmd = [
            "docetl",
            "convert",
            "--input",
            str(pdf_path),
            "--output",
            str(output_file),
            "--format",
            "markdown",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            click.echo(f"docetl error: {result.stderr}", err=True)
            raise click.Abort()

        click.echo("Successfully converted PDF to Markdown with docetl!")
        click.echo(f"Output file: {output_file}")
    except FileNotFoundError:
        click.echo(
            "docetl is not installed or not found in PATH. Install it with: pip install docetl",
            err=True,
        )
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error converting PDF with docetl: {str(e)}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    cli()
