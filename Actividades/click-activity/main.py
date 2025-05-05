import click
from datetime import datetime
import time
import pyfiglet
import requests
import random

@click.group()
def cli():
    pass

@cli.command()
@click.option("--count", default=1, help="Number of greetings.")
@click.option("--name", prompt="Your name", help="The person to greet.")
def hello(count, name):
    """Greets a person a specified number of times."""
    for _ in range(count):
        click.echo(f"Hello, {name}!")

@cli.command()
def currenttime():
    """Print the current time."""
    now = datetime.now()
    click.echo(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

@cli.command()
@click.option('--duration', type=int, help="Duration to run the clock in seconds. If omitted, runs indefinitely.")
def clock(duration):
    """Display a live updating clock with ASCII art."""
    start_time = time.time()
    figlet = pyfiglet.Figlet(font='big')  # puedes cambiar el estilo del arte aquí

    try:
        while True:
            now = datetime.now()
            time_str = now.strftime('%H:%M:%S')
            ascii_art = figlet.renderText(time_str)

            click.clear()
            click.echo(ascii_art)
            time.sleep(1)

            if duration and (time.time() - start_time) >= duration:
                break
    except KeyboardInterrupt:
        click.echo("\nClock stopped manually.")
        #la excepcion se lanza cuando el usuario presiona Ctrl+C
    finally:
        click.echo("\nGoodbye!")


@cli.command()
def randomquote():
    """Get a random inspirational quote from the internet or fallback to a local quote."""
    local_quotes = [
    ("死を恐れるな。失敗を恐れよ。", "Miyamoto Musashi"),
    ("死は人生の反対ではなく、その一部である。", "Haruki Murakami"),
    ("完璧な行為は、瞬間に宿る。", "Yukio Mishima"),
    ("人間は、いつだって自分自身を欺いて生きる。", "Ryūnosuke Akutagawa"),
    ("人はいつでも一番大切なことを忘れる。", "Yasunari Kawabata"),
    ("空にある星のように、見えないものこそ大切だ。", "Kenji Miyazawa"),
    ("Wer ein Warum zum Leben hat, erträgt fast jedes Wie.", "Friedrich Nietzsche"),
    ("Phantasie ist wichtiger als Wissen, denn Wissen ist begrenzt.", "Albert Einstein"),
    ("Leben heißt, sich langsam zu gebären.", "Rainer Maria Rilke"),
    ("Man sieht nur mit dem Herzen gut. Das Wesentliche ist für die Augen unsichtbar.", "Johann Wolfgang von Goethe"),
    ("Die Antwort liegt im Fragen.", "Rainer Maria Rilke"),
    ("Der Weg ist das Ziel.", "Hermann Hesse"),
    ("Тайна человеческого бытия не в том, чтобы просто жить, а в том, для чего жить.", "Fjodor Dostojewski"),
    ("Человек велик не тем, что он имеет, а тем, кем он является.", "Leo Tolstoy"),
    ("Человек без цели — как корабль без руля.", "Anton Chekhov"),
    ("Я верю, что самая трудная борьба — это борьба с самим собой.", "Boris Pasternak"),
    ("Смерть — это не конец, это только начало.", "Anna Akhmatova"),
    ("Слова — это не просто звуки, это бесконечность в каждом из них.", "Vladimir Nabokov"),
    ]

    try:
        response = requests.get('https://api.quotable.io/random', timeout=5)
        if response.status_code == 200:
            data = response.json()
            quote = data['content']
            author = data['author']
            click.echo(f'✨ "{quote}"\n- {author}')
        else:
            raise Exception("API Error")
    except (requests.RequestException, Exception):
        # If there is any problem, choose a random local quote
        quote, author = random.choice(local_quotes)
        click.echo(' No internet connection. Showing a local quote:')
        click.echo(f'✨ "{quote}"\n- {author}')




if __name__ == '__main__':
    cli()

